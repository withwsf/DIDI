# -*- coding: utf-8 -*-
"""
Created on Tue Jun 07 20:59:55 2016

@author: wsf
"""
engine='python'
import pandas as pd
from datetime import datetime
import os
import itertools
import numpy as np

def get_time_slice(s):
    '''
    获得此时间处于哪个slice
    输入：字符串
    输出：int，time slice
    '''
    dt=datetime.strptime(s,'%Y-%m-%d %H:%M:%S')
    init_time=datetime.combine(dt.date(),datetime.strptime('0:0:0','%H:%M:%S').time())
    return int((dt-init_time).total_seconds()/600)+1
def get_time_region(s):
    '''
    获得此时间处于一个time slice的前半段还是后半段，用在舍弃天气数据时
    输入：字符串
    输出：int：1或者2，前半个时间段返回1，后半个返回2
    '''
    dt=datetime.strptime(s,'%Y-%m-%d %H:%M:%S')
    init_time=datetime.combine(dt.date(),datetime.strptime('0:0:0','%H:%M:%S').time())
    if ((dt-init_time).total_seconds()%600)>300:
        return 2
    else:
        return 1
def get_weekofday(s):
    '''
    获得此时间处于周几
    输入：字符串
    输出：int，week of day，周一：1 周日：7
    '''
    ss=s.split(' ')[0].split('-')
    mydate=datetime(int(ss[0]),int(ss[1]),int(ss[2]))
    weekday=mydate.weekday()
    return weekday+1
def get_date(s):
    '''
    输入：标准日期时间字符串
    返回：日期
    '''
    return s.split(' ')[0]
    

     
def parse_weather(path,padding=True,search_range=12):
    '''
    参数：
       path:天气文件的路径
       padding:是否对数据缺失的time slice进行补充
       search_range:用来替代缺失time slice的搜寻范围，如果超过search_range的时间内都没有数据，则不进行补充
    返回：所有文件合并成的一个df文件
    '''
    files=os.listdir(path)
    list_of_weathers=[]
    for _file in files:
        print _file
        df=pd.read_csv(path+os.sep+_file,names=['Time','Weather','temperature','PM2.5'],sep='\t+')
        df['time_slice']=df.Time.map(lambda x:get_time_slice(x))
        df['date']=df.Time.map(lambda x:get_date(x))
        df['region']=df.Time.map(lambda x:get_time_region(x))
        df=df[df.region==1]
        df.drop('Time',axis=1,inplace=True)
        df.drop('region',axis=1,inplace=True)
        if padding:#如果需要补充缺失值
        #思路：求出所有可能record，然后与已有的record求差集，来得到缺失的record
         all_time_slices=set(range(1,145))
         cur_time_slices=set(df.time_slice.tolist())
         diff_=list(all_time_slices-cur_time_slices)
         if (144-len(diff_))!=len(df.index):#如果单个_file中time_slice不是唯一的，那么肯定存在错误
             print "天气数据存在异常！！！"
             print _file
         list_of_temp_s=[]         
         for lost_ts in diff_:#对于每个缺失的时间片，如果在其search range内有record，则用距离最近的那个来代替缺失值
             for time_delta in range(1,search_range+1):
                 if len(df[df.time_slice==(lost_ts+time_delta)].index)==1 or len(df[df.time_slice==(lost_ts-time_delta)].index)==1:
                    if len(df[df.time_slice==(lost_ts+time_delta)].index)==1:
                        ls=df[df.time_slice==(lost_ts+time_delta)].values.tolist()[0]
                    else:
                        ls=df[df.time_slice==(lost_ts-time_delta)].values.tolist()[0]
                    ls[3]=lost_ts#将符合条件的timeslice的值修改为缺失值，用来代替缺失值
                    temp_df=pd.DataFrame([ls],columns=['Weather','temperature','PM2.5','time_slice','date'])
                    list_of_temp_s.append(temp_df)
                    break
         if len(list_of_temp_s)>0:
           temp_df=pd.concat(list_of_temp_s,axis=0)
           df=pd.concat([df,temp_df],axis=0) 
        list_of_weathers.append(df)
    ret=pd.concat(list_of_weathers,axis=0)
    return ret


