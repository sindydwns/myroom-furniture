import torch
from tqdm import tqdm

class FurnitureModel(torch.nn.Module):
    def __init__(self):
        super(FurnitureModel, self).__init__()
        self.fc1 = torch.nn.Linear(in_features=1, out_features=1024)
        self.fc2 = torch.nn.Linear(in_features=1024, out_features=1)
        self.relu = torch.nn.ReLU()
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

device = "cuda" if torch.cuda.is_available() else "cpu"
model = FurnitureModel().to(device)
optim = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = torch.nn.MSELoss()
epochs = 200

X_train = torch.FloatTensor([0])
y_train = torch.FloatTensor([1])

model.train(True)
X_train = X_train.to(device)
y_train = y_train.to(device)
for epoch in range(epochs):
    optim.zero_grad()
    pred = model(X_train)
    loss = criterion(pred, y_train)
    loss.backward()
    optim.step()

    print(f"loss {pred.item()}\t{loss.item()}")
