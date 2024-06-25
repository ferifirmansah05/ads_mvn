import streamlit as st
import pandas as pd
import zipfile
import io
import os 
from glob import glob
import csv
import requests
import pickle
import os
import openpyxl
import numpy as np
import time
import datetime as dt
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import tempfile
import shutil

def download_file_from_github(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded successfully and saved to {save_path}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

def load_excel(file_path):
    with open(file_path, 'rb') as file:
        model = pd.read_excel(file, engine='openpyxl')
    return model

# URL file model .pkl di GitHub (gunakan URL raw dari file .pkl di GitHub)
url = 'https://raw.githubusercontent.com/ferifirmansah05/ads_mvn/main/database provinsi.xlsx'

# Path untuk menyimpan file yang diunduh
save_path = 'database provinsi.xlsx'

# Unduh file dari GitHub
download_file_from_github(url, save_path)

# Muat model dari file yang diunduh
if os.path.exists(save_path):
    df_prov = load_excel(save_path)
    print("Model loaded successfully")
else:
    print("Model file does not exist")

df_prov = df_prov[3:].dropna(subset=['Unnamed: 4']) 
df_prov.columns = df_prov.loc[3,:].values
df_prov = df_prov.loc[4:,]
df_prov = df_prov.loc[:265, ['Nama','Provinsi Alamat','Kota Alamat']]
df_prov = df_prov.rename(columns={'Nama':'Nama Cabang','Provinsi Alamat':'Provinsi', 'Kota Alamat': 'Kota/Kabupaten'})
list_cab = df_prov['Nama Cabang'].str.extract(r'\((.*?)\)')[0].values


st.title('Automate Breakdown Ojol')

all_cab = st.multiselect('Pilih Cabang', list_cab)
all_cab = list(all_cab)

# Tampilkan widget untuk memilih rentang tanggal
start_date = st.date_input("Pilih Tanggal Awal")
end_date = st.date_input("Pilih Tanggal Akhir")

# Jika tombol ditekan untuk memproses rentang tanggal
if (start_date is not None) & (end_date is not None):
    all_date = []
    current_date = start_date
    while current_date <= end_date:
        all_date.append(current_date.strftime('%Y-%m-%d'))
        current_date += dt.timedelta(days=1)

st.markdown('### Upload file *Zip')
uploaded_file = st.file_uploader("Pilih file ZIP", type="zip")

if uploaded_file is not None:
    st.write('File berhasil diupload')
    # Baca konten zip file

    if st.button('Process'):
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Ekstrak file ZIP ke direktori sementara
            with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                zip_ref.extractall(tmpdirname)
                    
            st.markdown('### Cleaning')
            st.write('GOJEK 1')
            main_folder = f'{tmpdirname}/_bahan/GOJEK 1'
            subfolders = [folder for folder in os.listdir(main_folder) if os.path.isdir(os.path.join(main_folder, folder))]
            combined_dataframes = []
            
            for subfolder in subfolders:
                # Glob pattern to get all CSV files in the subfolder
                files = glob(os.path.join(main_folder, subfolder, '*.csv'))
        
                # Check if there are CSV files in the subfolder
                if files:
                    # Concatenate CSV files within each subfolder
                    df = pd.concat([pd.read_csv(file) for file in files])
                    # Add a new column for the folder name
                    df['Folder'] = subfolder
                    combined_dataframes.append(df)
                else:
                    st.write(f"File in subfolder: {subfolder} does not exist. Please double check")
        
            if combined_dataframes:
                final_df = pd.concat(combined_dataframes)
                final_df.to_csv(f'{tmpdirname}/_merge/merge_Gojek 1.csv', index=False)
                st.write("File GOJEK 1 Concatenated")
            else:
                st.write("No dataframes to concatenate.")  
    
            st.write('GOJEK 2')
            main_folder = f'{tmpdirname}/_bahan/GOJEK 2'
            
            # Get the list of subfolders within the main folder
            subfolders = [folder for folder in os.listdir(main_folder) if os.path.isdir(os.path.join(main_folder, folder))]
            # List to store concatenated dataframes
            combined_dataframes = []
            
            # Iterate over each subfolder
            for subfolder in subfolders:
                # Glob pattern to get all CSV files in the subfolder
                files = glob(os.path.join(main_folder, subfolder, '*.csv'))
                st.write(files)
                # Concatenate CSV files within each subfolder
                dfs = [pd.read_csv(file) for file in files]
                if dfs:
                    df = pd.concat(dfs)
                    
                    # Add a new column for the folder name
                    df['Folder'] = subfolder
                    st.write(df)
                    combined_dataframes.append(df)
                else:
                    st.write(f"File in subfolder: {subfolder} does not exist. Please double check")
            st.write(combined_dataframes)
            # Check if there are any dataframes to concatenate
            if combined_dataframes:
                # Concatenate dataframes from all subfolders
                final_df_ = pd.concat(combined_dataframes)
                st.write(final_df)
                final_df.to_csv(f'{tmpdirname}/_merge/merge_Gojek 2.csv', index=False)
                st.write("File GOJEK 2 Concantenated")
            else:
                st.write("No dataframes to concatenate.")    
            st.write(final_df)
            
