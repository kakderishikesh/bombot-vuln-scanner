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
        # Decode the base64-encoded SBOM content
        file_content = base64.b64decode(request.file)
    except Exception as e:
        return JSONResponse(status_code=400, content={
            "error": "Invalid base64 input",
            "details": str(e)
        })

    # Determine file type from content
    if file_content.lstrip().startswith(b"{"):
        suffix = ".json"
    elif file_content.lstrip().startswith(b"<?xml"):
        suffix = ".xml"
    else:
        suffix = ".spdx"

    # Save decoded content to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name

    try:
        # Run osv-scanner with the temp SBOM file
        result = subprocess.run(
            ["osv-scanner", f"--sbom={tmp_path}", "--format", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        output = json.loads(result.stdout)
        return JSONResponse(content=output)

    except FileNotFoundError:
        return JSONResponse(
            status_code=500,
            content={"error": "osv-scanner not found. Make sure it is installed and in the PATH."}
        )

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
        # Clean up the temporary file
        os.remove(tmp_path)