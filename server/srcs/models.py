import csv
import util

class FurnitureMeta:
    def __init__(self, object_id, name, w, h):
        self.object_id = int(object_id)
        self.name = name
        self.w = int(w)
        self.h = int(h)
    
    def to_dict(self):
        return {
            "object_id": self.object_id,
            "name": self.name,
            "width": self.w,
            "height": self.h
        }
    
    def __str__(self):
        return f"{self.object_id},{self.name},{self.w},{self.h}"

class Database:
    def __init__(self, filename):
        self.datas = util.read_file_to_json(filename)["objects"]
        lam = lambda x: FurnitureMeta(x["id"], x["name"], x["width"], x["height"])
        self.datas = list(map(lam, self.datas))
        self.data_map: dict[int, FurnitureMeta] = {}
        for item in self.datas:
            self.data_map[item.object_id] = item

    def get(self, object_id):
        return self.data_map[object_id]
    
    def to_csv(self):
        header = ",".join(["object_id", "name", "width", "height"])
        lines = [ str(x) for x in self.datas ]
        return "\n".join([header, *lines])

database = Database("resources/items.json")

class Furniture:
    def __init__(self, object_id, instance_id, x, y, r, comment = ""):
        self.meta = database.get(object_id)
        self.object_id = object_id
        self.instance_id = instance_id
        self.x = x
        self.y = y
        self.r = r
        self.w = self.meta.w if self.r % 2 == 0 else self.meta.h
        self.h = self.meta.h if self.r % 2 == 0 else self.meta.w
        self.comment = comment
    
    def rotate(self, r: int):
        self.r = (self.r + r + 44444444) % 4
        self.w = self.meta.w if self.r % 2 == 0 else self.meta.h
        self.h = self.meta.h if self.r % 2 == 0 else self.meta.w
    
    def __str__(self):
        return f"{self.object_id},{self.instance_id},{self.x},{self.y},{self.r},{self.comment}"


def csv_to_furniture(filename):
    with open(filename, "r") as file:
        reader = csv.reader(file, skipinitialspace=True)
        res = []
        for i, row in enumerate(reader):
            if i != 0:
                item = Furniture(int(row[0]), int(row[1]), int(row[2]), int(row[3]), int(row[4]), row[5])
                res.append(item)
        return res

class Environment:
    def __init__(self, filename=None, ignore_base=False) -> None:
        self.base_env_path = "resources/environment.csv"
        self.preset_env_dir_path = "resources/presets/"
        self.objs: list[Furniture] = []
        if not ignore_base:
            self.objs += csv_to_furniture(self.base_env_path)
        if filename is not None:
            self.objs += csv_to_furniture(self.preset_env_dir_path + filename)
    
    def to_csv(self):
        header = ",".join(["object_id", "instance_id", "x", "y", "rotation", "comment"])
        lines = [ str(x) for x in self.objs ]
        return "\n".join([header, *lines])
    
    def to_list(self):
        return self.objs
    
    def add(self, furniture: Furniture):
        self.objs.append(furniture)
        return self

    def remove(self, instance_id):
        self.objs = list(filter(lambda x: x.instance_id != instance_id, self.objs))
        return self
    
    def get(self, instance_id) -> Furniture:
        for furniture in self.to_list():
            if furniture.instance_id == instance_id:
                return furniture
        return None

    def save(self, filename=None):
        if filename is None:
            filename = util.create_filename(".csv")
        with open(filename, "w+") as file:
            file.write(self.to_csv())
        return filename

class Location:
    def __init__(self, query: str):
        self.code = query[:2]
        self.instance_id = int(query[2:])

class Query:
    def __init__(self, query: str):
        try:
            print(query)
            self.valid = False
            if not query or query[0] not in ['A', 'E', 'D']:
                return
            qs = query.split(" ")
            self.mode = qs[0][0]
            self.meta: FurnitureMeta = database.get(int(qs[0][1:]))
            self.instance_id = int(qs[1])
            self.rotation = 0
            self.locations: list[Location] = []
            for q in qs[2:]:
                if q.startswith("R"):
                    self.rotation = int(q[1:])
                else:
                    self.locations.append(Location(q))
        except:
            raise "변환에 실패했습니다."

    def __str__(self):
        s = f"{self.mode}{self.meta.object_id} {self.instance_id} R{self.rotation}"
        for lo in self.locations:
            s += f"{lo.code}{lo.instance_id}"
        return s