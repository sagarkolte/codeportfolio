# -*- coding: utf-8 -*-
"""industrialProblem.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11h_G9f90WNgAL0CYdCKHRsXEo5DBFup6

# Importing kaggle.json
"""

from google.colab import files
files.upload()

!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/

!pip install kaggle

!chmod 600 /root/.kaggle/kaggle.json
!kaggle datasets list

!kaggle competitions download -c competitive-data-science-predict-future-sales

!pip install -q keras
import keras

import os
print(os.getcwd())

"""# Model session starts from here"""

from google.colab import drive
drive.mount('/content/drive')

!pip install --upgrade azureml-sdk[notebooks,automl]

"""#Import required packages """

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import read_csv
import math
import tensorflow as tf
import tensorflow.keras
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import os
import pickle
import distutils
if distutils.version.LooseVersion(tf.__version__) < '2.0':
    raise Exception('This notebook is compatible with TensorFlow 2.0 or higher.')

"""#Path to files"""

"""
Change path here so that we both don't need to change lot of lines while running the code
"""
PATH_TO_PREPARED_DATA = '/content/drive/MyDrive/IndustrialProblems/prepared_data-20210120.csv'
PATH_TO_PICKEL_FILE = '/content/drive/MyDrive/IndustrialProblems/AzureModel/model.pkl'
PATH_TO_TEST_FILE = '/content/drive/MyDrive/IndustrialProblems/KaggleDatasets/test.csv'
PATH_TO_ITEMS_FILE = '/content/drive/MyDrive/IndustrialProblems/KaggleDatasets/items.csv'
PATH_TO_ITEM_CATEGORY = '/content/drive/MyDrive/IndustrialProblems/KaggleDatasets/item_categories.csv'
PATH_TO_SALES_TRAIN = '/content/drive/MyDrive/IndustrialProblems/KaggleDatasets/sales_train.csv'
PATH_TO_SHOP = '/content/drive/MyDrive/IndustrialProblems/KaggleDatasets/shops.csv'

"""#Data Preprocessing"""

# import test and items dataset
test = pd.read_csv(PATH_TO_TEST_FILE)

def load_preparedData(location = PATH_TO_PREPARED_DATA):
  data = pd.read_csv(location)
  data = data.drop(columns=['Unnamed: 0',
                            'Unnamed: 0.1',
                            'Unnamed: 0.1.1',
                            'Unnamed: 0.1.1.1',
                            'date_block_num',
                            'item_price',
                            'item_category_id',
                            'shop_id',
                            'avg_monthly_sales',
                            'month-4',
                            'month-5',
                            'avg_monthly_sales_item_cat',
                            'item_category_id_unique_count',
                            'First',
                            'category_type_name_Accessories',
                            'category_type_name_Cinema',
                            'category_type_name_Game consoles',
                            'category_type_name_Games',
                            'category_type_name_Gifts',
                            'category_type_name_Music',
                            'category_type_name_PC Games',
                            'category_type_name_Payment cards',
                            'category_type_name_Programs',
                            'category_type_name_Books'
                            ])
  data = data.fillna(0)
  dataset = data.values
  dataset = dataset.astype('float32')
  #datasetX, datasetY = dataset[:,[1,2,3,4,5]],dataset[:,0]
  datasetX, datasetY = dataset[:,[1,2,3,]],dataset[:,0]
  # normalize the dataset
  x_scaler = MinMaxScaler()
  y_scaler = MinMaxScaler()
  datasetX = x_scaler.fit_transform(datasetX)
  datasetY = y_scaler.fit_transform(datasetY.reshape(-1, 1))
  # split into train and test sets
  train_size = int(len(dataset) * 0.99)
  test_size = len(dataset) - train_size
  trainX, testX = datasetX[0:train_size,:], datasetX[train_size:len(datasetX),:]
  trainY, testY = datasetY[0:train_size,:], datasetY[train_size:len(datasetY),:]
  # reshape input to be [samples, time steps, features]
  trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
  testX = np.reshape(testX, (testX.shape[0], 1, testX.shape[1]))
  return trainX, trainY,testX,testY,y_scaler,x_scaler

def lstm_model():
  # create and fit the LSTM network
  model = tf.keras.models.Sequential()
  #model.add(tf.keras.layers.LSTM(4, input_shape=(1, 5)))
  model.add(tf.keras.layers.LSTM(4, input_shape=(1, 3)))
  model.add(tf.keras.layers.Dense(3))
  model.add(tf.keras.layers.Dense(3))
  model.add(tf.keras.layers.Dense(1))
  return model

