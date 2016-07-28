# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 16:00:05 2016

@author: wsf
"""
import numpy as np
from sklearn import  preprocessing
import pandas as pd
min_max_scaler = preprocessing.MinMaxScaler()
def transform_feature(df,dropNa=False):
    if dropNa:
        df=df.dropna(axis=0,how='any')
    #对weekday进行dummy coding
    S_weekday=df.weekofday
    week_padding=pd.Series(range(1,8),index=range(-7,0))
    S_week_day_padded=pd.concat([week_padding,S_weekday],axis=0)
    week_ret=pd.get_dummies(data=S_week_day_padded,prefix='weekday')
    week_ret2=week_ret.ix[0:]
    df=pd.concat([df,week_ret2],axis=1)
    df.drop('weekofday',axis=1,inplace=True)
    #get traffic normalize by col

#    normed_traffic_class_1=pd.Series(min_max_scaler.fit_transform(df.tj_level1),name='traffic_1_col1')
#    normed_traffic_class_2=pd.Series(min_max_scaler.fit_transform(df.tj_level2),name='traffic_2_col1')
#    normed_traffic_class_3=pd.Series(min_max_scaler.fit_transform(df.tj_level3),name='traffic_3_col1')
#    normed_traffic_class_4=pd.Series(min_max_scaler.fit_transform(df.tj_level4),name='traffic_4_col1')
#    df=pd.concat([df,normed_traffic_class_1,normed_traffic_class_2,normed_traffic_class_3,normed_traffic_class_4],axis=1)
#    
#    normed_traffic_class_1=pd.Series(min_max_scaler.fit_transform(df.tj_level1_minus2),name='traffic_1_col2')
#    normed_traffic_class_2=pd.Series(min_max_scaler.fit_transform(df.tj_level2_minus2),name='traffic_2_col2')
#    normed_traffic_class_3=pd.Series(min_max_scaler.fit_transform(df.tj_level3_minus2),name='traffic_3_col2')
#    normed_traffic_class_4=pd.Series(min_max_scaler.fit_transform(df.tj_level4_minus2),name='traffic_4_col2')
#    df=pd.concat([df,normed_traffic_class_1,normed_traffic_class_2,normed_traffic_class_3,normed_traffic_class_4],axis=1)
#    
#    normed_traffic_class_1=pd.Series(min_max_scaler.fit_transform(df.tj_level1_minus3),name='traffic_1_col3')
#    normed_traffic_class_2=pd.Series(min_max_scaler.fit_transform(df.tj_level2_minus3),name='traffic_2_col3')
#    normed_traffic_class_3=pd.Series(min_max_scaler.fit_transform(df.tj_level3_minus3),name='traffic_3_col3')
#    normed_traffic_class_4=pd.Series(min_max_scaler.fit_transform(df.tj_level4_minus3),name='traffic_4_col3')
#    df=pd.concat([df,normed_traffic_class_1,normed_traffic_class_2,normed_traffic_class_3,normed_traffic_class_4],axis=1)
    
    #get traffic normalize by row
    df['change_rate1']=df.gap_minus1/df.gap_minus2
    df['change_rate2']=df.gap_minus2/df.gap_minus3
    df['change_rate3']=df.gap_minus1/df.gap_minus3
    df['gap_total']=df.gap_minus1+df.gap_minus2+df.gap_minus3
    
    df['o_change_rate1']=df.offered_minus1/df.offered_minus2
    df['o_change_rate2']=df.offered_minus2/df.offered_minus3
    df['o_change_rate3']=df.offered_minus1/df.offered_minus3
    df['o_gap_total']=df.offered_minus1+df.offered_minus2+df.offered_minus3
    
    df['t_change_rate1']=df.total_minus1/df.total_minus2
    df['t_change_rate2']=df.total_minus2/df.total_minus3
    df['t_change_rate3']=df.total_minus1/df.total_minus3
    df['t_gap_total']=df.total_minus1+df.total_minus2+df.total_minus3
    
    
    
    df_traffic=df[['tj_level1','tj_level2','tj_level3','tj_level4']]
    df_traffic.columns =['traffic_1_row1','traffic_2_row1','traffic_3_row1','traffic_4_row1']
    df_trafic_row_normalized=df_traffic.div(df_traffic.sum(axis=1), axis=0)
    df=pd.concat([df,df_trafic_row_normalized],axis=1)
    
    df_traffic=df[['tj_level1_minus2','tj_level2_minus2','tj_level3_minus2','tj_level4_minus2']]
    df_traffic.columns =['traffic_1_row2','traffic_2_row2','traffic_3_row2','traffic_4_row2']
    df_trafic_row_normalized=df_traffic.div(df_traffic.sum(axis=1), axis=0)
    df=pd.concat([df,df_trafic_row_normalized],axis=1)
    
    df_traffic=df[['tj_level1_minus3','tj_level2_minus3','tj_level3_minus3','tj_level4_minus3']]
    df_traffic.columns =['traffic_1_row3','traffic_2_row3','traffic_3_row3','traffic_4_row3']
    df_trafic_row_normalized=df_traffic.div(df_traffic.sum(axis=1), axis=0)
    df=pd.concat([df,df_trafic_row_normalized],axis=1)
    
    #对distric_id和time_slice进行dummy coding
    s_district=df.district_id
    district_padding=pd.Series(range(1,67),index=range(-66,0))
    padded_district=pd.concat([district_padding,s_district],axis=0)
    district_ret=pd.get_dummies(data=padded_district,prefix='district')
    district_ret2=district_ret.ix[0:]

    s_timeslice=df.time_slice
    timeslice_padding=pd.Series(range(1,145),index=range(-144,0))
    padded_timeslice=pd.concat([timeslice_padding,s_timeslice],axis=0)
    time_slice_ret=pd.get_dummies(data=padded_timeslice,prefix='time_slice')
    time_slice_ret2=time_slice_ret.ix[0:]
    df=pd.concat([df,district_ret2,time_slice_ret2],axis=1)
    df.drop('time_slice',axis=1,inplace=True)
    df.drop('district_id',axis=1,inplace=True)
    
    return df
    
    
 