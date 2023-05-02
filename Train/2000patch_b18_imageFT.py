# -*- coding: utf-8 -*-
"""Transfer_Learning_MicroscopyModel.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17-zzx4cXDFvCBJEJgosQwLo9qXf1F_yE

##Setup
"""

import pickle
import numpy as np
from sklearn import decomposition
from plotly import express as px
from matplotlib import pyplot as plt
from PIL import Image
import os
from scipy import ndimage
import pandas as pd
import requests
import zipfile
import sklearn
import json
import os.path
from scipy import stats, signal, ndimage, interpolate
import matplotlib.pyplot as plt
from matplotlib.pyplot import subplots, show
from numpy.linalg import norm 
from sklearn.mixture import GaussianMixture
import torch
import torchvision
from torchvision import transforms as T
import random
from pathlib import Path

def rgb_to_lightness(im):
    """Implement the lightness transform found here:
    https://stackoverflow.com/questions/596216/formula-to-determine-perceived-brightness-of-rgb-color
    """
    R, G, B = np.array(im).transpose([2, 0, 1])  # get each color channel
    L = (0.299 * R + 0.587 * G + 0.114 * B)  # one possible formula for luminance # ITU-R 601-2 luma transform
    #L = (0.2125 * R + 0.7154 * G + 0.0721 * B) # convert into gray scale #https://scikit-image.org/docs/dev/auto_examples/color_exposure/plot_rgb_to_gray.html
    return L


def autocrop(afm):
    # convert to lightness only
    L = rgb_to_lightness(afm)
    # find bounds
    afm_bounds = np.zeros(4, dtype=int)
    for i in range(2):
        min_pixels = np.argwhere(L.min(axis=i) < L.max()).flatten()
        gap_idx = np.argwhere(np.diff(min_pixels) > 1).flatten()[0]
        min_pixels = min_pixels[:gap_idx]
        if len(min_pixels) < 1:
            min_pixels = [L.shape[i]]

        median_pixels = np.argwhere(np.median(L, axis=i) < L.max()).flatten()
        if len(median_pixels) < 1:
            median_pixels = [L.shape[i]]

        afm_bounds[0 + i] = min(min_pixels[0], median_pixels[0])
        afm_bounds[2 + i] = min(min_pixels[-1], median_pixels[-1])

    return afm.crop(box=afm_bounds)


def smooth_histogram(L):
    #x = np.arange(0, 255)
    x = np.linspace(0, 12, num= 255)
    delta = 0.5*np.diff(x)[0]
    x_edge = np.hstack([x - delta, x[-1]+delta])
    yh, xh = np.histogram(L[np.logical_and(L>0, L<255)], bins=x_edge, density=True)
    xc = 0.5 * (xh[1:] + xh[:-1])
    yh = ndimage.gaussian_filter(yh, 6)
    L = np.delete(L,np.argwhere(L>=254))
    return xc, yh


def get_coverage(L, L_star):
    #L = np.delete(L,np.argwhere(L>=254))
    x = np.arange(0, 10.47)
    delta = 0.5*np.diff(x)[0]
    x_edge = np.hstack([x - delta, x[-1]+delta])
    yh, xh = np.histogram(L, bins=x_edge)
    coverage = 1 - np.cumsum(yh)/np.sum(yh)
    man_Lthres = L_star
    #man_Lthres = np.array(man_Lthres).astype(int)
    #all_c = []
    #for i in man_Lthres:
    pre_c = interpolate.interp1d(x, coverage)(man_Lthres)#([i]).tolist()
      #all_c.append(pre_c)
    #print(f'L_star of {man_Lthres} gives coverage of {pre_c}')
    #ax.plot(man_Lthres, man_c, 'rs')
    #print(all_c)
    print(pre_c)
    cover = pre_c
    return cover #, x, all_c

def rgbtogrey(im):
  import numpy as np
  import matplotlib.pyplot as plt
  import matplotlib.image as mpimg

  def rgb2grey(rgb):
      R, G, B = np.array(rgb).transpose([2, 0, 1])
      return (0.2125 * R + 0.7154 * G + 0.0721 * B)

  #np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140])
  grey = rgb2grey(im)    
  #plt.imshow(gray, cmap=plt.get_cmap('gray'), vmin=0, vmax=255)
  #plt.show()

  return grey    

