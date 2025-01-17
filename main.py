import pandas as pd
import numpy as np
from preprocessing.preprocessing import cleandata
from preprocessing.vectorization import counter, delete, get_vocab_size, encode
from preprocessing.ReviewDataset import ReviewsDataset
from model.MultiInputModel import MultiInputModel
from sklearn.metrics import mean_squared_error
import torch
import torch.nn as nn 
import torch.nn.functional as F 
import torch.optim as optim
from torch.autograd import Variable
from torch.utils.data import Dataset, DataLoader, TensorDataset
from sklearn.model_selection import train_test_split

print("Reading data....")
df = pd.read_json('data/Digital_Music_5.json', lines = True)

print("Cleaning data....")
df1 = cleandata(df)

print("Vectorizing data....")
item_counts = counter(df1, 'reviewText_item')
user_counts = counter(df1, 'reviewText_user')

item_counts = delete(item_counts)
user_counts = delete(user_counts)

item_words = get_vocab_size(item_counts)
user_words = get_vocab_size(user_counts)

df1['encoded_item'] = df1['reviewText_item'].apply(lambda x: np.array(encode(x, item_words[1])))
df1['encoded_user']=df1['reviewText_user'].apply(lambda x: np.array(encode(x, user_words[1])))

print("Creating training and validation datasets....")
X=list(df1['encoded_item'])
X2=list(df1['encoded_user'])
y = list(df1['overall_avg'])
y1=list(df1['overall_item'])
y2=list(df1['overall_user'])

X_item_train, X_item_valid, y_item_train, y_item_valid = train_test_split(X, y1, test_size=0.2)
X_user_train, X_user_valid, y_user_train, y_user_valid = train_test_split(X2, y2, test_size=0.2)

train_item_ds = ReviewsDataset(X_item_train, y_item_train)
valid_item_ds = ReviewsDataset(X_item_valid, y_item_valid)

train_user_ds = ReviewsDataset(X_user_train, y_user_train)
valid_user_ds = ReviewsDataset(X_user_valid, y_user_valid)

batch_size = 5000
item_vocab = len(item_words[0])
user_vocab = len(user_words[0])
item_train_dl = DataLoader(train_item_ds, batch_size=batch_size)
item_valid_dl = DataLoader(valid_item_ds, batch_size=batch_size)

user_train_dl = DataLoader(train_user_ds, batch_size=batch_size)
user_valid_dl = DataLoader(valid_user_ds, batch_size=batch_size)

print("Running MultiInputModel....")
MultiInputModel(item_train_dl,item_valid_dl,item_vocab,user_train_dl,user_valid_dl,user_vocab,100,70,y)
