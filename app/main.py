from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import base64
import tempfile
import subprocess
import os
import json

app = FastAPI()

@app.post("/check-sbom")
async def check_sbom(request: Request):
    data = await request.json()
    file_content = base64.b64decode(data["file"])

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
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
            content={"error": "Failed to scan SBOM", "details": e.stderr}
        )
    finally:
        os.remove(tmp_path)