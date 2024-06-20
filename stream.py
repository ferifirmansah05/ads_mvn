from pandas.core.api import Index
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pickle
import numpy as np
import subprocess
import plotly.express as px
import requests
import os

def download_file_from_github(url, save_path):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Memeriksa apakah permintaan berhasil
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded successfully and saved to {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download file: {e}")

def load_model(file_path):
    try:
        with open(file_path, 'rb') as file:
            model = pickle.load(file)
        print("Model loaded successfully")
        return model
    except Exception as e:
        print(f"Failed to load model: {e}")
        return None

def read(file_path):
    try:
        with open(file_path, 'rb') as file:
            df = pd.read_excel(file)
        print("Model loaded successfully")
        return df
    except Exception as e:
        print(f"Failed to load model: {e}")
        return None

url = 'https://github.com/ferifirmansah05/ads_mvn/edit/main/rf_model.pkl'
save_path = 'rf_model.pkl'
download_file_from_github(url, save_path)
if os.path.exists(save_path):
    model = load_model(save_path)
else:
    st.write("Model file does not exist")

url = 'https://github.com/ferifirmansah05/ads_mvn/blob/main/ad_conversion.xlsx'
save_path = 'ad_conversion.xlsx'
download_file_from_github(url, save_path)
if os.path.exists(save_path):
    df = read(save_path)
else:
    st.write("Excel file does not exist")


st.title("Prediction")
st.markdown('### Date Range')
bulan = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
tahun = list(range(2000, datetime.now().year + 2))

col = st.columns(2)

with col[0]:
  st.write("Select Start Month and Year:")
  selected_start_month = st.selectbox("Start Month", bulan, key='start_month')
  selected_start_year = st.selectbox("Start Year", tahun, key='start_year')

with col[1]:
  st.write("Select End Month and Year:")
  selected_end_month = st.selectbox("End Month", bulan, key='end_month')
  selected_end_year = st.selectbox("End Year", tahun, key='end_year')

start_month = bulan.index(selected_start_month) + 1  
start_year = selected_start_year

end_month = bulan.index(selected_end_month) + 1 
end_year = selected_end_year

def create_month_year_list(start_month, start_year, end_month, end_year):
  date_list = []
  datetime_list = []
  current_date = datetime(start_year, start_month, 1)

  while current_date <= datetime(end_year, end_month, 1):
      date_list.append(current_date.strftime("%B %Y"))
      datetime_list.append(current_date)
      if current_date.month == 12:
          current_date = datetime(current_date.year + 1, 1, 1)
      else:
          current_date = datetime(current_date.year, current_date.month + 1, 1)

  return date_list, datetime_list

bulan_tahun_list, bulan_tahun_list2 = create_month_year_list(start_month, start_year, end_month, end_year)

if "button_clicked" not in st.session_state:    
  st.session_state.button_clicked = False
def callback():
  st.session_state.button_clicked = True

if (    
st.button("Select", on_click=callback)     
or st.session_state.button_clicked   
 ):
  if len(bulan_tahun_list)<=12:
    st.markdown('### Input')
    col = st.columns(4)
    i=0
    input_x1 = []
    input_x2 = []

    for index, item in enumerate(bulan_tahun_list):
      with col[i]:
        st.write(item)
        spent = st.text_input('spent_usd', key=f'text_input_amount_{index}')
        impression = st.text_input('n_impressions', key=f'text_input_impres_{index}')
      input_x1.append(spent)
      input_x2.append(impression)
      i=i+1
      if i==4:
        i=0

    if st.button('Predict'):
      st.markdown(f'### {bulan_tahun_list[0]} - {bulan_tahun_list[-1]}')
      spent = [float(ele) for ele in input_x1]
      impression = [float(ele) for ele in input_x2]

      makeprediction = model.predict(np.array([spent,impression,np.log(impression)]).T)
      output=np.expm1(makeprediction)        
      output=np.round(output,2)

      df2 = pd.merge(pd.DataFrame({'Month':bulan_tahun_list2,'Predicted':output}),df[['Month','n_clicks']],on='Month',how='left').fillna(0).rename(columns={'n_clicks': 'Actual'})
      df2['Month']=df2['Month'].apply(lambda x: x.strftime("%m-%Y"))
      fig = px.line(df2, x='Month', y=['Predicted','Actual'], title='Actual vs Predicted Value', color_discrete_sequence=['red','blue'])
      
      def calculate_mape(actual, predicted):
        absolute_percentage_errors = abs((actual - predicted) / actual)
        mape = (sum(absolute_percentage_errors) / len(actual)) * 100
        formatted_mape = "{:.2f}".format(mape)  # Format to have 2 decimal places
        return formatted_mape

      mape = calculate_mape(df2[df2['Actual']>0]["Actual"], df2[df2['Actual']>0]["Predicted"])
      st.plotly_chart(fig)
      st.write(f'MAPE = {mape}%')

      def reset():
          st.session_state.start_month = 'January'
          st.session_state.end_month = 'January'
          st.session_state.start_year = 2000
          st.session_state.end_year = 2000
          st.session_state.button_clicked = False

      st.button('Reset', on_click=reset)
  else:
    st.warning('The maximum range of months is 12 months')