def enable_tpu():
  tf.keras.backend.clear_session()
  resolver = tf.distribute.cluster_resolver.TPUClusterResolver(tpu='grpc://' + os.environ['COLAB_TPU_ADDR'])
  tf.config.experimental_connect_to_cluster(resolver)
  # This is the TPU initialization code that has to be at the beginning.
  tf.tpu.experimental.initialize_tpu_system(resolver)
  print("All devices: ", tf.config.list_logical_devices('TPU'))
  strategy = tf.distribute.experimental.TPUStrategy(resolver)
  return strategy

def compile_fit(strategy,trainX,trainY,steps,n_epochs):
  with strategy.scope():
    training_model = lstm_model()
    training_model.compile(loss='mean_squared_error', optimizer='adam')
  training_model.fit(x=trainX, y=trainY,steps_per_epoch=steps,epochs=n_epochs)
  return training_model

def predict_evaluate(training_model,trainY,testY,trainX,testX,y_scaler,x_scaler):
  trainPredict = training_model.predict(trainX)
  testPredict = training_model.predict(testX)
  trainPredict = y_scaler.inverse_transform(trainPredict)
  trainY = y_scaler.inverse_transform(trainY)
  testPredict = y_scaler.inverse_transform(testPredict)
  testY = y_scaler.inverse_transform(testY)
  error_train = np.sqrt(((trainPredict-trainY)**2).sum())
  error_test = np.sqrt(((testPredict-testY)**2).sum())
  dfff = pd.DataFrame(testPredict)
  dfff['testY'] = testY
  dfff.columns = ['predicted','testY']
  sns.scatterplot(data=dfff,x='testY',y='predicted')
  total_predict = np.concatenate([trainPredict,testPredict])

  return total_predict,{"train_error":error_train,"test_error":error_test}

def prepare_sec_model_data(total_predict,location = PATH_TO_PREPARED_DATA):
  data = pd.read_csv(location)
  data['initialPredict'] = total_predict
  data = data.drop(columns = ['Unnamed: 0',
                              'Unnamed: 0.1',
                              'Unnamed: 0.1.1',
                              'Unnamed: 0.1.1.1',
                              'month-1',
                              'month-2',
                              'month-3',
                              'month-4',
                              'month-5',
                              'shop_id',
                              'First',
                              'item_category_id'])
  
  return data

def lstm_run(steps,n_epochs):
  trainX,trainY,testX,testY,y_scaler,x_scaler = load_preparedData(location = PATH_TO_PREPARED_DATA)
  strategy = enable_tpu()
  training_model = compile_fit(strategy,trainX,trainY,steps,n_epochs)
  total_predict,_ = predict_evaluate(training_model,trainY,testY,trainX,testX,y_scaler,x_scaler)
  data = prepare_sec_model_data(total_predict=total_predict)
  data.to_csv('/content/drive/MyDrive/IndustrialProblems/AzureModel/secondary_model_input.csv',header=True,index=False)
  return data,training_model,y_scaler,x_scaler

def azure_run(data):
  import azureml

  rmse_init = np.sqrt((data['item_cnt_day']-data['initialPredict'])**2).sum()/len(data)
  filename = PATH_TO_PICKEL_FILE
  azure_model = pickle.load(open(filename, 'rb'))

  input_sample = pd.DataFrame({"date_block_num": data['date_block_num'], 
                               "item_price": data['item_price'], 
                               "avg_monthly_sales": data['avg_monthly_sales'], 
                               "avg_monthly_sales_item_cat": data['avg_monthly_sales_item_cat'], 
                               "item_category_id_unique_count": data['item_category_id_unique_count'], 
                               "category_type_name_Accessories": data["category_type_name_Accessories"], 
                               "category_type_name_Books": data["category_type_name_Books"], 
                               "category_type_name_Cinema": data["category_type_name_Cinema"], 
                               "category_type_name_Game consoles": data["category_type_name_Game consoles"], 
                               "category_type_name_Games": data["category_type_name_Games"], 
                               "category_type_name_Gifts": data["category_type_name_Gifts"], 
                               "category_type_name_Music": data["category_type_name_Music"], 
                               "category_type_name_PC Games": data["category_type_name_PC Games"], 
                               "category_type_name_Payment cards": data["category_type_name_Payment cards"], 
                               "category_type_name_Programs": data["category_type_name_Programs"], 
                               "initialPredict": data["initialPredict"]})
  output_sample = np.array(data['item_cnt_day'])
  result = azure_model.predict(input_sample)
  print("initial_rmse",rmse_init,"rmse:",np.sqrt((result-output_sample)**2).sum()/len(data))
  data['azure_result'] = result
  orig_data = pd.read_csv(PATH_TO_PREPARED_DATA)
  data['shop_id'] = orig_data['shop_id']
  data['item_category_id'] = orig_data['item_category_id']
  data.to_csv('/content/drive/MyDrive/IndustrialProblems/AzureModel/final_train_output.csv')
  return data

