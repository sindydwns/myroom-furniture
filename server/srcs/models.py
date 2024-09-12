import csv
import util

class FurnitureMeta:
    def __init__(self, object_id, name, w, h, ghost=False):
        self.object_id = int(object_id)
        self.name = name
        self.w = int(w)
        self.h = int(h)
        self.c = self.w * self.h
        self.ghost = ghost
    
    def to_dict(self):
        return {
            "object_id": self.object_id,
            "name": self.name,
            "width": self.w,
            "height": self.h,
            "ghost": self.ghost,
        }
    
    def to_csv_line(self):
        return f"{self.object_id},{self.name},{self.w},{self.h}"
    
    def __str__(self):
        return f"{self.object_id},{self.name},{self.w},{self.h},{self.ghost}"

class Database:
    def __init__(self, filename):
        self.datas = util.read_file_to_json(filename)["objects"]
        lam = lambda x: FurnitureMeta(x["id"], x["name"], x["width"], x["height"], x["ghost"])
        self.datas = list(map(lam, self.datas))
        self.data_map: dict[int, FurnitureMeta] = {}
        for item in self.datas:
            self.data_map[item.object_id] = item

    def get(self, object_id):
        return self.data_map[object_id]
    
    def to_csv(self):
        header = ",".join(["object_id", "name", "width", "height"])
        lines = [ x.to_csv_line() for x in self.datas ]
        return "\n".join([header, *lines])

database = Database("resources/items.json")

class Furniture:
    def __init__(self, object_id, instance_id, x, y, r, comment = "", ghost = None):
        self.meta = database.get(object_id)
        self.object_id = object_id
        self.instance_id = instance_id
        self.x = x
        self.y = y
        self.r = r
        self.w = self.meta.w if self.r % 2 == 0 else self.meta.h
        self.h = self.meta.h if self.r % 2 == 0 else self.meta.w
        self.comment = comment
        if ghost is None:
            self.ghost = self.meta.ghost
        else:
            self.ghost = ghost
    
    def rotate(self, r: int):
        self.r = (self.r + r + 4) % 4
        self.w = self.meta.w if self.r % 2 == 0 else self.meta.h
        self.h = self.meta.h if self.r % 2 == 0 else self.meta.w
    
    def to_csv_line(self):
        return f"{self.object_id},{self.instance_id},{self.x},{self.y},{self.r},{self.comment}"
    def __str__(self):
        return f"{self.object_id},{self.instance_id},{self.x},{self.y},{self.r},{self.comment},{self.ghost}"


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
        lines = [ x.to_csv_line() for x in self.objs ]
        return "\n".join([header, *lines])
    
    def __str__(self):
        lines = [ str(x) for x in self.objs ]
        return "\n".join(lines)
    
    def to_list(self, _filter=None):
        if _filter is not None:
            return list(filter(_filter, self.objs))
        return self.objs
    
    def add(self, furniture: Furniture):
        self.objs.append(furniture)
        return self

    def remove(self, call):
        self.objs = list(filter(lambda x: call(x), self.objs))
        return self
    
    def get(self, instance_id) -> Furniture:
        for i in range(len(self.objs)):
            furniture = self.objs[i]
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
            self.valid = False
            self.query_str = query
            if not query or query[0] not in ['A', 'E', 'D']:
                return
            qs = query.split(" ")
            self.mode = qs[0][0]
            self.meta: FurnitureMeta = database.get(int(qs[0][1:]))
            self.instance_id = int(qs[1])
            self.rotation = 0
            self.rotation_manual = False
            self.locations: list[Location] = []
            for q in qs[2:]:
                if q.startswith("R"):
                    self.rotation = int(q[1:])
                    self.rotation_manual = True
                else:
                    self.locations.append(Location(q))
            self.valid = True
        except:
            self.valid = False

    def __str__(self):
        s = f"{self.mode}{self.meta.object_id} {self.instance_id}"
        if self.rotation_manual:
            s += f" R{self.rotation}"
        for lo in self.locations:
            s += f" {lo.code}{lo.instance_id}"
        return s
    
    def refine_queries(query_strs: list[str]) -> list["Query"]:
        queries = []
        for query_str in query_strs:
            query = Query(query_str)
            if query.valid == False:
                print("invalid:", query.query_str)
                continue
            queries.append(query)
        return queries
    
    def filter_queries(env: Environment, queries: list["Query"]):
        res = []
        for query in queries:
            if query.mode == 'A':
                res.append(query)
                continue
            instance = env.get(query.instance_id)
            if instance is not None:
                res.append(query)
                continue
            item = util.find(res, lambda x: x.instance_id == instance.instance_id)
            if item is not None:
                res.append(query)
                continue
            print("drop:", query)
        return res
    
    def invoke_queries(env: Environment, queries: list["Query"], apply: callable):
        _add = []
        _edit = []
        _del = []
        for query in queries:
            if query.mode in ['E', 'D']:
                instance = env.get(query.instance_id)
                if instance is not None:
                    instance.ghost = True
        for i, query in enumerate(queries):
            query_res = apply(env, query)
            if query_res is None:
                continue
            if query.mode == 'D':
                _del.append(query_res)
            if query.mode == 'E':
                _edit.append(query_res)
            if query.mode == 'A':
                _add.append(query_res)
            # for i in range(i, len(queries)):
            #     next_query = queries[i]
            #     if next_query.mode == 'A':
            #         continue
            #     if next_query.instance_id != query.instance_id:
            #         continue
            #     env.get(query.instance_id).ghost = True
            #     break
        return _add, _edit, _del
