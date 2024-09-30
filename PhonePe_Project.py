# import os
# os.environ["GIT_PYTHON_REFRESH"] = "quiet"
# import git
# repository_url = "https://github.com/PhonePe/pulse.git"
# destination_directory = "C:/Users/rajij/PhonePe Project/t1/data"
# git.Repo.clone_from (repository_url, destination_directory)




import pandas as pd
import json
import os
import streamlit as st
from streamlit_option_menu import option_menu

import plotly
import plotly.express as px

import dash
from dash import Dash, dcc, html, Input, Output,callback

# Initialize session state
# if 'shared_data' not in st.session_state:
#     st.session_state['shared_data'] = {}

# Navigation
# st.sidebar.title("Navigation")
# page = st.sidebar.radio("Go to", ["1_Agg txn.py", "2_Map txn.py"])

# if page == "1_Agg txn.py":
#     import pages.page_1
#     pages.page_1.show()
# elif page == "2_Map txn.py":
#     import pages.page_2
#     pages.page_2.show()

import mysql.connector
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://root:Guvi#1234@localhost/Phonepetables')
mydb = mysql.connector.connect(
host = "localhost",
user ="root",
password='Guvi#1234',
database ="Phonepetables")

cursor=mydb.cursor()


#st.sidebar.success("Select a page above")

path="C:/Users/rajij/PhonePe Project/rawdata/t1/data/aggregated/transaction/country/india/state"
Agg_state_list_1=os.listdir(path)

clm={'State':[], 'Year':[],'Quater':[],'Transaction_type':[], 'Transaction_count':[], 'Transaction_amount':[], 'Transaction_amount_rounded':[]}

for i in Agg_state_list_1:
    p_i= path + "/"+ i
    
    Agg_yr_1=os.listdir(p_i)
    for j in Agg_yr_1:
        p_j=p_i+"/"+ j
        Agg_yr_list_1=os.listdir(p_j)
        for k in Agg_yr_list_1:
            p_k=p_j +"/" +k
            Data=open(p_k,'r')
            D=json.load(Data)
            for z in D['data']['transactionData']:
              Name=z['name']
              count=z['paymentInstruments'][0]['count']
              amount=z['paymentInstruments'][0]['amount']
              amount1=round(amount)
              clm['Transaction_type'].append(Name)
              clm['Transaction_count'].append(count)
              clm['Transaction_amount'].append(amount)
              clm['Transaction_amount_rounded'].append(amount1)
              clm['State'].append(i)
              clm['Year'].append(j)
              clm['Quater'].append(int(k.strip('.json')))
#Succesfully created a dataframe
Agg_Trans1=pd.DataFrame(clm)
Agg_Trans1.drop(Agg_Trans1[Agg_Trans1['State'] == 'lakshadweep'].index, axis=0, inplace=True)


path2="C:/Users/rajij/PhonePe Project/rawdata/t1/data/aggregated/user/country/india/state"
Agg_state_list_2=os.listdir(path2)
#print(Agg_state_list_2)



clm2={'State':[], 'Year':[],'Quater':[],'Registered_Users':[], 'Brand':[],'brandusercount':[],'branduserpercent':[], 'branduserperrounded':[]}

for i in Agg_state_list_2:
    p_i_2= path2 + "/"+ i
    
    Agg_yr_2=os.listdir(p_i_2)
    for j in Agg_yr_2:
        p_j_2=p_i_2+"/"+ j
        Agg_yr_list_2=os.listdir(p_j_2)
        for k in Agg_yr_list_2:
            p_k_2=p_j_2 +"/" +k
            Data2=open(p_k_2,'r')
            D2=json.load(Data2)
            #print(D2)
            try:
                
                for z in D2['data']:
                    
                    Registered_Users = D2['data']['aggregated']['registeredUsers']
                    Brand = D2['data']['usersByDevice'][0]['brand']
                    brandusercount = D2['data']['usersByDevice'][0]['count']
                    branduserpercent = D2['data']['usersByDevice'][0]['percentage']
                    branduserperrounded=round(branduserpercent,2)
                    clm2['Registered_Users'].append(Registered_Users)
                    clm2['Brand'].append(Brand)
                    clm2['brandusercount'].append(brandusercount)
                    clm2['branduserpercent'].append(branduserpercent)
                    clm2['branduserperrounded'].append(branduserperrounded)
                    clm2['State'].append(i)
                    clm2['Year'].append(j)
                    clm2['Quater'].append(int(k.strip('.json')))
                
            except:
                pass
           
                
#Succesfully created a dataframe
Agg_Trans2=pd.DataFrame(clm2)


