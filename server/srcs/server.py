from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from myroom import encode, Environment
from util import parse
from stt import to_text
from pydantic import BaseModel
import os
import uvicorn
from uuid import uuid4
from datetime import datetime
import random
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
    print(data.current[0])
    return JSONResponse({
        "message": "샘플데이터 입니다. 구석에 테스트 물품 하나를 배치했습니다.",
        "add": [
            {"id": 1, "x": 0, "y": 0, "r": 0}
        ]
    })

app.mount("/static", StaticFiles(directory="resources/map"), name="static")

@app.get("/sample")
async def sample():
    
    
    folder_dir = "resources/presets"
    files = [f for f in os.listdir(folder_dir) if os.path.isfile(os.path.join(folder_dir, f))]
    random_file = random.choice(files)
    env = Environment(random_file)
    request_query = "침대 뺴" ##############################################################
    content, _ = encode(request_query, env)
    cmds = content.split("\n")
    return JSONResponse({
        "cmd": parse(cmds[0]),
        "cmd_str": cmds[0],
        "env": env.to_list(),
        "env_name": random_file
    })

class Answer(BaseModel):
    object_id: int
    instance_id: int
    x: int
    y: int
    r: int

class Trainset(BaseModel):
    res: Answer
    cmd: str
    env_file: str

@app.post("/trainset")
async def add_trainset(data: Trainset):
    # res=Answer(id=100, x=3, y=0, r=0) cmd='A100 100' env_file='single_bed.csv'
    lock.acquire()
    res = data.res
    env = Environment(data.env_file, ignore_base=True)
    env.objs = env.objs[env.objs["instance_id"] != res.instance_id]
    if res.instance_id == 999:
        res.instance_id = int(data.cmd.split(" ")[1])
    env.add(res.object_id, res.instance_id, res.x, res.y, res.r)
    new_env_file = env.save()
    with open("resources/dataset/data.csv", "+a") as file:
        file.write(f"{res.object_id},{res.instance_id},{res.x},{res.y},{res.r},{data.env_file},{new_env_file},{data.cmd}\n")
    lock.release()
    pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
