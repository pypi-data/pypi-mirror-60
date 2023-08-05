#!/usr/bin/env python

##  playing_with_cifar10.py

"""
This is very similar to the example script playing_with_sequential.py
but is based on the inner class ExperimentsWithCIFAR which uses more common
examples of networks for playing with the CIFAR-10 dataset.
"""

import random
import numpy
import torch
import os, sys

"""
seed = 0           
random.seed(seed)
torch.manual_seed(seed)
torch.cuda.manual_seed(seed)
numpy.random.seed(seed)
torch.backends.cudnn.deterministic=True
torch.backends.cudnn.benchmarks=False
os.environ['PYTHONHASHSEED'] = str(seed)
"""
##  watch -d -n 0.5 nvidia-smi

from DLStudio import *

dls = DLStudio(
                  dataroot = "/home/kak/ImageDatasets/CIFAR-10/",
                  image_size = [32,32],
                  path_saved_model = "./saved_model",
                  momentum = 0.9,
                  learning_rate = 0.00001,
                  epochs = 10,
                  batch_size = 8,
                  classes = ('plane','car','bird','cat','deer',
                             'dog','frog','horse','ship','truck'),
                  debug_train = 0,
                  debug_test = 1,
              )


exp_cifar = DLStudio.ExperimentsWithCIFAR( dl_studio = dls )

exp_cifar.load_cifar_10_dataset_with_augmentation()
model = exp_cifar.Net()
dls.show_network_summary(model)
exp_cifar.run_code_for_training(model)
exp_cifar.save_model(model)
exp_cifar.run_code_for_testing(model)