path3="C:/Users/rajij/PhonePe Project/rawdata/t1/data/map/transaction/hover/country/india/state"
Agg_state_list_3=os.listdir(path3)

clm3={'State':[], 'Year':[],'Quater':[],'MapName':[], 'Maptxn_count':[],'Maptxn_amt':[],'Maptxn_amt_rounded':[]}

for i in Agg_state_list_3:
    p_i_3= path3 + "/"+ i
    
    Agg_yr_3=os.listdir(p_i_3)
    for j in Agg_yr_3:
        p_j_3=p_i_3+"/"+ j
        Agg_yr_list_3=os.listdir(p_j_3)
        for k in Agg_yr_list_3:
            p_k_3=p_j_3 +"/" +k
            Data3=open(p_k_3,'r')
            D3=json.load(Data3)
            #print(D3)
                          
            for z in D3['data']['hoverDataList']:
                
                MapName=z['name']
                Maptxn_count=z['metric'][0]['count']
                Maptxn_amt=z['metric'][0]['amount']
                Maptxn_amt1 = round(Maptxn_amt)
                clm3['MapName'].append(MapName)
                clm3['Maptxn_count'].append(Maptxn_count)
                clm3['Maptxn_amt'].append(Maptxn_amt)
                clm3['Maptxn_amt_rounded'].append(Maptxn_amt1)
                clm3['State'].append(i)
                clm3['Year'].append(j)
                clm3['Quater'].append(int(k.strip('.json')))
#Succesfully created a dataframe

Agg_Trans3=pd.DataFrame(clm3)

path4="C:/Users/rajij/PhonePe Project/rawdata/t1/data/map/user/hover/country/india/state"
Agg_state_list_4=os.listdir(path4)

clm4={'State':[], 'Year':[],'Quater':[],'Mapname':[], 'Mapuserscount':[]}

for i in Agg_state_list_4:
    p_i_4= path4 + "/"+ i
    
    Agg_yr_4=os.listdir(p_i_4)
    for j in Agg_yr_4:
        p_j_4=p_i_4+"/"+ j
        Agg_yr_list_4=os.listdir(p_j_4)
        for k in Agg_yr_list_4:
            p_k_4=p_j_4 +"/" +k
            Data4=open(p_k_4,'r')
            D4=json.load(Data4)
            #print(D4)
               
            for keys, values in D4['data']['hoverData'].items():
                Mapname = keys
                #print(Mapname)
                mapvalue = values
                #print(mapvalue)
    
                Mapuserscount=mapvalue['registeredUsers']
                clm4['Mapname'].append(Mapname)
                clm4['Mapuserscount'].append(Mapuserscount)
                clm4['State'].append(i)
                clm4['Year'].append(j)
                clm4['Quater'].append(int(k.strip('.json')))
Agg_Trans4=pd.DataFrame(clm4)


path5="C:/Users/rajij/PhonePe Project/rawdata/t1/data/top/transaction/country/india/state"
Agg_state_list_5=os.listdir(path5)
clm5={'State':[], 'Year':[],'Quater':[], 'District_Name':[], 'Dist_usercount':[],'Dist_txn_amount':[],'Dist_txn_amount_rounded':[],'Pincode':[], 'Pincode_usercount':[],'Pincode_txn_amount':[],'Pincode_txn_amount_rounded':[] }

for i in Agg_state_list_5:
    p_i_5= path5 + "/"+ i
    
    Agg_yr_5=os.listdir(p_i_5)
    
    for j in Agg_yr_5:
        p_j_5=p_i_5+"/"+ j
        
        Agg_yr_list_5=os.listdir(p_j_5)
        for k in Agg_yr_list_5:
            p_k_5=p_j_5 +"/" +k
            
            Data5=open(p_k_5,'r')
            D5=json.load(Data5)
            #print(D5)
                
            for n in D5:
                
                for z in D5['data']['districts']:
                    District_Name = z['entityName']
                    Dist_usercount = z['metric']['count']
                    Dist_txn_amount= z['metric']['amount']
                    Dist_txn_amount1=round(Dist_txn_amount)
                for y in D5['data']['pincodes']:
                    Pincode = y['entityName']
                    Pincode_usercount = y['metric']['count']
                    Pincode_txn_amount= y['metric']['amount']
                    Pincode_txn_amount1=round(Pincode_txn_amount)
                    clm5['District_Name'].append(District_Name)
                    clm5['Dist_usercount'].append(Dist_usercount)
                    clm5['Dist_txn_amount'].append(Dist_txn_amount)
                    clm5['Dist_txn_amount_rounded'].append(Dist_txn_amount1)
                    clm5['Pincode'].append(Pincode)
                    clm5['Pincode_usercount'].append(Pincode_usercount)
                    clm5['Pincode_txn_amount'].append(Pincode_txn_amount)
                    clm5['Pincode_txn_amount_rounded'].append(Pincode_txn_amount1)    
                    clm5['State'].append(i)
                    clm5['Year'].append(j)
                    clm5['Quater'].append(int(k.strip('.json')))
    

