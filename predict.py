# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 23:51:58 2016

@author: wsf
"""


import sys
sys.path.append('/home/wsf/xgboost/python-package')
import xgboost as xgb
import pandas as pd
from sklearn import cross_validation
import numpy as np
import feature_transformation
import function as f

train_file="/home/wsf/data/cityData/new_data/season_2/train.csv"
test_file="/home/wsf/data/cityData/new_data/season_2/test.csv"

train_df=pd.read_csv(train_file)
test_df=pd.read_csv(test_file)

init_test_df=test_df.copy(deep=True)
init_train_df=train_df.copy(deep=True)


#msk = np.random.rand(len(train_df)) < 0.8
#np.save("msk",msk)
msk=np.load("msk.npy")
train_df = init_train_df[msk]
val_df = init_train_df[~msk]

init_val_df=val_df.copy(deep=True)




train_df.date = train_df.weekofday
train_labels = train_df.gap.as_matrix()
train_df.drop('weekofday',axis = 1,inplace = True)
train_df.drop('gap',axis = 1,inplace = True)
train_df.rename(columns = {'date':'weekofday'}, inplace=True)

val_df.date = val_df.weekofday
val_labels = val_df.gap.as_matrix()
val_df.drop('weekofday',axis = 1,inplace = True)
val_df.drop('gap',axis = 1,inplace = True)
val_df.rename(columns = {'date':'weekofday'}, inplace=True)


test_df.date=test_df.weekofday
test_df.drop('weekofday',axis=1,inplace=True)
test_df.rename(columns = {'date':'weekofday'}, inplace=True)


train_df=feature_transformation.transform_feature(train_df)
test_df=feature_transformation.transform_feature(test_df)
val_df=feature_transformation.transform_feature(val_df)




cols_train=list(train_df.columns.values)
cols_test=list(test_df.columns.values)

trainDMatrix=xgb.DMatrix(train_df.as_matrix(),label=train_labels,feature_names=cols_train,missing=np.nan)
valDMatrix=xgb.DMatrix(val_df.as_matrix(),label=val_labels,feature_names=cols_train,missing=np.nan)
testDMatrix=xgb.DMatrix(test_df.as_matrix(),feature_names=cols_test,missing=np.nan)

watchlist=[(valDMatrix,'eval'),(trainDMatrix,'train')]




########是否设置base line
mean_train=f.get_simple_guess_from_df(train_df)
mean_val=f.get_simple_guess_from_df(val_df)
mean_test=f.get_simple_guess_from_df(test_df)

trainDMatrix.set_base_margin(mean_train)
valDMatrix.set_base_margin(mean_val)
testDMatrix.set_base_margin(mean_test)

param={'booster':'gbtree','lambda':1,
              'subsample':0.7,
              'colsample_bytree':0.6,
              'max_depth':4,
              'eta':0.025}
              

              

model = xgb.train(param, trainDMatrix, 3500, watchlist, obj=f.mapeLoss1, feval=f.mymapeval, early_stopping_rounds=100)
ret=model.predict(testDMatrix)


##是否进行进行dummy coding，与normalize
#transformed_train_df=feature_transformation.transform_feature(train_df)
#transformed_test_df=feature_transformation.transform_feature(test_df)
#transformed_val_df=feature_transformation.transform_feature(val_df)
#
#transformed_cols_train=list(transformed_train_df.columns.values)
#transformed_cols_test=list(test_df.columns.values)
#
#transformed_trainDMatrix=xgb.DMatrix(transformed_train_df.as_matrix(),label=train_labels,feature_names=transformed_cols_train,missing=np.nan)
#transformed_valDMatrix=xgb.DMatrix(transformed_val_df.as_matrix(),label=val_labels,feature_names=transformed_cols_train,missing=np.nan)
#transformed_testDMatrix=xgb.DMatrix(transformed_test_df.as_matrix(),feature_names=transformed_cols_test,missing=np.nan)
#
#transformed_watchlist=[(transformed_valDMatrix,'eval'),(transformed_trainDMatrix,'train')]
#
#
#
#
#########是否设置base line
#transformed_mean_train=f.get_simple_guess_from_df(transformed_train_df)
#transformed_mean_val=f.get_simple_guess_from_df(transformed_val_df)
#transformed_mean_test=f.get_simple_guess_from_df(transformed_test_df)
#
#transformed_trainDMatrix.set_base_margin(transformed_mean_train)
#transformed_valDMatrix.set_base_margin(transformed_mean_val)
#transformed_testDMatrix.set_base_margin(transformed_mean_test)
#
#transformed_param={'booster':'gbtree','lambda':1,
#              'subsample':0.7,
#              'colsample_bytree':0.6,
#              'max_depth':4,
#              'eta':0.025}
#
#transformed_model = xgb.train(transformed_param, transformed_trainDMatrix, 25000, transformed_watchlist, obj=f.mapeLoss1, feval=f.mymapeval, early_stopping_rounds=100)
#transformed_ret=model.predict(testDMatrix)

#predicts_val=lau_data.gap.as_matrix()*1.03
#merged1=f.merger_big_small(predicts_val,mean_from_df1)
#merged2=f.merger_big_small(predicts_val,mean_from_df2)
#lau_data.gap=pd.Series(data=merged1,index=lau_data.index)
#lau_data.to_csv('lau_merge_mean1.csv',index=False,header=False)
#lau_data.gap=pd.Series(data=merged2,index=lau_data.index)
#lau_data.to_csv('lau_merge_mean2.csv',index=False,header=False)
#final=f.generate_sub(init_test_df,mean_test,savePath='/home/wsf/data/cityData/mean_test.csv')
#final=f.generate_sub(init_test_df,mean_test_2,savePath='/home/wsf/data/cityData/mean_test_直接求均值.csv')
print "done!"





