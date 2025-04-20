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
    extension: str | None = None  # optional file extension override (e.g., "spdx.json")

@app.post("/check-sbom")
async def check_sbom(request: SBOMRequest):
    try:
        # Decode the base64-encoded content
        file_content = base64.b64decode(request.file)
    except Exception as e:
        return JSONResponse(status_code=400, content={
            "error": "Invalid base64 input",
            "details": str(e)
        })

    # Determine file extension
    if request.extension:
        suffix = f".{request.extension.strip('.')}"
    else:
        # Try to guess the format from content
        if b"spdxVersion" in file_content:
            suffix = ".spdx.json"
        elif b"bomFormat" in file_content and b"cyclonedx" in file_content.lower():
            suffix = ".cdx.json"
        elif file_content.lstrip().startswith(b"<?xml"):
            suffix = ".spdx.xml"
        else:
            suffix = ".json"

    # Save the decoded content to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name

    try:
        # Run osv-scanner with appropriate format
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
        os.remove(tmp_path)