Agg_Trans5=pd.DataFrame(clm5)

path6="C:/Users/rajij/PhonePe Project/rawdata/t1/data/top/user/country/india/state"
Agg_state_list_6=os.listdir(path6)
clm6={'State':[], 'Year':[],'Quater':[], 'District_Name':[], 'Dist_usercount':[],'Pincode':[], 'Pincode_usercount':[]}

for i in Agg_state_list_6:
    p_i_6= path6 + "/"+ i
    
    Agg_yr_6=os.listdir(p_i_6)
    
    for j in Agg_yr_6:
        p_j_6=p_i_6+"/"+ j
        
        Agg_yr_list_6=os.listdir(p_j_6)
        for k in Agg_yr_list_6:
            p_k_6=p_j_6 +"/" +k
            
            Data6=open(p_k_6,'r')
            D6=json.load(Data6)
            #print(D6)
            
            for n in D6:
                
                for z in D6['data']['districts']:
                    District_Name = z['name']
                    Dist_usercount = z['registeredUsers']
                    
                for y in D6['data']['pincodes']:
                    Pincode = y['name']
                    Pincode_usercount = y['registeredUsers']
                    clm6['District_Name'].append(District_Name)
                    clm6['Dist_usercount'].append(Dist_usercount)
                    clm6['Pincode'].append(Pincode)
                    clm6['Pincode_usercount'].append(Pincode_usercount)
                    clm6['State'].append(i)
                    clm6['Year'].append(j)
                    clm6['Quater'].append(int(k.strip('.json')))
    

Agg_Trans6=pd.DataFrame(clm6)

map_dict={'andaman-&-nicobar-islands':'Andaman & Nicobar', 'andhra-pradesh':'Andhra Pradesh', 'arunachal-pradesh':'Arunachal Pradesh',
       'assam':'Assam', 'bihar':'Bihar', 'chandigarh':'Chandigarh', 'chhattisgarh':'Chhattisgarh',
       'dadra-&-nagar-haveli-&-daman-&-diu':'Dadra and Nagar Haveli and Daman and Diu', 'delhi':'Delhi', 'goa':'Goa', 'gujarat':'Gujarat',
       'haryana':'Haryana', 'himachal-pradesh':'Himachal Pradesh', 'jammu-&-kashmir':'Jammu & Kashmir', 'jharkhand':'Jharkhand',
       'karnataka':'Karnataka', 'kerala':'Kerala', 'ladakh':'Ladakh', 'madhya-pradesh':'Madhya Pradesh',
       'maharashtra':'Maharashtra', 'manipur':'Manipur', 'meghalaya':'Meghalaya', 'mizoram':'Mizoram', 'nagaland':'Nagaland',
       'odisha':'Odisha', 'puducherry':'Puducherry', 'punjab':'Punjab', 'rajasthan':'Rajasthan', 'sikkim':'Sikkim',
       'tamil-nadu':'Tamil Nadu', 'telangana':'Telangana', 'tripura':'Tripura', 'uttar-pradesh':'Uttar Pradesh',
       'uttarakhand':'Uttarakhand', 'west-bengal':'West Bengal'}

Agg_Trans1['State'] = Agg_Trans1['State'].map(map_dict)
Agg_Trans2['State'] = Agg_Trans2['State'].map(map_dict)
Agg_Trans3['State'] = Agg_Trans3['State'].map(map_dict)
Agg_Trans4['State'] = Agg_Trans4['State'].map(map_dict)
Agg_Trans5['State'] = Agg_Trans5['State'].map(map_dict)
Agg_Trans6['State'] = Agg_Trans6['State'].map(map_dict)


try:
    Agg_Trans1.to_sql(name='aggregatetxnq', con=engine, if_exists='append', index=False)
except:
    pass
try:
    Agg_Trans2.to_sql(name='aggregateuser', con=engine, if_exists='append', index=False)
except:
    pass
try:
    Agg_Trans3.to_sql(name='maptxn', con=engine, if_exists='append', index=False)
except:
    pass
Agg_Trans4.to_sql(name='mapusercount', con=engine, if_exists='append', index=False)
Agg_Trans5.to_sql(name='toptxn', con=engine, if_exists='append', index=False)
Agg_Trans6.to_sql(name='topusercount', con=engine, if_exists='append', index=False)
Agg_Trans6.to_sql(name='topusercount2', con=engine, if_exists='append', index=False)











  