def parse_traffic(path,padding=True,search_range=3):
    '''
    参数：
        path:交通状况文件的路径
        padding:是否对数据缺失的time slice进行补充
        search_range:用来替代缺失time slice的搜寻范围，如果超过search_range的时间内都没有数据，则不进行补充
    返回：所有文件合并成的一个df文件
    '''
    files=os.listdir(path)
    list_of_traffics=[]
    for _file in files:
        print _file
        df=pd.read_csv(path+os.sep+_file,sep='\t+',names=['district_id','tj_level1','tj_level2','tj_level3','tj_level4','Time'])
        df['time_slice']=df.Time.map(lambda x:get_time_slice(x))
        df['date']=df.Time.map(lambda x:get_date(x))
        df.district_id=df.district_id.replace(dist_dict)
        df.tj_level1=df.tj_level1.map(lambda x:x.split(':')[1])
        df.tj_level2=df.tj_level2.map(lambda x:x.split(':')[1])
        df.tj_level3=df.tj_level3.map(lambda x:x.split(':')[1])
        df.tj_level4=df.tj_level4.map(lambda x:x.split(':')[1])
        df.drop('Time',axis=1,inplace=True)
        if padding:#如果需要补充缺失值
        #思路：求出所有可能record，然后与已有的record求差集，来得到缺失的record
            cur_record=set(zip(df.time_slice.tolist(),df.district_id.tolist()))
            if len(cur_record)!=len(df.index):#如果单个_file中time_slice和district的组合不是唯一的，那么同一个时间段内有多份交通信息
               print "交通数据存在异常！！！"
               print _file
            time_slices=range(1,145)
            dist_ids=range(1,67)
            all_combinations=set(list(itertools.product(time_slices,dist_ids)))
            diff=all_combinations-cur_record
            list_of_temp_df=[]
            for lost_traffic in diff:
                t_s=lost_traffic[0]
                d_i=lost_traffic[1]
                for time_delta in range(1,search_range+1):
                    up_df=df[(df.district_id==d_i)&(df.time_slice==(t_s+time_delta))]
                    down_df=df[(df.district_id==d_i)&(df.time_slice==(t_s-time_delta))]
                    if len(up_df.index)==1 or len(down_df.index)==1:
                        if len(up_df.index)==1:
                           ls=up_df.values.tolist()[0]
                        else:
                           ls=down_df.values.tolist()[0]
                        ls[5]=t_s
                        temp_df=pd.DataFrame([ls],columns=['district_id','tj_level1','tj_level2','tj_level3','tj_level4','time_slice','date'])
                        list_of_temp_df.append(temp_df)
                        break
            if(len(list_of_temp_df)>0): 
                temp_df=pd.concat(list_of_temp_df,axis=0)
                df=pd.concat([df,temp_df],axis=0)            
        list_of_traffics.append(df)
    ret=pd.concat(list_of_traffics,axis=0)
    return ret