def train_run(steps,n_epochs):
  data,lstm_model,y_scaler,x_scaler = lstm_run(steps,n_epochs)
  data = azure_run(data)
  return data,lstm_model,y_scaler,x_scaler

def predict_final(date_block_num,lstm_model,x_scaler,y_scaler):
  orig_data = pd.read_csv(PATH_TO_PREPARED_DATA)
  data = orig_data[orig_data['date_block_num']==date_block_num-1]
  data = data.drop(columns=['Unnamed: 0',
                            'Unnamed: 0.1',
                            'Unnamed: 0.1.1',
                            'Unnamed: 0.1.1.1',
                            'date_block_num',
                            'item_price',
                            'item_category_id',
                            'shop_id',
                            'avg_monthly_sales',
                            'month-3',
                            'month-4',
                            'month-5',
                            'avg_monthly_sales_item_cat',
                            'item_category_id_unique_count',
                            'First',
                            'category_type_name_Accessories',
                            'category_type_name_Cinema',
                            'category_type_name_Game consoles',
                            'category_type_name_Games',
                            'category_type_name_Gifts',
                            'category_type_name_Music',
                            'category_type_name_PC Games',
                            'category_type_name_Payment cards',
                            'category_type_name_Programs',
                            'category_type_name_Books'
                            ])
  print(data.head())
  data = data.fillna(0)
  print(1)
  dataset = data.values
  print(2)
  dataset = dataset.astype('float32')
  print(3)
  dataset = x_scaler.fit_transform(dataset)
  print(4)
  dataset = np.reshape(dataset, (dataset.shape[0], 1, dataset.shape[1]))
  predict = lstm_model.predict(dataset)
  predict = y_scaler.inverse_transform(predict)
  print(5)
  orig_data = orig_data[orig_data['date_block_num']==date_block_num-1]
  print(6)
  orig_data['initialPredict']=predict
  orig_data = orig_data.drop(columns = ['Unnamed: 0',
                                        'Unnamed: 0.1',
                                        'Unnamed: 0.1.1',
                                        'Unnamed: 0.1.1.1',
                                        'month-1',
                                        'month-2',
                                        'month-3',
                                        'month-4',
                                        'month-5',
                                        'shop_id',
                                        'item_category_id',
                                        'First'])
  filename = PATH_TO_PICKEL_FILE
  azure_model = pickle.load(open(filename, 'rb'))
  input_sample = pd.DataFrame({"date_block_num": orig_data['date_block_num'], 
                               "item_price": orig_data['item_price'], 
                               "avg_monthly_sales": orig_data['avg_monthly_sales'], 
                               "avg_monthly_sales_item_cat": orig_data['avg_monthly_sales_item_cat'], 
                               "item_category_id_unique_count": orig_data['item_category_id_unique_count'], 
                               "category_type_name_Accessories": orig_data["category_type_name_Accessories"], 
                               "category_type_name_Books": orig_data["category_type_name_Books"], 
                               "category_type_name_Cinema": orig_data["category_type_name_Cinema"], 
                               "category_type_name_Game consoles": orig_data["category_type_name_Game consoles"], 
                               "category_type_name_Games": orig_data["category_type_name_Games"], 
                               "category_type_name_Gifts": orig_data["category_type_name_Gifts"], 
                               "category_type_name_Music": orig_data["category_type_name_Music"], 
                               "category_type_name_PC Games": orig_data["category_type_name_PC Games"], 
                               "category_type_name_Payment cards": orig_data["category_type_name_Payment cards"], 
                               "category_type_name_Programs": orig_data["category_type_name_Programs"], 
                               "initialPredict": orig_data["initialPredict"]})
  result = azure_model.predict(input_sample)
  orig_data['azure_result'] = result
  orig_data_2 = pd.read_csv(PATH_TO_PREPARED_DATA)
  orig_data_2 = orig_data_2[orig_data_2['date_block_num']==date_block_num-1]
  orig_data['shop_id'] = orig_data_2['shop_id']
  orig_data['item_category_id'] = orig_data_2['item_category_id']
  orig_data = orig_data.drop(columns=['date_block_num',
                                      'item_price',
                                      'item_cnt_day',
                                      'initialPredict',
                                      'item_category_id_unique_count',
                                      'category_type_name_Accessories',
                                      'category_type_name_Cinema',
                                      'category_type_name_Game consoles',
                                      'category_type_name_Games',
                                      'category_type_name_Gifts',
                                      'category_type_name_Music',
                                      'category_type_name_PC Games',
                                      'category_type_name_Payment cards',
                                      'category_type_name_Programs'
                                      ])
  return orig_data

