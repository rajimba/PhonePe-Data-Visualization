import streamlit as st
from streamlit_option_menu import option_menu

import pandas as pd
import plotly
import plotly.express as px
from plotly.subplots import make_subplots
import json

import dash
from dash import Dash, dcc, html, Input, Output,callback

import plotly.graph_objects as go
st.set_page_config(layout='wide')


import mysql.connector
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://root:Guvi#1234@localhost/Phonepetables')
mydb = mysql.connector.connect(
host = "localhost",
user ="root",
password='Guvi#1234',
database ="Phonepetables")

cursor=mydb.cursor()

##########1)AGG TXN DATA###############################################

def commontable_aggtxn():
 aggtxnamtcount = cursor.execute('select State, Year, Quater, Transaction_type, sum(Transaction_count) as Sumtxncount, sum(Transaction_amount_rounded) as Sumtxnamt from aggregatetxnq group by State, Year, Quater, Transaction_type')
 cursor.execute(aggtxnamtcount)
 aggtxn_amt_count = cursor.fetchall()
 aggtxn_amt_count_df= pd.DataFrame(aggtxn_amt_count, columns=cursor.column_names)
 return aggtxn_amt_count_df




def Aggregate_value_year(Year_d): 
 aggvalue_df = commontable_aggtxn()
 aggregated_df = aggvalue_df.groupby(['State','Year'])['Sumtxncount'].sum().reset_index()
 Year_d=str(Year_d)
 aggvalue_final = (aggregated_df[aggregated_df['Year']==Year_d])
 aggvalue_final = aggvalue_final.reset_index(drop=True)
 return aggvalue_final

def Aggregate_value_Q(Quarterselect):
 Database_yr = Aggregate_value_year(Year_d)
 aggvalue_df = commontable_aggtxn()
 aggvalue_df_Q = aggvalue_df.groupby(['Year','State','Quater'])['Sumtxncount'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect])
 return aggvalue_final_Q

def Year_Chart(Year_d):
 Database_yr = Aggregate_value_year(Year_d)

 col1, col2 = st.columns([2,1])
 with col1:

  st.subheader(f"{Database_yr['Year'].min()} Aggregated Transaction Count")
  
  fig = px.choropleth(
      Database_yr,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumtxncount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
##For total value to appear in the table
  total_row = pd.DataFrame({'Year': ['Total'], 'Sumtxncount': [Database_yr['Sumtxncount'].sum()]})
  df_with_tot = pd.concat([Database_yr, total_row], ignore_index=True)
##to remove <n/a> values in the table 
  df_with_total = df_with_tot.fillna('')
  st.dataframe(df_with_total,height=800,width=1000)

#####Groupby Tranasction Type
 aggvalue_df = commontable_aggtxn()
 aggvalue_type_df = aggvalue_df.groupby(['Year','Transaction_type'])['Sumtxncount'].sum().reset_index()
 Year_d=str(Year_d)
 aggvalue_type_final = (aggvalue_type_df[aggvalue_type_df['Year']==Year_d])
 aggvalue_type_final = aggvalue_type_final.reset_index(drop=True) 
 fig = px.pie(aggvalue_type_final, names='Transaction_type', values='Sumtxncount', title=f"Overall {Database_yr['Year'].min()} Transaction Type", width=1000)
 st.plotly_chart(fig)

##Groupby Year
 aggregated_df = aggvalue_df.groupby('Year')['Sumtxncount'].sum().reset_index()
 st.subheader(f"Aggregated Overall Yearwise Transaction Count w.r.t Transaction Type")
 fig = go.Figure()
 colorscale = px.colors.sequential.Plasma
##Add Bar Chart
 fig.add_trace(go.Bar(x=aggvalue_type_df['Year'], y=aggvalue_type_df['Sumtxncount'], marker=dict(color=aggvalue_type_df['Sumtxncount'], colorscale=colorscale, showscale=True) ))

 fig.add_trace(
    go.Scatter(x=aggregated_df['Year'], y=aggregated_df['Sumtxncount'], mode='lines+markers', name='Line Chart', marker_color='red'))
 

 fig.update_layout(
    title='Combined Bar and Line Graph',
    xaxis_title='Year',
    yaxis_title='Sumtxncount',
    barmode='stack')

 st.plotly_chart(fig)
 
 return df_with_total
   
#########QUARTERWISE DATA#########

def Aggregate_value_year_Quarter_(Quarterselect):
 
 Database_yr = Aggregate_value_year(Year_d)
 aggvalue_df = commontable_aggtxn()
 aggvalue_df_Q = aggvalue_df.groupby(['State','Year','Quater'])['Sumtxncount'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect])
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_d)
 aggvalue_final_Q = (aggvalue_final_Q[aggvalue_final_Q['Year']==Year_])

# ##For total value to appear in the table
 total_row_Q = pd.DataFrame({'Quater': ['Total'], 'Sumtxncount': [aggvalue_final_Q['Sumtxncount'].sum()]})
 df_with_tot_Q= pd.concat([aggvalue_final_Q, total_row_Q], ignore_index=True)
# ##to remove <n/a> values in the table 
 df_with_total_Q = df_with_tot_Q.fillna('')


##Data for Transaction type chart:

 
 aggvalue_type_final_Q = aggvalue_df.groupby(['Year','Quater','Transaction_type'])['Sumtxncount'].sum().reset_index()
 aggvalue_type_final_Q_yr=(aggvalue_type_final_Q[aggvalue_type_final_Q['Year']==Year_])
 aggvalue_type_final_Q_=(aggvalue_type_final_Q_yr[aggvalue_type_final_Q_yr['Quater']==Quarterselect])

 
####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} YEAR {Quarterselect} QUARTER Aggregated Transaction Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_Q,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumtxncount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(df_with_total_Q,height=800,width=1000) 

 
 fig = px.pie(aggvalue_type_final_Q_, names='Transaction_type', values='Sumtxncount', title=f"{Database_yr['Year'].min()} YEAR {Quarterselect} QUARTER Aggregated Transaction Count_Transaction_type", width=1000)
 st.plotly_chart(fig)
 st.dataframe(aggvalue_type_final_Q_)
 return aggvalue_final_Q

################STATE LEVEL DATA###########################################################
def Txn_count_state_yr(Year_d, State_d):
 
 Database_yr = Aggregate_value_year(Year_d)
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_d)
 
 
 aggvalue_final_st = (Database_yr[Database_yr['State']==State_d])



##Data for Transaction type chart:

 aggvalue_df = commontable_aggtxn()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','Transaction_type'])['Sumtxncount'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_d])


####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} YEAR {State_d} STATE Aggregated TRANSACTION COUNT")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumtxncount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=400,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st, names='Transaction_type', values='Sumtxncount', title=f"{Database_yr['Year'].min()} YEAR {State_d} STATE Aggregated Transaction Count_Transaction_type", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'Sumtxncount': [aggvalue_type_final_st['Sumtxncount'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st


def Txn_count_state_Q(Year_d, Quarterselect, State_d):
 
 Database_Q = Aggregate_value_Q(Quarterselect)
 Year_ = Database_Q["Year"].min()
 Year_=str(Year_d)
 
 aggvalue_final_st = (Database_Q[Database_Q['State']==State_d])
 aggvalue_final_st = (aggvalue_final_st[aggvalue_final_st['Year']==Year_])


##Data for Transaction type chart:
 aggvalue_df = commontable_aggtxn()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','Quater','Transaction_type'])['Sumtxncount'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st_=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_d])
 aggvalue_type_final_st_=(aggvalue_type_final_st_[aggvalue_type_final_st_['Quater']==Quarterselect])

 

####MAP
 
 st.subheader(f"{Database_Q['Quater'].min()} Quarter {Year_d} Year {State_d} State Aggregated Transaction Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumtxncount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st_, names='Transaction_type', values='Sumtxncount', title=f"{Database_Q['Quater'].min()} Quarter {Year_d} Year {State_d} State Aggregated Transaction Count", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'Sumtxncount': [aggvalue_type_final_st_['Sumtxncount'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st_, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st





###############************************************############################################################
########2)AGG TRANSACTION AMOUNT####################################################################################



def Aggregate_Amt_year(Year_d): 
 aggvalue_df = commontable_aggtxn()
 aggregated_df = aggvalue_df.groupby(['State','Year'])['Sumtxnamt'].sum().reset_index()
 Year_d=str(Year_d)
 aggvalue_final = (aggregated_df[aggregated_df['Year']==Year_d])
 aggvalue_final = aggvalue_final.reset_index(drop=True)
 return aggvalue_final

def Aggregate_Amt_Q(Quarterselect):
 Database_yr = Aggregate_value_year(Year_d)
 aggvalue_df = commontable_aggtxn()
 aggvalue_df_Q = aggvalue_df.groupby(['Year','State','Quater'])['Sumtxnamt'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect])
 return aggvalue_final_Q

def Year_Chart_Amt(Year_d):
 Database_yr = Aggregate_Amt_year(Year_d)

 col1, col2 = st.columns([2,1])
 with col1:

  st.subheader(f"{Database_yr['Year'].min()} Aggregated Transaction Amount")
  
  fig = px.choropleth(
      Database_yr,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumtxnamt',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
##For total value to appear in the table
  total_row = pd.DataFrame({'Year': ['Total'], 'Sumtxnamt': [Database_yr['Sumtxnamt'].sum()]})
  df_with_tot = pd.concat([Database_yr, total_row], ignore_index=True)
##to remove <n/a> values in the table 
  df_with_total = df_with_tot.fillna('')
  st.dataframe(df_with_total,height=800,width=1000)

#####Groupby Tranasction Type
 aggvalue_df = commontable_aggtxn()
 aggvalue_type_df = aggvalue_df.groupby(['Year','Transaction_type'])['Sumtxnamt'].sum().reset_index()
 Year_d=str(Year_d)
 aggvalue_type_final = (aggvalue_type_df[aggvalue_type_df['Year']==Year_d])
 aggvalue_type_final = aggvalue_type_final.reset_index(drop=True) 
 fig = px.pie(aggvalue_type_final, names='Transaction_type', values='Sumtxnamt', title=f"Overall {Database_yr['Year'].min()} Transaction Type", width=1000)
 st.plotly_chart(fig)
 total_row_ = pd.DataFrame({'Year': ['Total'], 'Sumtxnamt': [aggvalue_type_final['Sumtxnamt'].sum()]})
 df_with_tot_ = pd.concat([aggvalue_type_final, total_row_], ignore_index=True)
##to remove <n/a> values in the table 
 df_with_total_ = df_with_tot_.fillna('')
 st.dataframe(df_with_total_)



##Groupby Year
 aggregated_df = aggvalue_df.groupby('Year')['Sumtxnamt'].sum().reset_index()
 st.subheader(f"Aggregated Overall Yearwise Transaction Count w.r.t Transaction Type")
 fig = go.Figure()
 colorscale = px.colors.sequential.Plasma
##Add Bar Chart
 fig.add_trace(go.Bar(x=aggvalue_type_df['Year'], y=aggvalue_type_df['Sumtxnamt'], marker=dict(color=aggvalue_type_df['Sumtxnamt'], colorscale=colorscale, showscale=True) ))

 fig.add_trace(
    go.Scatter(x=aggregated_df['Year'], y=aggregated_df['Sumtxnamt'], mode='lines+markers', name='Line Chart', marker_color='red'))
 

 fig.update_layout(
    title='Combined Bar and Line Graph',
    xaxis_title='Year',
    yaxis_title='Sumtxnamt',
    barmode='stack')

 st.plotly_chart(fig)
 
 return df_with_total
   
#########QUARTERWISE DATA#########

def Aggregate_Amt_year_Quarter_(Quarterselect):
 
 Database_yr = Aggregate_Amt_year(Year_d)
 aggvalue_df = commontable_aggtxn()
 aggvalue_df_Q = aggvalue_df.groupby(['State','Year','Quater'])['Sumtxnamt'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect])
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_d)
 aggvalue_final_Q = (aggvalue_final_Q[aggvalue_final_Q['Year']==Year_])

# ##For total value to appear in the table
 total_row_Q = pd.DataFrame({'Quater': ['Total'], 'Sumtxnamt': [aggvalue_final_Q['Sumtxnamt'].sum()]})
 df_with_tot_Q= pd.concat([aggvalue_final_Q, total_row_Q], ignore_index=True)
# ##to remove <n/a> values in the table 
 df_with_total_Q = df_with_tot_Q.fillna('')


##Data for Transaction type chart:

 
 aggvalue_type_final_Q = aggvalue_df.groupby(['Year','Quater','Transaction_type'])['Sumtxnamt'].sum().reset_index()
 aggvalue_type_final_Q_yr=(aggvalue_type_final_Q[aggvalue_type_final_Q['Year']==Year_])
 aggvalue_type_final_Q_=(aggvalue_type_final_Q_yr[aggvalue_type_final_Q_yr['Quater']==Quarterselect])

 
####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} YEAR {Quarterselect} QUARTER Aggregated Transaction Amount")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_Q,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumtxnamt',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(df_with_total_Q,height=800,width=1000) 

 
 fig = px.pie(aggvalue_type_final_Q_, names='Transaction_type', values='Sumtxnamt', title=f"{Database_yr['Year'].min()} YEAR {Quarterselect} QUARTER Aggregated Transaction Count_Transaction_type", width=1000)
 st.plotly_chart(fig)
 total_row_Q_= pd.DataFrame({'Quater': ['Total'], 'Sumtxnamt': [aggvalue_type_final_Q_['Sumtxnamt'].sum()]})
 df_with_tot_Q_= pd.concat([aggvalue_type_final_Q_, total_row_Q_], ignore_index=True)
# ##to remove <n/a> values in the table 
 df_with_total_Q_ = df_with_tot_Q_.fillna('')
 st.dataframe(df_with_total_Q_)
 return aggvalue_final_Q

################STATE LEVEL DATA###########################################################
def Txn_Amt_state_yr(Year_d, State_d):
 
 Database_yr = Aggregate_Amt_year(Year_d)
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_d)
 
 
 aggvalue_final_st = (Database_yr[Database_yr['State']==State_d])



##Data for Transaction type chart:

 aggvalue_df = commontable_aggtxn()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','Transaction_type'])['Sumtxnamt'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_d])


####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} YEAR {State_d} STATE Aggregated Transaction Amount")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumtxnamt',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=400,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st, names='Transaction_type', values='Sumtxnamt', title=f"{Database_yr['Year'].min()} YEAR {State_d} STATE Aggregated Transaction Amount_Transaction_type", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'Sumtxnamt': [aggvalue_type_final_st['Sumtxnamt'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st

###########################################
def Txn_Amt_state_Q(Year_d, Quarterselect, State_d):
 
 Database_Q = Aggregate_Amt_Q(Quarterselect)
 Year_ = Database_Q["Year"].min()
 Year_=str(Year_d)
 
 aggvalue_final_st = (Database_Q[Database_Q['State']==State_d])
 aggvalue_final_st = (aggvalue_final_st[aggvalue_final_st['Year']==Year_])


##Data for Transaction type chart:
 aggvalue_df = commontable_aggtxn()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','Quater','Transaction_type'])['Sumtxnamt'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st_=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_d])
 aggvalue_type_final_st_=(aggvalue_type_final_st_[aggvalue_type_final_st_['Quater']==Quarterselect])

 

####MAP
 
 st.subheader(f"{Database_Q['Quater'].min()} Quarter {Year_d} Year {State_d} State Aggregated Transaction Amount")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumtxnamt',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st_, names='Transaction_type', values='Sumtxnamt', title=f"{Database_Q['Quater'].min()} Quarter {Year_d} Year {State_d} State Aggregated Transaction Amount", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'Sumtxnamt': [aggvalue_type_final_st_['Sumtxnamt'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st_, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st




###############************************************############################################################
#########3)AGG REG USER ####################################################################################



def commontable_Reguser():
 Regusercount = cursor.execute('select State, Year, Quater, Brand, sum(Registered_Users) as SumRegUsers, sum(brandusercount) as SumBrandUserCt, sum(branduserperrounded) as branduserperrounded from aggregateuser group by State, Year, Quater, Brand')
 cursor.execute(Regusercount)
 Reg_User_Count = cursor.fetchall()
 Reg_User_Count_df= pd.DataFrame(Reg_User_Count, columns=cursor.column_names)
 return Reg_User_Count_df

def Reg_User_year(Year_d): 
 aggvalue_df = commontable_Reguser()
 aggregated_df = aggvalue_df.groupby(['State','Year'])['SumRegUsers'].sum().reset_index()
 Year_d=str(Year_d)
 aggvalue_final = (aggregated_df[aggregated_df['Year']==Year_d])
 aggvalue_final = aggvalue_final.reset_index(drop=True)
 return aggvalue_final

