from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import base64
import tempfile
import subprocess
import os
import json

app = FastAPI()

class SBOMRequest(BaseModel):
    file: str  # base64-encoded SBOM content

@app.post("/check-sbom")
async def check_sbom(request: SBOMRequest):
    try:
        # Decode the base64 file string
        file_content = base64.b64decode(request.file)
    except Exception as e:
        return JSONResponse(status_code=400, content={
            "error": "Invalid base64 input",
            "details": str(e)
        })

    # Try to guess the file type by sniffing the content
    if file_content.lstrip().startswith(b"{"):
        suffix = ".json"
    elif file_content.lstrip().startswith(b"<?xml"):
        suffix = ".xml"
    else:
        suffix = ".spdx"

    # Save to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name

    try:
        # Run osv-scanner with --sbom
        result = subprocess.run(
            ["osv-scanner", f"--sbom={tmp_path}", "--json"],
            capture_output=True,
            text=True,
            check=True
        )
        output = json.loads(result.stdout)
        return JSONResponse(content=output)

    except subprocess.CalledProcessError as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Failed to scan SBOM",
                "command": e.cmd,
                "stdout": e.stdout,
                "stderr": e.stderr
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Unexpected error", "details": str(e)}
        )
    finally:
        # Always clean up the temp file
        os.remove(tmp_path)