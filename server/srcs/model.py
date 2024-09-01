import torch
from tqdm import tqdm

# input [*]
# output [x, y, r]

class FurnitureModel(torch.nn.Module):
    def __init__(self):
        super(FurnitureModel, self).__init__()
        self.add_model = torch.nn.Sequential(
            torch.nn.Linear(1, 128),
            torch.nn.ReLU(),
            torch.nn.Linear(128, 64),
        )
        self.env_model = torch.nn.Sequential(
            torch.nn.Linear(1, 128),
            torch.nn.ReLU(),
            torch.nn.Linear(128, 64),
        )
        self.fusion_model = torch.nn.Sequential(
            torch.nn.Linear(128, 128),
            torch.nn.ReLU(),
            torch.nn.Linear(128, 1)
        )
    
    def forward(self, add, env):
        add_feat = self.add_model(add)
        env_feat = self.env_model(env)
        concat_feat = torch.cat([add_feat, env_feat])
        out = self.fusion_model(concat_feat)
        return out

device = "cuda" if torch.cuda.is_available() else "cpu"
model = FurnitureModel().to(device)
optim = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = torch.nn.MSELoss()
epochs = 200

X_train1 = torch.FloatTensor([0])
X_train2 = torch.FloatTensor([0])
y_train = torch.FloatTensor([1])

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

    print(f"loss {pred.item()}\t{loss.item()}")
