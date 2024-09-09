from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from myroom import encode, apply, Environment
from stt import to_text
from pydantic import BaseModel
import os
import uvicorn
from uuid import uuid4
from datetime import datetime
import threading
lock = threading.Lock()

class Furniture(BaseModel):
    id: int
    x: int
    y: int
    r: int

class RequestData(BaseModel):
    current: list[Furniture]
    message: str

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
    env = Environment()
    instance_id = 100
    for d in data.current:
        env.add(d.id, instance_id, d.x, d.y, d.r)
        instance_id += 1
    _add = []
    _edit = []
    _del = []
    try:
        m, ms = encode(data.message, env)
        queries = m.split("\n")
    except BaseException as e:
        print(data.message)
        return JSONResponse({ 
            "message": "no request",
            "add": _add, "edit": _edit, "del": _del
        })
    for query in queries:
        try:
            if query.startswith("D"):
                _del.append(apply(env, query))
            if query.startswith("E"):
                _edit.append(apply(env, query))
            if query.startswith("A"):
                _add.append(apply(env, query))
        except BaseException as e:
            print("error:", e)
            continue
    return JSONResponse({ 
        "message": ", ".join(queries),
        "add": _add, "edit": _edit, "del": _del
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
