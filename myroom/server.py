from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from core import encode, apply, to_numpy, Environment
from stt import to_text
from pydantic import BaseModel
import os
import uvicorn
from uuid import uuid4
from datetime import datetime
import threading
from models import Query
from models import Furniture as Fur
import util
from fewshot import update_fallbacks
lock = threading.Lock()

class Furniture(BaseModel):
    id: int
    x: int
    y: int
    r: int

class RequestData(BaseModel):
    current: list[Furniture]
    message: str

update_fallbacks()

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
    print("\n\n*********************************************************\n")
    env = Environment()
    instance_id = 100
    for d in data.current:
        new_instance = Fur(d.id, instance_id, d.x, d.y, d.r)
        env.add(new_instance)
        instance_id += 1
    start_env = to_numpy(env)
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
            "concept": 0,
            "add": [], "edit": [], "del": []
        })
    queries = Query.refine_queries(query_strs)
    queries = Query.filter_queries(env, queries)
    concept = list(filter(lambda x: x.mode == 'C', queries))
    concept = concept[-1].object_id if len(concept) > 0 else 0
    _add, _edit, _del = Query.invoke_queries(env, queries, apply)
    room = to_numpy(env)
    util.print_list("=== 초기 방 모습 ===", start_env)
    util.print_list("=== 최종 방 모습 ===", room)
    util.print_list("req:", query_strs)
    util.print_list("_add:", _add)
    util.print_list("_edit:", _edit)
    util.print_list("_del:", _del)
    print("_concept:", concept)
    
    return JSONResponse({ 
        "message": ", ".join(query_strs),
        "concept": concept,
        "add": _add, "edit": _edit, "del": _del
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