def main_run(steps,n_epochs):
  data,lstm_model,y_scaler,x_scaler = train_run(steps,n_epochs)
  data = predict_final(34,lstm_model,x_scaler,y_scaler)
  test_data = pd.read_csv(PATH_TO_TEST_FILE)
  item_cat = pd.read_csv(PATH_TO_ITEMS_FILE)
  item_cat = item_cat.drop(columns=['item_name'])
  test_data = pd.merge(test_data,item_cat,how='left',on='item_id')
  submission = pd.merge(test_data,data, how = 'left' , on=['shop_id','item_category_id'])
  submission = submission.drop(columns=['item_category_id'])
  submission['azure_result'] = submission['azure_result'].clip(lower = 0,upper=20)
  submission.fillna(0,inplace=True)
  submission.azure_result = submission.azure_result.astype(int)
  final_submission = submission[['ID','azure_result']]
  final_submission.columns = ['ID','item_cnt_month']
  final_submission.to_csv('my_submission.csv',index=False, header=True)
  return final_submission

"""Read test and items dataset """

main_run(10,200)

"""# Submission to Kaggle"""

#submit the file to kaggle
!kaggle competitions submit competitive-data-science-predict-future-sales -f my_submission.csv -m "Yeah! I submit my file through the Google Colab!"

"""Code for avg_monthly_sales per Item Category 

"""

# prepared_data = pd.read_csv(PATH_TO_PREPARED_DATA)
# avg_monthly_sales_item_category = prepared_data.groupby(by=['item_category_id','date_block_num']).mean().reset_index()
# avg_monthly_sales_item_category.rename(columns = {'item_price':'avg_monthly_sales_item_cat'}, inplace = True) 
# prepared_data = pd.merge(prepared_data,avg_monthly_sales_item_category[['item_category_id','date_block_num','avg_monthly_sales_item_cat']],on=['item_category_id','date_block_num'],how='left')
# prepared_data.to_csv(PATH_TO_PREPARED_DATA)



"""Item_category_count shop_wise"""

# !pip install google_trans_new
# from google_trans_new import google_translator

# prepared_data = pd.read_csv(PATH_TO_PREPARED_DATA)
# item_category_count_shop_wise = prepared_data.groupby('shop_id')['item_category_id'].transform('nunique').reset_index()
# item_category_count_shop_wise.columns = ['shop_id','item_category_id_unique_count']
# prepared_data = pd.merge(prepared_data,item_category_count_shop_wise, on='shop_id', how= 'left')


# df = pd.read_csv('/content/drive/MyDrive/IndustrialProblems/AzureModel/final_train_output.csv')
# df['error'] = df['azure_result'] - df['item_cnt_day']
# item_cate_error = df.groupby('item_category_id')['error'].mean().reset_index()
# item_category = pd.read_csv(PATH_TO_ITEM_CATEGORY)

# translator = google_translator()
# translations = {}

# unique_elements = item_category['item_category_name'].unique()
# for element in unique_elements:
#     # add translation to the dictionary
#     translations[element] = translator.translate(element,lang_src='ru',lang_tgt='en')
    
# item_category['item_category_name'].replace(translations, inplace = True)
# item_cate_error = pd.merge(item_cate_error,item_category,on='item_category_id',how='left')
# item_cate_error[['First','Last']] = item_cate_error.item_category_name.str.split(' - ',expand=True)
# list_of_first = ['Books','Gifts','Games','Accessories','Game consoles','Music','Programs','PC Games','Cinema','Payment cards']
# item_cate_error['First'] = item_cate_error['First'].apply(lambda x: x if x in list_of_first else 'Others')

# prepared_data = pd.merge(prepared_data,item_cate_error[['First','item_category_id']],on='item_category_id',how='left')
# y = pd.get_dummies(prepared_data.First, prefix='category_type_name')
# y.drop(columns='category_type_name_Others',inplace=True)
# prepared_data = prepared_data.join(y)

# # save prepared data

# prepared_data.to_csv(PATH_TO_PREPARED_DATA)