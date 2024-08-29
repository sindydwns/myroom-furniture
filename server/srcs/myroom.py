from pydantic import BaseModel

from openai import OpenAI
import numpy as np
import json
client = OpenAI()

query = "왼쪽 벽에 침대를 붙여서 배치하고 오른쪽 벽에 소파를 배치해"
# query = "침대와 책상 의자 그리고 스탠딩 조명을 멋있게 배치해줘"
# query = "침대는 방 구석에 배치하고 대각선 반대편에 책상과 의자를 둬. 남은 공간에 소파도 배치해"
# query = "구석에 침대를 두고 남은 공간의 중앙에는 책상을 배치해 그리고 그 앞에는 의자를 두고 책상 옆에 스탠딩 조명을 둬"
# query = "방의 모든 가장자리에 화분을 배치해"


database = [
    {"id": 0, "name": "침대", "width": 2, "height": 3},
    {"id": 1, "name": "책상", "width": 2, "height": 1},
    {"id": 2, "name": "의자", "width": 1, "height": 1},
    {"id": 3, "name": "소파", "width": 3, "height": 1},
    {"id": 4, "name": "화분", "width": 1, "height": 1},
    {"id": 5, "name": "스탠딩조명", "width": 1, "height": 1},
    {"id": 6, "name": "탁자", "width": 2, "height": 1},
    {"id": 7, "name": "곰인형", "width": 1, "height": 1},
    {"id": 8, "name": "변기", "width": 1, "height": 1},
    {"id": 9, "name": "세면대", "width": 1, "height": 1},
    {"id": 10, "name": "쓰레기통", "width": 1, "height": 1},
]
system_prompt = """당신은 인테리어 전문가이며 다음 규칙에 따라 가구를 배치해야 합니다.

다음 사항은 반드시 알아야 합니다.
1. 방은 8x8 격자 좌표로 이루어져 있습니다.
2. 사용자는 방을 대각선에서 isometric시점으로 바라봅니다. 방의 북서는 위쪽, 북동은 오른쪽, 남동은 아래쪽, 남서는 왼쪽입니다.
3. 사용자 시점에서 오른쪽 벽에는 창문이 있습니다.
4. 가구는 직사각형이며 width와 height를 가집니다.
5. 가구는 회전값을 가지며, 기본 상태는 0이고 오른쪽으로 90도 회전하는 양에 따라 0, 1, 2, 3의 값을 갖습니다.

다음 사항은 반드시 지키세요.
1. 사용자가 원하는 가구만 배치해야 하며 요청하는 것 이외의 행동은 하지 않습니다.
2. 절대 이미 놓여진 가구과 겹쳐서는 안됩니다. 여러 가구를 한 번에 배치할 때에도 당신이 이전에 배치한 가구와 겹쳐서도 안됩니다.
3. 최대한 이미 놓여진 가구과 조화롭게 배치해야 합니다.

당신은 반드시 다음과 같은 JSON 형태로 답변합니다.
{
    "objects": [
        {"id": <int>, "x": <int>, "y": <int>, "r": <int>}
        ...
    ],
    "message": <string>
}
"id"는 가구의 id, "x"와 "y" 는 가구의 시작 위치, "r"은 가구의 회전값입니다. 회전값은 0, 1, 2, 3만을 갖습니다.
반드시 파싱이 가능한 JSON 형태여야 하며 어떠한 주석도 넣지 마세요.

배치 가능한 가구:\n""" + "\n".join([json.dumps(data, ensure_ascii=False) for data in database]) + """
이미 배치된 가구:

"""

# {"id": 4, "x": 0, "y": 0, "w": 5, "h": 3}
# {"id": 3, "x": 5, "y": 0, "w": 2, "h": 3}
# {"id": 2, "x": 5, "y": 3, "w": 1, "h": 1}
# {"id": 6, "x": 7, "y": 7, "w": 1, "h": 1}
# {"id": 1, "x": 0, "y": 3, "w": 1, "h": 1}
# {"id": 1, "x": 4, "y": 3, "w": 1, "h": 1}


fewshot = """
사용자의 요청 예시: 방 구석에 침대를 두고 그 옆에 화분을 둬
답변 예시:
{
    "message": "침대를 왼쪽 벽에 붙여서 배치하고 머리맡에 화분을 배치했습니다.",
    "objects": [
        {"id": 0, "x": 0, "y": 3, "r": 0},
        {"id": 4, "x": 2, "y": 0, "r": 0}
    ]
}
사용자의 요청 예시: 책상을 창문 방향에 두고 그 앞에 의자를 두었으면 좋겠어.
답변 예시:
{
    "message": "창문 앞에 책상을 두고 의자를 두었습니다. 의자에 앉아 책상을 사용하는 것을 고려하여 중앙에 배치했습니다",
    "objects": [
        {"id": 1, "x": 3, "y": 0, "r": 0},
        {"id": 2, "x": 4, "y": 1, "r": 0}
    ]
}
"""




system_prompt2 = """당신은 사용자가 하는 요청을 해석하여 구체적인 명령단위의 항목으로 분해해야 합니다.
사용자가 요청한 내용은 구어체일 수 있음을 참고하세요.
사용자 요청 예: 방 중앙에 침대를 가로로 배치하고 구석에는 책상을 둬. 그리고 방 가장자리에는 화분으로 가득 채워
당신의 답변 예:
- 방 중앙에 침대 가로로 배치
- 방 구석에 책상 배치
- 방 가장자리 모든 칸에 화분 배치
"""

query_prompt = "사용자의 요청: " + query
completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        { "role": "system", "content": system_prompt2},
        { "role": "user", "content": query_prompt },
    ], temperature=1e-19
)
query = completion.choices[0].message.content
print(query)

query_prompt = "사용자의 요청: " + query
completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        { "role": "system", "content": system_prompt + fewshot},
        { "role": "user", "content": query_prompt },
    ], temperature=1e-19
)

res = completion.choices[0].message.content
print(res)
res = json.loads(res)
room = np.zeros((8, 8))
for o in res["objects"]:
    id, x, y, r = o["id"], o["x"], o["y"], o["r"]
    item = list(filter(lambda x: x["id"] == id, database))[0]
    w = item["width"] if r % 2 == 0 else item["height"]
    h = item["height"] if r % 2 == 0 else item["width"]
    print(id, item["name"])
    for xx in range(x, x + w):
        for yy in range(y, y + h):
            room[yy, xx] = id + .1
    # print(room)
print(room)











    # "objects": [

    #     {"id": 3, "x": 5, "y": 0, "w": 2, "h": 3},
    #     {"id": 2, "x": 5, "y": 3, "w": 1, "h": 1},
    #     {"id": 6, "x": 7, "y": 7, "w": 1, "h": 1}
    # ]
    
    
    # 0 0 0 0 0 0 0 0 
    # 0 0 0 0 0 0 0 0 
    # 0 0 0 0 0 0 0 0 
    # 0 0 0 0 0 0 0 0 
    # 0 0 0 0 0 0 0 0 
    # 0 0 0 0 0 0 0 0 
    # 0 0 0 0 0 0 0 0 
    # 0 0 0 0 0 0 0 0 







class Furniture(BaseModel):
    id: int
    x: int
    y: int
    r: int

class RequestData(BaseModel):
    current: list[Furniture]
    message: str