def Reg_User_Q(Quarterselect):
 Database_yr = Reg_User_year(Year_d)
 aggvalue_df = commontable_Reguser()
 aggvalue_df_Q = aggvalue_df.groupby(['Year','State','Quater'])['SumRegUsers'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect])
 return aggvalue_final_Q


def Year_Chart_Reg_User(Year_d):
 Database_yr = Reg_User_year(Year_d)

 col1, col2 = st.columns([2,1])
 with col1:

  st.subheader(f"{Database_yr['Year'].min()} Registerd User Count")
  
  fig = px.choropleth(
      Database_yr,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='SumRegUsers',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
##For total value to appear in the table
  total_row = pd.DataFrame({'Year': ['Total'], 'SumRegUsers': [Database_yr['SumRegUsers'].sum()]})
  df_with_tot = pd.concat([Database_yr, total_row], ignore_index=True)
##to remove <n/a> values in the table 
  df_with_total = df_with_tot.fillna('')
  st.dataframe(df_with_total,height=800,width=1000)

#####Groupby Tranasction Type
 aggvalue_df = commontable_Reguser()
 aggvalue_type_df = aggvalue_df.groupby(['Year','Brand'])['SumRegUsers'].sum().reset_index()
 Year_d=str(Year_d)
 aggvalue_type_final = (aggvalue_type_df[aggvalue_type_df['Year']==Year_d])
 aggvalue_type_final = aggvalue_type_final.reset_index(drop=True) 
 fig = px.pie(aggvalue_type_final, names='Brand', values='SumRegUsers', title=f"Overall {Database_yr['Year'].min()} Brandwise Registered User Count", width=1000)
 st.plotly_chart(fig)
 total_row_ = pd.DataFrame({'Year': ['Total'], 'SumRegUsers': [aggvalue_type_final['SumRegUsers'].sum()]})
 df_with_tot_ = pd.concat([aggvalue_type_final, total_row_], ignore_index=True)
##to remove <n/a> values in the table 
 df_with_total_ = df_with_tot_.fillna('')
 st.dataframe(df_with_total_,height=800,width=1000)



##Groupby Year
 aggregated_df = aggvalue_df.groupby('Year')['SumRegUsers'].sum().reset_index()
 st.subheader(f"Aggregated Overall Yearwise Registered User Count w.r.t Brand")
 fig = go.Figure()
 colorscale = px.colors.sequential.Plasma
##Add Bar Chart
 fig.add_trace(go.Bar(x=aggvalue_type_df['Year'], y=aggvalue_type_df['SumRegUsers'], marker=dict(color=aggvalue_type_df['SumRegUsers'], colorscale=colorscale, showscale=True) ))

 fig.add_trace(
    go.Scatter(x=aggregated_df['Year'], y=aggregated_df['SumRegUsers'], mode='lines+markers', name='Line Chart', marker_color='red'))
 

 fig.update_layout(
    title='Combined Bar and Line Graph',
    xaxis_title='Year',
    yaxis_title='SumRegUsers',
    barmode='stack')

 st.plotly_chart(fig)
 
 return df_with_total
   
#########QUARTERWISE DATA#########33

def Reg_User_Year_Quarter_(Quarterselect):
 
 Database_yr = Reg_User_year(Year_d)
 aggvalue_df = commontable_Reguser()
 aggvalue_df_Q = aggvalue_df.groupby(['State','Year','Quater'])['SumRegUsers'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect])
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_d)
 aggvalue_final_Q = (aggvalue_final_Q[aggvalue_final_Q['Year']==Year_])

# ##For total value to appear in the table
 total_row_Q = pd.DataFrame({'Quater': ['Total'], 'SumRegUsers': [aggvalue_final_Q['SumRegUsers'].sum()]})
 df_with_tot_Q= pd.concat([aggvalue_final_Q, total_row_Q], ignore_index=True)
# ##to remove <n/a> values in the table 
 df_with_total_Q = df_with_tot_Q.fillna('')


##Data for Transaction type chart:

 
 aggvalue_type_final_Q = aggvalue_df.groupby(['Year','Quater','Brand'])['SumRegUsers'].sum().reset_index()
 aggvalue_type_final_Q_yr=(aggvalue_type_final_Q[aggvalue_type_final_Q['Year']==Year_])
 aggvalue_type_final_Q_=(aggvalue_type_final_Q_yr[aggvalue_type_final_Q_yr['Quater']==Quarterselect])

 
####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} YEAR {Quarterselect} QUARTER Registered User Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_Q,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='SumRegUsers',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(df_with_total_Q,height=800,width=1000) 

 
 fig = px.pie(aggvalue_type_final_Q_, names='Brand', values='SumRegUsers', title=f"{Database_yr['Year'].min()} YEAR {Quarterselect} QUARTER Registered User Count_Brand", width=1000)
 st.plotly_chart(fig)
 total_row_Q_= pd.DataFrame({'Quater': ['Total'], 'SumRegUsers': [aggvalue_type_final_Q_['SumRegUsers'].sum()]})
 df_with_tot_Q_= pd.concat([aggvalue_type_final_Q_, total_row_Q_], ignore_index=True)
# ##to remove <n/a> values in the table 
 df_with_total_Q_ = df_with_tot_Q_.fillna('')
 st.dataframe(df_with_total_Q_)
 return aggvalue_final_Q

################STATE LEVEL DATA###########################################################
def Reg_User_State_Yr(Year_d, State_d):
 
 Database_yr = Reg_User_year(Year_d)
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_d)
 
 
 aggvalue_final_st = (Database_yr[Database_yr['State']==State_d])



##Data for Transaction type chart:

 aggvalue_df = commontable_Reguser()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','Brand'])['SumRegUsers'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_d])


####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} YEAR {State_d} STATE Registered User Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='SumRegUsers',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=400,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st, names='Brand', values='SumRegUsers', title=f"{Database_yr['Year'].min()} YEAR {State_d} STATE Registered User Count", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'SumRegUsers': [aggvalue_type_final_st['SumRegUsers'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st


def Reg_User_State_Q(Year_d, Quarterselect, State_d):
 
 Database_Q = Reg_User_Q(Quarterselect)
 Year_ = Database_Q["Year"].min()
 Year_=str(Year_d)
 
 aggvalue_final_st = (Database_Q[Database_Q['State']==State_d])
 aggvalue_final_st = (aggvalue_final_st[aggvalue_final_st['Year']==Year_])


##Data for Transaction type chart:
 aggvalue_df = commontable_Reguser()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','Quater','Brand'])['SumRegUsers'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st_=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_d])
 aggvalue_type_final_st_=(aggvalue_type_final_st_[aggvalue_type_final_st_['Quater']==Quarterselect])

 

####MAP
 
 st.subheader(f"{Database_Q['Quater'].min()} Quarter {Year_d} Year {State_d} State Registered User Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='SumRegUsers',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st_, names='Brand', values='SumRegUsers', title=f"{Database_Q['Quater'].min()} Quarter {Year_d} Year {State_d} State Registered User Count", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'SumRegUsers': [aggvalue_type_final_st_['SumRegUsers'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st_, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st

############4)REG BRAND USER COUNT###############################




def Reg_Brand_User_year(Year_d): 
 aggvalue_df = commontable_Reguser()
 aggregated_df = aggvalue_df.groupby(['State','Year'])['SumBrandUserCt'].sum().reset_index()
 Year_d=str(Year_d)
 aggvalue_final = (aggregated_df[aggregated_df['Year']==Year_d])
 aggvalue_final = aggvalue_final.reset_index(drop=True)
 return aggvalue_final

def Reg_Brand_User_Q(Quarterselect):
 Database_yr = Reg_Brand_User_year(Year_d)
 aggvalue_df = commontable_Reguser()
 aggvalue_df_Q = aggvalue_df.groupby(['Year','State','Quater'])['SumBrandUserCt'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect])
 return aggvalue_final_Q


def Year_Chart_Reg_Brand_User(Year_d):
 Database_yr = Reg_Brand_User_year(Year_d)

 col1, col2 = st.columns([2,1])
 with col1:

  st.subheader(f"{Database_yr['Year'].min()} Registerd Brand User Count")
  
  fig = px.choropleth(
      Database_yr,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='SumBrandUserCt',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})

#fig= fig.show()
  st.plotly_chart(fig)

 with col2:
##For total value to appear in the table
  total_row = pd.DataFrame({'Year': ['Total'], 'SumBrandUserCt': [Database_yr['SumBrandUserCt'].sum()]})
  df_with_tot = pd.concat([Database_yr, total_row], ignore_index=True)
##to remove <n/a> values in the table 
  df_with_total = df_with_tot.fillna('')
  st.dataframe(df_with_total,height=800,width=1000)

#####Groupby Tranasction Type
 aggvalue_df = commontable_Reguser()
 aggvalue_type_df = aggvalue_df.groupby(['Year','Brand'])['SumBrandUserCt'].sum().reset_index()
 Year_d=str(Year_d)
 aggvalue_type_final = (aggvalue_type_df[aggvalue_type_df['Year']==Year_d])
 aggvalue_type_final = aggvalue_type_final.reset_index(drop=True) 
 fig = px.pie(aggvalue_type_final, names='Brand', values='SumBrandUserCt', title=f"Overall {Database_yr['Year'].min()} Brandwise_Brand User Count", width=1000)
 st.plotly_chart(fig)
 total_row_ = pd.DataFrame({'Year': ['Total'], 'SumBrandUserCt': [aggvalue_type_final['SumBrandUserCt'].sum()]})
 df_with_tot_ = pd.concat([aggvalue_type_final, total_row_], ignore_index=True)
##to remove <n/a> values in the table 
 df_with_total_ = df_with_tot_.fillna('')
 st.dataframe(df_with_total_,height=800,width=1000)



##Groupby Year
 aggregated_df = aggvalue_df.groupby('Year')['SumBrandUserCt'].sum().reset_index()
 st.subheader(f"Aggregated Overall Yearwise Registered Brand User Count w.r.t Brand")
 fig = go.Figure()
 colorscale = px.colors.sequential.Plasma
##Add Bar Chart
 fig.add_trace(go.Bar(x=aggvalue_type_df['Year'], y=aggvalue_type_df['SumBrandUserCt'], marker=dict(color=aggvalue_type_df['SumBrandUserCt'], colorscale=colorscale, showscale=True) ))

 fig.add_trace(
    go.Scatter(x=aggregated_df['Year'], y=aggregated_df['SumBrandUserCt'], mode='lines+markers', name='Line Chart', marker_color='red'))
 

 fig.update_layout(
    title='Combined Bar and Line Graph',
    xaxis_title='Year',
    yaxis_title='SumBrandUserCt',
    barmode='stack')

 st.plotly_chart(fig)
 
 return df_with_total
   
#########QUARTERWISE DATA#########33



def Reg_Brand_User_Year_Quarter_(Quarterselect):
 
 Database_yr = Reg_Brand_User_year(Year_d)
 aggvalue_df = commontable_Reguser()
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_d)
 aggvalue_df_Q = aggvalue_df.groupby(['State','Year','Quater'])['SumBrandUserCt'].sum().reset_index()
 aggvalue_final_Q_y = (aggvalue_df_Q[aggvalue_df_Q['Year']==Year_])
 aggvalue_final_Q = (aggvalue_final_Q_y[aggvalue_final_Q_y['Quater']==Quarterselect])


# ##For total value to appear in the table
 total_row_Q = pd.DataFrame({'Quater': ['Total'], 'SumBrandUserCt': [aggvalue_final_Q['SumBrandUserCt'].sum()]})
 df_with_tot_Q= pd.concat([aggvalue_final_Q, total_row_Q], ignore_index=True)
# ##to remove <n/a> values in the table 
 df_with_total_Q = df_with_tot_Q.fillna('')


##Data for Transaction type chart:

 
 aggvalue_type_final_Q = aggvalue_df.groupby(['Year','Quater','Brand'])['SumBrandUserCt'].sum().reset_index()
 aggvalue_type_final_Q_yr=(aggvalue_type_final_Q[aggvalue_type_final_Q['Year']==Year_])
 aggvalue_type_final_Q_=(aggvalue_type_final_Q_yr[aggvalue_type_final_Q_yr['Quater']==Quarterselect])

 
####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} YEAR {Quarterselect} QUARTER Registered Brand User Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_Q,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='SumBrandUserCt',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(df_with_total_Q,height=800,width=1000) 

 
 fig = px.pie(aggvalue_type_final_Q_, names='Brand', values='SumBrandUserCt', title=f"{Database_yr['Year'].min()} YEAR {Quarterselect} QUARTER Registered Brand User Count_Brand", width=1000)
 st.plotly_chart(fig)
 total_row_Q_= pd.DataFrame({'Quater': ['Total'], 'SumBrandUserCt': [aggvalue_type_final_Q_['SumBrandUserCt'].sum()]})
 df_with_tot_Q_= pd.concat([aggvalue_type_final_Q_, total_row_Q_], ignore_index=True)
# ##to remove <n/a> values in the table 
 df_with_total_Q_ = df_with_tot_Q_.fillna('')
 st.dataframe(df_with_total_Q_)
 return aggvalue_final_Q

################STATE LEVEL DATA###########################################################
def Reg_Brand_User_State_Yr(Year_d, State_d):
 
 Database_yr = Reg_Brand_User_year(Year_d)
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_d)
 
 
 aggvalue_final_st = (Database_yr[Database_yr['State']==State_d])



##Data for Transaction type chart:

 aggvalue_df = commontable_Reguser()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','Brand'])['SumBrandUserCt'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_d])


####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} YEAR {State_d} STATE Registered Brand User Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='SumBrandUserCt',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=400,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st, names='Brand', values='SumBrandUserCt', title=f"{Database_yr['Year'].min()} YEAR {State_d} STATE Registered Brand User Count", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'SumBrandUserCt': [aggvalue_type_final_st['SumBrandUserCt'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st



def Reg_Brand_User_State_Q(Year_d, Quarterselect, State_d):
 
 Database_Q = Reg_Brand_User_Q(Quarterselect)

 Year_ = Database_Q["Year"].min()
 Year_=str(Year_d)
 
 aggvalue_final_st = (Database_Q[Database_Q['State']==State_d])
 aggvalue_final_st = (aggvalue_final_st[aggvalue_final_st['Year']==Year_])


##Data for Transaction type chart:
 aggvalue_df = commontable_Reguser()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','Quater','Brand'])['SumBrandUserCt'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st_=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_d])
 aggvalue_type_final_st_=(aggvalue_type_final_st_[aggvalue_type_final_st_['Quater']==Quarterselect])

 

####MAP
 
 st.subheader(f"{Database_Q['Quater'].min()} Quarter {Year_d} Year {State_d} State Registered Brand User Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='SumBrandUserCt',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st_, names='Brand', values='SumBrandUserCt', title=f"{Database_Q['Quater'].min()} Quarter {Year_d} Year {State_d} State Registered Brand User Count", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'SumBrandUserCt': [aggvalue_type_final_st_['SumBrandUserCt'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st_, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st



###################5)BRAND USER PERCENTAGE###############################





def Brand_User_year_Per(Year_d): 
 aggvalue_df = commontable_Reguser()
 aggregated_df = aggvalue_df.groupby(['State','Year','Brand'])[['SumRegUsers','SumBrandUserCt','branduserperrounded']].sum().reset_index()
 Year_d=str(Year_d)
 aggvalue_final = (aggregated_df[aggregated_df['Year']==Year_d])
 aggvalue_final = aggvalue_final.reset_index(drop=True)
 return aggvalue_final

def Brand_User_Q_Per(Quarterselect):
 Database_yr = Brand_User_year_Per(Year_d)
 aggvalue_df = commontable_Reguser()
 aggvalue_df_Q = aggvalue_df.groupby(['Year','State','Quater'])['SumRegUsers','SumBrandUserCt','branduserperrounded'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect])
 return aggvalue_final_Q


def Year_Chart_Reg_Brand_User_Per(Year_d,Brand_d):
 Database_yr = Brand_User_year_Per(Year_d)

 Database_yr_1 = Database_yr.groupby(['State','Year','Brand'])[['branduserperrounded']].sum().reset_index()
 Database_yr_2 = (Database_yr_1[Database_yr_1['Brand']==Brand_d])
 Database_yr_table = (Database_yr[Database_yr['Brand']==Brand_d])

 col1, col2 = st.columns([2,1])
 with col1:

  st.subheader(f"{Database_yr['Year'].min()} Registerd Brand User Percentage")
  
  fig = px.choropleth(
      Database_yr_2,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='branduserperrounded',
      color_continuous_scale='picnic_r',
      
      height=800,
      width=1300
   )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  total_row = pd.DataFrame({'Year': ['Total'], 'SumRegUsers': [Database_yr_table['SumRegUsers'].sum()],'SumBrandUserCt': [Database_yr_table['SumBrandUserCt'].sum()], 'branduserperrounded': [Database_yr_table['branduserperrounded'].sum()]})
  df_with_tot = pd.concat([Database_yr_table, total_row], ignore_index=True)