def parse_train_order(path,padding=True):#暂时强制使用padding，所以padding参数无效
    '''
    输入：
        path： 订单数据文件夹
        padding：默认True，是否对没有数据的区域+时间组合进行补0操作
    输出：
        处理好的order订单
    '''
    files=os.listdir(path)
    list_of_orders=[]
    for _file in files:
        print _file
        df=pd.read_csv(path+os.sep+_file,sep='\t+',names=['order_id','driver_id','passenger_id','start_district_hash','dest_district_hash','Price','Time'])
        df['time_slice']=df.Time.map(lambda x:get_time_slice(x))
        df['date']=df.Time.map(lambda x:get_date(x))
        df['district_id']=df.start_district_hash.replace(dist_dict)
        df.dest_district_hash=df.dest_district_hash.replace(dist_dict)
       
        total=df.groupby(['date','district_id','time_slice']).size()
        total=total.rename("total")
        '''使用total-offered来获取gap更好（更方便后去gap=0的情况)
        df_gap=df[df.driver_id.isnull()]
        gap=df_gap.groupby(['date','district_id','time_slice']).size()
        gap=gap.rename("gap")
        '''
        df_offered=df[df.driver_id.notnull()]
        offered=df_offered.groupby(['date','district_id','time_slice']).size()
        offered=offered.rename("offered")
        
        #将total中有但在offered中没有的纪录补0
        offered_diff_index=total.index.difference(offered.index)
        padded_offered=pd.Series(data=np.zeros(len(offered_diff_index)),index=offered_diff_index,name="offered")
        offered=offered.append(padded_offered)
        
        #计算供应率
        rate=offered.divide(total)        
        rate=rate.rename("rate")
        
        #计算gap
        gap=total-offered
        gap=gap.rename("gap")
        
        #header
        header=gap.reset_index()
        header=header[header.time_slice>3]#从第四个时间段开始取数据
        header['time_slice_minus_1']=header.time_slice-1#10min之前
        header['time_slice_minus_2']=header.time_slice-2#20min之前
        header['time_slice_minus_3']=header.time_slice-3#30min之前
        
        
        #if padding: #如果gap存在，那么其前面30min中有数据缺失的话，全补为0       
        #get combination of all time_slice and district
        districts=range(1,67)
        time_slices=range(1,145)
        today=[df.date.loc[0]]
        all_combinations=list(itertools.product(today,districts,time_slices))
        all_indexs = pd.MultiIndex.from_tuples(all_combinations, names=['date', 'district_id','time_slice'])
        diff_indexs=all_indexs.difference(total.index)
        padding=pd.Series(data=np.zeros(len(diff_indexs)),index=diff_indexs,name="total")
        total=total.append(padding)
         
        padding=padding.rename("gap")
        gap=gap.append(padding)
         
        padding=padding.rename("offered")
        offered=offered.append(padding)
         
        rate_padding=pd.Series(data=np.ones(len(diff_indexs)),index=diff_indexs,name='rate')
        rate=rate.append(rate_padding)
        
        offered=offered.reset_index()
        total=total.reset_index()
        gap=gap.reset_index()
        rate=rate.reset_index()
        
        new_df=pd.merge(total,gap,on=['date','district_id','time_slice'],how="left")
        new_df=pd.merge(new_df,offered,on=['date','district_id','time_slice'],how="left")
        new_df=pd.merge(new_df,rate,on=['date','district_id','time_slice'],how="left")
               
       
       
        header=pd.merge(header,new_df,left_on=["date","district_id","time_slice_minus_1"],right_on=["date","district_id","time_slice"],how="left",suffixes=('', '_minus1'))
        header=pd.merge(header,new_df,left_on=["date","district_id","time_slice_minus_2"],right_on=["date","district_id","time_slice"],how="left",suffixes=('', '_minus2'))
        header=pd.merge(header,new_df,left_on=["date","district_id","time_slice_minus_3"],right_on=["date","district_id","time_slice"],how="left",suffixes=('', '_minus3'))
        
        #重命名，删除多余列
        header.rename(columns={'total':'total_minus1'}, inplace=True)
        header.rename(columns={'offered':'offered_minus1'}, inplace=True)
        header.rename(columns={'rate':'rate_minus1'}, inplace=True)
        header.drop('time_slice_minus1',axis=1,inplace=True)
        header.drop('time_slice_minus2',axis=1,inplace=True)
        header.drop('time_slice_minus3',axis=1,inplace=True)                    
        list_of_orders.append(header)
    ret=pd.concat(list_of_orders,axis=0)
    return ret
        

def parse_poi(path):
    '''
    输入：poi文件的路径
    输出：Dataframe，每一行某个地区的基础设施的种类与数量
    '''
    lines=open(path).readlines()
    classes=set()
    print path
    for line in lines:
        l=line.split('	')
        for i in range(1,len(l)):
            record=l[i]
            cls=record.split(":")[0]
            cls2=cls.split("#")
            fir=cls2[0]
            classes.add(fir)
            for j in range(1,len(cls2)):
                fir=fir+"#"+cls2[j]
                classes.add(fir)
    temp=list(classes)
    temp.sort()           
    cols=['district_id']+temp
    loc_dict=dict(zip(temp,range(1,len(temp)+1)))
    data_=np.zeros([len(lines),len(cols)])
    
    row_num=0
    for line in lines:
        l=line.split('	')
        dis_id=dist_dict[l[0]]
        data_[row_num,0]=dis_id
        for i in range(1,len(l)):
            record=l[i]
            cls=record.split(":")[0]
            nums_=record.split(":")[1]
            cls2=cls.split("#")
            fir=cls2[0]
            data_[row_num,loc_dict[fir]]=(int(data_[row_num,loc_dict[fir]])+int(nums_))
            for j in range(1,len(cls2)):
                fir=fir+"#"+cls2[j]
                data_[row_num,loc_dict[fir]]=(int(data_[row_num,loc_dict[fir]])+int(nums_))
                
        row_num=row_num+1
    ret=pd.DataFrame(data=data_,columns=cols)
    return ret   

