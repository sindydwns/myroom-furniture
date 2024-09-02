import uuid
from datetime import datetime

def parse(str: str):
    strs = str.split(" ")
    try:
        mode, object_id = strs[0][0], int(strs[0][1:])
        instance_id = int(strs[1])
        if len(strs) > 2 and strs[2][0] == 'R':
            rotation = int(strs[2][1])
            locations = [[x[:2], int(x[2:])] for x in strs[3:]]
        else:
            rotation = 0
            locations = [[x[:2], int(x[2:])] for x in strs[2:]]
        return {
            "mode": mode, # A|E|D
            "object_id": object_id, # 100
            "instance_id": instance_id, # 101
            "rotation": rotation, # 0, 1, 2, 3
            "locations": locations # [['le', 100], ['le', 100]]
        }
    except:
        print("except:", str)
        return None
    
def create_filename(suffix):
    date_str = datetime.now().strftime("%m%d_%H%M")
    unique_id = uuid.uuid4().hex[:10]
    file_name = f"{date_str}_{unique_id}_{suffix}"
    return file_name