##to remove <n/a> values in the table 
  df_with_total = df_with_tot.fillna('')
  st.dataframe(df_with_total,height=300,width=1000)


#####Groupby Brand
 aggvalue_df = commontable_Reguser()
 aggvalue_type_df = aggvalue_df.groupby(['Year','Brand'])[['SumRegUsers','SumBrandUserCt','branduserperrounded']].sum().reset_index()
 Year_d=str(Year_d)
 aggvalue_type_final = (aggvalue_type_df[aggvalue_type_df['Year']==Year_d])
 aggvalue_type_final = aggvalue_type_final.reset_index(drop=True) 

 fig = px.pie(aggvalue_type_final, names='Brand', values='branduserperrounded', title=f"Overall {Database_yr['Year'].min()} Brandwise_Brand User Count", width=1000)
 st.plotly_chart(fig)
 total_row_ = pd.DataFrame({'Year': ['Total'], 'SumRegUsers': [Database_yr['SumRegUsers'].sum()],'SumBrandUserCt': [Database_yr['SumBrandUserCt'].sum()], 'branduserperrounded': [Database_yr['branduserperrounded'].sum()]})
 df_with_tot_ = pd.concat([aggvalue_type_final, total_row_], ignore_index=True)
##to remove <n/a> values in the table 
 df_with_total_ = df_with_tot_.fillna('')
 st.dataframe(df_with_total_,height=800,width=1000)

##Groupby Year
 aggregated_df = aggvalue_df.groupby('Year','Brand')['branduserperrounded'].sum().reset_index()
 st.subheader(f"Aggregated Overall Yearwise Registered Brand User Percentage w.r.t Brand")
 fig = go.Figure()
 colorscale = px.colors.sequential.Plasma
##Add Bar Chart
 fig.add_trace(go.Bar(x=aggregated_df['Year'], y=aggregated_df['branduserperrounded'], marker=dict(color=aggregated_df['branduserperrounded'], colorscale=colorscale, showscale=True) ))

 fig.add_trace(
    go.Scatter(x=aggregated_df['Year'], y=aggregated_df['branduserperrounded'], mode='lines+markers', name='Line Chart', marker_color='red'))
 

 fig.update_layout(
    title='Combined Bar and Line Graph',
    xaxis_title='Year',
    yaxis_title='branduserperrounded',
    barmode='stack')

 st.plotly_chart(fig)


#################################################################################################333
####################6) MAP TRANSACTION COUNT##########

def commontable_maptxn():
 aggtxnamtcount = cursor.execute('select State, Year, Quater, MapName, sum(Maptxn_count) as Summaptxncount, sum(Maptxn_amt_rounded) as Summaptxnamt from maptxn group by State, Year, Quater, MapName')
 cursor.execute(aggtxnamtcount)
 aggtxn_amt_count = cursor.fetchall()
 aggtxn_amt_count_df= pd.DataFrame(aggtxn_amt_count, columns=cursor.column_names)
 return aggtxn_amt_count_df




def maptxn_count_year(Year_m): 
 aggvalue_df = commontable_maptxn()
 aggregated_df = aggvalue_df.groupby(['State','Year'])['Summaptxncount'].sum().reset_index()
 Year_m=str(Year_m)
 aggvalue_final = (aggregated_df[aggregated_df['Year']==Year_m])
 aggvalue_final = aggvalue_final.reset_index(drop=True)
 return aggvalue_final

def maptxn_count_Q(Quarterselect_m):
 Database_yr = maptxn_count_year(Year_m)
 aggvalue_df = commontable_maptxn()
 aggvalue_df_Q = aggvalue_df.groupby(['Year','State','Quater'])['Summaptxncount'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect_m])
 return aggvalue_final_Q

def Year_Chart_Map_Count(Year_m):
 Database_yr = maptxn_count_year(Year_m)

 col1, col2 = st.columns([2,1])
 with col1:

  st.subheader(f"{Database_yr['Year'].min()} Aggregated Map Transaction Count")
  
  fig = px.choropleth(
      Database_yr,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Summaptxncount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
##For total value to appear in the table
  total_row = pd.DataFrame({'Year': ['Total'], 'Summaptxncount': [Database_yr['Summaptxncount'].sum()]})
  df_with_tot = pd.concat([Database_yr, total_row], ignore_index=True)
##to remove <n/a> values in the table 
  df_with_total = df_with_tot.fillna('')
  st.dataframe(df_with_total,height=800,width=1000)

##Groupby Year
 aggvalue_df = commontable_maptxn()
 aggregated_df = aggvalue_df.groupby('Year')['Summaptxncount'].sum().reset_index()
 st.subheader(f"Aggregated Overall Yearwise Transaction Count")
 fig = go.Figure()
 colorscale = px.colors.sequential.Plasma
##Add Bar Chart
 fig.add_trace(go.Bar(x=aggregated_df['Year'], y=aggregated_df['Summaptxncount'], marker=dict(color=aggregated_df['Summaptxncount'], colorscale=colorscale, showscale=True) ))
 st.plotly_chart(fig)

 st.subheader(f"Aggregated {Database_yr['Year'].min()} YEAR Quarterwise Map Transaction Count")

 aggregated_df_r = aggvalue_df.groupby(['Year','Quater'])['Summaptxncount'].sum().reset_index()
 Year_m=str(Year_m)
 aggvalue_Q = (aggregated_df_r[aggregated_df_r['Year']==Year_m])
 fig = px.pie(aggvalue_Q, names='Quater', values='Summaptxncount', title=f"{Database_yr['Year'].min()} Year Quarterwise Aggregated Map Transaction Count", width=1000)
 st.plotly_chart(fig)

 st.subheader(f"{Database_yr['Year'].min()} Aggregated Map State and District Transaction Count")
 
 aggvalue_type_df = aggvalue_df.groupby(['Year','State','MapName'])['Summaptxncount'].sum().reset_index()
 Year_m=str(Year_m)
 aggvalue_type_final = (aggvalue_type_df[aggvalue_type_df['Year']==Year_m])
 aggvalue_type_final = aggvalue_type_final.reset_index(drop=True) 
 st.dataframe(aggvalue_type_final)
 
 return df_with_total
   
#########QUARTERWISE DATA#########



def Map_txn_year_Quarter_(Quarterselect_m):
 
 Database_yr = maptxn_count_year(Year_m)
 aggvalue_df = commontable_maptxn()
 aggvalue_df_Q = aggvalue_df.groupby(['State','Year','Quater'])['Summaptxncount'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect_m])
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_m)
 aggvalue_final_Q = (aggvalue_final_Q[aggvalue_final_Q['Year']==Year_])

# ##For total value to appear in the table
 total_row_Q = pd.DataFrame({'Quater': ['Total'], 'Summaptxncount': [aggvalue_final_Q['Summaptxncount'].sum()]})
 df_with_tot_Q= pd.concat([aggvalue_final_Q, total_row_Q], ignore_index=True)
# ##to remove <n/a> values in the table 
 df_with_total_Q = df_with_tot_Q.fillna('')


##Data for Transaction type chart:

 
 aggvalue_type_final_Q = aggvalue_df.groupby(['Year','Quater','MapName'])['Summaptxncount'].sum().reset_index()
 aggvalue_type_final_Q_yr=(aggvalue_type_final_Q[aggvalue_type_final_Q['Year']==Year_])
 aggvalue_type_final_Q_=(aggvalue_type_final_Q_yr[aggvalue_type_final_Q_yr['Quater']==Quarterselect_m])

 
####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} YEAR {Quarterselect_m} QUARTER Aggregated Map Transaction Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_Q,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Summaptxncount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(df_with_total_Q,height=800,width=1000) 

 st.subheader(f"{Database_yr['Year'].min()} Year {Quarterselect_m} Quarter Aggregated Map State and District Transaction Count")
 st.dataframe(aggvalue_type_final_Q_)
 return aggvalue_final_Q

################STATE LEVEL DATA###########################################################
def Map_Txn_count_state_yr(Year_m, State_m):
 
 Database_yr = maptxn_count_year(Year_m)
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_m)
 
 
 aggvalue_final_st = (Database_yr[Database_yr['State']==State_m])



##Data for Transaction type chart:

 aggvalue_df = commontable_maptxn()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','MapName'])['Summaptxncount'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_m])


####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} Year {State_m} State Aggregated Map Transaction Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Summaptxncount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=400,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st, names='MapName', values='Summaptxncount', title=f"{Database_yr['Year'].min()} YEAR {State_m} STATE Aggregated Transaction Count_Transaction_type", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'Summaptxncount': [aggvalue_type_final_st['Summaptxncount'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st



def Map_Txn_count_state_Q(Year_m, Quarterselect_m, State_m):
 
 Database_Q = maptxn_count_Q(Quarterselect_m)
 Year_ = Database_Q["Year"].min()
 Year_=str(Year_m)
 
 aggvalue_final_st = (Database_Q[Database_Q['State']==State_m])
 aggvalue_final_st = (aggvalue_final_st[aggvalue_final_st['Year']==Year_])


##Data for Transaction type chart:
 aggvalue_df = commontable_maptxn()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','Quater','MapName'])['Summaptxncount'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st_=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_m])
 aggvalue_type_final_st_=(aggvalue_type_final_st_[aggvalue_type_final_st_['Quater']==Quarterselect_m])

 

####MAP
 
 st.subheader(f"{Database_Q['Quater'].min()} Quarter {Year_m} Year {State_m} State Aggregated Map Transaction Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Summaptxncount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=500,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st_, names='MapName', values='Summaptxncount', title=f"{Database_Q['Quater'].min()} Quarter {Year_m} Year {State_m} State Aggregated Transaction Count", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'Summaptxncount': [aggvalue_type_final_st_['Summaptxncount'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st_, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st



##################7)MAP TRANSACTION AMOUNT#####################################33



def Maptxn_Amt_year(Year_m): 
 aggvalue_df = commontable_maptxn()
 aggregated_df = aggvalue_df.groupby(['State','Year'])['Summaptxnamt'].sum().reset_index()
 Year_m=str(Year_m)
 aggvalue_final = (aggregated_df[aggregated_df['Year']==Year_m])
 aggvalue_final = aggvalue_final.reset_index(drop=True)
 return aggvalue_final

def Maptxn_Amt_Q(Quarterselect):
 Database_yr = Maptxn_Amt_year(Year_m)
 aggvalue_df = commontable_maptxn()
 aggvalue_df_Q = aggvalue_df.groupby(['Year','State','Quater'])['Summaptxnamt'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect_m])
 return aggvalue_final_Q

def Year_Chart_Map_Amt(Year_m):
 Database_yr = Maptxn_Amt_year(Year_m)

 col1, col2 = st.columns([2,1])
 with col1:

  st.subheader(f"{Database_yr['Year'].min()} Aggregated Map Transaction Amount")
  
  fig = px.choropleth(
      Database_yr,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Summaptxnamt',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
##For total value to appear in the table
  total_row = pd.DataFrame({'Year': ['Total'], 'Summaptxnamt': [Database_yr['Summaptxnamt'].sum()]})
  df_with_tot = pd.concat([Database_yr, total_row], ignore_index=True)
##to remove <n/a> values in the table 
  df_with_total = df_with_tot.fillna('')
  st.dataframe(df_with_total,height=800,width=1000)
 
#####Groupby Tranasction Type
 aggvalue_df = commontable_maptxn()
 aggregated_df = aggvalue_df.groupby('Year')['Summaptxnamt'].sum().reset_index()
 st.subheader(f"Aggregated Overall Yearwise Map Transaction Amount")
 fig = go.Figure()
 colorscale = px.colors.sequential.Plasma
##Add Bar Chart
 fig.add_trace(go.Bar(x=aggregated_df['Year'], y=aggregated_df['Summaptxnamt'], marker=dict(color=aggregated_df['Summaptxnamt'], colorscale=colorscale, showscale=True) ))
 st.plotly_chart(fig)
 
 st.subheader(f"Aggregated {Database_yr['Year'].min()} YEAR Quarterwise Map Transaction Amount")

 aggregated_df_r = aggvalue_df.groupby(['Year','Quater'])['Summaptxnamt'].sum().reset_index()
 Year_m=str(Year_m)
 aggvalue_Q = (aggregated_df_r[aggregated_df_r['Year']==Year_m])
 fig = px.pie(aggvalue_Q, names='Quater', values='Summaptxnamt', title=f"{Database_yr['Year'].min()} Year Quarterwise Aggregated Map Transaction Value", width=1000)
 st.plotly_chart(fig)

 st.subheader(f"{Database_yr['Year'].min()} Aggregated Map State and District Transaction Count")
 
 aggvalue_type_df = aggvalue_df.groupby(['Year','State','MapName'])['Summaptxnamt'].sum().reset_index()
 Year_m=str(Year_m)
 aggvalue_type_final = (aggvalue_type_df[aggvalue_type_df['Year']==Year_m])
 aggvalue_type_final = aggvalue_type_final.reset_index(drop=True) 
 st.dataframe(aggvalue_type_final)
 return df_with_total
   
#########QUARTERWISE DATA#########33



def Map_txn_Amt_year_Quarter_(Quarterselect_m):
 
 Database_yr = Aggregate_Amt_year(Year_m)
 aggvalue_df = commontable_maptxn()
 aggvalue_df_Q = aggvalue_df.groupby(['State','Year','Quater'])['Summaptxnamt'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect_m])
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_m)
 aggvalue_final_Q = (aggvalue_final_Q[aggvalue_final_Q['Year']==Year_])

# ##For total value to appear in the table
 total_row_Q = pd.DataFrame({'Quater': ['Total'], 'Summaptxnamt': [aggvalue_final_Q['Summaptxnamt'].sum()]})
 df_with_tot_Q= pd.concat([aggvalue_final_Q, total_row_Q], ignore_index=True)
# ##to remove <n/a> values in the table 
 df_with_total_Q = df_with_tot_Q.fillna('')


##Data for Transaction type chart:

 
 aggvalue_type_final_Q = aggvalue_df.groupby(['Year','Quater','MapName'])['Summaptxnamt'].sum().reset_index()
 aggvalue_type_final_Q_yr=(aggvalue_type_final_Q[aggvalue_type_final_Q['Year']==Year_])
 aggvalue_type_final_Q_=(aggvalue_type_final_Q_yr[aggvalue_type_final_Q_yr['Quater']==Quarterselect_m])

 
####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} Year {Quarterselect_m} Quarter Aggregated Map Transaction Amount")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_Q,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Summaptxnamt',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(df_with_total_Q,height=800,width=1000) 

  st.subheader(f"{Database_yr['Year'].min()} YEAR {Quarterselect_m} QUARTER Aggregated Map State and District Transaction Count")
 total_row_Q_= pd.DataFrame({'Quater': ['Total'], 'Summaptxnamt': [aggvalue_type_final_Q_['Summaptxnamt'].sum()]})
 df_with_tot_Q_= pd.concat([aggvalue_type_final_Q_, total_row_Q_], ignore_index=True)
# ##to remove <n/a> values in the table 
 df_with_total_Q_ = df_with_tot_Q_.fillna('')
 st.dataframe(df_with_total_Q_)
 return aggvalue_final_Q

################STATE LEVEL DATA###########################################################
def Map_Txn_Amt_state_yr(Year_m, State_m):
 
 Database_yr = Maptxn_Amt_year(Year_m)

 Year_ = Database_yr["Year"].min()
 Year_=str(Year_m)
 
 
 aggvalue_final_st = (Database_yr[Database_yr['State']==State_m])



##Data for Transaction type chart:

 aggvalue_df = commontable_maptxn()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','MapName'])['Summaptxnamt'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_m])

####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} Year {State_m} State Aggregated Map Transaction Amount")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Summaptxnamt',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=400,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st, names='MapName', values='Summaptxnamt', title=f"{Database_yr['Year'].min()} YEAR {State_m} STATE Aggregated Transaction Amount_Transaction_type", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'Summaptxnamt': [aggvalue_type_final_st['Summaptxnamt'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st


