from myroom import query, base_env
import json

with open("resources/requests.txt", "r") as i, \
        open("resources/train.jsonl", "+a") as o, \
        open("resources/responses.txt", "+a") as r:
    lines = i.readlines()
    skipmode = False
    add_env = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("###"):
            skipmode = not skipmode
            continue
        if skipmode:
            continue
        if line.startswith("#"):
            print(line)
            continue
        if line.startswith("@"):
            filename = line[1:].strip()
            with open("resources/presets/" + filename, "r") as preset:
                add_env = "".join(preset.readlines()[1:])
            continue
        result = query(line, base_env + add_env)
        print("요청:", line.strip())
        print(result[-1]["content"].strip(), "\n")
        json_text = json.dumps({"messages": result}, ensure_ascii=False)
        o.write(json_text + "\n")
        r.writelines([line.strip(), "\n", *result[-1]["content"].split("\n"), "\n\n"])


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
