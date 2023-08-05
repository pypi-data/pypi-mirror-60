# -*- coding: utf-8 -*-

__version__   = '1.0.3'
__author__    = "Avinash Kak (kak@purdue.edu)"
__date__      = '2020-January-26'   
__url__       = 'https://engineering.purdue.edu/kak/distDLS/DLStudio-1.0.3.html'
__copyright__ = "(C) 2020 Avinash Kak. Python Software Foundation."

__doc__ = '''

DLStudio.py

Version: ''' + __version__ + '''
   
Author: Avinash Kak (kak@purdue.edu)

Date: ''' + __date__ + '''


@title
CHANGE LOG:

  Version 1.0.3:

    This is the first public release version of this module.

@title
INTRODUCTION:

    Every design activity involves mixing and matching things and doing so
    repeatedly until you have achieved the desired results.  The same thing
    is true of modern deep learning networks.  When you are working with a
    new data domain, it is likely that you would want to experiment with
    different network layouts that you may have dreamed of yourself or that
    you may have seen somewhere in a publication or at some web site.

    The goal of this module is to make it easier to engage in this process.
    The idea is that you would drop in the module a new network and you
    would be able to see right away the results you would get with the new
    network.

    This module also allows you to specify a deep network with a
    configuration string.  The module parses the string and creates the
    network.  In upcoming revisions of this module, I am planning to add
    additional features to this approach in order to make it more general
    and more useful for production work.


@title
INSTALLATION:

    The DLStudio class was packaged using setuptools.  For
    installation, execute the following command in the source directory
    (this is the directory that contains the setup.py file after you have
    downloaded and uncompressed the package):
 
            sudo python setup.py install

    and/or, for the case of Python3, 

            sudo python3 setup.py install

    On Linux distributions, this will install the module file at a location
    that looks like

             /usr/local/lib/python2.7/dist-packages/

    and, for the case of Python3, at a location that looks like

             /usr/local/lib/python3.6/dist-packages/

    If you do not have root access, you have the option of working directly
    off the directory in which you downloaded the software by simply
    placing the following statements at the top of your scripts that use
    the DLStudio class:

            import sys
            sys.path.append( "pathname_to_DLStudio_directory" )

    To uninstall the module, simply delete the source directory, locate
    where the DLStudio module was installed with "locate
    DLStudio" and delete those files.  As mentioned above,
    the full pathname to the installed version is likely to look like
    /usr/local/lib/python2.7/dist-packages/DLStudio*

    If you want to carry out a non-standard install of the
    DLStudio module, look up the on-line information on
    Disutils by pointing your browser to

              http://docs.python.org/dist/dist.html

@title
USAGE:

    If you want to specify a network with just a configuration string,
    your usage of the module is going to look like:


        from DLStudio import *
        
        convo_layers_config = "2x[128,7,7,1]-MaxPool(2) 1x[16,3,3,1]-MaxPool(2)"
        fc_layers_config = [-1,1024,10]
        
        dls = DLStudio(   dataroot = "/home/kak/ImageDatasets/CIFAR-10/",
                          image_size = [32,32],
                          convo_layers_config = convo_layers_config,
                          fc_layers_config = fc_layers_config,
                          path_saved_model = "./saved_model",
                          momentum = 0.9,
                          learning_rate = 0.00001,
                          epochs = 10,
                          batch_size = 8,
                          classes = ('plane','car','bird','cat','deer',
                                     'dog','frog','horse','ship','truck'),
                          debug_train = 0,
                          debug_test = 0,
                      )
        
        configs_for_all_convo_layers = dls.parse_config_string_for_convo_layers()
        convo_layers = dls.build_convo_layers2( configs_for_all_convo_layers )
        fc_layers = dls.build_fc_layers()
        model = dls.Net(convo_layers, fc_layers)
        dls.show_network_summary(model)
        dls.load_cifar_10_dataset()
        dls.run_code_for_training(model)
        dls.save_model(model)
        dls.run_code_for_testing(model)
                

    or, if you would rather experiment with a drop-in network, your usage
    of the module is going to look something like:


        dls = DLStudio(   dataroot = "/home/kak/ImageDatasets/CIFAR-10/",
                          image_size = [32,32],
                          path_saved_model = "./saved_model",
                          momentum = 0.9,
                          learning_rate = 0.00001,
                          epochs = 10,
                          batch_size = 8,
                          classes = ('plane','car','bird','cat','deer',
                                     'dog','frog','horse','ship','truck'),
                          debug_train = 0,
                          debug_test = 0,
                      )
        
        exp_seq = DLStudio.ExperimentsWithSequential( dl_studio = dls )   ## for your drop-in network
        exp_seq.load_cifar_10_dataset_with_augmentation()
        model = exp_seq.Net()
        dls.show_network_summary(model)
        exp_seq.run_code_for_training(model)
        exp_seq.save_model(model)
        exp_seq.run_code_for_testing(model)

        
    This assumes that you copy-and-pasted the network you want to
    experiment with in a class like ExperimentsWithSequential that is
    included in the module.


@title
CONSTRUCTOR PARAMETERS: 

    batch_size:  Carries the usual meaning in the neural network context.

    classes:  A list of the symbolic names for the classes.

    convo_layers_config: This parameter allows you to specify a convolutional network
                  with a configuration string.  Must be formatted as explained in the
                  comment block associated with the method
                  "parse_config_string_for_convo_layers()"

    dataroot: This points to where your dataset is located.

    debug_test: Setting it allow you to see images being used and their predicted
                 class labels every 2000 batch-based iterations of testing.

    debug_train: Does the same thing during training that debug_test does during
                 testing.

    epochs: Specifies the number of epochs to be used for training the network.

    fc_layers_config: This parameter allows you to specify the final
                 fully-connected portion of the network with just a list of
                 the number of nodes in each layer of this portion.  The
                 first entry in this list must be the number '-1', which
                 stands for the fact that the number of nodes in the first
                 layer will be determined by the final activation volume of
                 the convolutional portion of the network.

    image_size:  The heightxwidth size of the images in your dataset.

    learning_rate:  Again carries the usual meaning.

    momentum:  Carries the usual meaning and needed by the optimizer.

    path_saved_model: The path to where you want the trained model to be
                  saved in your disk so that it can be retrieved later
                  for inference.

    debug_train: By setting it, you will see the intermediate results
                    during training.  At the moment, when debug_train
                    evaluates to True, you will see the training images,
                    the ground truth, and the predictions every 2000
                    iterations of batch-based processing.
    
    debug_test: What debug_train does during training, debug_test does
                    during testing.


@title
PUBLIC METHODS:

    (1)  build_convo_layers()

         This method creates the convolutional layers from the parameters
         in the configuration string that was supplied through the
         constructor option 'convo_layers_config'.  The output produced by
         the call to 'parse_config_string_for_convo_layers()' is supplied
         as the argument to build_convo_layers().

    (2)  build_fc_layers()

         From the list of ints supplied through the constructor option
         'fc_layers_config', this method constructs the fully-connected
         portion of the overall network.

    (3)  check_a_sampling_of_images()        

         Displays the first batch_size number of images in your dataset.


    (4)  display_tensor_as_image()

         This method will display any tensor of shape (3,H,W), (1,H,W), or
         just (H,W) as an image. If any further data normalizations is
         needed for constructing a displayable image, the method takes care
         of that.  It has two input parameters: one for the tensor you want
         displayed as an image and the other for a title for the image
         display.  The latter parameter is default initialized to an empty
         string.

    (5)  load_cifar_10_dataset()

         This is just a convenience method that calls on Torchvision's
         functionality for creating a data loader.

    (6)  load_cifar_10_dataset_with_augmentation()             

         This convenience method also creates a data loader but it also
         includes the syntax for data augmentation.

    (7)  parse_config_string_for_convo_layers()

         As mentioned in the Introduction, DLStudio module allows you to
         specify a convolutional network with a string provided the string
         obeys the formatting convention described in the comment block of
         this method.  This method is for parsing such a string. The string
         itself is presented to the module through the constructor option
         'convo_layers_config'.

    (8)  run_code_for_testing()

         This is the method runs the trained model on the test data. Its
         output is a confusion matrix for the classes and the overall
         accuracy for each class.  The method has one input parameter which
         is set to the network to be tested.  This learnable parameters in
         the network are initialized with the disk-stored version of the
         trained model.

    (9)  run_code_for_training()

         This is the method that does all the training work. If a GPU was
         detected at the time an instance of the module was created, this
         method takes care of making the appropriate calls in order to
         transfer the tensors involved into the GPU memory.

    (10) save_model()

         Writes the model out to the disk at the location specified by the
         constructor option 'path_saved_model'.  Has one input parameter
         for the model that needs to be written out.

    (11) show_network_summary()

         Displays a print representation of your network and calls on the
         torchsummary module to print out the shape of the tensor at the
         output of each layer in the network. The method has one input
         parameter which is set to the network whose summary you want to
         see.


@title 
INNER CLASSES OF THE MODULE:

    The purpose of the following two inner classes is to demonstrate how
    you can create a custom class for your own network and test it within
    the framework provided by the DLStudio module.

    (1)  class ExperimentsWithSequential

         This class is my demonstration of experimenting with a network
         that I found on GitHub.  I copy-and-pasted it in this class to
         test its capabilities.  How to call on such a custom class is
         shown by the following script in the Examples directory:

                     playing_with_sequential.py

    (2)  class ExperimentsWithCIFAR

         This is very similar to the previous inner class, but uses a
         common example of a network for experimenting with the CIFAR-10
         dataset. Consisting of 32x32 images, this is a great dataset for
         creating classroom demonstrations of convolutional networks.
         As to how you should use this class is shown in the following
         script

                    playing_with_cifar10.py

         in the Examples directory of the distribution.


@title 
THE Examples DIRECTORY:

    The Examples subdirectory in the distribution contains the following
    three scripts:

    (1)  playing_with_reconfig.py

         Shows how you can specify a convolution network with a
         configuration string.  The DLStudio module parses the string
         constructs the network.

    (2)  playing_with_sequential.py

         Shows you how you can call on a custom inner class of the
         'DLStudio' module that is meant to experiment with your own
         network.  The name of the inner class in this example script is
         ExperimentsWithSequential

    (3)  playing_with_cifar10.py

         This is very similar to the previous example script but is based
         on the inner class ExperimentsWithCIFAR which uses more common
         examples of networks for playing with the CIFAR-10 dataset.


@title
BUGS:

    Please notify the author if you encounter any bugs.  When sending
    email, please place the string 'DLStudio' in the subject line to get
    past the author's spam filter.


@title
ABOUT THE AUTHOR:

    The author, Avinash Kak, is a professor of Electrical and Computer
    Engineering at Purdue University.  For all issues related to this
    module, contact the author at kak@purdue.edu If you send email, please
    place the string "DLStudio" in your subject line to get past the
    author's spam filter.

@title
COPYRIGHT:

    Python Software Foundation License

    Copyright 2020 Avinash Kak

@endofdocs
'''