def Map_Txn_Amt_state_Q(Year_m, Quarterselect_m, State_m):
 
 Database_Q = Maptxn_Amt_Q(Quarterselect_m)

 Year_ = Database_Q["Year"].min()
 Year_=str(Year_m)
 
 aggvalue_final_st = (Database_Q[Database_Q['State']==State_m])
 aggvalue_final_st = (aggvalue_final_st[aggvalue_final_st['Year']==Year_])


##Data for Transaction type chart:
 aggvalue_df = commontable_maptxn()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','Quater','MapName'])['Summaptxnamt'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st_=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_m])
 aggvalue_type_final_st_=(aggvalue_type_final_st_[aggvalue_type_final_st_['Quater']==Quarterselect_m])

 

####MAP
 
 st.subheader(f"{Database_Q['Quater'].min()} Quarter {Year_m} Year {State_m} State Aggregated Map Transaction Amount")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Summaptxnamt',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st_, names='MapName', values='Summaptxnamt', title=f"{Database_Q['Quater'].min()} Quarter {Year_m} Year {State_m} State Aggregated Transaction Amount", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'Summaptxnamt': [aggvalue_type_final_st_['Summaptxnamt'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st_, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st


##############
#######################8)MAP USER COUNT################################################


def commontable_mapuser():
 aggtxnamtcount = cursor.execute('select State, Year, Quater, MapName, sum(Mapuserscount) as SumMapuserscount from mapusercount group by State, Year, Quater, MapName')
 cursor.execute(aggtxnamtcount)
 aggtxn_amt_count = cursor.fetchall()
 aggtxn_amt_count_df= pd.DataFrame(aggtxn_amt_count, columns=cursor.column_names)
 return aggtxn_amt_count_df




def mapuser_count_year(Year_m): 
 aggvalue_df = commontable_mapuser()
 aggregated_df = aggvalue_df.groupby(['State','Year'])['SumMapuserscount'].sum().reset_index()
 Year_m=str(Year_m)
 aggvalue_final = (aggregated_df[aggregated_df['Year']==Year_m])
 aggvalue_final = aggvalue_final.reset_index(drop=True)
 return aggvalue_final

def mapuser_count_Q(Quarterselect_m):
 Database_yr = mapuser_count_year(Year_m)
 aggvalue_df = commontable_mapuser()
 aggvalue_df_Q = aggvalue_df.groupby(['Year','State','Quater'])['SumMapuserscount'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect_m])
 return aggvalue_final_Q

def Year_Chart_Map_User_Count(Year_m):
 Database_yr = mapuser_count_year(Year_m)

 col1, col2 = st.columns([2,1])
 with col1:

  st.subheader(f"{Database_yr['Year'].min()} Aggregated Map User Count")
  
  fig = px.choropleth(
      Database_yr,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='SumMapuserscount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
##For total value to appear in the table
  total_row = pd.DataFrame({'Year': ['Total'], 'SumMapuserscount': [Database_yr['SumMapuserscount'].sum()]})
  df_with_tot = pd.concat([Database_yr, total_row], ignore_index=True)
##to remove <n/a> values in the table 
  df_with_total = df_with_tot.fillna('')
  st.dataframe(df_with_total,height=800,width=1000)


##Groupby Year
 aggvalue_df = commontable_mapuser()
 aggregated_df = aggvalue_df.groupby('Year')['SumMapuserscount'].sum().reset_index()
 st.subheader(f"Aggregated Overall Yearwise Map User Count")
 fig = go.Figure()
 colorscale = px.colors.sequential.Plasma
##Add Bar Chart
 fig.add_trace(go.Bar(x=aggregated_df['Year'], y=aggregated_df['SumMapuserscount'], marker=dict(color=aggregated_df['SumMapuserscount'], colorscale=colorscale, showscale=True) ))
 st.plotly_chart(fig)

 st.subheader(f"Aggregated {Database_yr['Year'].min()} YEAR Quarterwise Map User Count")

 aggregated_df_r = aggvalue_df.groupby(['Year','Quater'])['SumMapuserscount'].sum().reset_index()
 Year_m=str(Year_m)
 aggvalue_Q = (aggregated_df_r[aggregated_df_r['Year']==Year_m])
 fig = px.pie(aggvalue_Q, names='Quater', values='SumMapuserscount', title=f"{Database_yr['Year'].min()} Year Quarterwise Aggregated Map User Count", width=1000)
 st.plotly_chart(fig)

 st.subheader(f"{Database_yr['Year'].min()} Aggregated Map State and District User Count")
 
 aggvalue_type_df = aggvalue_df.groupby(['Year','State','MapName'])['SumMapuserscount'].sum().reset_index()
 Year_m=str(Year_m)
 aggvalue_type_final = (aggvalue_type_df[aggvalue_type_df['Year']==Year_m])
 aggvalue_type_final = aggvalue_type_final.reset_index(drop=True) 

 st.dataframe(aggvalue_type_final)
 

 
 return df_with_total
   
#########QUARTERWISE DATA#########



def Map_User_Year_Quarter_(Quarterselect_m):
 
 Database_yr = mapuser_count_year(Year_m)
 aggvalue_df = commontable_mapuser()
 aggvalue_df_Q = aggvalue_df.groupby(['State','Year','Quater'])['SumMapuserscount'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect_m])
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_m)
 aggvalue_final_Q = (aggvalue_final_Q[aggvalue_final_Q['Year']==Year_])

# ##For total value to appear in the table
 total_row_Q = pd.DataFrame({'Quater': ['Total'], 'SumMapuserscount': [aggvalue_final_Q['SumMapuserscount'].sum()]})
 df_with_tot_Q= pd.concat([aggvalue_final_Q, total_row_Q], ignore_index=True)
# ##to remove <n/a> values in the table 
 df_with_total_Q = df_with_tot_Q.fillna('')


##Data for Transaction type chart:

 
 aggvalue_type_final_Q = aggvalue_df.groupby(['Year','Quater','MapName'])['SumMapuserscount'].sum().reset_index()
 aggvalue_type_final_Q_yr=(aggvalue_type_final_Q[aggvalue_type_final_Q['Year']==Year_])
 aggvalue_type_final_Q_=(aggvalue_type_final_Q_yr[aggvalue_type_final_Q_yr['Quater']==Quarterselect_m])
 
####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} YEAR {Quarterselect_m} QUARTER Aggregated Map User Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_Q,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='SumMapuserscount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(df_with_total_Q,height=800,width=1000) 

 st.subheader(f"{Database_yr['Year'].min()} Year {Quarterselect_m} Quarter Aggregated Map State and District User Count")
 st.dataframe(aggvalue_type_final_Q_)
 return aggvalue_final_Q

################STATE LEVEL DATA###########################################################
def Map_User_count_state_yr(Year_m, State_m):
 
 Database_yr = mapuser_count_year(Year_m)
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_m)
 
 
 aggvalue_final_st = (Database_yr[Database_yr['State']==State_m])



##Data for Transaction type chart:

 aggvalue_df = commontable_mapuser()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','MapName'])['SumMapuserscount'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_m])


####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} Year {State_m} State Aggregated Map User Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='SumMapuserscount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=400,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st, names='MapName', values='SumMapuserscount', title=f"{Database_yr['Year'].min()} YEAR {State_m} STATE Aggregated User Count", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'SumMapuserscount': [aggvalue_type_final_st['SumMapuserscount'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st



def Map_User_count_state_Q(Year_m, Quarterselect_m, State_m):
 
 Database_Q = mapuser_count_Q(Quarterselect_m)
 Year_ = Database_Q["Year"].min()
 Year_=str(Year_m)
 
 aggvalue_final_st = (Database_Q[Database_Q['State']==State_m])
 aggvalue_final_st = (aggvalue_final_st[aggvalue_final_st['Year']==Year_])


##Data for Transaction type chart:
 aggvalue_df = commontable_mapuser()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','Quater','MapName'])['SumMapuserscount'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st_=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_m])
 aggvalue_type_final_st_=(aggvalue_type_final_st_[aggvalue_type_final_st_['Quater']==Quarterselect_m])

###MAP
 
 st.subheader(f"{Database_Q['Quater'].min()} Quarter {Year_m} Year {State_m} State Aggregated Map User Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='SumMapuserscount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=500,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st_, names='MapName', values='SumMapuserscount', title=f"{Database_Q['Quater'].min()} Quarter {Year_m} Year {State_m} State Aggregated User Count", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'SumMapuserscount': [aggvalue_type_final_st_['SumMapuserscount'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st_, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st


######################9)DIST TOP TXN USER COUNT#################

def commontable_toptxn():
 aggtxnamtcount = cursor.execute('select State, Year, Quater, District_Name, Pincode, sum(Dist_usercount) as Sumdistusercount, sum(Dist_txn_amount_rounded) as Sumdisttxnamt, sum(Pincode_usercount) as Sumpincodeusercount, sum(Pincode_txn_amount_rounded) as Sumpincodetxnamt from toptxn group by State, District_Name, Pincode, Year, Quater')
 cursor.execute(aggtxnamtcount)
 aggtxn_amt_count = cursor.fetchall()
 aggtxn_amt_count_df= pd.DataFrame(aggtxn_amt_count, columns=cursor.column_names)
 return aggtxn_amt_count_df




def top_Dist_txn_count_year(Year_t): 
 aggvalue_df = commontable_toptxn()
 aggregated_df = aggvalue_df.groupby(['State','District_Name','Year'])['Sumdistusercount'].sum().reset_index()
 Year_t=str(Year_t)
 aggvalue_final = (aggregated_df[aggregated_df['Year']==Year_t])
 aggvalue_final = aggvalue_final.reset_index(drop=True)
 return aggvalue_final

def top_Dist_txn_count_Q(Quarterselect_t):
 Database_yr = top_Dist_txn_count_year(Year_t)
 aggvalue_df = commontable_toptxn()
 aggvalue_df_Q = aggvalue_df.groupby(['State','District_Name','Year','Quater'])['Sumdistusercount'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect_t])
 return aggvalue_final_Q

def Year_Chart_Dist_txn_Count(Year_t):
 Database_yr = top_Dist_txn_count_year(Year_t)
 st.dataframe(Database_yr)
 col1, col2 = st.columns([2,1])
 with col1:

  st.subheader(f"{Database_yr['Year'].min()} Top Tranasction State and District level User Count")
  
  fig = px.choropleth(
      Database_yr,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumdistusercount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
##For total value to appear in the table
  total_row = pd.DataFrame({'Year': ['Total'], 'Sumdistusercount': [Database_yr['Sumdistusercount'].sum()]})
  df_with_tot = pd.concat([Database_yr, total_row], ignore_index=True)
##to remove <n/a> values in the table 
  df_with_total = df_with_tot.fillna('')
  st.dataframe(df_with_total,height=800,width=1000)


##Groupby Year
 aggvalue_df = commontable_toptxn()
 aggregated_df = aggvalue_df.groupby('Year')['Sumdistusercount'].sum().reset_index()
 st.subheader(f"Aggregated Overall Top Transaction District level User Count")
 fig = go.Figure()
 colorscale = px.colors.sequential.Plasma
##Add Bar Chart
 fig.add_trace(go.Bar(x=aggregated_df['Year'], y=aggregated_df['Sumdistusercount'], marker=dict(color=aggregated_df['Sumdistusercount'], colorscale=colorscale, showscale=True) ))
 st.plotly_chart(fig)


 st.subheader(f"Aggregated {Database_yr['Year'].min()} Year Quarterwise Top Transaction District level User Count")

 aggregated_df_r = aggvalue_df.groupby(['Year','Quater'])['Sumdistusercount'].sum().reset_index()
 Year_t=str(Year_t)
 aggvalue_Q = (aggregated_df_r[aggregated_df_r['Year']==Year_t])
 fig = px.pie(aggvalue_Q, names='Quater', values='Sumdistusercount', title=f"{Database_yr['Year'].min()} Year Quarterwise Top Transaction District level User Count", width=1000)
 st.plotly_chart(fig)

 st.subheader(f"{Database_yr['Year'].min()} Top District User Count")
 
 aggvalue_type_df = aggvalue_df.groupby(['Year','District_Name'])['Sumdistusercount'].sum().reset_index()
 Year_t=str(Year_t)
 aggvalue_type_final = (aggvalue_type_df[aggvalue_type_df['Year']==Year_t])
 aggvalue_type_final = aggvalue_type_final.reset_index(drop=True) 

 st.dataframe(aggvalue_type_final)
 return df_with_total
   
#########QUARTERWISE DATA#########



def top_dist_txn_year_Quarter_(Quarterselect_t):
 
 Database_yr = top_Dist_txn_count_year(Year_t)
 aggvalue_df = commontable_toptxn()
 aggvalue_df_Q = aggvalue_df.groupby(['State','District_Name','Year','Quater'])['Sumdistusercount'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect_t])
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_t)
 aggvalue_final_Q = (aggvalue_final_Q[aggvalue_final_Q['Year']==Year_])

# ##For total value to appear in the table
 total_row_Q = pd.DataFrame({'Quater': ['Total'], 'Sumdistusercount': [aggvalue_final_Q['Sumdistusercount'].sum()]})
 df_with_tot_Q= pd.concat([aggvalue_final_Q, total_row_Q], ignore_index=True)
# ##to remove <n/a> values in the table 
 df_with_total_Q = df_with_tot_Q.fillna('')


##Data for Transaction type chart:

 
 aggvalue_type_final_Q = aggvalue_df.groupby(['Year','Quater','District_Name'])['Sumdistusercount'].sum().reset_index()
 aggvalue_type_final_Q_yr=(aggvalue_type_final_Q[aggvalue_type_final_Q['Year']==Year_])
 aggvalue_type_final_Q_=(aggvalue_type_final_Q_yr[aggvalue_type_final_Q_yr['Quater']==Quarterselect_t])

 
####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} YEAR {Quarterselect_t} Quarter Top Transaction State and District User Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_Q,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumdistusercount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(df_with_total_Q,height=800,width=1000) 

 st.subheader(f"{Database_yr['Year'].min()} Year {Quarterselect_t } Quarter Top District User Count")
 st.dataframe(aggvalue_type_final_Q_)
 return aggvalue_final_Q

################STATE LEVEL DATA###########################################################
def Top_District_Txn_count_state_yr(Year_t, State_t):
 
 Database_yr = top_Dist_txn_count_year(Year_t)
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_t)
 
 
 aggvalue_final_st = (Database_yr[Database_yr['State']==State_t])



##Data for Transaction type chart:

 aggvalue_df = commontable_toptxn()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','District_Name'])['Sumdistusercount'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_t])


####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} Year {State_t} State Top Transaction User Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumdistusercount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=400,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st, names='District_Name', values='Sumdistusercount', title=f"{Database_yr['Year'].min()} Year {State_m} State Top User Count", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'Sumdistusercount': [aggvalue_type_final_st['Sumdistusercount'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st

###########################################3

def Top_District_Txn_count_state_Q(Year_t, Quarterselect_t, State_t):
 
 Database_Q = top_Dist_txn_count_Q(Quarterselect_t)
 Year_ = Database_Q["Year"].min()
 Year_=str(Year_t)
 
 aggvalue_final_st = (Database_Q[Database_Q['State']==State_t])
 aggvalue_final_st = (aggvalue_final_st[aggvalue_final_st['Year']==Year_])


##Data for Transaction type chart:
 aggvalue_df = commontable_toptxn()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','Quater','District_Name'])['Sumdistusercount'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st_=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_t])
 aggvalue_type_final_st_=(aggvalue_type_final_st_[aggvalue_type_final_st_['Quater']==Quarterselect_t])

###MAP
 
 st.subheader(f"{Database_Q['Quater'].min()} Quarter {Year_t} Year {State_t} State Top Transaction User Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumdistusercount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=500,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st_, names='District_Name', values='Sumdistusercount', title=f"{Database_Q['Quater'].min()} Quarter {Year_t} Year {State_t} State Top Transaction User Count", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'Sumdistusercount': [aggvalue_type_final_st_['Sumdistusercount'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st_, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st

##################10)DIST TOP TXN AMT#########################




def top_Dist_txn_amt_year(Year_t): 
 aggvalue_df = commontable_toptxn()
 aggregated_df = aggvalue_df.groupby(['State','District_Name','Year'])['Sumdisttxnamt'].sum().reset_index()
 Year_t=str(Year_t)
 aggvalue_final = (aggregated_df[aggregated_df['Year']==Year_t])
 aggvalue_final = aggvalue_final.reset_index(drop=True)
 return aggvalue_final

def top_Dist_txn_amt_Q(Quarterselect_t):
 Database_yr = top_Dist_txn_amt_year(Year_t)
 aggvalue_df = commontable_toptxn()
 aggvalue_df_Q = aggvalue_df.groupby(['State','District_Name','Year','Quater'])['Sumdisttxnamt'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect_t])
 return aggvalue_final_Q