def rescaleto96(afm):
  from sklearn import preprocessing
  scaler = preprocessing.MinMaxScaler(feature_range=(0, 10.47))
  afm = scaler.fit_transform(afm).reshape(-1, 1)
  return afm

url = 'https://pennstateoffice365-my.sharepoint.com/:u:/g/personal/wfr5091_psu_edu/EXfY0Qt9qKJFiHvyVd7Rx7gBbale5WiFnas19qHZ-hEYHw?e=pU7vQY'
r = requests.get(url + '&download=1')
with open('data.pkl', 'wb') as fid:
    for chunk in r.iter_content(chunk_size=8192): 
        fid.write(chunk)

with open('data.pkl', 'rb') as fid:
    coverage_data = pickle.load(fid)

coverage_keys = list(coverage_data.keys())
l_curves = np.array([coverage_data[k]['lightness'] for k in coverage_keys])
coverage_est = np.array([val['coverage'][val['estimates']['min']] for val in coverage_data.values()])



class Dataset():
  'Characterizes a dataset for PyTorch'
  def __init__(self, list_IDs, labels, transform):
        'Initialization'
        self.list_IDs = list_IDs
        self.labels = labels
        self.transform = transform

  def __len__(self):
        'Denotes the total number of samples' 
        return len(self.list_IDs)

  def __getitem__(self, index):
        'Generates one sample of data'
        # Select sample
        ID = self.list_IDs[index]
        
        # Load data and get label
        X = self.transform(ID)
        y = self.labels[index]
        return X, y




transform = T.Compose([
      T.ToPILImage(),
      T.RandomHorizontalFlip(p = 0.5),
      T.RandomVerticalFlip(p = 0.5),
      #T.RandomRotation(degrees = (0, 360)),
      T.ToTensor(),
        ])

def flatten_json(nested_json, exclude=['']):
    """Flatten json object with nested keys into a single level.
        Args:
            nested_json: A nested json object.
            exclude: Keys to exclude from output.
        Returns:
            The flattened json object if successful, None otherwise.
    """
    out = {}

    def flatten(x, name='', exclude=exclude):
        if type(x) is dict:
            for a in x:
                if a not in exclude: flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(nested_json)
    return out

import pickle

with open("/noether/s0/cfw5463/Data/Data_patch_img", "rb") as fp:   # Unpickling
  Data_CNN = pickle.load(fp)

with open("/noether/s0/cfw5463/Data/Target_patch_cover", "rb") as fp:   # Unpickling
  Target_CNN = pickle.load(fp)

print(type(Data_CNN))
print(Data_CNN.shape)
print(Target_CNN.shape)



print(Data_CNN.shape)
Data_CNN_rgb = np.repeat(Data_CNN[..., np.newaxis], 3, -1)
print(Data_CNN_rgb.shape)
Data_CNN_rgb = Data_CNN_rgb.transpose(0, 3, 1, 2)
print(Data_CNN_rgb.shape)

"""##Training"""


import pretrained_microscopy_models as pmm
import torch.utils.model_zoo as model_zoo

model_micro = torch.hub.load('pytorch/vision:v0.10.0', 'resnet18', weights="IMAGENET1K_V1")
#url = pmm.util.get_pretrained_microscopynet_url('resnet50', 'microscopynet')
#url = pmm.util.get_pretrained_microscopynet_url('resnet18', 'image-micronet')
#map_location=torch.device('cpu')
#model_micro.load_state_dict(model_zoo.load_url(url))
#model_micro.eval()  # <- MicrosNet model for


from torch import nn

class Identity(nn.Module):
    def __init__(self):
        super(Identity, self).__init__()

    def forward(self,x):
        return x

use_cuda = torch.cuda.is_available()
device = torch.device("cuda:0" if use_cuda else "cpu")
torch.backends.cudnn.benchmark = True

for param in model_micro.parameters():
    param.required_grad = False
    
#model_micro.layer3 = Identity()
#model_micro.layer4 = Identity()
#model_micro.avgpool = Identity()
#for i in range(0, 3):
#    model_micro.layer4[i] = Identity()
#print(model_vgg16.features[23])
model_micro.fc = nn.Sequential(nn.ReLU(),
                               nn.Dropout(p=0.60), #0.55
                               nn.Linear(512, 100), #150, 1
                                nn.ReLU(),
                                nn.Dropout(p=0.60),
                                 nn.Linear(100, 1)
                                 )

model_micro.to(device)
#print(model_micro)

