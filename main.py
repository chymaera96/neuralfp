import os
import random
import numpy as np
import torch
import argparse
import json
import torch_optimizer as optim
import torch.nn as nn

# Neuralfp
from neuralfp.modules.data import NeuralfpDataset
from neuralfp.modules.transformations import TransformNeuralfp
from neuralfp.neuralfp import Neuralfp
from neuralfp.modules.nt_xent import NT_Xent
import neuralfp.modules.encoder as encoder




parser = argparse.ArgumentParser(description='Neuralfp Training')
parser.add_argument('--epochs', default=500, type=int, metavar='N',
                    help='number of total epochs to run')
parser.add_argument('--resume', default='', type=str, metavar='PATH',
                    help='path to latest checkpoint (default: none)')
parser.add_argument('--seed', default=None, type=int,
                    help='seed for initializing training. ')

# Directories
root = os.path.dirname(__file__)
model_folder = os.path.join(root,"model")
data_dir = os.path.join(root,"data/fma_10k")
# json_dir = os.path.join(root,"data/fma_10k.json")
ir_dir = os.path.join(root,'data/ir_filters')
noise_dir = os.path.join(root,'data/noise')

device = torch.device("cuda")


def train(train_loader, model, optimizer, criterion):
    loss_epoch = 0
    for idx, (x_i, x_j) in enumerate(train_loader):
        
        # if idx==0:
        #     overfit_x_i = x_i
        #     overfit_x_j = x_j
        # else:
        #     x_i = overfit_x_i
        #     x_j = overfit_x_j
            
        optimizer.zero_grad()
        x_i = x_i.to(device)
        x_j = x_j.to(device)

        # positive pair, with encoding
        h_i, h_j, z_i, z_j = model(x_i, x_j)
        loss = criterion(z_i, z_j)

        # if torch.count_nonzero(torch.isnan(loss)) > 0:
        #     print(z_i)
        loss.backward()

        optimizer.step()

        if idx % 10 == 0:
            print(f"Step [{idx}/{len(train_loader)}]\t Loss: {loss.item()}")
        
        

        loss_epoch += loss.item()
    return loss_epoch

def save_ckp(state,epoch):
    if not os.path.exists(model_folder): os.makedirs(model_folder)
    torch.save(state, "{}/model_ver9_epoch_{}.pth".format(model_folder,epoch))

def load_ckp(checkpoint_fpath, model, optimizer, scheduler):
    checkpoint = torch.load(checkpoint_fpath)
    model.load_state_dict(checkpoint['state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer'])
    scheduler.load_state_dict(checkpoint['scheduler'])
    return model, optimizer, scheduler, checkpoint['epoch'], checkpoint['loss']

def seed_worker(worker_id):
    worker_seed = torch.initial_seed() % 2**32
    np.random.seed(worker_seed)
    random.seed(worker_seed)
    
def load_index(dirpath):
    dataset = {}
    idx = 0
    print('=>Loading indices of train data')
    json_path = os.path.join(data_dir, dirpath.split('/')[-1] + ".json")

    for filename in os.listdir(dirpath):
      if filename.endswith(".wav") or filename.endswith(".mp3"): 
        dataset[idx] = filename
        idx += 1
    with open(json_path, 'w') as fp:
        json.dump(dataset, fp)

    return json_path

def main():
    args = parser.parse_args()
    json_dir = load_index(data_dir)
    
    # Hyperparameters
    batch_size = 250
    learning_rate = 1e-4
    num_epochs = args.epochs
    
    if args.seed is not None:
        seed = args.seed
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.cuda.manual_seed(seed)
        np.random.seed(seed)
        random.seed(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        
    train_dataset = NeuralfpDataset(path=data_dir, json_dir=json_dir, transform=TransformNeuralfp(ir_dir=ir_dir, noise_dir=noise_dir,sample_rate=8000))
    train_loader = torch.utils.data.DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True,
        num_workers=4, pin_memory=True, drop_last=True)
    
    model = Neuralfp(encoder=encoder.Encoder())
    model = nn.DataParallel(model).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max = 500, eta_min = 1e-7)
    criterion = NT_Xent(batch_size, temperature = 0.1)

       
    if args.resume:
        if os.path.isfile(args.resume):
            print("=> loading checkpoint '{}'".format(args.resume))
            model, optimizer, scheduler, start_epoch, loss_log = load_ckp(args.resume, model, optimizer, scheduler)
        else:
            print("=> no checkpoint found at '{}'".format(args.resume))
            
    else:
        start_epoch = 0
        loss_log = []
        
    

    
    best_loss = train(train_loader, model, optimizer, criterion)
    
    # training
    model.train()
    for epoch in range(start_epoch+1, num_epochs+1):
        print("#######Epoch {}#######".format(epoch))
        loss_epoch = train(train_loader, model, optimizer, criterion)
        loss_log.append(loss_epoch)
        if loss_epoch < best_loss and epoch%10==0:
            best_loss = loss_epoch
            
            checkpoint = {
                'epoch': epoch,
                'loss': loss_log,
                'state_dict': model.state_dict(),
                'optimizer': optimizer.state_dict(),
                'scheduler': scheduler.state_dict()
            }
            save_ckp(checkpoint,epoch)
        scheduler.step()
    
  
        
if __name__ == '__main__':
    main()
