from openai import OpenAI
import os
import util
import numpy as np
import math
from models import Furniture, Environment, Location, Query, database
    
client = OpenAI()
if "MODEL" in os.environ:
    model = os.environ["MODEL"]
else:
    model = "gpt-4o"
print("model:", model)

system_prompt = util.read_file_to_text("resources/prompt.txt")
fewshot = util.read_file_to_text("resources/fewshot.txt")

def to_numpy(env: Environment):
    room_instance = env.get(1)
    room = np.zeros((room_instance.meta.h, room_instance.meta.w), dtype=np.int32)
    for o in env.to_list():
        i, id, x, y, r = o.object_id, o.instance_id, o.x, o.y, o.r
        meta = database.get(i)
        w, h = meta.w if r % 2 == 0 else meta.h, meta.h if r % 2 == 0 else meta.w
        for xx in range(x, x + w):
            for yy in range(y, y + h):
                if i >= 100:
                    room[yy, xx] = i * 1000 + id
    return room
    
        
def encode(q, env: Environment):
    query_prompt = "사용자의 요청: " + q
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": fewshot},
        {"role": "system", "content": "\n*** 메타데이타_정보.csv ***\n" + database.to_csv()},
        {"role": "system", "content": "\n*** 환경정보.csv ***\n" + env.to_csv()},
        {"role": "user", "content": query_prompt},
    ]
    completion = client.chat.completions.create(model=model, messages=messages, temperature=0)
    content = completion.choices[0].message.content
    role = completion.choices[0].message.role
    strip_content = "\n".join([c.strip() for c in content.split("\n")])
    new_message = {"role": role, "content": strip_content}
    messages.append(new_message)
    return strip_content, messages

def place_zero(room: np, item: Furniture):
    for w in range(item.w):
        for h in range(item.h):
            x = item.x
            y = item.y
            if x + w < room.shape[1] and y + h < room.shape[0]:
                room[y + h, x + w] = 0

def calc_cell_score(env: Environment, loc: Location, weight: float = 1.) -> list:
    
    room_instance = env.get(1)
    room = np.zeros((room_instance.meta.h, room_instance.meta.w), dtype=np.float32)
    
    item_instance = env.get(loc.instance_id)

    center_x = item_instance.x + item_instance.w / 2 - 0.5
    center_y = item_instance.y + item_instance.h / 2 - 0.5
    c = (center_x, center_y)
    max_len = math.sqrt(pow(room.shape[1], 2) + pow(room.shape[0], 2))
    
    for w in range(room_instance.meta.w):
        for h in range(room_instance.meta.h):
            p = (w, h)
            score = math.dist(c, p) / max_len
            ghost = item_instance.instance_id < 100
            if loc.code == "ne" or loc.code == "in" or loc.code == "ce":
                score = 1 - score
            elif loc.code == "fa":
                pass
            elif loc.code == "le":
                score = 1 - score if ghost or w - item_instance.x < h - item_instance.y else 0
            elif loc.code == "ri":
                score = 1 - score if ghost or w - item_instance.x > h - item_instance.y else 0
            elif loc.code == "on":
                th = room.shape[0] - 1 - h
                iy = room.shape[0] - 1 - item_instance.y
                score = 1 - score if ghost or w - item_instance.x < th - iy else 0
            elif loc.code == "un":
                th = room.shape[0] - 1 - h
                iy = room.shape[0] - 1 - item_instance.y
                score = 1 - score if ghost or w - item_instance.x > th - iy else 0
            elif loc.code == "fr":
                if item_instance.r == 0:
                    score = 1 - score if ghost or h > item_instance.y else 0
                elif item_instance.r == 1:
                    score = 1 - score if ghost or w < item_instance.x else 0
                elif item_instance.r == 2:
                    score = 1 - score if ghost or h < item_instance.y else 0
                elif item_instance.r == 3:
                    score = 1 - score if ghost or w > item_instance.x else 0
            elif loc.code == "ba":
                if item_instance.r == 0:
                    score = 1 - score if ghost or h > item_instance.y else 0
                elif item_instance.r == 1:
                    score = 1 - score if ghost or w < item_instance.x else 0
                elif item_instance.r == 2:
                    score = 1 - score if ghost or h > item_instance.y else 0
                elif item_instance.r == 3:
                    score = 1 - score if ghost or w < item_instance.x else 0
            room[h, w] = score * weight
    return room