#input = torch.randn(16, 3, 224, 224).to(device)
#input.to(device)
#print(input.shape)
#output = model_micro(input)
#output.shape

#model_micro.eval()

import torch
from torch import nn
from torch.nn import Conv2d
from torch import optim
from torchvision import datasets, transforms
from torch.utils.data import random_split
import torchvision.datasets as datasets
import torch.nn.functional as F

torch.backends.cudnn.deterministic = True
random.seed(1)
torch.manual_seed(1)
torch.cuda.manual_seed(1)
np.random.seed(1)
batch_size = 18

# CUDA for PyTorch
use_cuda = torch.cuda.is_available()
device = torch.device("cuda:0" if use_cuda else "cpu")
torch.backends.cudnn.benchmark = True



# Datasets
#data = torch.tensor(all_img, dtype=torch.float32)    #all_img
#target = torch.tensor(np.array(target), dtype = torch.float32)   #target

from sklearn.model_selection import train_test_split

from sklearn.model_selection import train_test_split

train_X, test_X, train_Y, test_Y = train_test_split(Data_CNN_rgb, Target_CNN, test_size=0.1, random_state=42) 
print(f'train_X.shape: {train_X.shape}, train_Y.shape: {train_Y.shape}')
print(f'test_X.shape: {test_X.shape}, test_Y.shape: {test_Y.shape}')

#x_train, x_test, y_train, y_test = train_test_split(old_patch_rgb, old_patch_Target, test_size = 0.1)

#x_train = torch.tensor(x_train, dtype=torch.float32)    #all_img
#y_train = torch.tensor(np.array(y_train), dtype = torch.float32)   #target

#x_val = torch.tensor(x_test, dtype=torch.float32).cuda()    #all_img
#y_val = torch.tensor(np.array(y_test), dtype = torch.float32)  #target

#Train_X, val_X, Train_Y, val_Y = train_test_split(train_X, train_Y, test_size = 0.1)

xtrain = torch.tensor(train_X, dtype=torch.float32)    #all_img
ytrain = torch.tensor(np.array(train_Y), dtype = torch.float32)   #target

x_val = torch.tensor(test_X, dtype=torch.float32)    #all_img
y_val = torch.tensor(np.array(test_Y), dtype = torch.float32)  #target

#xtest = torch.tensor(x_test, dtype=torch.float32).cuda()    #all_img
#ytest = torch.tensor(np.array(y_test), dtype = torch.float32).cuda()  #target

# Generators
# Train, validation split
from torch.utils.data import DataLoader, TensorDataset
train_dataset = Dataset(xtrain, ytrain, transform)
val_dataset = Dataset(x_val, y_val, transform)
#test_dataset = Dataset(xtest, ytest, transform)


train_loader = DataLoader(train_dataset,  batch_size = batch_size, shuffle = True, pin_memory=False)#, drop_last=True)#, num_workers= 2)
val_loader = DataLoader(val_dataset, batch_size = batch_size, shuffle = True, pin_memory=False)#, drop_last=True)
#test_loader = DataLoader(test_dataset,  batch_size = 1, shuffle = True, drop_last=True)

#define lossfunction
#loss = nn.MSELoss()

import torch.optim as optim


#criterion = nn.CrossEntropyLoss()
criterion = nn.MSELoss().cuda()
mae = nn.L1Loss().cuda()
#optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)
optimizer = optim.Adam(model_micro.parameters(), lr=0.0000225)#, weight_decay = 0.0001) # 0.005 was used in the saved model I

running_loss_list = []
val_running_loss_list = []
mean_abs_error_list = []
val_mean_abs_error_list = []
performance_record = {'train': {'loss': [], 'mae': []}, 'val': {'val_loss': [], 'val_mae': []}}

