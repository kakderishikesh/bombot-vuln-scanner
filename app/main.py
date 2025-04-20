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
        # Decode base64-encoded content
        file_content = base64.b64decode(request.file)
    except Exception as e:
        return JSONResponse(status_code=400, content={
            "error": "Invalid base64 input",
            "details": str(e)
        })

    # Determine the file extension
    if request.extension:
        suffix = f".{request.extension.strip('.')}"
    else:
        if b"spdxVersion" in file_content:
            suffix = ".spdx.json"
        elif b"bomFormat" in file_content and b"cyclonedx" in file_content.lower():
            suffix = ".cdx.json"
        elif file_content.lstrip().startswith(b"<?xml"):
            suffix = ".spdx.xml"
        else:
            suffix = ".json"

    # Write the content to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name

    try:
        # Run osv-scanner without check=True
        result = subprocess.run(
            ["osv-scanner", f"--sbom={tmp_path}", "--format", "json"],
            capture_output=True,
            text=True
        )

        # Try to parse output even if exit code is non-zero
        try:
            output = json.loads(result.stdout)
            return JSONResponse(content=output)
        except json.JSONDecodeError:
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Failed to parse osv-scanner output",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            )

    except FileNotFoundError:
        return JSONResponse(
            status_code=500,
            content={"error": "osv-scanner not found. Make sure it is installed and in the PATH."}
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Unexpected error", "details": str(e)}
        )

    finally:
        os.remove(tmp_path)