def Year_Chart_Dist_txn_amt(Year_t):
 Database_yr = top_Dist_txn_amt_year(Year_t)

 col1, col2 = st.columns([2,1])
 with col1:

  st.subheader(f"{Database_yr['Year'].min()} Top State and District level Transaction Amount")
  
  fig = px.choropleth(
      Database_yr,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumdisttxnamt',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})

  st.plotly_chart(fig)

 with col2:
##For total value to appear in the table
  total_row = pd.DataFrame({'Year': ['Total'], 'Sumdisttxnamt': [Database_yr['Sumdisttxnamt'].sum()]})
  df_with_tot = pd.concat([Database_yr, total_row], ignore_index=True)
##to remove <n/a> values in the table 
  df_with_total = df_with_tot.fillna('')
  st.dataframe(df_with_total,height=800,width=1000)





##Groupby Year
 aggvalue_df = commontable_toptxn()
 aggregated_df = aggvalue_df.groupby('Year')['Sumdisttxnamt'].sum().reset_index()
 st.subheader(f"Aggregated Overall Top District level Transaction Amount")
 fig = go.Figure()
 colorscale = px.colors.sequential.Plasma
##Add Bar Chart
 fig.add_trace(go.Bar(x=aggregated_df['Year'], y=aggregated_df['Sumdisttxnamt'], marker=dict(color=aggregated_df['Sumdisttxnamt'], colorscale=colorscale, showscale=True) ))
 st.plotly_chart(fig)

 st.dataframe(aggvalue_type_final)
 

 
 return df_with_total
   
#########QUARTERWISE DATA#########



def top_dist_txn_Amt_year_Quarter_(Quarterselect_t):
 
 Database_yr = top_Dist_txn_amt_year(Year_t)
 aggvalue_df = commontable_toptxn()
 aggvalue_df_Q = aggvalue_df.groupby(['State','District_Name','Year','Quater'])['Sumdisttxnamt'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect_t])
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_t)
 aggvalue_final_Q = (aggvalue_final_Q[aggvalue_final_Q['Year']==Year_])

# ##For total value to appear in the table
 total_row_Q = pd.DataFrame({'Quater': ['Total'], 'Sumdisttxnamt': [aggvalue_final_Q['Sumdisttxnamt'].sum()]})
 df_with_tot_Q= pd.concat([aggvalue_final_Q, total_row_Q], ignore_index=True)
# ##to remove <n/a> values in the table 
 df_with_total_Q = df_with_tot_Q.fillna('')


##Data for Transaction type chart:

 
 aggvalue_type_final_Q = aggvalue_df.groupby(['Year','Quater','District_Name'])['Sumdisttxnamt'].sum().reset_index()
 aggvalue_type_final_Q_yr=(aggvalue_type_final_Q[aggvalue_type_final_Q['Year']==Year_])
 aggvalue_type_final_Q_=(aggvalue_type_final_Q_yr[aggvalue_type_final_Q_yr['Quater']==Quarterselect_t])

 
####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} Year {Quarterselect_t} Quarter Top State and District Transaction Amount")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_Q,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumdisttxnamt',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(df_with_total_Q) 

 st.subheader(f"{Database_yr['Year'].min()} Year {Quarterselect_t } Quarter Top District Transaction Amount")
 st.dataframe(aggvalue_type_final_Q_)
 return aggvalue_final_Q

################STATE LEVEL DATA###########################################################
def Top_District_Txn_amt_state_yr(Year_t, State_t):
 
 Database_yr = top_Dist_txn_amt_year(Year_t)
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_t)
 
 
 aggvalue_final_st = (Database_yr[Database_yr['State']==State_t])



##Data for Transaction type chart:

 aggvalue_df = commontable_toptxn()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','District_Name'])['Sumdisttxnamt'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_t])


####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} Year {State_t} State Top Transaction Amount")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumdisttxnamt',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=400,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st, names='District_Name', values='Sumdisttxnamt', title=f"{Database_yr['Year'].min()} Year {State_m} State Top Transaction Amount", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'Sumdisttxnamt': [aggvalue_type_final_st['Sumdisttxnamt'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st



def Top_District_Txn_amt_state_Q(Year_t, Quarterselect_t, State_t):
 
 Database_Q = top_Dist_txn_amt_Q(Quarterselect_t)
 Year_ = Database_Q["Year"].min()
 Year_=str(Year_t)
 
 aggvalue_final_st = (Database_Q[Database_Q['State']==State_t])
 aggvalue_final_st = (aggvalue_final_st[aggvalue_final_st['Year']==Year_])


##Data for Transaction type chart:
 aggvalue_df = commontable_toptxn()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','Quater','District_Name'])['Sumdisttxnamt'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st_=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_t])
 aggvalue_type_final_st_=(aggvalue_type_final_st_[aggvalue_type_final_st_['Quater']==Quarterselect_t])

###MAP
 
 st.subheader(f"{Database_Q['Quater'].min()} Quarter {Year_t} Year {State_t} State Top Transaction Amount")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumdisttxnamt',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=500,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st_, names='District_Name', values='Sumdisttxnamt', title=f"{Database_Q['Quater'].min()} Quarter {Year_t} Year {State_t} State Top Transaction Amount", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'Sumdisttxnamt': [aggvalue_type_final_st_['Sumdisttxnamt'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st_, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st



######################11)TOP PINCODE USER COUNT###################################3



def top_pincode_txn_count_year(Year_t): 
 aggvalue_df = commontable_toptxn()
 aggregated_df = aggvalue_df.groupby(['State','Pincode','Year'])['Sumpincodeusercount'].sum().reset_index()
 Year_t=str(Year_t)
 aggvalue_final = (aggregated_df[aggregated_df['Year']==Year_t])
 aggvalue_final = aggvalue_final.reset_index(drop=True)
 return aggvalue_final

def top_pincode_txn_count_Q(Quarterselect_t):
 Database_yr = top_pincode_txn_count_year(Year_t)
 aggvalue_df = commontable_toptxn()
 aggvalue_df_Q = aggvalue_df.groupby(['State','District_Name','Pincode','Year','Quater'])['Sumpincodeusercount'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect_t])
 return aggvalue_final_Q

def Year_Chart_Pincode_txn_Count(Year_t):
 Database_yr = top_pincode_txn_count_year(Year_t)

 col1, col2 = st.columns([2,1])
 with col1:

  st.subheader(f"{Database_yr['Year'].min()} Top Transaction_State and Pincode User Count")
  
  fig = px.choropleth(
      Database_yr,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumpincodeusercount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
##For total value to appear in the table
  total_row = pd.DataFrame({'Year': ['Total'], 'Sumpincodeusercount': [Database_yr['Sumpincodeusercount'].sum()]})
  df_with_tot = pd.concat([Database_yr, total_row], ignore_index=True)
##to remove <n/a> values in the table 
  df_with_total = df_with_tot.fillna('')
  st.dataframe(df_with_total,height=800,width=800)


##Groupby Year
 aggvalue_df = commontable_toptxn()
 aggregated_df = aggvalue_df.groupby('Year')['Sumpincodeusercount'].sum().reset_index()
 st.subheader(f"Aggregated Overall Top Transaction Pincode User Count")
 fig = go.Figure()
 colorscale = px.colors.sequential.Plasma
##Add Bar Chart
 fig.add_trace(go.Bar(x=aggregated_df['Year'], y=aggregated_df['Sumpincodeusercount'], marker=dict(color=aggregated_df['Sumpincodeusercount'], colorscale=colorscale, showscale=True) ))
 st.plotly_chart(fig)

 st.subheader(f"Aggregated {Database_yr['Year'].min()} Year Quarterwise Top Transaction Pincode User Count")

 aggregated_df_r = aggvalue_df.groupby(['Year','Quater'])['Sumpincodeusercount'].sum().reset_index()
 Year_t=str(Year_t)
 aggvalue_Q = (aggregated_df_r[aggregated_df_r['Year']==Year_t])
 fig = px.pie(aggvalue_Q, names='Quater', values='Sumpincodeusercount', title=f"{Database_yr['Year'].min()} Year Quarterwise Top Transaction Pincode User Count", width=1000)
 st.plotly_chart(fig)

 st.subheader(f"{Database_yr['Year'].min()} Top Transaction Pincode User Count")
 
 aggvalue_type_df = aggvalue_df.groupby(['Year','Pincode'])['Sumpincodeusercount'].sum().reset_index()
 Year_t=str(Year_t)
 aggvalue_type_final = (aggvalue_type_df[aggvalue_type_df['Year']==Year_t])
 aggvalue_type_final = aggvalue_type_final.reset_index(drop=True) 
 st.dataframe(aggvalue_type_final)
 

 
 return df_with_total
   
#########QUARTERWISE DATA#########


def top_pincode_txn_year_Quarter_(Quarterselect_t):
 
 Database_yr = top_Dist_txn_count_year(Year_t)
 aggvalue_df = commontable_toptxn()
 aggvalue_df_Q = aggvalue_df.groupby(['State','District_Name','Pincode','Year','Quater'])['Sumpincodeusercount'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect_t])
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_t)
 aggvalue_final_Q = (aggvalue_final_Q[aggvalue_final_Q['Year']==Year_])

# ##For total value to appear in the table
 total_row_Q = pd.DataFrame({'Quater': ['Total'], 'Sumpincodeusercount': [aggvalue_final_Q['Sumpincodeusercount'].sum()]})
 df_with_tot_Q= pd.concat([aggvalue_final_Q, total_row_Q], ignore_index=True)
# ##to remove <n/a> values in the table 
 df_with_total_Q = df_with_tot_Q.fillna('')


##Data for Transaction type chart:

 
 aggvalue_type_final_Q = aggvalue_df.groupby(['Year','Quater','Pincode'])['Sumpincodeusercount'].sum().reset_index()
 aggvalue_type_final_Q_yr=(aggvalue_type_final_Q[aggvalue_type_final_Q['Year']==Year_])
 aggvalue_type_final_Q_=(aggvalue_type_final_Q_yr[aggvalue_type_final_Q_yr['Quater']==Quarterselect_t])

 
####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} YEAR {Quarterselect_t} Quarter Top Transaction State and Pincode User Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_Q,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumpincodeusercount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(df_with_total_Q,height=800,width=1000) 

 st.subheader(f"{Database_yr['Year'].min()} Year {Quarterselect_t } Quarter Top Transaction Pincode User Count")
 st.dataframe(aggvalue_type_final_Q_)
 return aggvalue_final_Q

################STATE LEVEL DATA###########################################################
def Top_Pincode_Txn_count_state_yr(Year_t, State_t):
 
 Database_yr = top_pincode_txn_count_year(Year_t)
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_t)
 
 
 aggvalue_final_st = (Database_yr[Database_yr['State']==State_t])



##Data for Transaction type chart:

 aggvalue_df = commontable_toptxn()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','Pincode'])['Sumpincodeusercount'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_t])

####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} Year {State_t} State Pincode Top Transaction User Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumpincodeusercount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=400,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st, names='Pincode', values='Sumpincodeusercount', title=f"{Database_yr['Year'].min()} Year {State_m} State Top Transaction User Count", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'Sumpincodeusercount': [aggvalue_type_final_st['Sumpincodeusercount'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st


def Top_Pincode_Txn_count_state_Q(Year_t, Quarterselect_t, State_t):
 
 Database_Q = top_pincode_txn_count_Q(Quarterselect_t)
 Year_ = Database_Q["Year"].min()
 Year_=str(Year_t)
 
 aggvalue_final_st = (Database_Q[Database_Q['State']==State_t])
 aggvalue_final_st = (aggvalue_final_st[aggvalue_final_st['Year']==Year_])


##Data for Transaction type chart:
 aggvalue_df = commontable_toptxn()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','District_Name','Quater','Pincode'])['Sumpincodeusercount'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st_=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_t])
 aggvalue_type_final_st_=(aggvalue_type_final_st_[aggvalue_type_final_st_['Quater']==Quarterselect_t])

###MAP
 
 st.subheader(f"{Database_Q['Quater'].min()} Quarter {Year_t} Year {State_t} State Top Transaction User Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumpincodeusercount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=500,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st_, names='Pincode', values='Sumpincodeusercount', title=f"{Database_Q['Quater'].min()} Quarter {Year_t} Year {State_t} State Top Transaction User Count", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'Sumpincodeusercount': [aggvalue_type_final_st_['Sumpincodeusercount'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st_, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st


###########################12)TOP PINCODE TRANSACTION AMOUNT###############################



def top_pincode_txn_amt_year(Year_t): 
 aggvalue_df = commontable_toptxn()
 aggregated_df = aggvalue_df.groupby(['State','District_Name','Pincode','Year'])['Sumpincodetxnamt'].sum().reset_index()
 Year_t=str(Year_t)
 aggvalue_final = (aggregated_df[aggregated_df['Year']==Year_t])
 aggvalue_final = aggvalue_final.reset_index(drop=True)
 return aggvalue_final

def top_pincode_txn_amt_Q(Quarterselect_t):
 Database_yr = top_Dist_txn_count_year(Year_t)
 aggvalue_df = commontable_toptxn()
 aggvalue_df_Q = aggvalue_df.groupby(['State','District_Name','Pincode','Year','Quater'])['Sumpincodetxnamt'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect_t])
 return aggvalue_final_Q

def Year_Chart_Pincode_txn_amt(Year_t):
 Database_yr = top_pincode_txn_amt_year(Year_t)

 col1, col2 = st.columns([2,1])
 with col1:

  st.subheader(f"{Database_yr['Year'].min()} Top State and Pincode Transaction Amount")
  
  fig = px.choropleth(
      Database_yr,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumpincodetxnamt',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})

  st.plotly_chart(fig)

 with col2:
##For total value to appear in the table
  total_row = pd.DataFrame({'Year': ['Total'], 'Sumpincodetxnamt': [Database_yr['Sumpincodetxnamt'].sum()]})
  df_with_tot = pd.concat([Database_yr, total_row], ignore_index=True)
##to remove <n/a> values in the table 
  df_with_total = df_with_tot.fillna('')
  st.dataframe(df_with_total,height=800,width=1000)


##Groupby Year
 aggvalue_df = commontable_toptxn()
 aggregated_df = aggvalue_df.groupby('Year')['Sumpincodetxnamt'].sum().reset_index()
 st.subheader(f"Aggregated Overall Yearwise Top Pincode Transaction Amount")
 fig = go.Figure()
 colorscale = px.colors.sequential.Plasma
##Add Bar Chart
 fig.add_trace(go.Bar(x=aggregated_df['Year'], y=aggregated_df['Sumpincodetxnamt'], marker=dict(color=aggregated_df['Sumpincodetxnamt'], colorscale=colorscale, showscale=True) ))
 st.plotly_chart(fig)


 st.subheader(f"Aggregated {Database_yr['Year'].min()} Year Quarterwise Top District level Transaction Amount")

 aggregated_df_r = aggvalue_df.groupby(['Year','Quater'])['Sumpincodetxnamt'].sum().reset_index()
 Year_t=str(Year_t)
 aggvalue_Q = (aggregated_df_r[aggregated_df_r['Year']==Year_t])
 fig = px.pie(aggvalue_Q, names='Quater', values='Sumpincodetxnamt', title=f"{Database_yr['Year'].min()} Year Quarterwise Top Pincode Transaction Amount", width=1000)
 st.plotly_chart(fig)

 st.subheader(f"{Database_yr['Year'].min()} Top Pincode Transaction Amount")
 
 aggvalue_type_df = aggvalue_df.groupby(['Year','Pincode'])['Sumpincodetxnamt'].sum().reset_index()
 Year_t=str(Year_t)
 aggvalue_type_final = (aggvalue_type_df[aggvalue_type_df['Year']==Year_t])
 aggvalue_type_final = aggvalue_type_final.reset_index(drop=True) 

 st.dataframe(aggvalue_type_final)
 

 
 return df_with_total
   
#########QUARTERWISE DATA#########

def top_pincode_txn_Amt_year_Quarter_(Quarterselect_t):
 
 Database_yr = top_pincode_txn_amt_year(Year_t)
 aggvalue_df = commontable_toptxn()
 aggvalue_df_Q = aggvalue_df.groupby(['State','District_Name','Pincode','Year','Quater'])['Sumpincodetxnamt'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect_t])
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_t)
 aggvalue_final_Q = (aggvalue_final_Q[aggvalue_final_Q['Year']==Year_])

