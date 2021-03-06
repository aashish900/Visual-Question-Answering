# -*- coding: utf-8 -*-
"""Finalof NNFL_Scratch.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1d_C6IY6l4gSO-WQZWSgpoc70ZljvODAI
"""

from google.colab import drive
drive.mount('/content/gdrive')

"""### **Check GPU and RAM availability**"""

# memory footprint support libraries/code
!ln -sf /opt/bin/nvidia-smi /usr/bin/nvidia-smi
!pip install gputil
!pip install psutil

!pip install humanize
import psutil
import humanize
import os
import GPUtil as GPU
GPUs = GPU.getGPUs()
# XXX: only one GPU on Colab and isn’t guaranteed
gpu = GPUs[0]
def printm():
  process = psutil.Process(os.getpid())
  print("Gen RAM Free: " + humanize.naturalsize( psutil.virtual_memory().available ), " | Proc size: " + humanize.naturalsize( process.memory_info().rss))
  print("GPU RAM Free: {0:.0f}MB | Used: {1:.0f}MB | Util {2:3.0f}% | Total {3:.0f}MB".format(gpu.memoryFree, gpu.memoryUsed, gpu.memoryUtil*100, gpu.memoryTotal))
printm()

"""### **Download Data**"""

'''
Link to file in google drive
'''

# https://drive.google.com/open?id=19l8nja9Sr7iGs4H3rpKpwCarLXH8h3mM

'''
File ID = 19l8nja9Sr7iGs4H3rpKpwCarLXH8h3mM
'''
# Download data from drive
!wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=19l8nja9Sr7iGs4H3rpKpwCarLXH8h3mM' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=19l8nja9Sr7iGs4H3rpKpwCarLXH8h3mM" -O NNFL && rm -rf /tmp/cookies.txt

!ls

!mv NNFL NNFL.zip

!ls

"""### **Unzip the Data**"""

!unzip NNFL.zip

"""##Keras code"""

from __future__ import print_function
import json
import os.path
#import random as ra
import random
#import tensorflow as tf
from keras.backend import tf
import numpy as np
import keras
from keras.optimizers import Adam
from keras import backend as K
from keras.layers import Input, Dense, Dropout, BatchNormalization, Reshape, Lambda, Embedding, LSTM, Conv2D, Activation
from keras.layers import MaxPooling2D, TimeDistributed, RepeatVector, Concatenate, Bidirectional, Conv1D, MaxPooling1D
from keras.models import Model
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence
from keras.models import Sequential, Model
from keras.callbacks import ModelCheckpoint, TensorBoard
from scipy import ndimage, misc
import pickle

#with open("Quest_Answers.json") as f:
#    data= json.load(f);
  
#data= data["quest_answers"]
#data

ls

def load_data(split, n, vocab_size, sequence_length, tokenizer=None):
  # Dataset paths
  #path = '../../Datasets/CLEVR_v1.0'
  #questions_path = path + '/questions/CLEVR_' + split + '_questions.json'
  #subset_questions_path = path + '/questions/CLEVR_' + split + '_questions_' + str(n) + '.json'
  #images_path = path + '/images/' + split + '/'

  x_text = []     # List of questions
  x_image = []    # List of images
  y = []          # List of answers
  num_labels = 0  # Current number of labels, used to create index mapping
  labels = {}     # Dictionary mapping of ints to labels
  images = {}     # Dictionary of images, to minimize number of imread ops
  #x_index = []

  # Attempt to load saved JSON subset of the questions
  print('Loading data...')

  """fos.path.exists(subset_questions_path):
    with open(subset_questions_path) as f:
      data = json.load(f)
  else:
    with open(questions_path) as f:
      data = json.load(f)

    data = data['questions'][0:n]

    with open(subset_questions_path, 'w') as outfile:
      json.dump(data, outfile)

    print('JSON subset saved to file...')"""
  
  with open("Quest_Answers.json") as f:
    data= json.load(f);
  
  data= data["quest_answers"][0:n]
  for i in data:
    i["Answer"] = str(i["Answer"])
  
  # Store image data and labels in dictionaries
  print('Storing image data...')

  for q in data[0:n]:
    # Create an index for each answer
    if not q["Answer"] in labels:
      labels[q['Answer']] = num_labels
      num_labels += 1

    # Create an index for each image
    if not q['Image'] in images:
      images[q['Image']] = misc.imread('images/' + q['Image'] + '.png', mode='RGB')

    x_text.append(q['Question'])
    x_image.append(images[q['Image']])
    #x_index.append((q['Index']))
    y.append(labels[q['Answer']])

  # Convert question corpus into sequential encoding for LSTM
  print('Processing text data...')

  if not tokenizer:
    tokenizer = Tokenizer(num_words=vocab_size)

  tokenizer.fit_on_texts(x_text)
  sequences = tokenizer.texts_to_sequences(x_text)
  x_text = sequence.pad_sequences(sequences, maxlen=sequence_length)

  # Convert x_image to np array
  x_image = np.array(x_image)

  # Convert labels to categorical labels
  y = keras.utils.to_categorical(y, num_labels)

  print('Text: ', x_text.shape)
  print('Image: ', x_image.shape)
  print('Labels: ', y.shape)

  return ([x_text, x_image], y), num_labels, tokenizer

