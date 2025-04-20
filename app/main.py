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
        file_content = base64.b64decode(request.file)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": "Invalid base64 input", "details": str(e)})

    # Guess file type from content (basic heuristic)
    if file_content.lstrip().startswith(b"<?xml"):
        suffix = ".xml"
    elif file_content.lstrip().startswith(b"{"):
        suffix = ".json"
    else:
        suffix = ".spdx"  # Assume SPDX tag-value

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name

    try:
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
    finally:
        os.remove(tmp_path)