# ##For total value to appear in the table
 total_row_Q = pd.DataFrame({'Quater': ['Total'], 'Sumpincodetxnamt': [aggvalue_final_Q['Sumpincodetxnamt'].sum()]})
 df_with_tot_Q= pd.concat([aggvalue_final_Q, total_row_Q], ignore_index=True)
# ##to remove <n/a> values in the table 
 df_with_total_Q = df_with_tot_Q.fillna('')


##Data for Transaction type chart:

 
 aggvalue_type_final_Q = aggvalue_df.groupby(['Year','Quater','District_Name','Pincode'])['Sumpincodetxnamt'].sum().reset_index()
 aggvalue_type_final_Q_yr=(aggvalue_type_final_Q[aggvalue_type_final_Q['Year']==Year_])
 aggvalue_type_final_Q_=(aggvalue_type_final_Q_yr[aggvalue_type_final_Q_yr['Quater']==Quarterselect_t])

 
####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} Year {Quarterselect_t} Quarter Top State and Pincode Transaction Amount")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_Q,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumpincodetxnamt',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(df_with_total_Q) 

 st.subheader(f"{Database_yr['Year'].min()} Year {Quarterselect_t } Quarter Top Pincode Transaction Amount")

 st.dataframe(aggvalue_type_final_Q_)
 return aggvalue_final_Q

################STATE LEVEL DATA###########################################################
def Top_Pincode_Txn_amt_state_yr(Year_t, State_t):
 
 Database_yr = top_pincode_txn_amt_year(Year_t)
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_t)
 
 
 aggvalue_final_st = (Database_yr[Database_yr['State']==State_t])



##Data for Transaction type chart:

 aggvalue_df = commontable_toptxn()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','District_Name','Pincode'])['Sumpincodetxnamt'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_t])


####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} Year {State_t} State Pincode Top Transaction Amount")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumpincodetxnamt',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=400,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st, names='Pincode', values='Sumpincodetxnamt', title=f"{Database_yr['Year'].min()} Year {State_m} State Top Transaction Amount", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'Sumpincodetxnamt': [aggvalue_type_final_st['Sumpincodetxnamt'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st

###########################################3

def Top_Pincode_Txn_amt_state_Q(Year_t, Quarterselect_t, State_t):
 
 Database_Q = top_pincode_txn_amt_Q(Quarterselect_t)
 Year_ = Database_Q["Year"].min()
 Year_=str(Year_t)
 
 aggvalue_final_st = (Database_Q[Database_Q['State']==State_t])
 aggvalue_final_st = (aggvalue_final_st[aggvalue_final_st['Year']==Year_])


##Data for Transaction type chart:
 aggvalue_df = commontable_toptxn()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','Quater','District_Name','Pincode'])['Sumpincodetxnamt'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st_=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_t])
 aggvalue_type_final_st_=(aggvalue_type_final_st_[aggvalue_type_final_st_['Quater']==Quarterselect_t])

###MAP
 
 st.subheader(f"{Database_Q['Quater'].min()} Quarter {Year_t} Year {State_t} State Pincode Top Transaction Amount")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='Sumpincodetxnamt',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=500,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st_, names='Pincode', values='Sumpincodetxnamt', title=f"{Database_Q['Quater'].min()} Quarter {Year_t} Year {State_t} State Pincode Top Transaction Amount", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'Sumpincodetxnamt': [aggvalue_type_final_st_['Sumpincodetxnamt'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st_, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st




#######################13) DIST TOP USER##################################


def commontable_topusercount():
 aggtxnamtcount = cursor.execute('select State, Year, Quater, District_Name, Pincode, sum(Dist_usercount) as sumdtusercount, sum(Pincode_usercount) as pinusercount from topusercount2 group by State, District_Name, Pincode, Year, Quater')
 cursor.execute(aggtxnamtcount)
 aggtxn_amt_count = cursor.fetchall()
 aggtxn_amt_count_df= pd.DataFrame(aggtxn_amt_count, columns=cursor.column_names)
 return aggtxn_amt_count_df


def Dist_tuser_count_year(Year_t): 
 aggvalue_df = commontable_topusercount()
 aggregated_df = aggvalue_df.groupby(['State','District_Name','Year'])['sumdtusercount'].sum().reset_index()
 Year_t=str(Year_t)
 aggvalue_final = (aggregated_df[aggregated_df['Year']==Year_t])
 aggvalue_final = aggvalue_final.reset_index(drop=True)
 return aggvalue_final

def dist_top_User_Quarter_(Quarterselect_t):
 Database_yr = Dist_tuser_count_year(Year_t)
 aggvalue_df = commontable_topusercount()
 aggvalue_df_Q = aggvalue_df.groupby(['State','District_Name','Year','Quater'])['sumdtusercount'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect_t])
 return aggvalue_final_Q

def Year_Chart_Dist_top_User_Count(Year_t):
 Database_yr = Dist_tuser_count_year(Year_t)

 col1, col2 = st.columns([2,1])
 with col1:

  st.subheader(f"{Database_yr['Year'].min()} Top State and District level User Count")
  
  fig = px.choropleth(
      Database_yr,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='sumdtusercount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
##For total value to appear in the table
  total_row = pd.DataFrame({'Year': ['Total'], 'sumdtusercount': [Database_yr['sumdtusercount'].sum()]})
  df_with_tot = pd.concat([Database_yr, total_row], ignore_index=True)
##to remove <n/a> values in the table 
  df_with_total = df_with_tot.fillna('')
  st.dataframe(df_with_total,height=800,width=1000)


##Groupby Year
 aggvalue_df = commontable_topusercount()
 aggregated_df = aggvalue_df.groupby('Year')['sumdtusercount'].sum().reset_index()
 st.subheader(f"Aggregated Overall Top District User Count")
 fig = go.Figure()
 colorscale = px.colors.sequential.Plasma
##Add Bar Chart
 fig.add_trace(go.Bar(x=aggregated_df['Year'], y=aggregated_df['sumdtusercount'], marker=dict(color=aggregated_df['sumdtusercount'], colorscale=colorscale, showscale=True) ))
 st.plotly_chart(fig)


 st.subheader(f"Aggregated {Database_yr['Year'].min()} Year Quarterwise Top District level User Count")

 aggregated_df_r = aggvalue_df.groupby(['Year','Quater'])['sumdtusercount'].sum().reset_index()
 Year_t=str(Year_t)
 aggvalue_Q = (aggregated_df_r[aggregated_df_r['Year']==Year_t])
 fig = px.pie(aggvalue_Q, names='Quater', values='sumdtusercount', title=f"{Database_yr['Year'].min()} Year Quarterwise Top District User Count", width=1000)
 st.plotly_chart(fig)

 st.subheader(f"{Database_yr['Year'].min()} Top District User Count")
 
 aggvalue_type_df = aggvalue_df.groupby(['Year','District_Name'])['sumdtusercount'].sum().reset_index()
 Year_t=str(Year_t)
 aggvalue_type_final = (aggvalue_type_df[aggvalue_type_df['Year']==Year_t])
 aggvalue_type_final = aggvalue_type_final.reset_index(drop=True) 

 st.dataframe(aggvalue_type_final)
 
 return df_with_total
   
#########QUARTERWISE DATA#########



def dist_top_User_year_Quarter_(Quarterselect_t):
 
 Database_yr = Dist_tuser_count_year(Year_t)
 aggvalue_df = commontable_topusercount()
 aggvalue_df_Q = aggvalue_df.groupby(['State','District_Name','Year','Quater'])['sumdtusercount'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect_t])
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_t)
 aggvalue_final_Q = (aggvalue_final_Q[aggvalue_final_Q['Year']==Year_])

# ##For total value to appear in the table
 total_row_Q = pd.DataFrame({'Quater': ['Total'], 'sumdtusercount': [aggvalue_final_Q['sumdtusercount'].sum()]})
 df_with_tot_Q= pd.concat([aggvalue_final_Q, total_row_Q], ignore_index=True)
# ##to remove <n/a> values in the table 
 df_with_total_Q = df_with_tot_Q.fillna('')


##Data for Transaction type chart:

 
 aggvalue_type_final_Q = aggvalue_df.groupby(['Year','Quater','District_Name'])['sumdtusercount'].sum().reset_index()
 aggvalue_type_final_Q_yr=(aggvalue_type_final_Q[aggvalue_type_final_Q['Year']==Year_])
 aggvalue_type_final_Q_=(aggvalue_type_final_Q_yr[aggvalue_type_final_Q_yr['Quater']==Quarterselect_t])

 
####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} YEAR {Quarterselect_t} Quarter Top State and District User Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_Q,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='sumdtusercount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(df_with_total_Q,height=800,width=1000) 

 st.subheader(f"{Database_yr['Year'].min()} Year {Quarterselect_t } Quarter Top District User Count")

 st.dataframe(aggvalue_type_final_Q_)
 return aggvalue_final_Q

################STATE LEVEL DATA###########################################################
def dist_top_User_state_yr(Year_t, State_t):
 
 Database_yr = Dist_tuser_count_year(Year_t)
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_t)
 
 
 aggvalue_final_st = (Database_yr[Database_yr['State']==State_t])



##Data for Transaction type chart:

 aggvalue_df = commontable_topusercount()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','District_Name'])['sumdtusercount'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_t])

####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} Year {State_t} State Top User Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='sumdtusercount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=400,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st, names='District_Name', values='sumdtusercount', title=f"{Database_yr['Year'].min()} Year {State_m} State Top User Count", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'sumdtusercount': [aggvalue_type_final_st['sumdtusercount'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st

###########################################

def dist_top_user_count_state_Q(Year_t, Quarterselect_t, State_t):
 
 Database_Q = dist_top_User_Quarter_(Quarterselect_t)
 Year_ = Database_Q["Year"].min()
 Year_=str(Year_t)
 
 aggvalue_final_st = (Database_Q[Database_Q['State']==State_t])
 aggvalue_final_st = (aggvalue_final_st[aggvalue_final_st['Year']==Year_])


##Data for Transaction type chart:
 aggvalue_df = commontable_topusercount()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','Quater','District_Name'])['sumdtusercount'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st_=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_t])
 aggvalue_type_final_st_=(aggvalue_type_final_st_[aggvalue_type_final_st_['Quater']==Quarterselect_t])

###MAP
 
 st.subheader(f"{Database_Q['Quater'].min()} Quarter {Year_t} Year {State_t} State Top User Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='sumdtusercount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=500,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st_, names='District_Name', values='sumdtusercount', title=f"{Database_Q['Quater'].min()} Quarter {Year_t} Year {State_t} State Top Transaction User Count", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'sumdtusercount': [aggvalue_type_final_st_['sumdtusercount'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st_, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st


##########################14)PINCODE USER COUNT#############

def commontable_topusercount():
 aggtxnamtcount = cursor.execute('select State, Year, Quater, District_Name, Pincode, sum(Dist_usercount) as sumdtusercount, sum(Pincode_usercount) as pinusercount from topusercount2 group by State, District_Name, Pincode, Year, Quater')
 cursor.execute(aggtxnamtcount)
 aggtxn_amt_count = cursor.fetchall()
 aggtxn_amt_count_df= pd.DataFrame(aggtxn_amt_count, columns=cursor.column_names)
 return aggtxn_amt_count_df


def Pincode_tuser_count_year(Year_t): 
 aggvalue_df = commontable_topusercount()
 aggregated_df = aggvalue_df.groupby(['State','Year','District_Name','Pincode'])['pinusercount'].sum().reset_index()
 Year_t=str(Year_t)
 aggvalue_final = (aggregated_df[aggregated_df['Year']==Year_t])
 aggvalue_final = aggvalue_final.reset_index(drop=True)
 return aggvalue_final

def pincode_top_User_Quarter_(Quarterselect_t):
 Database_yr = Pincode_tuser_count_year(Year_t)
 aggvalue_df = commontable_topusercount()
 aggvalue_df_Q = aggvalue_df.groupby(['State','District_Name','Pincode','Year','Quater'])['pinusercount'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect_t])
 return aggvalue_final_Q

def Year_Chart_pincode_top_User_Count(Year_t):
 Database_yr = Pincode_tuser_count_year(Year_t)

 col1, col2 = st.columns([2,1])
 with col1:

  st.subheader(f"{Database_yr['Year'].min()} Top State and Pincode User Count")
  
  fig = px.choropleth(
      Database_yr,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='pinusercount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})

  st.plotly_chart(fig)

 with col2:
##For total value to appear in the table
  total_row = pd.DataFrame({'Year': ['Total'], 'pinusercount': [Database_yr['pinusercount'].sum()]})
  df_with_tot = pd.concat([Database_yr, total_row], ignore_index=True)
##to remove <n/a> values in the table 
  df_with_total = df_with_tot.fillna('')
  st.dataframe(df_with_total,height=800,width=1000)


##Groupby Year
 aggvalue_df = commontable_topusercount()
 aggregated_df = aggvalue_df.groupby('Year')['pinusercount'].sum().reset_index()
 st.subheader(f"Aggregated Overall Top Pincode User Count")
 fig = go.Figure()
 colorscale = px.colors.sequential.Plasma
##Add Bar Chart
 fig.add_trace(go.Bar(x=aggregated_df['Year'], y=aggregated_df['pinusercount'], marker=dict(color=aggregated_df['pinusercount'], colorscale=colorscale, showscale=True) ))
 st.plotly_chart(fig)


 st.subheader(f"Aggregated {Database_yr['Year'].min()} Year Quarterwise Top Pincode User Count")

 aggregated_df_r = aggvalue_df.groupby(['Year','Quater'])['pinusercount'].sum().reset_index()
 Year_t=str(Year_t)
 aggvalue_Q = (aggregated_df_r[aggregated_df_r['Year']==Year_t])
 fig = px.pie(aggvalue_Q, names='Quater', values='pinusercount', title=f"{Database_yr['Year'].min()} Year Quarterwise Top Pincode User Count", width=1000)
 st.plotly_chart(fig)

 st.subheader(f"{Database_yr['Year'].min()} Top Pincode User Count")
 
 aggvalue_type_df = aggvalue_df.groupby(['Year','District_Name','Pincode'])['pinusercount'].sum().reset_index()
 Year_t=str(Year_t)
 aggvalue_type_final = (aggvalue_type_df[aggvalue_type_df['Year']==Year_t])
 aggvalue_type_final = aggvalue_type_final.reset_index(drop=True) 

 st.dataframe(aggvalue_type_final)
 
 return df_with_total
   
#########QUARTERWISE DATA#########



def pincode_top_User_year_Quarter_(Quarterselect_t):
 
 Database_yr = Pincode_tuser_count_year(Year_t)
 aggvalue_df = commontable_topusercount()
 aggvalue_df_Q = aggvalue_df.groupby(['State','District_Name','Pincode','Year','Quater'])['pinusercount'].sum().reset_index()
 aggvalue_final_Q = (aggvalue_df_Q[aggvalue_df_Q['Quater']==Quarterselect_t])
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_t)
 aggvalue_final_Q = (aggvalue_final_Q[aggvalue_final_Q['Year']==Year_])

# ##For total value to appear in the table
 total_row_Q = pd.DataFrame({'Quater': ['Total'], 'pinusercount': [aggvalue_final_Q['pinusercount'].sum()]})
 df_with_tot_Q= pd.concat([aggvalue_final_Q, total_row_Q], ignore_index=True)
# ##to remove <n/a> values in the table 
 df_with_total_Q = df_with_tot_Q.fillna('')


##Data for Transaction type chart:

 
 aggvalue_type_final_Q = aggvalue_df.groupby(['Year','Quater','Pincode'])['pinusercount'].sum().reset_index()
 aggvalue_type_final_Q_yr=(aggvalue_type_final_Q[aggvalue_type_final_Q['Year']==Year_])
 aggvalue_type_final_Q_=(aggvalue_type_final_Q_yr[aggvalue_type_final_Q_yr['Quater']==Quarterselect_t])

 
####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} YEAR {Quarterselect_t} Quarter Top State and Pincode User Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_Q,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='pinusercount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=800,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(df_with_total_Q,height=800,width=1000) 

 st.subheader(f"{Database_yr['Year'].min()} Year {Quarterselect_t } Quarter Top Pincode User Count")

 st.dataframe(aggvalue_type_final_Q_)
 return aggvalue_final_Q

################STATE LEVEL DATA###########################################################
def pincode_top_User_state_yr(Year_t, State_t):
 
 Database_yr = Pincode_tuser_count_year(Year_t)
 Year_ = Database_yr["Year"].min()
 Year_=str(Year_t)

 
 aggvalue_final_st = (Database_yr[Database_yr['State']==State_t])



##Data for Transaction type chart:

 aggvalue_df = commontable_topusercount()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','Pincode'])['pinusercount'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_t])


