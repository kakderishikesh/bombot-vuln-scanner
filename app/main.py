from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
import os
import json
import tempfile
import subprocess

app = FastAPI()

@app.post("/check-sbom")
async def check_sbom(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        # Run osv-scanner on the file
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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)