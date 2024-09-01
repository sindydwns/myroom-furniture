from myroom import encode, Environment
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

def action(cmds, env: Environment):
    for cmd in cmds:
        print(cmd)
        cmd = parse(cmd)
        if cmd["mode"] == "A":
            pass
        if cmd["mode"] == "E":
            env.objs = env.objs[env.objs.instance_id != cmd["instance_id"]]
            
        if cmd["mode"] == "D":
            env.objs = env.objs[env.objs.instance_id != cmd["instance_id"]]
    return env

env = Environment("single_bed.csv")
request_query = "침대 뺴"
content, _ = encode(request_query, env)
contents = content.split("\n")
result_env = action(contents, env)
