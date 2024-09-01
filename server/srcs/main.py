from myroom import encode, get_env
import json

def parse(str: str):
    strs = str.split(" ")
    try:
        mode, object_id = strs[0][0], int(strs[0][1:])
        instance_id = int(strs[1])
        locations = [[x[:2], int(x[2:])] for x in strs[2:]]
        return {
            "mode": mode,
            "object_id": object_id,
            "instance_id": instance_id,
            "locations": locations
        }
    except:
        print("except:", str)
        return None

def action(cmds, env):
    for cmd in cmds:
        cmd = parse(cmd)
        if cmd["mode"] == "A":
            pass
        if cmd["mode"] == "E":
            pass
        if cmd["mode"] == "D":
            pass

request_query = "방 안에 침대 배치해줘"
content, _ = encode(request_query, get_env())
contents = content.split("\n")
action(contents)
