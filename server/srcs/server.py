from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from myroom import encode, apply, to_numpy, Environment
from stt import to_text
from pydantic import BaseModel
import os
import uvicorn
from uuid import uuid4
from datetime import datetime
import threading
from models import Query
import util
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
        m, _ = encode(data.message, env)
        query_strs = m.split("\n")
    except BaseException as e:
        print(data.message, e)
        return JSONResponse({ 
            "message": "no request",
            "add": _add, "edit": _edit, "del": _del
        })
    queries = Query.refine_queries(query_strs)
    for query in queries:
        query_res = apply(env, query)
        if query_res is None:
            continue
        if query.mode == 'D':
            _del.append(query_res)
        if query.mode == 'E':
            _edit.append(query_res)
        if query.mode == 'A':
            _add.append(query_res)
    room = to_numpy(env)
    util.print_list("=== 최종 방 모습 ===", room)
    return JSONResponse({ 
        "message": ", ".join(query_strs),
        "add": _add, "edit": _edit, "del": _del
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