def parse_test_order(path,padding=True):#暂时强制使用padding，所以padding参数无效
    to_predict_lines=[line.strip() for line in open(path+os.sep+"read_me_2.txt").readlines()[1:]]
    district_ids=range(1,67)
    combinations=list(itertools.product(to_predict_lines,district_ids))
    list_of_dates=[]
    list_of_time_slices=[]
    list_of_districts=[]
    for r in combinations:
        list_of_districts.append(r[1])
        dates_list=r[0].split('-')
        list_of_time_slices.append(int(dates_list[3]))
        list_of_dates.append(dates_list[0]+'-'+dates_list[1]+'-'+dates_list[2])
    header=pd.concat([pd.Series(list_of_dates,name="date"),pd.Series(list_of_districts,name="district_id"),pd.Series(list_of_time_slices,name="time_slice")],axis=1)
    header['time_slice_minus_1']=header.time_slice-1#10min之前
    header['time_slice_minus_2']=header.time_slice-2#20min之前
    header['time_slice_minus_3']=header.time_slice-3#30min之前    
    files=os.listdir(path+os.sep+'order_data')
    list_of_orders=[]
    for _file in files:
        print _file
        df=pd.read_csv(path+os.sep+"order_data"+os.sep+_file,sep='\t+',names=['order_id','driver_id','passenger_id','start_district_hash','dest_district_hash','Price','Time'])
        df['time_slice']=df.Time.map(lambda x:get_time_slice(x))
        df['date']=df.Time.map(lambda x:get_date(x))
        df['district_id']=df.start_district_hash.replace(dist_dict)
        df.dest_district_hash=df.dest_district_hash.replace(dist_dict)
       
        total=df.groupby(['date','district_id','time_slice']).size()
        total=total.rename("total")
        '''使用total-offered来获取gap更好（更方便后去gap=0的情况)
        df_gap=df[df.driver_id.isnull()]
        gap=df_gap.groupby(['date','district_id','time_slice']).size()
        gap=gap.rename("gap")
        '''
        df_offered=df[df.driver_id.notnull()]
        offered=df_offered.groupby(['date','district_id','time_slice']).size()
        offered=offered.rename("offered")
        
        #将total中有但在offered中没有的纪录补0
        offered_diff_index=total.index.difference(offered.index)
        padded_offered=pd.Series(data=np.zeros(len(offered_diff_index)),index=offered_diff_index,name="offered")
        offered=offered.append(padded_offered)
        
        #计算供应率
        rate=offered.divide(total)        
        rate=rate.rename("rate")
        
        #计算gap
        gap=total-offered
        gap=gap.rename("gap")
        
       
        
        
        
        #if padding: #如果gap存在，那么其前面30min中有数据缺失的话，全补为0       
        #get combination of all time_slice and district
        districts=range(1,67)
        time_slices=range(1,145)
        today=[df.date.loc[0]]
        all_combinations=list(itertools.product(today,districts,time_slices))
        all_indexs = pd.MultiIndex.from_tuples(all_combinations, names=['date', 'district_id','time_slice'])
        diff_indexs=all_indexs.difference(total.index)
        padding=pd.Series(data=np.zeros(len(diff_indexs)),index=diff_indexs,name="total")
        total=total.append(padding)
        padding=padding.rename("gap")
        gap=gap.append(padding)
        padding=padding.rename("offered")
        offered=offered.append(padding)
        rate_padding=pd.Series(data=np.ones(len(diff_indexs)),index=diff_indexs,name='rate')
        rate=rate.append(rate_padding)
            
             
        offered=offered.reset_index()
        total=total.reset_index()
        gap=gap.reset_index()
        rate=rate.reset_index()
        #else:
        new_df=pd.merge(total,gap,on=['date','district_id','time_slice'],how="left")
        new_df=pd.merge(new_df,offered,on=['date','district_id','time_slice'],how="left")
        new_df=pd.merge(new_df,rate,on=['date','district_id','time_slice'],how="left")
        list_of_orders.append(new_df)
        
       
       
        
    order_df=pd.concat(list_of_orders,axis=0)    
    header=pd.merge(header,order_df,left_on=["date","district_id","time_slice_minus_1"],right_on=["date","district_id","time_slice"],how="left",suffixes=('', '_minus1'))
    header=pd.merge(header,order_df,left_on=["date","district_id","time_slice_minus_2"],right_on=["date","district_id","time_slice"],how="left",suffixes=('', '_minus2'))
    header=pd.merge(header,order_df,left_on=["date","district_id","time_slice_minus_3"],right_on=["date","district_id","time_slice"],how="left",suffixes=('', '_minus3'))
        
    #重命名，删除多余列
    header.rename(columns={'total':'total_minus1'}, inplace=True)
    header.rename(columns={'offered':'offered_minus1'}, inplace=True)
    header.rename(columns={'rate':'rate_minus1'}, inplace=True)
    header.rename(columns={'gap':'gap_minus1'}, inplace=True)
    header.drop('time_slice_minus1',axis=1,inplace=True)
    header.drop('time_slice_minus2',axis=1,inplace=True)
    header.drop('time_slice_minus3',axis=1,inplace=True)                    
    return header
   
