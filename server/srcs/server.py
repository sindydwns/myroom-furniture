from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from stt import to_text
from myroom import RequestData
import os
import uvicorn
from uuid import uuid4
from datetime import datetime

app = FastAPI()

os.makedirs("upload", exist_ok=True)

@app.get("/")
async def root():
    return {"message": "hi"}

@app.post("/api/v1/stt")
async def stt(audio: UploadFile):
    path = datetime.now().strftime(f"upload/v_%m%d_%H%M%S_")
    path += f"{str(uuid4()).split('-')[0]}_{audio.filename}"
    with open(path, "wb") as f:
        f.write(audio.file.read())
    text = to_text(path)
    return JSONResponse({"text": text})

@app.post("/api/v1/prediction")
async def predict(data: RequestData):
    print(data.current[0])
    return JSONResponse({
        "message": "샘플데이터 입니다. 구석에 테스트 물품 하나를 배치했습니다.",
        "add": [
            {"id": 1, "x": 0, "y": 0, "r": 0}
        ]
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)