def find_candidate_cell(room: np, item: Furniture):
    res = []
    for room_y in range(room.shape[0]):
        for room_x in range(room.shape[1]):
            score = 0
            err = False
            for item_y in range(item.h):
                for item_x in range(item.w):
                    y = room_y + item_y
                    x = room_x + item_x
                    if x >= room.shape[1] or y >= room.shape[0] or room[y, x] == 0:
                        err = True
                        break
                    score += room[y, x].item()
                if err:
                    break
            if not err:
                res.append({"score": score, "x": room_x, "y": room_y})
    return res
                    
def apply(env: Environment, query: Query):
    print(f"\n--------- {query.query_str} ---------")
    if query.mode == "D":
        target_instance = env.get(query.instance_id)
        target_instance.ghost = True
        util.print_list("(result)", [str(x) for x in env.to_list()])
        return {
            "id": query.meta.object_id,
            "idx": target_instance.instance_id - 100,
            "x": target_instance.x,
            "y": target_instance.y,
            "r": target_instance.r
        }

    target_instance = env.get(query.instance_id)
    if target_instance is not None:
        target_instance.ghost = True
    if target_instance is None and query.mode in ['E', 'D']:
        print("(error)", "수정 또는 삭제 불가")
        return None

    room_instance = env.get(1)
    room = np.ones((room_instance.meta.h, room_instance.meta.w), dtype=np.float32)
    for item in env.to_list(lambda x: x.ghost == False):
        place_zero(room, item)

    if query.mode == 'E':
        room *= calc_cell_score(env, Location(f"ne{target_instance.instance_id}"), 0.1)
    for location in query.locations:
        room *= calc_cell_score(env, location)

    new_instance = Furniture(query.meta.object_id, query.instance_id, 0, 0, 0)
    if query.rotation_manual:
        new_instance.rotate(query.rotation)

    cells = find_candidate_cell(room, new_instance)
    cells = sorted(cells, key=lambda x: x["score"], reverse=True)
    if len(cells) == 0:
        print("(error)", "불가능한 요청")
        return None
    cell = cells[0]
    new_instance.x = cell["x"]
    new_instance.y = cell["y"]
    env.add(new_instance)
    util.print_list("(score)", room)
    util.print_list("(result)", [str(x) for x in env.to_list()])
    
    if query.mode == 'A':
        return {
            "id":query.meta.object_id,
            "idx":-1,
            "x": cell["x"], "y": cell["y"], "r": new_instance.r,
        }
    else:
        return {
            "id":query.meta.object_id,
            "idx":new_instance.instance_id - 100,
            "x": cell["x"], "y": cell["y"], "r": new_instance.r,
        }
        
def test_cmd(env: Environment, queries: list[Query]):
    before = to_numpy(env)
    util.print_list("query list:", queries)
    _add, _edit, _del = Query.invoke_queries(env, queries, apply)
    res = [*_add, *_edit, *_del]
    env.remove(lambda x: x.object_id < 100 or x.ghost == False)
    after = to_numpy(env)
    util.print_list("\n========= 이전 방 모습 =========", before)
    util.print_list("\n========= 최종 방 모습 =========", after)
    return res

def test_all(env: Environment, message: str):
    m, _ = encode(message, env)
    query_strs = m.split("\n")
    queries = Query.refine_queries(query_strs)
    queries = Query.filter_queries(env, queries)
    res = test_cmd(env, queries)
    return res

if __name__ == "__main__":
    # res = test_all(Environment(), "침대를 둬")
    
    env = Environment()
    res = test_cmd(env, [
        Query("A100 100"),
        Query("A100 101"),
        Query("E100 100 R2")
    ])
    util.print_list("테스트 결과:", res)
