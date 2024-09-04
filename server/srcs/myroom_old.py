from pydantic import BaseModel

from openai import OpenAI
import numpy as np
import json
client = OpenAI()

# query = "빈 공간에 소파를 배치해"
# query = "침대와 책상 의자 그리고 스탠딩 조명을 멋있게 배치해줘"
# query = "침대는 방 구석에 배치하고 대각선 반대편에 책상과 의자를 둬. 남은 공간에 소파도 배치해"
# query = "구석에 침대를 두고 남은 공간의 중앙에는 책상을 배치해 그리고 그 앞에는 의자를 두고 책상 옆에 스탠딩 조명을 둬"
# query = "방의 모든 가장자리에 화분을 배치해"


database = [
    {"id": 1, "name": "room", "width": 6, "height": 6},
    {"id": 2, "name": "wall", "width": 6, "height": 0},
    {"id": 3, "name": "window", "width": 2, "height": 0},
    {"id": 100, "name": "침대", "width": 2, "height": 3},
    {"id": 101, "name": "책상", "width": 2, "height": 1},
    {"id": 102, "name": "의자", "width": 1, "height": 1},
    {"id": 103, "name": "소파", "width": 3, "height": 1},
    {"id": 104, "name": "화분", "width": 1, "height": 1},
    {"id": 105, "name": "스탠딩조명", "width": 1, "height": 1},
    {"id": 106, "name": "탁자", "width": 2, "height": 1},
    {"id": 107, "name": "곰인형", "width": 1, "height": 1},
    {"id": 108, "name": "변기", "width": 1, "height": 1},
    {"id": 109, "name": "세면대", "width": 1, "height": 1},
    {"id": 110, "name": "쓰레기통", "width": 1, "height": 1}
]
system_prompt = """당신은 방을 꾸미는 어시스던트이며 다음과 같은 정보를 알고 있습니다.
방은 8x8 격자 좌표로 이루어져 있으며 사용자의 요청에 맞게 가구를 배치해야 합니다.
다음 사항은 반드시 지키세요.
- 사용자가 원하는 가구만 배치해야 하며 요청하는 것 이외의 행동은 하지 않습니다.
- 절대 이미 놓여진 가구과 겹쳐서는 안됩니다. 여러 가구를 한 번에 배치할때 당신이 배치한 가구과 겹쳐서도 안됩니다.
- 최대한 이미 놓여진 가구과 조화롭게 배치해야 합니다.
- 가구를 배치할때 사용자의 동선을 고려해야 합니다.
다음 사항을 참고하세요.
- 모든 가구는 직사각형입니다.
- 각 가구는 상하좌우 4개의 면을 가지며 긴 면은 width와 height를 참고하여 알 수 있습니다.
당신은 반드시 다음과 같은 JSON 형태로 답변합니다.
{
    "objects": [
        {"id": <int>, "x": <int>, "y": <int>, "w": <int>, "h": <int>}
        ...
    ],
    "message": <string>
}
"id"는 가구의 id, "x"와 "y" 는 가구의 시작 위치, "w"와 "h"는 가구의 너비와 높이입니다. 가구는 90도씩 회전이 가능합니다.
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
    "message": "침대를 방 구석에 배치하고 머리맡에 화분을 배치했습니다.",
    "objects": [
        {"id": 4, "x": 0, "y": 0, "w": 5, "h": 3},
        {"id": 2, "x": 0, "y": 3, "w": 1, "h": 1}
    ]
}
사용자의 요청 예시: 책상을 창문 방향에 두고 그 앞에 의자를 두었으면 좋겠어.
답변 예시:
{
    "message": "창문 앞에 책상을 두고 의자를 두었습니다. 의자에 앉아 책상을 사용하는 것을 고려하여 중앙에 배치했습니다",
    "objects": [
        {"id": 3, "x": 0, "y": 4, "w": 2, "h": 3},
        {"id": 2, "x": 2, "y": 5, "w": 1, "h": 1}
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

def run(query):
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
    return res

res = run("침대 배치해")
room = np.zeros((8, 8))
for o in res["objects"]:
    id, x, y, w, h = o["id"], o["x"], o["y"], o["w"], o["h"]
    for xx in range(x, x + w):
        for yy in range(y, y + h):
            room[yy, xx] = id
    # print(room)
print(room)