def merger_infos(order_df,weather_df=None,traffic_df=None,poi_df=None):
    new_df=order_df
    
    if weather_df is not None:
        new_df=pd.merge(new_df,weather_df,left_on=["date","time_slice_minus_1"],right_on=["date","time_slice"],how="left",suffixes=("","_minus1"))
        new_df=pd.merge(new_df,weather_df,left_on=["date","time_slice_minus_2"],right_on=["date","time_slice"],how="left",suffixes=("","_minus2"))
        new_df=pd.merge(new_df,weather_df,left_on=["date","time_slice_minus_3"],right_on=["date","time_slice"],how="left",suffixes=("","_minus3"))
        new_df.drop('time_slice_minus1',axis=1,inplace=True)
        new_df.drop('time_slice_minus2',axis=1,inplace=True)
        new_df.drop('time_slice_minus3',axis=1,inplace=True)
    if traffic_df is not None:
        new_df=pd.merge(new_df,traffic_df,left_on=["date","district_id","time_slice_minus_1"],right_on=["date","district_id","time_slice"],how="left",suffixes=("","_minus1"))
        new_df=pd.merge(new_df,traffic_df,left_on=["date","district_id","time_slice_minus_2"],right_on=["date","district_id","time_slice"],how="left",suffixes=("","_minus2"))
        new_df=pd.merge(new_df,traffic_df,left_on=["date","district_id","time_slice_minus_3"],right_on=["date","district_id","time_slice"],how="left",suffixes=("","_minus3"))
        new_df.drop('time_slice_minus1',axis=1,inplace=True)
        new_df.drop('time_slice_minus2',axis=1,inplace=True)
        new_df.drop('time_slice_minus3',axis=1,inplace=True)
    if poi_df is not None:
        new_df=pd.merge(new_df,poi_df,on="district_id") 
    new_df["weekofday"]=new_df.date.map(lambda x:get_weekofday(x))
    new_df.drop('time_slice_minus_1',axis=1,inplace=True)
    new_df.drop('time_slice_minus_2',axis=1,inplace=True)
    new_df.drop('time_slice_minus_3',axis=1,inplace=True)
    return new_df
def preprocess(train_path,test_path,save_path=None):
    test_order_df=parse_test_order(test_path)
    test_weather_df=parse_weather(test_path+os.sep+"weather_data",padding=True)
    test_traffic_df=parse_traffic(test_path+os.sep+"traffic_data")
    test_poi_df=parse_poi(test_path+os.sep+"poi_data"+os.sep+"poi_data")
    
    #train_order_df=parse_train_order(train_path+os.sep+"order_data")
    #train_weather_df=parse_weather(train_path+os.sep+"weather_data",padding=True)
    #train_traffic_df=parse_traffic(train_path+os.sep+"traffic_data")
    #train_poi_df=parse_poi(train_path+os.sep+"poi_data"+os.sep+"poi_data")
    
    
    
    #train_df=merger_infos(train_order_df,train_weather_df,train_traffic_df,train_poi_df)
    test_df=merger_infos(test_order_df,test_weather_df,test_traffic_df,test_poi_df)
    if save_path!=None:
        #train_df.to_csv(save_path+os.sep+"train.csv",index=False)
        test_df.to_csv(save_path+os.sep+"test.csv",index=False)
    else:
        #train_df.to_csv("train.csv",index=False)
        test_df.to_csv("test.csv",index=False)
    
   
    
#weather='E:/Data/cityData/season_1/training_data/weather_data/weather_data_2016-01-01'
#df=pd.read_csv(weather,sep='\t+',names=['Time','Weather','temperature','PM2.5'])

home="/home/wsf/data/cityData/new_data/season_2"
train_path=home+os.sep+"training_data"
test_path=home+os.sep+"test_set_2"
df_dict=pd.read_csv(train_path+os.sep+"cluster_map"+os.sep+"cluster_map",names=["district_hash","district_id"],sep='\t+')
dist_dict=dict(zip(df_dict.district_hash.tolist(),map(int,df_dict.district_id.tolist())))

preprocess(train_path,test_path,save_path=home)