#
# Environment Parameters
#
samples = 135000
epochs = 5
batch_size = 64
learning_rate = .00025
vocab_size = 1024
sequence_length = 48
img_rows, img_cols = 120, 160
image_input_shape = (img_rows, img_cols, 3)

#
# Load & Preprocess CLEVR
#
(x_train, y_train), num_labels, tokenizer = load_data('train', samples, vocab_size, sequence_length)

# saving
with open('tokenizer.pickle', 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

# loading
with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

cp gdrive/My\ Drive/tokenizer.pickle tokenizer.pickle

with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

ls

print("x_train[0].shape = Text: {}".format(x_train[0].shape))
print("x_train[1].shape = Image: {}".format(x_train[1].shape))

"""## **New Start**"""

from keras.applications.vgg16 import VGG16
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.applications.vgg16 import preprocess_input
from keras.layers import Input

def vgg(shape):
  image_in = Input(shape = shape) 
  model = VGG16(include_top = False, weights = 'imagenet')#, input_tensor = image_in)
  #print(model.summary())
  return model

def lstm(sequence_length, text_in):
  #text_in = Input(shape = (sequence_length,), name = 'text_in')
  text_in = text_in
  emb = Embedding(output_dim=256, input_dim=vocab_size, input_length=64)(text_in)
  emb = LSTM(256)(emb)
  emb = Dropout(0.5)(emb)
  return emb

# Load model

def conv(shape, image_in):
  #image_in = Input(shape = shape, name = 'image_in')
  image_in = image_in
  image_x = Conv2D(24, kernel_size=(3, 3), strides=2, activation='relu')(image_in)
  image_x = BatchNormalization()(image_x)
  image_x = Conv2D(48, kernel_size=(3, 3), strides=2, activation='relu')(image_x)
  image_x = BatchNormalization()(image_x)
  image_x = Conv2D(48, kernel_size=(3, 3), strides=2, activation='relu')(image_x)
  image_x = BatchNormalization()(image_x)
  image_x = Conv2D(64, kernel_size=(3, 3), strides=2, activation='relu')(image_x)
  image_x = BatchNormalization()(image_x)
  image_x = Conv2D(64, kernel_size=(3, 3), strides=2, activation='relu')(image_x)
  image_x = BatchNormalization()(image_x)
  image_x = keras.layers.Flatten()(image_x)
  #image_x = Conv2D(24, kernel_size=(3, 3), strides=2, activation='relu')(image_x)
  #image_x = BatchNormalization()(image_x)
  return image_x

def conv1D(sequence_length, text_in):
  text_in = text_in
  emb = Embedding(output_dim=256, input_dim=vocab_size, input_length=sequence_length)(text_in)
  emb = Conv1D(128, kernel_size = 3, strides = 2, activation = 'relu')(emb)
  emb = BatchNormalization()(emb)
  emb = keras.layers.Flatten()(emb)
  return emb

shape = (120, 160, 3)
text_in = Input(shape = (sequence_length,), name = 'text_in')
image_in = Input(shape = shape, name = 'image_in')

conv = conv(shape, image_in)

#vgg = vgg(shape)

lstm = conv1D(sequence_length, text_in)

x = keras.layers.concatenate([lstm, conv], axis=-1)

x = Dropout(0.5)(x)

x = Dense(256, activation = 'relu')(x)

x = Dropout(0.5)(x)

outputs = Dense(26, activation = 'softmax')(x)

model = Model(inputs = [text_in, image_in], outputs = outputs)

model.compile(optimizer=Adam(lr=learning_rate), loss='categorical_crossentropy', metrics=['accuracy'])

cp gdrive/My\ Drive/NNFL_Project_NEW_CNN.h5 NNFL_Project_NEW_CNN.h5

model2 = keras.models.load_model('NNFL_Project_NEW_CNN.h5')

ls

from keras.callbacks import ModelCheckpoint, EarlyStopping, LearningRateScheduler
checkpoint = ModelCheckpoint('NNFL_checkpoint_model_CNN.h5', monitor = 'val_loss', verbose = 1, save_best_only = True, save_weights_only = False, mode = 'auto', period = 1)

history = model2.fit(x_train, y_train, batch_size=32, epochs=10, validation_split= 0.1, shuffle=True, verbose=1, callbacks = [checkpoint])

model.save('NNFL_Project_NEW_CNN_1.h5')

ls

model2 = keras.models.load_model('NNFL_Project_NEW_CNN_1.h5')

model3 = keras.models.load_model('NNFL_checkpoint_model_CNN.h5')

cp NNFL_Project_NEW_CNN_1.h5 gdrive/My\ Drive/NNFL_Project_NEW_CNN_1.h5

cp NNFL_checkpoint_model_CNN.h5 gdrive/My\ Drive/NNFL_checkpoint_model_CNN.h5

#cp tokenizer.pickle gdrive/My\ Drive/tokenizer.pickle

print(history.history.keys())

import matplotlib.pyplot as plt
#  "Accuracy"
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'validation'], loc='upper left')
plt.show()

# "Loss"
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'validation'], loc='upper left')
plt.show()

model.summary()

from keras.utils import plot_model
plot_model(model, to_file='model.png')

cp model.png gdrive/My\ Drive/model.png

!pip install pydot

# https://pypi.python.org/pypi/pydot
!apt-get -qq install -y graphviz && pip install -q pydot
import pydot

!pip install -q pydot