import sys,os,os.path
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision                  
import torchvision.transforms as tvt
import torch.optim as optim
from torchsummary import summary           
import numpy as np
import re
import math
import random
import copy
import matplotlib.pyplot as plt

#______________________________  DLStudio Class Definition  ________________________________

class DLStudio(object):

    def __init__(self, *args, **kwargs ):
        if args:
            raise ValueError(  
                   '''DLStudio constructor can only be called with keyword arguments for 
                      the following keywords: epochs, learning_rate, batch_size, momentum,
                      convo_layers_config, image_size, dataroot, path_saved_model, classes, 
                      image_size, convo_layers_config, fc_layers_config, debug_train, and 
                      debug_test''')
        learning_rate = epochs = batch_size = convo_layers_config = momentum = None
        image_size = fc_layers_config = dataroot =  path_saved_model = classes = None
        debug_train  = debug_test = None
        if 'dataroot' in kwargs                      :   dataroot = kwargs.pop('dataroot')
        if 'learning_rate' in kwargs                 :   learning_rate = kwargs.pop('learning_rate')
        if 'momentum' in kwargs                      :   momentum = kwargs.pop('momentum')
        if 'epochs' in kwargs                        :   epochs = kwargs.pop('epochs')
        if 'batch_size' in kwargs                    :   batch_size = kwargs.pop('batch_size')
        if 'convo_layers_config' in kwargs           :   convo_layers_config = kwargs.pop('convo_layers_config')
        if 'image_size' in kwargs                    :   image_size = kwargs.pop('image_size')
        if 'fc_layers_config' in kwargs              :   fc_layers_config = kwargs.pop('fc_layers_config')
        if 'path_saved_model' in kwargs              :   path_saved_model = kwargs.pop('path_saved_model')
        if 'classes' in kwargs                       :   classes = kwargs.pop('classes') 
        if 'debug_train' in kwargs                   :   debug_train = kwargs.pop('debug_train') 
        if 'debug_test' in kwargs                    :   debug_test = kwargs.pop('debug_test') 
        if len(kwargs) != 0: raise ValueError('''You have provided unrecognizable keyword args''')
        if dataroot:
            self.dataroot = dataroot
        if convo_layers_config:
            self.convo_layers_config = convo_layers_config
        if image_size:
            self.image_size = image_size
        if fc_layers_config:
            self.fc_layers_config = fc_layers_config
            if fc_layers_config[0] is not -1:
                raise Exception("""\n\n\nYour 'fc_layers_config' construction option is not correct. """
                                """The first element of the list of nodes in the fc layer must be -1 """
                                """because the input to fc will be set automatically to the size of """
                                """the final activation volume of the convolutional part of the network""")
        if  path_saved_model:
            self.path_saved_model = path_saved_model
        if classes:
            self.class_labels = classes
        if learning_rate:
            self.learning_rate = learning_rate
        else:
            self.learning_rate = 1e-6
        if momentum:
            self.momentum = momentum
        if epochs:
            self.epochs = epochs
        if batch_size:
            self.batch_size = batch_size
        if debug_train:                             
            self.debug_train = debug_train
        else:
            self.debug_train = 0
        if debug_test:                             
            self.debug_test = debug_test
        else:
            self.debug_test = 0
        self.debug_config = 0
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


    def parse_config_string_for_convo_layers(self):
        '''
        Each collection of 'n' otherwise identical layers in a convolutional network is 
        specified by a string that looks like:

                                 "nx[a,b,c,d]-MaxPool(k)"
        where 
                n      =  num of this type of convo layer
                a      =  number of out_channels                      [in_channels determined by prev layer] 
                b,c    =  kernel for this layer is of size (b,c)      [b along height, c along width]
                d      =  stride for convolutions
                k      =  maxpooling over kxk patches with stride of k

        Example:
                     "n1x[a1,b1,c1,d1]-MaxPool(k1)  n2x[a2,b2,c2,d2]-MaxPool(k2)"
        '''
        configuration = self.convo_layers_config
        configs = configuration.split()
        all_convo_layers = []
        image_size_after_layer = self.image_size
        for k,config in enumerate(configs):
            two_parts = config.split('-')
            how_many_conv_layers_with_this_config = int(two_parts[0][:config.index('x')])
            if self.debug_config:
                print("\n\nhow many convo layers with this config: %d" % how_many_conv_layers_with_this_config)
            maxpooling_size = int(re.findall(r'\d+', two_parts[1])[0])
            if self.debug_config:
                print("\nmax pooling size for all convo layers with this config: %d" % maxpooling_size)
            for conv_layer in range(how_many_conv_layers_with_this_config):            
                convo_layer = {'out_channels':None, 
                               'kernel_size':None, 
                               'convo_stride':None, 
                               'maxpool_size':None,
                               'maxpool_stride': None}
                kernel_params = two_parts[0][config.index('x')+1:][1:-1].split(',')
                if self.debug_config:
                    print("\nkernel_params: %s" % str(kernel_params))
                convo_layer['out_channels'] = int(kernel_params[0])
                convo_layer['kernel_size'] = (int(kernel_params[1]), int(kernel_params[2]))
                convo_layer['convo_stride'] =  int(kernel_params[3])
                image_size_after_layer = [x // convo_layer['convo_stride'] for x in image_size_after_layer]
                convo_layer['maxpool_size'] = maxpooling_size
                convo_layer['maxpool_stride'] = maxpooling_size
                image_size_after_layer = [x // convo_layer['maxpool_size'] for x in image_size_after_layer]
                all_convo_layers.append(convo_layer)
        configs_for_all_convo_layers = {i : all_convo_layers[i] for i in range(len(all_convo_layers))}
        if self.debug_config:
            print("\n\nAll convo layers: %s" % str(configs_for_all_convo_layers))
        last_convo_layer = configs_for_all_convo_layers[len(all_convo_layers)-1]
        out_nodes_final_layer = image_size_after_layer[0] * image_size_after_layer[1] * \
                                                                      last_convo_layer['out_channels']
        self.fc_layers_config[0] = out_nodes_final_layer
        self.configs_for_all_convo_layers = configs_for_all_convo_layers
        return configs_for_all_convo_layers


    def build_convo_layers(self, configs_for_all_convo_layers):
        conv_layers = nn.ModuleList()
        in_channels_for_next_layer = None
        for layer_index in configs_for_all_convo_layers:
            if self.debug_config:
                print("\n\n\nLayer index: %d" % layer_index)
            in_channels = 3 if layer_index == 0 else in_channels_for_next_layer
            out_channels = configs_for_all_convo_layers[layer_index]['out_channels']
            kernel_size = configs_for_all_convo_layers[layer_index]['kernel_size']
            padding = tuple((k-1) // 2 for k in kernel_size)
            stride       = configs_for_all_convo_layers[layer_index]['convo_stride']
            maxpool_size = configs_for_all_convo_layers[layer_index]['maxpool_size']
            if self.debug_config:
                print("\n     in_channels=%d   out_channels=%d    kernel_size=%s     stride=%s    \
                maxpool_size=%s" % (in_channels, out_channels, str(kernel_size), str(stride), 
                str(maxpool_size)))
            conv_layers.append( nn.Conv2d( in_channels,out_channels,kernel_size,stride=stride,padding=padding) )
            conv_layers.append( nn.MaxPool2d( maxpool_size ) )
            conv_layers.append( nn.ReLU() ),
            in_channels_for_next_layer = out_channels
        return conv_layers


    def build_fc_layers(self):
        fc_layers = nn.ModuleList()
        for layer_index in range(len(self.fc_layers_config) - 1):
            fc_layers.append( nn.Linear( self.fc_layers_config[layer_index], 
                                                                self.fc_layers_config[layer_index+1] ) )
        return fc_layers            


    def load_cifar_10_dataset(self):       
        '''
        We make sure that the transformation applied to the image end the images being normalized.
        Consider this call to normalize: "Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))".  The three
        numbers in the first tuple affect the means in the three color channels and the three 
        numbers in the second tuple affect the standard deviations.  In this case, we want the 
        image value in each channel to be changed to:

                 image_channel_val = (image_channel_val - mean) / std

        So with mean and std both set 0.5 for all three channels, if the image tensor originally 
        was between 0 and 1.0, after this normalization, the tensor will be between -1.0 and +1.0. 
        If needed we can do inverse normalization  by

                 image_channel_val  =   (image_channel_val * std) + mean
        '''
        ##   The call to ToTensor() converts the usual int range 0-255 for pixel values to 0-1.0 float vals
        ##   But then the call to Normalize() changes the range to -1.0-1.0 float vals.
        transform = tvt.Compose([tvt.ToTensor(),
                                 tvt.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])    ## accuracy: 51%
        ##  Define where the training and the test datasets are located:
        train_data_loc = torchvision.datasets.CIFAR10(root=self.dataroot, train=True,
                                                    download=True, transform=transform)
        test_data_loc = torchvision.datasets.CIFAR10(root=self.dataroot, train=False,
                                                    download=True, transform=transform)
        ##  Now create the data loaders:
        self.train_data_loader = torch.utils.data.DataLoader(train_data_loc,batch_size=self.batch_size,
                                                                            shuffle=True, num_workers=2)
        self.test_data_loader = torch.utils.data.DataLoader(test_data_loc,batch_size=self.batch_size,
                                                                           shuffle=False, num_workers=2)

    def load_cifar_10_dataset_with_augmentation(self):             
        '''
        In general, we want to do data augmentation for training:
        '''
        transform_train = tvt.Compose([
                                  tvt.RandomCrop(32, padding=4),
                                  tvt.RandomHorizontalFlip(),
                                  tvt.ToTensor(),
#                                  tvt.Normalize((0.20, 0.20, 0.20), (0.20, 0.20, 0.20))]) 
                                  tvt.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])        
        ##  Don't need any augmentation for the test data: 
        transform_test = tvt.Compose([
                               tvt.ToTensor(),
#                               tvt.Normalize((0.20, 0.20, 0.20), (0.20, 0.20, 0.20))])  
                               tvt.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
        ##  Define where the training and the test datasets are located
        train_data_loc = torchvision.datasets.CIFAR10(
                        root=self.dataroot, train=True, download=True, transform=transform_train)
        test_data_loc = torchvision.datasets.CIFAR10(
                      root=self.dataroot, train=False, download=True, transform=transform_test)
        ##  Now create the data loaders:
        self.train_data_loader = torch.utils.data.DataLoader(train_data_loc, batch_size=self.batch_size, 
                                                                     shuffle=True, num_workers=2)
        self.test_data_loader = torch.utils.data.DataLoader(test_data_loc, batch_size=self.batch_size, 
                                                                 shuffle=False, num_workers=2)

    def imshow(self, img):
        '''
        called by display_tensor_as_image() for displaying the image
        '''
        img = img / 2 + 0.5     # unnormalize
        npimg = img.numpy()
        plt.imshow(np.transpose(npimg, (1, 2, 0)))
        plt.show()


    class Net(nn.Module):
        def __init__(self, convo_layers, fc_layers):
            super(DLStudio.Net, self).__init__()
            self.my_modules_convo = convo_layers
            self.my_modules_fc = fc_layers
        def forward(self, x):
            for m in self.my_modules_convo:
                x = m(x)
            x = x.view(x.size(0), -1)
            for m in self.my_modules_fc:
                x = m(x)
            return x

    def show_network_summary(self, net):
        print("\n\n\nprinting out the model:")
        print(net)
        print("\n\n\na summary of input/output for the model:")
#        summary(net, (3,32,32),-1, device='cpu')
        summary(net, (3,self.image_size[0],self.image_size[1]),-1, device='cpu')


    def run_code_for_training(self, net):        
        net = copy.deepcopy(net)
        net = net.to(self.device)
        '''
        We will use torch.nn.CrossEntropyLoss for the loss function.  Assume that the vector
        x corresponds to the values at the 10 output nodes. We will interpret normalized versions
        of these values as  probabilities --- the normalization being as shown inside the square
        brackets below.  Let 'class' be the true class for the input --- remember 'class' in an
        integer index in range(10). If our classification was absolutely correct, the NORMALIZED
        value for x[class], with normalization being carried out by the ratio inside the square
        brackets, would be 1 and x would be zero at the other nine positions in the vector.
        In this case, the ratio inside the brackets shown below would be 1.0 and the log of
        that would be 0.  That is, when a correct classification decision is made, the value for 
        CrossEntropyLoss would be zero.  On other hand, when an incorrect decision is made
        and we examine the value of the same element x[class], it will DEFINITELY be less
        than 1 and possibly even 0. The closer x[class] is to zero, the larger the value for
        CrossEntropyLoss shown below.
                                                  _                      _                              
                                                 |     exp( x[class] )    |
              CrossEntropyLoss(x, class) = - log |  --------------------- |
                                                 |_  \sum_j exp( x[j] )  _|
                                                    
        Note that "exp( x[class])"  is always positive and, by normalizing it with the
        summation in the denominator, the quantity inside the square brackets is guaranteed
        to be in the range [0,1.0].  Since the log of a fraction is always negative, the
        value calculated for the CrossEntropyLoss when the label assigned to an input is
        'class' will always be a positive number in the range [0, +inf).  In summary, the loss
        is zero when the output classification is correct and some large positive number when
        the classification is wrong.
        '''
        criterion = nn.CrossEntropyLoss()

        ##  The most straightforward way to do gradient descent is to (1) visualize the loss as
        ##  defining a cost function over the hyperplane spanned by all the learnable parameters;
        ##  (2) standing at the point in the hyperplane that corresponds to the currently known
        ##  values for the parameters and looking straight up at the loss-function surface; 
        ##  (3) estimating the gradient of the loss-function surface at that point; (4) taking
        ##  a small step in the hyperplane in a direction opposite to that of the gradient, the
        ##  size of the step being the product of the gradient and the learning rate.
        ##
        ##  The scenario painted above would work well when the cost-function surface is
        ##  well-rounded around the global minimum.  Unfortunately, the cost-function surfaces 
        ##  associated with real-world problems tend to be complex: instead of being well-rounded,
        ##  the surface may form a narrow valley in the vicinity of the global and, in addition,
        ##  there may also exist local minima.  While the problems caused by local minima can be
        ##  somewhat mitigated by using SGD instead by the traditional GD, the problems
        ##  caused by narrow long valleys are best dealt with by using smart stepping strategies
        ##  that, in the context of DL, are handled by the modern day optimizers. One strategy
        ##  when calculating the step to take at the current point in the hyperplane is to also
        ##  examine the gradient at the previous step. If the current gradient and the previous
        ##  gradient are of the same sign, that mean you are headed straight down the hill. On
        ##  the other hand, if the current gradient's sign is opposite of the sign of the previous
        ##  you have reached the bottom spine of a narrow valley and now you are on the other
        ##  side of the spine.  Just by the expedient of adding momentum times the previous
        ##  gradient with the current gradient using the result for calculating the new step
        ##  dampens the oscillations that the path will otherwise go through around the bottom
        ##  spine of a narrow valley.
        optimizer = optim.SGD(net.parameters(), lr=self.learning_rate, momentum=self.momentum)
        
        ##  Loop over the dataset as many times as self.epochs
        for epoch in range(self.epochs):  
            ##  We will use running_loss to accumulate the losses over 2000 batches in order
            ##  to present an averaged (over 2000) loss to the user.
            running_loss = 0.0
            for i, data in enumerate(self.train_data_loader):
                ##  If batch_size is, say, 4, inputs is a tensor of shape (4,3,32,32) where 3 is
                ##  for the color channels, and labels is something like 'tensor([8, 7, 5, 1])' 
                ##  where the individual integers correspond to the labels of the four images 
                ##  in a batch.  BTW, You can print out the label integers as a list by calling
                ##  "list(labels.numpy())"
                inputs, labels = data
                if self.debug_train and i % 2000 == 1999:
                    print("\n\n[iter=%d:] Ground Truth:     " % (i+1) + 
                    ' '.join('%5s' % self.class_labels[labels[j]] for j in range(self.batch_size)))
                inputs_cuda = inputs.to(self.device)
                labels_cuda = labels.to(self.device)
                ##  Since PyTorch likes to construct dynamic computational graphs, we need to
                ##  zero out the previously calculated gradients for the learnable parameters:
                optimizer.zero_grad()
                # Make the predictions with the model:
                outputs_cuda = net(inputs_cuda)
                ##  The 'output' tensor at this point is going to look like:
                ##        tensor([[-0.06, 0.08, -0.05, -0.04, 0.08, -0.08, -0.12, -0.01, -0.02, -0.01],
                ##                [-0.05, 0.08, -0.04, -0.03, 0.08, -0.08, -0.11, -0.00, -0.03, -0.00],
                ##                [-0.06, 0.08, -0.06, -0.04, 0.08, -0.09, -0.12, -0.01, -0.02, -0.01],
                ##                [-0.06, 0.09, -0.04, -0.04, 0.07, -0.09, -0.12, -0.01, -0.04, -0.01]], 
                ##                        device='cuda:0', grad_fn=<AddmmBackward>)
                loss_cuda = criterion(outputs_cuda, labels_cuda)
                if self.debug_train and i % 2000 == 1999:
                    _, predicted = torch.max(outputs_cuda.data, 1)
                    print("[iter=%d:] Predicted Labels: " % (i+1) + 
                     ' '.join('%5s' % self.class_labels[predicted[j]] for j in range(self.batch_size)))
                    self.display_tensor_as_image(torchvision.utils.make_grid(inputs, normalize=True), 
                                            "see terminal for TRAINING results at iter=%d" % (i+1))
                ##  The call to backward() will cause the calculation of the gradients of Loss
                ##  with respect to each of the learnable parameters
                loss_cuda.backward()
                ##  Note that we take the next step in the parameter hyperplane for EACH batch.
                ##  The larger the size of the batch, the less noisy the steps --- but at the
                ##  cost of a lower probability to escape local minima and saddle points in 
                ##  the overall loss surface over the hyperplane defined by all the learnable 
                ##  parameters.
                optimizer.step()
                ##  Present to the average value of the loss over the past 2000 batches:            
                running_loss += loss_cuda.item()
                if i % 2000 == 1999:    
                    print("\n[epoch:%d, batch:%5d] loss: %.3f" % 
                                            (epoch + 1, i + 1, running_loss / float(2000)))
                    running_loss = 0.0
        print("\nFinished Training\n")


    def display_tensor_as_image(self, tensor, title=""):
        '''
        This method converts the argument tensor into a photo image that you can display
        in your terminal screen. It can convert tensors of three different shapes
        into images: (3,H,W), (1,H,W), and (H,W), where H, for height, stands for the
        number of pixels in the vertical direction and W, for width, for the same
        along the horizontal direction.  When the first element of the shape is 3,
        that means that the tensor represents a color image in which each pixel in
        the (H,W) plane has three values for the three color channels.  On the other
        hand, when the first element is 1, that stands for a tensor that will be
        shown as a grayscale image.  And when the shape is just (H,W), that is
        automatically taken to be for a grayscale image.
        '''
        tensor_range = (torch.min(tensor).item(), torch.max(tensor).item())
#            print("\n\n\ndisplay_tensor_as_image() called with tensor values range: %s" % str(tensor_range))
        if tensor_range == (-1.0,1.0):
            ##  The tensors must be between 0.0 and 1.0 for the display:
            print("\n\n\nimage un-normalization called")
            tensor = tensor/2.0 + 0.5     # unnormalize

        ###  The 'plt' in the following statement stands for the plotting module
        ###  matplotlib.pyplot.  See the module import declarations at the beginning of
        ###  this module.
        plt.figure(title)
        ###  The call to plt.imshow() shown below needs a numpy array. We must also
        ###  transpose the array so that the number of channels (the same thing as the
        ###  number of color planes) is in the last element.  For a tensor, it would be in
        ###  the first element.
        if tensor.shape[0] == 3 and len(tensor.shape) == 3:
            plt.imshow( tensor.numpy().transpose(1,2,0) )
        ###  If the grayscale image was produced by calling torchvision.transform's
        ###  ".ToPILImage()", and the result converted to a tensor, the tensor shape will
        ###  again have three elements in it, however the first element that stands for
        ###  the number of channels will now be 1
        elif tensor.shape[0] == 1 and len(tensor.shape) == 3:
            tensor = tensor[0,:,:]
            plt.imshow( tensor.numpy(), cmap = 'gray' )
        ###  For any one color channel extracted from the tensor representation of a color
        ###  image, the shape of the tensor will be (W,H):
        elif len(tensor.shape) == 2:
            plt.imshow( tensor.numpy(), cmap = 'gray' )
        else:
            sys.exit("\n\n\ntensor for image is ill formed -- aborting")
        plt.show()


    def check_a_sampling_of_images(self):
        '''
        Displays the first batch_size number of images in your dataset.
        '''
        dataiter = iter(self.train_data_loader)
        images, labels = dataiter.next()
        # Since negative pixel values make no sense for display, setting the 'normalize' 
        # option to True will change the range back from (-1.0,1.0) to (0.0,1.0):
        self.display_tensor_as_image(torchvision.utils.make_grid(images, normalize=True))
        # Print class labels for the images shown:
        print(' '.join('%5s' % self.class_labels[labels[j]] for j in range(self.batch_size)))


    def save_model(self, model):
        '''
        Save the trained model to a disk file
        '''
        torch.save(model.state_dict(), self.path_saved_model)
    

    def run_code_for_testing(self, net):
        ##  Let's now load in the model that was learned from training session --- assuming that
        ##  the model was saved to a disk file that is at self.path_saved_model:
        ##  Note how we recreate our model from what we stored in a disk file at the
        ##  end of the training session.  We first instantiate the class Net and then, in 
        ##  the next statement, we restore its learnable parameters to what we obtained
        ##  from training:
#        net = DLStudio.ExperimentsWithCIFAR.Net()
        net.load_state_dict(torch.load(self.path_saved_model))

        ##  In what follows, in addition to determining the predicted label for each test
        ##  image, we will some compute some stats to measure the overall performance of
        ##  the trained network.  This we will do in two different ways: For each class,
        ##  we will measure how frequently the network predicts the correct labels.  In
        ##  we will compute the confusion matrix for the predictions.
        correct = 0
        total = 0
        confusion_matrix = torch.zeros(len(self.class_labels), len(self.class_labels))
        class_correct = [0] * len(self.class_labels)
        class_total = [0] * len(self.class_labels)

        ##  Since the default behavior of PyTorch is to construct a computational graph and
        ##  calculate the partial derivatives at the nodes of the graph, these partial derivatives
        ##  being used in the backpropagation of the the loss for the estimation of the 
        ##  gradients of the loss with respect to the learnable parameters.  All of that 
        ##  work would be a waste of time during the testing phase.  So we suppress it with
        ##  the directive "torch.no_grad()" as shown below:
        with torch.no_grad():
            for i,data in enumerate(self.test_data_loader):
                ##  data is set to the images and the labels for one batch at a time:
                images, labels = data
                if self.debug_test and i % 1000 == 0:
                    print("\n\n[i=%d:] Ground Truth:     " %i + ' '.join('%5s' % self.class_labels[labels[j]] 
                                                                    for j in range(self.batch_size)))
                outputs = net(images)
                ##  max() returns two things: the max value and its index in the 10 element
                ##  output vector.  We are only interested in the index --- since that is 
                ##  essentially the predicted class label:
                _, predicted = torch.max(outputs.data, 1)
                if self.debug_test and i % 1000 == 0:
                    print("[i=%d:] Predicted Labels: " %i + ' '.join('%5s' % self.class_labels[predicted[j]]
                                                                    for j in range(self.batch_size)))
                    self.display_tensor_as_image(torchvision.utils.make_grid(images, normalize=True), 
                                                         "see terminal for test results at i=%d" % i)
                for label,prediction in zip(labels,predicted):
                        confusion_matrix[label][prediction] += 1
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
                ##  comp is a list of size batch_size of "True" and "False" vals
                comp = predicted == labels       
                for j in range(self.batch_size):
                    label = labels[j]
                    ##  The following works because, in a numeric context, the boolean value
                    ##  "False" is the same as number 0 and the boolean value True is the 
                    ##  same as number 1. For that reason "4 + True" will evaluate to 5 and
                    ##  "4 + False" will evaluate to 4.  Also, "1 == True" evaluates to "True"
                    ##  "1 == False" evaluates to "False".  However, note that "1 is True" 
                    ##  evaluates to "False" because the operator "is" does not provide a 
                    ##  numeric context for "True". And so on.  In the statement that follows,
                    ##  while  c[j].item() will either return "False" or "True", for the 
                    ##  addition operator, Python will use the values 0 and 1 instead.
                    class_correct[label] += comp[j].item()
                    class_total[label] += 1
        for j in range(len(self.class_labels)):
            print('Prediction accuracy for %5s : %2d %%' % (
                               self.class_labels[j], 100 * class_correct[j] / class_total[j]))
        print("\n\n\nOverall accuracy of the network on the 10000 test images: %d %%" % 
                                                               (100 * correct / float(total)))
        print("\n\nDisplaying the confusion matrix:\n")
        out_str = "         "
        for j in range(len(self.class_labels)):  out_str +=  "%7s" % self.class_labels[j]   
        print(out_str + "\n")
        for i,label in enumerate(self.class_labels):
            out_percents = [100 * confusion_matrix[i,j] / float(class_total[i]) 
                                                      for j in range(len(self.class_labels))]
            out_percents = ["%.2f" % item.item() for item in out_percents]
            out_str = "%6s:  " % self.class_labels[i]
            for j in range(len(self.class_labels)): out_str +=  "%7s" % out_percents[j]
            print(out_str)


    ##################  Start Definition of Inner Class ExperimentsWithSequential ##############

    class ExperimentsWithSequential(nn.Module):                                
        """
        Demonstrates how to use the torch.nn.Sequential container class
        """
        def __init__(self, dl_studio ):
            super(DLStudio.ExperimentsWithSequential, self).__init__()
            self.dl_studio = dl_studio

        def load_cifar_10_dataset(self):       
            self.dl_studio.load_cifar_10_dataset()

        def load_cifar_10_dataset_with_augmentation(self):             
            self.dl_studio.load_cifar_10_dataset_with_augmentation()

        class Net(nn.Module):
            """
            To see if the DLStudio class would work with any network that a user may want
            to experiment with, I copy-and-pasted the the network shown below from the following
            page by Zhenye at GitHub:
                         https://zhenye-na.github.io/2018/09/28/pytorch-cnn-cifar10.html
            """
            def __init__(self):
                super(DLStudio.ExperimentsWithSequential.Net, self).__init__()
                self.conv_seqn = nn.Sequential(
                    # Conv Layer block 1:
                    nn.Conv2d(in_channels=3, out_channels=32, kernel_size=3, padding=1),
                    nn.BatchNorm2d(32),
                    nn.ReLU(inplace=True),
                    nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1),
                    nn.ReLU(inplace=True),
                    nn.MaxPool2d(kernel_size=2, stride=2),
                    # Conv Layer block 2:
                    nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, padding=1),
                    nn.BatchNorm2d(128),
                    nn.ReLU(inplace=True),
                    nn.Conv2d(in_channels=128, out_channels=128, kernel_size=3, padding=1),
                    nn.ReLU(inplace=True),
                    nn.MaxPool2d(kernel_size=2, stride=2),
                    nn.Dropout2d(p=0.05),
                    # Conv Layer block 3:
                    nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, padding=1),
                    nn.BatchNorm2d(256),
                    nn.ReLU(inplace=True),
                    nn.Conv2d(in_channels=256, out_channels=256, kernel_size=3, padding=1),
                    nn.ReLU(inplace=True),
                    nn.MaxPool2d(kernel_size=2, stride=2),
                )
                self.fc_seqn = nn.Sequential(
                    nn.Dropout(p=0.1),
                    nn.Linear(4096, 1024),
                    nn.ReLU(inplace=True),
                    nn.Linear(1024, 512),
                    nn.ReLU(inplace=True),
                    nn.Dropout(p=0.1),
                    nn.Linear(512, 10)
                )
    
            def forward(self, x):
                x = self.conv_seqn(x)
                # flatten
                x = x.view(x.size(0), -1)
                x = self.fc_seqn(x)
                return x

        def run_code_for_training(self, net):        
            self.dl_studio.run_code_for_training(net)

            
        def save_model(self, model):
            '''
            Save the trained model to a disk file
            '''
            torch.save(model.state_dict(), self.dl_studio.path_saved_model)


        def run_code_for_testing(self, model):
            self.dl_studio.run_code_for_testing(model)


    ##################  Start Definition of Inner Class ExperimentsWithCIFAR ##############

    class ExperimentsWithCIFAR(nn.Module):              

        def __init__(self, dl_studio ):
            super(DLStudio.ExperimentsWithCIFAR, self).__init__()
            self.dl_studio = dl_studio

        def load_cifar_10_dataset(self):       
            self.dl_studio.load_cifar_10_dataset()

        def load_cifar_10_dataset_with_augmentation(self):             
            self.dl_studio.load_cifar_10_dataset_with_augmentation()

        class Net(nn.Module):

            def __init__(self):
                super(DLStudio.ExperimentsWithCIFAR.Net, self).__init__()
                ## in_channels=3  out_channels=6  kernel_size=5x5
                ## kernel_size, stride, and padding can either be single nums or tuple of 2 nums 
                ## here we use a default of 1 for stride
                self.conv1 = nn.Conv2d(3, 6, (6,6))
                ## The first arg for MaxPool is for patch-size and the second for stride 
                ## Each arg is either a single num or a tuple of two nums (for height and width)
                ## If stride is not provided, BY DEFAULT stride is set to patch-size.
                self.pool = nn.MaxPool2d(2, 2)
                self.relu = nn.ReLU()
                ## In the following layer, in_channels=6  out_channels=16  kernel_size=4x4 
                self.conv2 = nn.Conv2d(6, 16, 4)
                self.fc1 = nn.Linear(16 * 5 * 5, 150)
                self.fc2 = nn.Linear(150, 100)
                self.fc3 = nn.Linear(100, 10)
        
            def forward(self, x):
                ##  We know that forward() begins its with work x shaped as (4,3,32,32) where
                ##  4 is the batch size, 3 in_channels, and where the input image size is 32x32.
                x = self.relu(self.conv1(x))
                ##  The shape of this x is (4,6,27,27). So the question is why has the image size 
                ##  gone down from 32x32 to 27x27.   To understand this, consider a 1-D digital
                ##  signal that has 32 elements in it.  We want to correlate it with a window
                ##  of size 6 elements.  For the first position of the window, we will at its
                ##  leftmost position where it will be over the signal elements 1 through 6.
                ##  Next we will move the 6-element window one element to the right. At this
                ##  position, the window will be over the signal elements 2 though 7; and so 
                ##  on. At the 27th position of the window, the window will be over the signal
                ##  elements 27 through 32. The window CAN NOT be moved any further to the right.
                ##  Therefore, the convolution (or the correlation) will ONLY produce 27 values.
                ##
                ##  In general, if you are convolving a signal of width N elements with a window
                ##  of size W, you will get exactly N-W+1 output values (assuming that you do not
                ##  want the window to be moved beyond the boundaries of signal in either direction.)

                ##  Therefore, the input tensor to the following maxpooling operation is of shape
                ##  (4,6,27,27)
                x = self.pool(x)                                 
                ##  This maxpooling will be carried out with a patch size of 2x2 and stride of
                ##  (2,2).  To understand what the size of the output will be, let's consider
                ##  a 1-D signal consisting of 27 elements.  We will scan it with NONoverlapping
                ##  2-element windows and choose the maximum value in each window position.
                ##  Since we can only accommodate 13 such NONoverlapping windows, we will only
                ##  13 output values.  For the 2-D case of 27x27 images, the output of this
                ##  maxpooling operation will be of size 13x13.   
                ##
                ##  Since maxpooling is applied to each channel separately, the shape of this
                ##  maxpooling output is (4,6,13,13)

                ##  To understand the change in shape of the tensor x in the next operation,
                ##  you just have to combine the previous two explanations.  First, the operation
                ##  self.conv2() has a kernel of size (4,4) and a default stride of size (1,1).
                ##  Keeping in the input image to the convo layer is of size 13x13 and applying 
                ##  the "N-W+1" formula to this image with N=13 and W=4, the output of
                ##  self.conv2() will be an image of size 10x10.  Since out_channels for 
                ##  self.conv2() is 16, the shape of the tensor at the output of self.conv2()
                ##  will be (4,16,10,10).  
                ##
                ##  This (4,16,10,10) is subject to the maxpooling operation with a patch
                ##  size of (2,2) and a stride of (2,2).  Since maxpooling is applied to each
                ##  channel separately, the output of maxpooling will be of shape (4,16,5,5).
                x = self.pool(self.relu(self.conv2(x)))   

                ##  That bring us to the first fully-connected layer.  We must reshape our
                ##  the (4,16,5,5) tensor so that FOR IMAGE IN THE BATCH it looks like a
                ##  1-D vector with its number of elements equal to the total number of 
                ##  elements in the output of the previous maxpooling operation (for each
                ##  image in the batch) --- which 16*5*5 = 400.  This can be done with:
                x = x.view(-1, 16 * 5 * 5)
                ##  The shape of x now is (4,400) 

                ##  Since the fc layer self.fc1() has its input of size 400 and the output
                ##  of size 150:
                x = self.relu(self.fc1( x ))
                ##  the shape of x is now (4, 150)
               
                ##  And since the fc layer self.fc2() has its input of size 150 and the output
                ##  of size 100
                x = self.relu(self.fc2( x ))
                ##  the shape of x is now (4, 100)

                ##  Since the fc layer self.fc3() has its input of size 100 and the output 
                ##  of size 10, 
                x = self.fc3(x)
                ##  the shape of x is now (4,10)
                return x

        def run_code_for_training(self, net):        
            self.dl_studio.run_code_for_training(net)
            
        def save_model(self, model):
            '''
            Save the trained model to a disk file
            '''
            torch.save(model.state_dict(), self.dl_studio.path_saved_model)

        def run_code_for_testing(self, model):
            self.dl_studio.run_code_for_testing(model)


    def plot_loss(self):
        plt.figure()
        plt.plot(self.LOSS)
        plt.show()

#_________________________  End of DLStudio Class Definition ___________________________

#______________________________    Test code follows    _________________________________

if __name__ == '__main__': 
    pass
