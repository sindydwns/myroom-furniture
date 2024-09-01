import numpy as np
import torch
from tqdm import tqdm

class FurnitureModel(torch.nn.Module):
    def __init__(self):
        super(FurnitureModel, self).__init__()
        self.loc_model = torch.nn.Sequential(
            torch.nn.Linear(16, 128),
            torch.nn.ReLU(),
            torch.nn.Linear(128, 64),
        )
        self.env_model = torch.nn.Sequential(
            torch.nn.Linear(72, 256),
            torch.nn.ReLU(),
            torch.nn.Linear(256, 64),
        )
        self.fusion_model = torch.nn.Sequential(
            torch.nn.Linear(128, 128),
            torch.nn.ReLU(),
            torch.nn.Linear(128, 3)
        )
    
    def forward(self, add, env):
        add_feat = self.loc_model(add)
        env_feat = self.env_model(env)
        concat_feat = torch.cat([add_feat, env_feat])
        out = self.fusion_model(concat_feat)
        return out

device = "cuda" if torch.cuda.is_available() else "cpu"
model = FurnitureModel().to(device)
optim = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = torch.nn.MSELoss()
epochs = 200

X_train1 = torch.FloatTensor(np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]))
X_train2 = torch.FloatTensor(np.array([0,0,0,0,6,6,0,1,1,0,0,6,0,0,1,2,0,0,0,6,0,1,3,6,0,0,6,0,1,4,0,6,6,0,0,2,5,2,0,2,0,0,0,0,0,0,0,0]))
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