for epoch in range(1, 1000):  # loop over the dataset multiple times  2000,3000
  running_loss = 0.0
  val_running_loss = 0.0
  mean_abs_error = 0
  val_mean_abs_error = 0
  

  #batch_size = 16
  train_nbatch = len(ytrain) // batch_size
  val_nbatch = len(y_val) // batch_size
  model_micro.train()
  for i, data in enumerate(train_loader, 0):
    
    #print(i)
    # get the inputs; data is a list of [inputs, labels]
    inputs, labels = data
    inputs, labels = inputs.to(device), labels.to(device)
    
    # zero the parameter gradients
    optimizer.zero_grad()

    # forward + backward  + optimize
    
    outputs = model_micro(inputs)#.flatten()
    #print(outputs.dtype)
    #print(labels.dtype)
    loss = criterion(outputs, labels)
    loss.backward()
    optimizer.step()


    # print statistics

    running_loss += loss.item()
    
    #abs_error += torch.abs(outputs - labels).sum()
    mean_abs_error += mae(outputs, labels)
    #if i + 1 == train_nbatch:  # print every 2000 mini-batches
    
  # print(torch.cuda.memory_summary())    

  #with torch.no_grad():    
  model_micro.eval()
  for i, data in enumerate(val_loader, 0):
            
        inputs, labels = data
        inputs, labels = inputs.to(device), labels.to(device)
        outputs = model_micro(inputs)#.flatten()
        val_loss = criterion(outputs, labels)
        val_running_loss += val_loss.item()
        
        val_mean_abs_error += mae(outputs, labels)

    # print(torch.cuda.memory_summary())    
        
      
  running_loss_list.append(float(f'{running_loss /train_nbatch :.4f}'))
  val_running_loss_list.append(float(f'{val_running_loss /val_nbatch :.4f}'))
  mean_abs_error_list.append(float(f'{mean_abs_error/train_nbatch :.4f}'))
  val_mean_abs_error_list.append(float(f'{val_mean_abs_error /val_nbatch:.4f}'))
  print(f'Epoch{epoch}: loss: {running_loss /train_nbatch :.4f} val_loss: {val_running_loss / val_nbatch:.4f}, mae: {mean_abs_error/train_nbatch :.4f} val_mae:  {val_mean_abs_error /val_nbatch :.4f}')

performance_record['train']['loss'] += running_loss_list
performance_record['train']['mae'] += mean_abs_error_list
performance_record['val']['val_loss'] += val_running_loss_list
performance_record['val']['val_mae']  += val_mean_abs_error_list   
print('Finished Training')

checkpoint = {'state_dict': model_micro.state_dict(),
              'optimizer': optimizer.state_dict(),
              'epoch': epoch,
              'loss': loss}
torch.save(checkpoint, '/noether/s0/cfw5463/Model/2000epochs_b18_imagenetFT_checkpoint.pth')

with open("/noether/s0/cfw5463/Model/2000epochs_b18_imagenetFT_perfromance", "wb") as fp:   #Pickling
  pickle.dump(performance_record, fp)
  
# to save model
PATH = '/noether/s0/cfw5463/Model/2000epochs_b18_imagenetFT_model.pth'
torch.save(model_micro.state_dict(), PATH)

# specify path
PATH = "/noether/s0/cfw5463/Model/2000epochs_b18_imagenetFT_model.pth"
# to load model

#model = 
model_micro.load_state_dict(torch.load(PATH))
model_micro

from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from pylab import *

history_dict = performance_record
loss_values = history_dict['train']['loss']
val_loss_values = history_dict['val']['val_loss']

acc_values = history_dict['train']['mae']
val_acc_values = history_dict['val']['val_mae']
epochs = range(1, len(acc_values) + 1)
N = 200



fig, ax1 = plt.subplots()
rc('axes', linewidth=1.5)
plt.rcParams['font.size'] = '16'
#plt.rcParams['font.weight'] = 'bold'
plt.rcParams['font.style'] = 'italic'
plt.xlabel('Epochs', size=20)
plt.ylabel('MSE', size=20)

#plt.style.use("bmh")

plt.rcParams.update({'figure.figsize': (12.0, 8.0)})


# These are in unitless percentages of the figure size. (0,0 is bottom left)
left, bottom, width, height = [0.39, 0.55, 0.5, 0.32]
#left, bottom, width, height = [0.45, 0.45, 0.45, 0.45]
#ax2 = fig.add_axes([left, bottom, width, height])

ax1.plot(range(1, len(val_loss_values) + 1), val_loss_values, 'b', label = 'Validation Loss')
ax1.plot(range(1, len(loss_values) + 1), loss_values, 'r', label = 'Training Loss')

#ax2.plot(epochs[N:], val_loss_values[N:], 'b', label = 'Validation Loss')
#ax2.plot(epochs[N:], loss_values[N:], 'r', label = 'Training Loss')
#ax2.grid(axis='y')
#ax1.set_yscale('log')

ax1.grid(axis='y')


ax1.set_yticks([0.01], minor=True)

