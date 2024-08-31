from openai import OpenAI
import json
client = OpenAI()

with open("resources/prompt.txt", "r") as f_prompt, \
        open("resources/fewshot.txt", "r") as f_fewshot, \
        open("resources/enviroment.csv", "r") as f_environment, \
        open("resources/items.json", "r") as f_items:
    system_prompt = f_prompt.read()
    database = json.load(f_items)["items"]
    fewshot = f_fewshot.read()
    environment = f_environment.read()

def query(q):
    query_prompt = "사용자의 요청: " + q
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": fewshot},
        {"role": "system", "content": environment},
        {"role": "system", "content": "\n".join([json.dumps(data, ensure_ascii=False) for data in database])},
        {"role": "user", "content": query_prompt},
    ]
    completion = client.chat.completions.create(model="gpt-4o", messages=messages, temperature=0)
    content = completion.choices[0].message.content
    role = completion.choices[0].message.role
    strip_content = "\n".join([c.strip() for c in content.split("\n")])
    new_message = {"role": role, "content": strip_content}
    messages.append(new_message)
    return messages

with open("resources/requests.txt", "r") as i, open("resources/train.jsonl", "+a") as o:
    lines = i.readlines()
    for line in lines:
        if not line.strip() :
            continue
        if line.startswith("#"):
            print(line.strip())
            continue
        result = query(line)
        print("요청:", line.strip())
        print(result[-1]["content"].strip(), "\n")
        json_text = json.dumps({"messages": result}, ensure_ascii=False)
        o.write(json_text + "\n")


# query_prompt = "사용자의 요청: " + q
# completion = client.chat.completions.create(
#     model="gpt-4o-mini",
#     messages=[
#         { "role": "system", "content": system_prompt + fewshot},
#         { "role": "user", "content": query_prompt },
#     ], temperature=1e-19
# )

# res = completion.choices[0].message.content
# print(res)
# res = json.loads(res)
# room = np.zeros((8, 8))
# for o in res["objects"]:
#     id, x, y, w, h = o["id"], o["x"], o["y"], o["w"], o["h"]
#     for xx in range(x, x + w):
#         for yy in range(y, y + h):
#             room[yy, xx] = id
# print(room)
