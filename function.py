# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 14:07:28 2016

@author: wsf
"""
import numpy as np
import pandas as pd
#function for loss

def generate_submission(init_df,pres,savePath=None):
    '''
    输入：原始格式的df（包含日期、time slice和district id等属性）与预测值
    输入：根据预测值生成符合要求的提交格式
    '''
    dis_id_s=init_df.district_id
    date_s=init_df.date
    time_slice_s=init_df.time_slice
    time_s=date_s.astype(str)+'-'+time_slice_s.astype(str)
    pres_s=pd.Series(data=pres,name='gap')
    ret_df=pd.concat([dis_id_s,time_s,pres_s],axis=1)
    if savePath is not None:
        ret_df.to_csv(savePath,index=False,header=False)
    else:
        ret_df.to_csv('ret.csv',index=False,header=False)
        
def merger_big_small(small,big,threshold=40):
    bools=big>threshold
    big[~bools]=0
    small[bools]=0
    return big+small
    
def mapeLoss1(pres,dtrain):#损失函数1
    pres=pres.astype(float)
    gap=dtrain.get_label().astype(float)
    grad=np.divide(np.sign(pres-gap),gap)
    hess=1/(gap)
    grad[np.isinf(grad)]=0#如果gap是0的话，一阶和二阶导数都是0，也就是不需要调整，这样真的好么？
    hess[np.isinf(hess)]=0#
    return grad,hess

def mapeLoss2(pres,dtrain):#损失函数2
    pres=pres.astype(float)
    gap=dtrain.get_label().astype(float)
    inter=np.sign(pres-gap)
    grad=np.divide(inter,gap)
    hess=1/abs(pres-gap)
    grad[np.isinf(grad)]=0#如果gap是0的话，一阶和二阶导数都是0，也就是不需要调整，这样真的好么？
    hess[np.isinf(hess)]=0
    return grad,hess
def mymapeval(pres,dtrain):#返回损失的函数
   pres = pres.astype(float)
   gap = dtrain.get_label().astype(float)
   #随机选择   
   #idx = np.random.choice(np.arange(len(pres)), 2838, replace=False)
   #pres = pres[idx]
   #gap = gap[idx]   
   #进行预处理
   pres[pres<1.3]=1
   pres[(1.7<pres)&(pres<2.3)]=2
   pres[(2.7<pres)&(pres<3.3)]=3
   pres[(3.7<pres)&(pres<4.3)]=4
   error=np.divide(np.abs(pres-gap),gap)
   error[np.isinf(error)]=0
   return 'error', np.mean(error)

def mymapeval2(pres,gap):
   pres=pres.astype(float)
   gap=gap.astype(float)
   pres[pres<1.3]=1
   pres[(1.6<pres)&(pres<2.4)]=2
   pres[(2.6<pres)&(pres<3.4)]=3
   pres[(3.7<pres)&(pres<4.3)]=4
   pres[(4.7<pres)&(pres<5.3)]=5
   pres[(5.7<pres)&(pres<6.3)]=6
   pres[(6.7<pres)&(pres<7.3)]=7
   pres[(7.7<pres)&(pres<8.3)]=8
   pres[(8.7<pres)&(pres<9.3)]=9 
   error=np.divide(np.abs(pres-gap),gap)
   error[np.isinf(error)]=0
   return np.mean(error)

def mymapeval3(pres,gap):
   pres=pres.astype(float)
   gap=gap.astype(float)
   pres[pres<1]=1 
   error=np.divide(np.abs(pres-gap),gap)
   error[np.isinf(error)]=0
   return np.mean(error)
   
def trans_narray(pres):
   pres[pres<1.3]=1
   pres[(1.6<pres)&(pres<2.4)]=2
   pres[(2.6<pres)&(pres<3.4)]=3
   pres[(3.7<pres)&(pres<4.3)]=4
   pres[(4.7<pres)&(pres<5.3)]=5
   pres[(5.7<pres)&(pres<6.3)]=6
   pres[(6.7<pres)&(pres<7.3)]=7
   pres[(7.7<pres)&(pres<8.3)]=8
   pres[(8.7<pres)&(pres<9.3)]=9   
   return pres

def get_simple_guess_from_df(df):
    gap1=df.gap_minus1.as_matrix()
    gap2=df.gap_minus2.as_matrix()
    gap3=df.gap_minus3.as_matrix()
    gap1[np.isnan(gap1)]=0
    gap2[np.isnan(gap2)]=0
    gap3[np.isnan(gap3)]=0
    mymean=(0.65*gap1+0.25*gap2+0.15*gap3)/2
    mymean[mymean<1]=1
    return mymean


def get_mean_from_df(df):
    '''
    从df获取均值
    '''
    gap1=df.gap_minus1.as_matrix()
    gap2=df.gap_minus2.as_matrix()
    gap3=df.gap_minus3.as_matrix()
    gap1[np.isnan(gap1)]=0
    gap2[np.isnan(gap2)]=0
    gap3[np.isnan(gap3)]=0
    mymean=(0.5*gap1+0.3*gap2+0.2*gap3)
    mymean[mymean<1]=1
    return mymean