#ax1.set_yticks([0.007], minor=False)
#ax1.yaxis.grid(True, which='major')
#ax1.yaxis.grid(True, which='minor')
#plt.title('Training and validation accuracy')
plt.legend()

#plt.savefig("/noether/s0/iam5249/IM_models/IM_coverage_loss_resnet28_patch.png", dpi=600)
plt.savefig("/noether/s0/cfw5463/Model/2000epochs_b18_imagenetFT_MSE_best.png", dpi=600)
plt.show()

fig, ax1 = plt.subplots()
rc('axes', linewidth=1.5)
plt.rcParams['font.size'] = '16'
#plt.rcParams['font.weight'] = 'bold'
plt.rcParams['font.style'] = 'italic'
plt.xlabel('Epochs', size=20)
plt.ylabel('MAE', size=20)

#plt.style.use("bmh")

plt.rcParams.update({'figure.figsize': (12.0, 8.0)})


# These are in unitless percentages of the figure size. (0,0 is bottom left)
left, bottom, width, height = [0.39, 0.55, 0.5, 0.32]
#left, bottom, width, height = [0.45, 0.45, 0.45, 0.45]
#ax2 = fig.add_axes([left, bottom, width, height])

ax1.plot(range(1, len(val_loss_values) + 1), val_acc_values, 'b', label = 'Validation MAE')
ax1.plot(range(1, len(loss_values) + 1), acc_values, 'r', label = 'Training MAE')

#ax2.plot(epochs[N:], val_loss_values[N:], 'b', label = 'Validation Loss')
#ax2.plot(epochs[N:], loss_values[N:], 'r', label = 'Training Loss')
#ax2.grid(axis='y')
#ax1.set_yscale('log')
ax1.grid(axis='y')
#ax1.set_yticks([0.02, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175], minor=False)
#plt.title('Training and validation accuracy')
plt.legend()
#plt.savefig("/noether/s0/iam5249/IM_models/IM_coverage_mae_resnet_patch.png", dpi=600)

plt.savefig("/noether/s0/cfw5463/Model/2000epochs_b18_imagenetFT_MAE_best.png", dpi=600)
plt.show()

"""##Trasfer Learning"""

#x_val = torch.tensor(x_test, dtype=torch.float32).cuda()    #all_img
#test_y_val = torch.tensor(np.array(y_test).flatten(), dtype = torch.float32)  #target
#testval_dataset = Dataset(x_val, test_y_val, transform)

test_loader = DataLoader(val_dataset,  batch_size = 1, shuffle = True)


Test_X = []
Test_Y = []
#test_nbatch = 344
#test_mean_abs_error = 0
#test_mean_abs_error_list = []
with torch.no_grad():
    for i, data in enumerate(test_loader, 0):
            
        inputs, labels = data
        inputs, labels = inputs.to(device), labels.to(device)
        outputs = model_micro(inputs)
        #print(type(labels.tolist()))
        #print(type(outputs.tolist()))
        #break
        Test_X.append( labels.tolist() )
        Test_Y.append( outputs.tolist())
        #break the upcoming talk at MRS in April.

pred_Y1 = []
for example in Test_Y:
  #print(example)
  pred_Y1.append(example[0])

x_vals = []
for example in Test_X:
  x_vals.append(example[0])

y_vals =np.array(pred_Y1)
x_vals = np.array(x_vals)

with open('/noether/s0/cfw5463/Data/IMFT_x_vals.pkl', 'wb') as fid:
  pickle.dump(x_vals, fid)


with open('/noether/s0/cfw5463/Data/IMFT_y_vals.pkl', 'wb') as fid:
  pickle.dump(y_vals, fid)


from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
from matplotlib import  style


fig, ax = plt.subplots(figsize=(5, 5))
#ax.plot(Train_x, Train_y, '.', label = 'Train')
ax.scatter(x_vals, y_vals, s = 4,  label = 'Data')
ax.plot(x_vals, x_vals, label='Reference', c = 'r')
ax.set_aspect('equal')  # very helpful to show y = x relationship
ax.set_xlim([0, 1])
ax.set_ylim([0, 1])

# add labels and legend
ax.set_title('R2: ' + str(r2_score(x_vals, y_vals)))
ax.set_xlabel('Coverage', fontsize=15)
ax.set_ylabel('CNN coverage', fontsize=15)
ax.legend()
plt.savefig("/noether/s0/cfw5463/Model/2000epochs_b18_imagenetFT_parityplot.png", dpi=600)
plt.show()