import os
import json
import time

import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
#from torchvision import datasets, transforms

class Example():
    adj = [(0,1), (0,-1), (1,0), (-1,0)]
#    adj = [(0,0)]

    def __init__(self, filename):
        with open(filename, 'r') as fp:
            self.raw = raw = fp.read()

        self.cells = {}
        for y, line in enumerate(raw.split('\n')):
            for x, char in enumerate(line):
                self.cells[(x,y)] = 1 if char == '0' else 0

        self.w, self.h = x+1, y+1

    def make_training_set(self, size):
        inputs = []
        outputs = []

        for x in range(self.w):
            for y in range(self.h):
                pos = (x,y)
                if self.cells.get(pos, False) != 1:
                    continue

                answers, invectors = self.get_input_vectors(pos, size)
                for offset in self.adj:
                    inval = invectors[offset]
                    outval = [0]*len(self.adj)
                    idx = self.adj.index(offset)
                    outval[idx] = answers[offset]
                    inputs.append(inval)
                    outputs.append(outval)
        return inputs, outputs

    def get_input_vectors(self, pos, size):
        invectors = {a:[] for a in self.adj}
        answers = {}
        for offset in self.adj:
            for dx in range(-size, size+1):
                for dy in range(-size, size+1):
                    dpos = (pos[0]+dx, pos[1]+dy)
                    if (dx, dy) == offset:
                        value = 0
                        answers[offset]=self.cells.get(dpos, 0)
                    else:
                        value = self.cells.get(dpos, 0)
                    invectors[offset].append(value)
        return answers, invectors


SIZE = 15
DEVICE = 'cuda'
BATCH_SIZE = 64

class MyDataset(Dataset):
    def __init__(self):
        self.inputs = []
        self.outputs = []

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, idx):
        return self.inputs[idx], self.outputs[idx]

    def add_data(self, invals, outvals):
        for _in, _out in zip(invals, outvals):
            _in = torch.tensor(_in, device=DEVICE, dtype=torch.float)
            _out = torch.tensor(_out, device=DEVICE, dtype=torch.float)
            self.inputs.append(_in)
            self.outputs.append(_out)

def load_cave(filename):
    a = Example(filename)
    inputs, outputs = a.make_training_set(SIZE)
    return inputs, outputs

def save_cave(outfile, inputs, outputs):
    with open(outfile, 'w') as fp:
       json.dump({'inputs':inputs, 'outputs':outputs}, fp)

def load_json(filename):
    with open(filename, 'r') as fp:
        data = json.load(fp)
    return data['inputs'], data['outputs']

def translate_caves():
    for idx in range(15):
        print(idx)
        inputs, outputs = load_cave(f'{idx}.cave')
        save_cave(f'cave{idx}.json', inputs, outputs)

if False:
    translate_caves()

def make_data_loader(files):

    training_data = MyDataset()

    for filename in files:
        print(f'Loading {filename}')
        a = Example(filename)
        inputs, outputs = a.make_training_set(SIZE)
#        inputs, outputs = load_cave(filename)
        print(f'Adding to dataset')
        training_data.add_data(inputs, outputs)

    train_dataloader = DataLoader(training_data, batch_size=BATCH_SIZE)
    return train_dataloader

class Network(nn.Module):
    def __init__(self):
        super().__init__()
#        self.flatten = nn.Flatten()
        layer_size = 512
        self.linear_relu_stack = nn.Sequential(
            nn.Linear((2*SIZE+1)**2, layer_size),
            nn.ReLU(),
            nn.Linear(layer_size, layer_size),
            nn.ReLU(),
            nn.Linear(layer_size, layer_size),
            nn.ReLU(),
            nn.Linear(layer_size, layer_size),
            nn.ReLU(),
            nn.Linear(layer_size, layer_size),
            nn.ReLU(),

            nn.Linear(layer_size, 4)
            )

    def forward(self, x):
#        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits

    def get_stuff(self, inputs):
        inputs = torch.tensor(inputs, device=DEVICE, dtype=torch.float)
        output = self(inputs)
        result = {}
        for pos, val in zip(Example.adj, output):
            result[pos]  = val.item()
        return result

if __name__ == '__main__':

    #train_dataloader = make_data_loader({f'cave{x}.json' for x in range(7)})
    #test_dataloader = make_data_loader({f'cave{x}.json'for x in range(7, 15)})
    train_dataloader = make_data_loader({f'{x}.cave' for x in range(15)})
#    test_dataloader = make_data_loader({f'{x}.cave'for x in range(14, 15)})
    test_dataloader = train_dataloader


    model = Network().to(DEVICE)
    loss_function = nn.CrossEntropyLoss()
    #loss_function = nn.L1Loss()
    optimizer = torch.optim.SGD(model.parameters(), lr=1e-3)

    def train(dataloader, model, loss_function, optimizer):
        size =  len(dataloader.dataset)
        model.train()
        for batch, (X, y) in enumerate(dataloader):
            X,y = X.to(DEVICE), y.to(DEVICE)

            pred = model(X)
            loss = loss_function(pred, y)

            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

            if batch%300 == 0:
                loss, current = loss.item(), (batch+1)*len(X)
                print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")

    def test(dataloader, model, loss_fn):
        size = len(dataloader.dataset)
        num_batches = len(dataloader)
        model.eval()
        test_loss, correct = 0, 0
        with torch.no_grad():
            for X, y in dataloader:
                X, y = X.to(DEVICE), y.to(DEVICE)
                pred = model(X)
                test_loss += loss_fn(pred, y).item()
                correct += (pred.argmax() == y).type(torch.float).sum().item()
        test_loss /= num_batches
        correct /= size
        print(f"Test Error: \n Accuracy: {(100*correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")

    epochs = 80
    for t in range(epochs):
        print(f"Epoch {t+1}\n-------------------------------")
        train(train_dataloader, model, loss_function, optimizer)
        test(test_dataloader, model, loss_function)
    print("Done!")

    torch.save(model.state_dict(), 'model.pth')

    #X = torch.tensor(inputs[0], device=DEVICE, dtype=torch.float)
    #print(X)

    #logits = model(X)
    #print(logits)

    #print(inputs[0])
    #print(outputs[0])