####MAP
 
 st.subheader(f"{Database_yr['Year'].min()} Year {State_t} State Top Pincode User Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='pinusercount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=400,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st, names='Pincode', values='pinusercount', title=f"{Database_yr['Year'].min()} Year {State_t} State Top Pincode User Count", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'pinusercount': [aggvalue_type_final_st['pinusercount'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st

###########################################

def pincode_top_user_count_state_Q(Year_t, Quarterselect_t, State_t):
 
 Database_Q = pincode_top_User_Quarter_(Quarterselect_t)
 Year_ = Database_Q["Year"].min()
 Year_=str(Year_t)
 
 aggvalue_final_st = (Database_Q[Database_Q['State']==State_t])
 aggvalue_final_st = (aggvalue_final_st[aggvalue_final_st['Year']==Year_])


##Data for Transaction type chart:
 aggvalue_df = commontable_topusercount()
 aggvalue_type_final_st = aggvalue_df.groupby(['Year','State','Quater','Pincode'])['pinusercount'].sum().reset_index()
 aggvalue_type_final_st=(aggvalue_type_final_st[aggvalue_type_final_st['Year']==Year_])
 aggvalue_type_final_st_=(aggvalue_type_final_st[aggvalue_type_final_st['State']==State_t])
 aggvalue_type_final_st_=(aggvalue_type_final_st_[aggvalue_type_final_st_['Quater']==Quarterselect_t])

###MAP
 
 st.subheader(f"{Database_Q['Quater'].min()} Quarter {Year_t} Year {State_t} State Top User Count")
 col1, col2 = st.columns([2,1])
 with col1:


  
  fig = px.choropleth(
      aggvalue_final_st,
      geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
      featureidkey='properties.ST_NM',
      locations='State',
      color='pinusercount',
      color_continuous_scale=px.colors.diverging.swatches_continuous(),
      color_continuous_midpoint=0,
      height=500,
      width=1300
  )

  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":1,"t":0,"l":0,"b":200})
  st.plotly_chart(fig)

 with col2:
  st.dataframe(aggvalue_final_st) 

 
 fig = px.pie(aggvalue_type_final_st_, names='Pincode', values='pinusercount', title=f"{Database_Q['Quater'].min()} Quarter {Year_t} Year {State_t} State Top Pincode User Count", width=1000)
 st.plotly_chart(fig)
 total_row_Q_type = pd.DataFrame({'State': ['Total'], 'pinusercount': [aggvalue_type_final_st_['pinusercount'].sum()]})
 df_with_tot_Q_type= pd.concat([aggvalue_type_final_st_, total_row_Q_type], ignore_index=True)
 df_with_tot_Q_type = df_with_tot_Q_type.fillna('')
 st.dataframe(df_with_tot_Q_type)

 return aggvalue_final_st






















































###
###
###
####

 st.set_page_config(layout='wide')
 st.title("Phonepe Data Analysis")
with st.sidebar:
    select= option_menu("Main Page",["HomePage","Data Analysis","Queries"])
if select =="HomePage":
 st.title("Phonepe Pulse Data Visualization and Exploration")
 st.subheader("A live geo visualization dashboard that displays information and insights from the Phonepe pulse Github repository.")
 st.write("PhonePe Group is India’s leading fintech company. Its flagship product, the PhonePe digital payments app, was launched in Aug 2016. Within a short period of time, the company has scaled rapidly to become India’s leading consumer payments app. On the back of its leadership in digital payments, PhonePe Group has expanded into financial services - Insurance, Lending, & Wealth as well as new consumer tech businesses - Pincode and Indus Appstore.")
# Insert an image
 col1, col2, col3 = st.columns([1,1,1])
 with col2:
  st.image("C:/Users/rajij/Downloads/_1.jpg", width=300) 
   

 
elif select=='Data Analysis':
 tab1,tab2,tab3= st.tabs(["Aggregated Data Analysis","Map Data Analysis", "Top Data Analysis"])
 with tab1:
  Dropdown1 = st.radio("Select one of the below option:", ["Aggregated Transaction Data", "Aggregated User Data"])
######################################Aggregated Transaction Count#################################################3
  if Dropdown1 =="Aggregated Transaction Data":
   Dropdown2 = st.radio("Select one of the below option:", ["Aggregated Transaction Count", "Aggregated Transaction Amount"])
   if Dropdown2 == "Aggregated Transaction Count":
    cursor.execute('select Distinct(Year) from aggregatetxnq')
    Yearlist = cursor.fetchall()
    Year_list = pd.DataFrame(Yearlist, columns=cursor.column_names)
    
    col1, col2 = st.columns([10,1])
    with col1:
      Year_d = st.selectbox('Choose a Year from the Dropdown below:', Year_list,index=None, key=None)
      cursor.execute('select Distinct(Quater) from aggregatetxnq')
      Quarterlist = cursor.fetchall()
      Quarter_list = pd.DataFrame(Quarterlist , columns=cursor.column_names)
      Quarterselect = st.selectbox('Choose a Quarter from the Dropdown below:', Quarter_list, index=None, key=None)
      cursor.execute('select Distinct(State) from aggregatetxnq')
      Statelist = cursor.fetchall()
      State_list = pd.DataFrame(Statelist, columns=cursor.column_names)
      State_d = st.selectbox('Choose a State from the Dropdown below:', State_list,index=None, key=None)
      if Year_d is None:
       pass
      else:
       if Quarterselect is None and State_d is None:
        Year_Chart(Year_d)
       elif State_d is None:
        Aggregate_value_year_Quarter_(Quarterselect)
       elif Quarterselect is None:
        Txn_count_state_yr(Year_d,State_d)
       else:
        Txn_count_state_Q(Year_d, Quarterselect,State_d)

###############################################AGG TRANSACTION AMOUNT#################################
   if Dropdown2 == "Aggregated Transaction Amount":
    cursor.execute('select Distinct(Year) from aggregatetxnq')
    Yearlist = cursor.fetchall()
    Year_list = pd.DataFrame(Yearlist, columns=cursor.column_names)
    
    col1, col2 = st.columns([10,1])
    with col1:
      Year_d = st.selectbox('Choose a Year from the Dropdown below:', Year_list,index=None, key=None)
      cursor.execute('select Distinct(Quater) from aggregatetxnq')
      Quarterlist = cursor.fetchall()
      Quarter_list = pd.DataFrame(Quarterlist , columns=cursor.column_names)
      Quarterselect = st.selectbox('Choose a Quarter from the Dropdown below:', Quarter_list, index=None, key=None)
      cursor.execute('select Distinct(State) from aggregatetxnq')
      Statelist = cursor.fetchall()
      State_list = pd.DataFrame(Statelist, columns=cursor.column_names)
      State_d = st.selectbox('Choose a State from the Dropdown below:', State_list,index=None, key=None)
      if Year_d is None:
       pass
      else:
       if Quarterselect is None and State_d is None:
        Year_Chart_Amt(Year_d)
       elif State_d is None:
        Aggregate_Amt_year_Quarter_(Quarterselect)
       elif Quarterselect is None:
        Txn_Amt_state_yr(Year_d,State_d)
       else:
        Txn_Amt_state_Q(Year_d, Quarterselect,State_d)

#######################################################AGG REG USER DATA######################################


  if Dropdown1 =="Aggregated User Data":
   Dropdown2 = st.radio("Select one of the below option:", ["Aggregared Registered_Users", "Aggregated Brand User", "Brand User Percentage - A comparison"])
   if Dropdown2 == "Aggregared Registered_Users":
    cursor.execute('select Distinct(Year) from aggregateuser')
    Yearlist = cursor.fetchall()
    Year_list = pd.DataFrame(Yearlist, columns=cursor.column_names)
    
    col1, col2 = st.columns([10,1])
    with col1:
      Year_d = st.selectbox('Choose a Year from the Dropdown below:', Year_list,index=None, key=None)
      cursor.execute('select Distinct(Quater) from aggregateuser')
      Quarterlist = cursor.fetchall()
      Quarter_list = pd.DataFrame(Quarterlist , columns=cursor.column_names)
      Quarterselect = st.selectbox('Choose a Quarter from the Dropdown below:', Quarter_list, index=None, key=None)
      cursor.execute('select Distinct(State) from aggregateuser')
      Statelist = cursor.fetchall()
      State_list = pd.DataFrame(Statelist, columns=cursor.column_names)
      State_d = st.selectbox('Choose a State from the Dropdown below:', State_list,index=None, key=None)
      if Year_d is None:
       pass
      else:
       if Quarterselect is None and State_d is None:
        Year_Chart_Reg_User(Year_d)
       elif State_d is None:
        Reg_User_Year_Quarter_(Quarterselect)
       elif Quarterselect is None:
        Reg_User_State_Yr(Year_d, State_d)
       else:
        Reg_User_State_Q(Year_d, Quarterselect, State_d)

############################################################BRAND USER#################################
   if Dropdown2 == "Aggregated Brand User":
    cursor.execute('select Distinct(Year) from aggregateuser')
    Yearlist = cursor.fetchall()
    Year_list = pd.DataFrame(Yearlist, columns=cursor.column_names)
    
    col1, col2 = st.columns([10,1])
    with col1:
      Year_d = st.selectbox('Choose a Year from the Dropdown below:', Year_list,index=None, key=None)
      cursor.execute('select Distinct(Quater) from aggregateuser')
      Quarterlist = cursor.fetchall()
      Quarter_list = pd.DataFrame(Quarterlist , columns=cursor.column_names)
      Quarterselect = st.selectbox('Choose a Quarter from the Dropdown below:', Quarter_list, index=None, key=None)
      cursor.execute('select Distinct(State) from aggregateuser')
      Statelist = cursor.fetchall()
      State_list = pd.DataFrame(Statelist, columns=cursor.column_names)
      State_d = st.selectbox('Choose a State from the Dropdown below:', State_list,index=None, key=None)
      if Year_d is None:
       pass
      else:
       if Quarterselect is None and State_d is None:
        Year_Chart_Reg_Brand_User(Year_d)
       elif State_d is None:
        Reg_Brand_User_Year_Quarter_(Quarterselect)
       elif Quarterselect is None:
        Reg_Brand_User_State_Yr(Year_d, State_d)
       else:
        Reg_Brand_User_State_Q(Year_d, Quarterselect, State_d)

   if Dropdown2 == "Brand User Percentage - A comparison":
    cursor.execute('select Distinct(Year) from aggregateuser')
    Yearlist = cursor.fetchall()
    Year_list = pd.DataFrame(Yearlist, columns=cursor.column_names)
        
    col1, col2 = st.columns([10,1])
    with col1:
      cursor.execute('select Distinct(Brand) from aggregateuser')
      Brandlist = cursor.fetchall()
      Brand_list = pd.DataFrame(Brandlist, columns=cursor.column_names)
      Brand_d = st.selectbox('Choose a Brand from the Dropdown below:', Brand_list,index=None, key=None)
      Year_d = st.selectbox('Choose a Year from the Dropdown below:', Year_list,index=None, key=None)
      
      if Brand_d is None:
       pass
      elif Year_d is None:
       pass
      else:
       Year_Chart_Reg_Brand_User_Per(Year_d,Brand_d)
       

 with tab2:
  Dropdown2 = st.radio("Select one of the below option:", ["Map Transaction Data", "Map User Data"])
  if Dropdown2 =="Map Transaction Data":
   Dropdown2 = st.radio("Select one of the below option:", ["Map Transaction Count", "Map Transaction Amount"])
   if Dropdown2 == "Map Transaction Count":
    cursor.execute('select Distinct(Year) from maptxn')
    Yearlist_m = cursor.fetchall()
    Year_list_m = pd.DataFrame(Yearlist_m, columns=cursor.column_names)
    
    col1, col2 = st.columns([10,1])
    with col1:
      Year_m= st.selectbox('Choose a Year from the Dropdown below:', Year_list_m,index=None,key=Year_list_m)
      cursor.execute('select Distinct(Quater) from maptxn')
      Quarterlist_m = cursor.fetchall()
      Quarter_list_m = pd.DataFrame(Quarterlist_m , columns=cursor.column_names)
      Quarterselect_m = st.selectbox('Choose a Quarter from the Dropdown below:', Quarter_list_m, index=None,key=Quarter_list_m)
      cursor.execute('select Distinct(State) from maptxn')
      Statelist_m = cursor.fetchall()
      State_list_m = pd.DataFrame(Statelist_m, columns=cursor.column_names)
      State_m = st.selectbox('Choose a State from the Dropdown below:', State_list_m,index=None,key=State_list_m)
      if Year_m is None:
       pass
      else:
       if Quarterselect_m is None and State_m is None:
        Year_Chart_Map_Count(Year_m)
       elif State_m is None:
        Map_txn_year_Quarter_(Quarterselect_m)
       elif Quarterselect_m is None:
        Map_Txn_count_state_yr(Year_m, State_m)
       else:
        Map_Txn_count_state_Q(Year_m, Quarterselect_m, State_m)

###################################################################MAPTRANSACTION AMOUNT#################################
   if Dropdown2 == "Map Transaction Amount":

    
    col1, col2 = st.columns([10,1])
    with col1:
      cursor.execute('select Distinct(Year) from maptxn')
      Yearlist_m = cursor.fetchall()
      Year_list_m = pd.DataFrame(Yearlist_m, columns=cursor.column_names)
      Year_m= st.selectbox('Choose a Year from the Dropdown below:', Year_list_m,index=None,key=Year_list_m)
      cursor.execute('select Distinct(Quater) from maptxn')
      Quarterlist_m = cursor.fetchall()
      Quarter_list_m = pd.DataFrame(Quarterlist_m , columns=cursor.column_names)
      Quarterselect_m = st.selectbox('Choose a Quarter from the Dropdown below:', Quarter_list_m, index=None,key=Quarter_list_m)
      cursor.execute('select Distinct(State) from maptxn')
      Statelist_m = cursor.fetchall()
      State_list_m = pd.DataFrame(Statelist_m, columns=cursor.column_names)
      State_m = st.selectbox('Choose a State from the Dropdown below:', State_list_m,index=None,key=State_list_m)

      if Year_m is None:
       pass
      else:
       if Quarterselect_m is None and State_m is None:
        Year_Chart_Map_Amt(Year_m)
       elif State_m is None:
        Map_txn_Amt_year_Quarter_(Quarterselect_m)
       elif Quarterselect_m is None:
        Map_Txn_Amt_state_yr(Year_m, State_m)
       else:
        Map_Txn_Amt_state_Q(Year_m, Quarterselect_m, State_m)

  if Dropdown2 =="Map User Data":
   Dropdown2 = st.radio("Select one of the below option:", ["Map User Count"])
   if Dropdown2 == "Map User Count":
    cursor.execute('select Distinct(Year) from mapusercount')
    Yearlist_m = cursor.fetchall()
    Year_list_m = pd.DataFrame(Yearlist_m, columns=cursor.column_names)
    
    col1, col2 = st.columns([10,1])
    with col1:
      Year_m= st.selectbox('Choose a Year from the Dropdown below:', Year_list_m,index=None,key=Year_list_m)
      cursor.execute('select Distinct(Quater) from mapusercount')
      Quarterlist_m = cursor.fetchall()
      Quarter_list_m = pd.DataFrame(Quarterlist_m , columns=cursor.column_names)
      Quarterselect_m = st.selectbox('Choose a Quarter from the Dropdown below:', Quarter_list_m, index=None,key=Quarter_list_m)
      cursor.execute('select Distinct(State) from mapusercount')
      Statelist_m = cursor.fetchall()
      State_list_m = pd.DataFrame(Statelist_m, columns=cursor.column_names)
      State_m = st.selectbox('Choose a State from the Dropdown below:', State_list_m,index=None,key=State_list_m)
      if Year_m is None:
       pass
      else:
       if Quarterselect_m is None and State_m is None:
        Year_Chart_Map_User_Count(Year_m)
       elif State_m is None:
        Map_User_Year_Quarter_(Quarterselect_m)
       elif Quarterselect_m is None:
        Map_User_count_state_yr(Year_m, State_m)
       else:
        Map_User_count_state_Q(Year_m, Quarterselect_m, State_m)

 with tab3:
  Dropdown3 = st.radio("Select one of the below option:", ["Top Transaction Data", "Top User Data"])
  if Dropdown3 == "Top Transaction Data":
   Dropdown_1a = st.radio("Select one of the below option:", ["District User Count", "District Transaction Amount", "Pincode User Count", "Pincode Transaction Amount"])
   if Dropdown_1a == "District User Count":
    cursor.execute('select Distinct(Year) from toptxn')
    Yearlist = cursor.fetchall()
    Year_list_t = pd.DataFrame(Yearlist, columns=cursor.column_names)
    
    col1, col2 = st.columns([10,1])
    with col1:
      for i, year in enumerate(Year_list_t):
       Year_t = st.selectbox(
        'Choose a Year from the Dropdown below:',
        Year_list_t,
        index=None,
        key=f"year_selectbox_{i}"  # Use a unique key for each widget
    )
      cursor.execute('select Distinct(Quater) from toptxn')
      Quarterlist = cursor.fetchall()
      Quarter_list_t = pd.DataFrame(Quarterlist , columns=cursor.column_names)
      
      for i, Quarter in enumerate(Quarter_list_t):
       Quarterselect_t = st.selectbox(
        'Choose a Quarter from the Dropdown below:',
        Quarter_list_t,
        index=None,
        key=f"Quarter_selectbox_{i}"  # Use a unique key for each widget
    )
      cursor.execute('select Distinct(State) from toptxn')
      Statelist = cursor.fetchall()
      State_list_t = pd.DataFrame(Statelist, columns=cursor.column_names)
      
      for i, State in enumerate(State_list_t):
       State_t = st.selectbox(
        'Choose a State from the Dropdown below:',
        State_list_t,
        index=None,
        key=f"State_selectbox_{i}"  # Use a unique key for each widget
    )

    #   cursor.execute('select Distinct(District_Name) from toptxn')
    #   Distlist = cursor.fetchall()
    #   Dist_list_t = pd.DataFrame(Distlist, columns=cursor.column_names)
      
    #   for i, District in enumerate(Dist_list_t):
    #    District_t = st.selectbox(
    #     'Choose a District from the Dropdown below:',
    #     Dist_list_t,
    #     index=None,
    #     key=f"District_Name_selectbox_{i}"  # Use a unique key for each widget
    # )

      if Year_t is None:
       pass
      else:
       if Quarterselect_t is None and State_t is None:
        Year_Chart_Dist_txn_Count(Year_t)
       elif State_t is None:
        top_dist_txn_year_Quarter_(Quarterselect_t)
       elif Quarterselect_t is None:
        Top_District_Txn_count_state_yr(Year_t, State_t)
       else:
        Top_District_Txn_count_state_Q(Year_t, Quarterselect_t, State_t)
    

#######################################################################TOPTRANSACTION AMOUNT#################################
   if Dropdown_1a == "District Transaction Amount":
    cursor.execute('select Distinct(Year) from toptxn')
    Yearlist = cursor.fetchall()
    Year_list_t = pd.DataFrame(Yearlist, columns=cursor.column_names)
    
    col1, col2 = st.columns([10,1])
    with col1:
      for i, year in enumerate(Year_list_t):
       Year_t = st.selectbox(
        'Choose a Year from the Dropdown below:',
        Year_list_t,
        index=None,
        key=f"year_selectbox_{i}"  # Use a unique key for each widget
    )
      cursor.execute('select Distinct(Quater) from toptxn')
      Quarterlist = cursor.fetchall()
      Quarter_list_t = pd.DataFrame(Quarterlist , columns=cursor.column_names)
      
      for i, Quarter in enumerate(Quarter_list_t):
       Quarterselect_t = st.selectbox(
        'Choose a Quarter from the Dropdown below:',
        Quarter_list_t,
        index=None,
        key=f"Quarter_selectbox_{i}"  # Use a unique key for each widget
    )
      cursor.execute('select Distinct(State) from toptxn')
      Statelist = cursor.fetchall()
      State_list_t = pd.DataFrame(Statelist, columns=cursor.column_names)
      
      for i, State in enumerate(State_list_t):
       State_t = st.selectbox(
        'Choose a State from the Dropdown below:',
        State_list_t,
        index=None,
        key=f"State_selectbox_{i}"  # Use a unique key for each widget
    )



      if Year_t is None:
       pass
      else:
       if Quarterselect_t is None and State_t is None:
        Year_Chart_Dist_txn_amt(Year_t)
       elif State_t is None:
        top_dist_txn_Amt_year_Quarter_(Quarterselect_t)
       elif Quarterselect_t is None:
        Top_District_Txn_amt_state_yr(Year_t, State_t)
       else:
        Top_District_Txn_amt_state_Q(Year_t, Quarterselect_t, State_t)
   
   if Dropdown_1a == "Pincode User Count":
    cursor.execute('select Distinct(Year) from toptxn')
    Yearlist = cursor.fetchall()
    Year_list_t = pd.DataFrame(Yearlist, columns=cursor.column_names)
    
    col1, col2 = st.columns([10,1])
    with col1:
      for i, year in enumerate(Year_list_t):
       Year_t = st.selectbox(
        'Choose a Year from the Dropdown below:',
        Year_list_t,
        index=None,
        key=f"year_selectbox_{i}"  # Use a unique key for each widget
    )
      cursor.execute('select Distinct(Quater) from toptxn')
      Quarterlist = cursor.fetchall()
      Quarter_list_t = pd.DataFrame(Quarterlist , columns=cursor.column_names)
      
      for i, Quarter in enumerate(Quarter_list_t):
       Quarterselect_t = st.selectbox(
        'Choose a Quarter from the Dropdown below:',
        Quarter_list_t,
        index=None,
        key=f"Quarter_selectbox_{i}"  # Use a unique key for each widget
    )
      cursor.execute('select Distinct(State) from toptxn')
      Statelist = cursor.fetchall()
      State_list_t = pd.DataFrame(Statelist, columns=cursor.column_names)
      
      for i, State in enumerate(State_list_t):
       State_t = st.selectbox(
        'Choose a State from the Dropdown below:',
        State_list_t,
        index=None,
        key=f"State_selectbox_{i}"  # Use a unique key for each widget
    )



      if Year_t is None:
       pass
      else:
       if Quarterselect_t is None and State_t is None:
        Year_Chart_Pincode_txn_Count(Year_t)
       elif State_t is None:
        top_pincode_txn_year_Quarter_(Quarterselect_t)
       elif Quarterselect_t is None:
        Top_Pincode_Txn_count_state_yr(Year_t, State_t)
       else:
        Top_Pincode_Txn_count_state_Q(Year_t, Quarterselect_t, State_t)

   if Dropdown_1a == "Pincode Transaction Amount":
    cursor.execute('select Distinct(Year) from toptxn')
    Yearlist = cursor.fetchall()
    Year_list_t = pd.DataFrame(Yearlist, columns=cursor.column_names)
    
    col1, col2 = st.columns([10,1])
    with col1:
      for i, year in enumerate(Year_list_t):
       Year_t = st.selectbox(
        'Choose a Year from the Dropdown below:',
        Year_list_t,
        index=None,
        key=f"year_selectbox_{i}"  # Use a unique key for each widget
    )
      cursor.execute('select Distinct(Quater) from toptxn')
      Quarterlist = cursor.fetchall()
      Quarter_list_t = pd.DataFrame(Quarterlist , columns=cursor.column_names)
      
      for i, Quarter in enumerate(Quarter_list_t):
       Quarterselect_t = st.selectbox(
        'Choose a Quarter from the Dropdown below:',
        Quarter_list_t,
        index=None,
        key=f"Quarter_selectbox_{i}"  # Use a unique key for each widget
    )
      cursor.execute('select Distinct(State) from toptxn')
      Statelist = cursor.fetchall()
      State_list_t = pd.DataFrame(Statelist, columns=cursor.column_names)
      
      for i, State in enumerate(State_list_t):
       State_t = st.selectbox(
        'Choose a State from the Dropdown below:',
        State_list_t,
        index=None,
        key=f"State_selectbox_{i}"  # Use a unique key for each widget
    )



      if Year_t is None:
       pass
      else:
       if Quarterselect_t is None and State_t is None:
        Year_Chart_Pincode_txn_amt(Year_t)
       elif State_t is None:
        top_pincode_txn_Amt_year_Quarter_(Quarterselect_t)
       elif Quarterselect_t is None:
        Top_Pincode_Txn_amt_state_yr(Year_t, State_t)
       else:
        Top_Pincode_Txn_amt_state_Q(Year_t, Quarterselect_t, State_t)        
###########################################################################TOPUSER DATA######################################

  if Dropdown3 =="Top User Data":
   Dropdown_1b = st.radio("Select one of the below option:", ["District Top User Count", "Pincode Top User Count"])
   if Dropdown_1b == "District Top User Count":
    cursor.execute('select Distinct(Year) from topusercount2')
    Yearlist = cursor.fetchall()
    Year_list_t = pd.DataFrame(Yearlist, columns=cursor.column_names)
    
    col1, col2 = st.columns([10,1])
    with col1:
      for i, year in enumerate(Year_list_t):
       Year_t = st.selectbox(
        'Choose a Year from the Dropdown below:',
        Year_list_t,
        index=None,
        key=f"year_selectbox_{i}"  # Use a unique key for each widget
    )
      cursor.execute('select Distinct(Quater) from topusercount2')
      Quarterlist = cursor.fetchall()
      Quarter_list_t = pd.DataFrame(Quarterlist , columns=cursor.column_names)
      
      for i, Quarter in enumerate(Quarter_list_t):
       Quarterselect_t = st.selectbox(
        'Choose a Quarter from the Dropdown below:',
        Quarter_list_t,
        index=None,
        key=f"Quarter_selectbox_{i}"  # Use a unique key for each widget
    )
      cursor.execute('select Distinct(State) from topusercount2')
      Statelist = cursor.fetchall()
      State_list_t = pd.DataFrame(Statelist, columns=cursor.column_names)
      
      for i, State in enumerate(State_list_t):
       State_t = st.selectbox(
        'Choose a State from the Dropdown below:',
        State_list_t,
        index=None,
        key=f"State_selectbox_{i}"  # Use a unique key for each widget
    )


      if Year_t is None:
       pass
      else:
       if Quarterselect_t is None and State_t is None:
        Year_Chart_Dist_top_User_Count(Year_t)
       elif State_t is None:
        dist_top_User_year_Quarter_(Quarterselect_t)
       elif Quarterselect_t is None:
        dist_top_User_state_yr(Year_t, State_t)
       else:
        dist_top_user_count_state_Q(Year_t, Quarterselect_t, State_t)

   if Dropdown_1b == "Pincode Top User Count":
    cursor.execute('select Distinct(Year) from topusercount2')
    Yearlist = cursor.fetchall()
    Year_list_t = pd.DataFrame(Yearlist, columns=cursor.column_names)
    
    col1, col2 = st.columns([10,1])
    with col1:
      for i, year in enumerate(Year_list_t):
       Year_t = st.selectbox(
        'Choose a Year from the Dropdown below:',
        Year_list_t,
        index=None,
        key=f"year_selectbox_{i}"  # Use a unique key for each widget
    )
      cursor.execute('select Distinct(Quater) from topusercount2')
      Quarterlist = cursor.fetchall()
      Quarter_list_t = pd.DataFrame(Quarterlist , columns=cursor.column_names)
      
      for i, Quarter in enumerate(Quarter_list_t):
       Quarterselect_t = st.selectbox(
        'Choose a Quarter from the Dropdown below:',
        Quarter_list_t,
        index=None,
        key=f"Quarter_selectbox_{i}"  # Use a unique key for each widget
    )
      cursor.execute('select Distinct(State) from topusercount2')
      Statelist = cursor.fetchall()
      State_list_t = pd.DataFrame(Statelist, columns=cursor.column_names)
      
      for i, State in enumerate(State_list_t):
       State_t = st.selectbox(
        'Choose a State from the Dropdown below:',
        State_list_t,
        index=None,
        key=f"State_selectbox_{i}"  # Use a unique key for each widget
    )


      if Year_t is None:
       pass
      else:
       if Quarterselect_t is None and State_t is None:
        Year_Chart_pincode_top_User_Count(Year_t)
       elif State_t is None:
        pincode_top_User_year_Quarter_(Quarterselect_t)
       elif Quarterselect_t is None:
        pincode_top_User_state_yr(Year_t, State_t)
       else:
        pincode_top_user_count_state_Q(Year_t, Quarterselect_t, State_t)       

elif select=='Queries':

  st.title("Please Select an Option from the Dropdown Below")

  Queries = st.selectbox("Query: ",
                      ['1.	What are the top 5 state with the highest sum of aggregated transaction count till date?',
                        '2.	What are the top 5 state with the lowest sum of aggregated transaction count till date?', 
                        '3.	What are the top 5 state with the highest sum of aggregated transaction amount till date?',
                        '4.	What are the top 5 state with the lowest sum of aggregated transaction amount till date?',
                        '5.	Which state has the highest registered users?',
                        '6.	Which phone brand has the highest registered user in the year 2022?',
                        '7.	Which district in India has the highest top transaction user count?',
                        '8.	Which district in India has the lowest top transaction user count in the year 2024?',
                        '9.	What is the overall average transaction amount in the state of Tamilnade in a year?',
                        '10.	What is the overall average transaction amount in India in a year?'])



  if Queries =='1.	What are the top 5 state with the highest sum of aggregated transaction count till date?':
   Query1 = commontable_aggtxn()
   agg_df= Query1.groupby(['State'])['Sumtxncount'].sum().reset_index()
   top_5_transactions = agg_df.sort_values(by='Sumtxncount', ascending=False).head(5)
   st.dataframe(top_5_transactions)
  elif Queries =='2.	What are the top 5 state with the lowest sum of aggregated transaction count till date?':
   Query2 = commontable_aggtxn()
   agg_df= Query2.groupby(['State'])['Sumtxncount'].sum().reset_index()
   bottom_5_transactions = agg_df.sort_values(by='Sumtxncount', ascending=True).head(5)
   st.dataframe(bottom_5_transactions)
  elif Queries== '3.	What are the top 5 state with the highest sum of aggregated transaction amount till date?':
   Query3 = commontable_aggtxn()
   agg_df= Query3.groupby(['State'])['Sumtxnamt'].sum().reset_index()
   top_5_transactions = agg_df.sort_values(by='Sumtxnamt', ascending=False).head(5)
   st.dataframe(top_5_transactions)
      
  elif Queries=='4.	What are the top 5 state with the lowest sum of aggregated transaction amount till date?':
   Query4 = commontable_aggtxn()
   agg_df= Query4.groupby(['State'])['Sumtxnamt'].sum().reset_index()
   bottom_5_transactions = agg_df.sort_values(by='Sumtxnamt', ascending=True).head(5)
   st.dataframe(bottom_5_transactions)

 
  elif Queries=='5.	Which state has the highest registered users?':
   Query5 = commontable_Reguser()
   agg_df= Query5.groupby(['State'])['SumRegUsers'].sum().reset_index()
   top_transactions = agg_df.sort_values(by='SumRegUsers', ascending=False).head(1)
   st.dataframe(top_transactions)  
      

  elif Queries=='6.	Which phone brand has the highest registered user in the year 2022?':
   Query6 = commontable_Reguser()
   agg_df= Query6.groupby(['Brand','Year'])['SumBrandUserCt'].sum().reset_index()
   agg_df_=(agg_df[agg_df['Year']==str(2022)]) 
   top_transactions = agg_df_.sort_values(by='SumBrandUserCt', ascending=False).head(1)
   st.dataframe(top_transactions)
    

  elif Queries=='7.	Which district in India has the highest top transaction user count?':
   Query7 = commontable_toptxn()
   agg_df= Query7.groupby(['District_Name','State'])['Sumdistusercount'].sum().reset_index()
   top_transactions = agg_df.sort_values(by='Sumdistusercount', ascending=False).head(1)
   st.dataframe(top_transactions)
      

  elif Queries=='8.	Which district in India has the lowest top transaction user count in the year 2024?':
   Query8 = commontable_toptxn()
   agg_df= Query8.groupby(['District_Name','State','Year'])['Sumdistusercount'].sum().reset_index()
   agg_df_=(agg_df[agg_df['Year']==str(2022)])
   top_transactions = agg_df_.sort_values(by='Sumdistusercount', ascending=True).head(1)
   st.dataframe(top_transactions)
      

  elif Queries=='9.	What is the overall average transaction amount in the state of Tamilnade in a year?':
   Query9 = commontable_aggtxn()
   
   agg_df_=(Query9[Query9['State']=='Tamil Nadu'])
   average_= agg_df_.groupby(['State','Year'])['Sumtxnamt'].mean().reset_index()
   
   st.dataframe(average_)
      

  elif Queries=='10.	What is the overall average transaction amount in India in a year?':
   Query10 = commontable_aggtxn()
   average_= Query10.groupby(['Year'])['Sumtxnamt'].mean().reset_index()
   
   st.dataframe(average_)
      
























































































##########################################################################################################################################################################################################################################################
##########################################################################################################################################################################################################################################################







    