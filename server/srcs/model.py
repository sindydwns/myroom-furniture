import numpy as np
import torch
import pandas as pd
from myroom import Environment
from util import parse
from tqdm import tqdm

class FurnitureModel(torch.nn.Module):
    def __init__(self):
        super(FurnitureModel, self).__init__()
        # [ADD|EDIT, object_id, instance_id, rotation, *location, *location, *location, *location]
        self.loc_model = torch.nn.Sequential(
            torch.nn.Linear(12, 128),
            torch.nn.ReLU(),
            torch.nn.Linear(128, 128),
        )
        # [*[object_id, instance_id, x, y, r] x 40]
        self.env_model = torch.nn.Sequential(
            torch.nn.Linear(200, 512),
            torch.nn.ReLU(),
            torch.nn.Linear(512, 128),
        )
        self.fusion_model = torch.nn.Sequential(
            torch.nn.Linear(256, 512),
            torch.nn.ReLU(),
            torch.nn.Linear(512, 3)
        )
        # [x, y, r]
    
    def forward(self, add, env):
        add_feat = self.loc_model(add)
        env_feat = self.env_model(env)
        concat_feat = torch.cat([add_feat, env_feat])
        out = self.fusion_model(concat_feat)
        return out

    def encode_location(self, code):
        if code == "ne": return 1.
        if code == "fa": return 2.
        if code == "le": return 3.
        if code == "ri": return 4.
        if code == "on": return 5.
        if code == "un": return 6.
        if code == "in": return 7.
        if code == "fr": return 8.
        if code == "ba": return 9.
        if code == "ce": return 10.
        return 0.

    def encode_cmd(self, data):
        print(data)
        res = np.zeros((12), dtype=np.float32)
        res[0] = 0. if data["mode"] == "A" else 1.
        res[1] = float(data["object_id"])
        res[2] = float(data["instance_id"])
        res[3] = float(data["rotation"])
        for i, k in enumerate(data["locations"]):
            res[4 + i * 2] = self.encode_location(k[0])
            res[5 + i * 2] = float(k[1])
        return res

    def encode_env(self, data: Environment):
        data = data.objs
        res = np.zeros((200), dtype=np.float32)
        data = data[["object_id", "instance_id", "x", "y", "rotation"]].to_numpy()
        data = data.flatten()
        data = data[:200]
        res[:len(data)] = data
        return res

device = "cuda" if torch.cuda.is_available() else "cpu"
model = FurnitureModel().to(device)
optim = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = torch.nn.MSELoss()
epochs = 200

encoded_cmd = model.encode_cmd(parse("A100 100 R3 ne1"))
encoded_env = model.encode_env(Environment())

print(encoded_cmd)
print(encoded_env)

X_train1 = torch.FloatTensor(encoded_cmd).to(device)
X_train2 = torch.FloatTensor(encoded_env).to(device)
y_train = torch.FloatTensor(np.array([0, 0, 0]))

model.train(True)
X_train1 = X_train1.to(device)
X_train2 = X_train2.to(device)
y_train = y_train.to(device)
for epoch in range(epochs):
    optim.zero_grad()
    pred = model(X_train1, X_train2)
    loss = criterion(pred, y_train)
    loss.backward()
    optim.step()

    print(f"loss {pred}\t{loss.item()}")
