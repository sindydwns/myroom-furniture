from typing import Callable
import util

class Node:
    def __init__(self) -> None:
        self.conn_to: list[Link] = []
        self.conn_fr: list[Link] = []
    
    def link(self, node: "Node", conn, weight=1.0) -> None:
        link = Link(conn, self, node, weight)
        self.conn_to.append(link)
        node.conn_fr.append(link)
    
    def get_link_to(self, func:  Callable[["Link"], bool]) -> list["Link"]:
        return list(filter(func, self.conn_to))
    
    def get_link_fr(self, func: Callable[["Link"], bool]) -> list["Link"]:
        return list(filter(func, self.conn_fr))
    
    def unlink(self, link: "Link") -> None:
        self.conn_to.remove(link)

CONN_NEAR = 0
CONN_FAR = 1
CONN_LEFT = 2
CONN_RIGHT = 3
CONN_ON = 4
CONN_UNDER = 5
CONN_IN = 6
CONN_FRONT = 7
CONN_BACK = 8
CONN_CENTER = 9
CONN_SIDE = 10
WEIGHT_FIXED = 999999.0
WEIGHT_DEFAULT = 1.0
WEIGHT_BIT = 0.000001
class Link:
    def __init__(self, conn, node1, node2, weight=1.0) -> None:
        self.node1: Node = node1
        self.node2: Node = node2
        self.conn: int = conn
        self.weight: float = weight

class ItemMeta:
    def __init__(self, object_id, name, w, h, ghost=False):
        self.object_id = int(object_id)
        self.name = name
        self.w = int(w)
        self.h = int(h)
        self.c = self.w * self.h

    def to_csv_line(self):
        return f"{self.object_id},{self.name},{self.w},{self.h}"
    
    def __str__(self):
        return f"{self.object_id},{self.name},{self.w},{self.h}"

class Item(Node):
    def __init__(self, name, width=1, height=1) -> None:
        super(Item, self).__init__()
        self.name = name
        self.width = width
        self.height = height
        self.rotation = Rotation()
        self.location = Location()
        self.ref: ItemMeta = None

class Rotation:
    def __init__(self, w=0) -> None:
        self.r = None
        self.w = w

class Location:
    def __init__(self, w=0) -> None:
        self.x = None
        self.y = None
        self.w = w

class Database:
    def __init__(self, filename):
        self.datas = util.read_file_to_json(filename)["objects"]
        lam = lambda x: ItemMeta(x["id"], x["name"], x["width"], x["height"], x["ghost"])
        self.datas = list(map(lam, self.datas))
        self.data_map: dict[int, ItemMeta] = {}
        for item in self.datas:
            self.data_map[item.object_id] = item

    def get(self, object_id):
        return self.data_map[object_id]
    
    def to_csv(self):
        header = ",".join(["object_id", "name", "width", "height"])
        lines = [ x.to_csv_line() for x in self.datas ]
        return "\n".join([header, *lines])

database = Database("resources/items.json")

if __name__ == "__main__":
    room = Item("room", 6, 6)
    window = Item("window", 2, 0)
    room.link(window, CONN_SIDE, WEIGHT_FIXED)
