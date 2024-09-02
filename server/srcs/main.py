from myroom import encode, Environment
from util import parse
import json

def action(cmds, env: Environment):
    for cmd in cmds:
        print(cmd)
        cmd = parse(cmd)
        if cmd["mode"] == "A":
            pass
        if cmd["mode"] == "E":
            pass
        if cmd["mode"] == "D":
            env.objs = env.objs[env.objs.instance_id != cmd["instance_id"]]
    return env

env = Environment("empty.csv")
request_query = "침대 뺴"
content, _ = encode(request_query, env)
contents = content.split("\n")
result_env = action(contents, env)
