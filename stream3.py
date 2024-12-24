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
import subprocess
from pandas.errors import ParserError


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

def list_files_in_directory(dir_path):
    # Fungsi untuk mencetak semua isi dari suatu direktori
    for root, dirs, files in os.walk(dir_path):
        st.write(f'Direktori: {root}')
        for file_name in files:
            st.write(f'  - {file_name}')

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

            st.markdown('### Cleaning & Preparing')
            st.write('CANCEL NOTA')
            main_folder = f'{tmpdirname}/_bahan/CANCEL_NOTA'
                        
            
            # Iterate over each subfolder
            files = glob(os.path.join(main_folder, '*.xlsx'))
            
            dfs = []
            for file in files:
                    try:
                            df = pd.read_excel(file,sheet_name='Rekap nota cancel & salah input', header=0)
                            df = df.loc[:,df.columns[:9]].dropna(subset=['Unnamed: 2']).reset_index(drop=True)
                            df.columns = df.loc[0,:].values
                            df = df.loc[1:,]
                            df = df[df['TANGGAL']!='TANGGAL']
                            df['TOTAL BILL'] = df['TOTAL BILL'].astype('float')
                            df['CAB'] = file.split('/')[-1].split(' ')[0]
                            df['KET'] = ''
                            df = df[df['TOTAL BILL']>0]
                            df['TOTAL BILL'] = df['TOTAL BILL'].astype('float')
                            df['TANGGAL'] = df['TANGGAL'].fillna('0').astype('int').astype('str')
                            dfs.append(df)
                    except Exception as excel_exception:
                            print(f"Error process {file} as Excel: {excel_exception}")
            
            # Check if there are any dataframes to concatenate
            if dfs:
                # Concatenate dataframes from all subfolders
                cn = pd.concat(dfs,ignore_index=True)
            
                st.write("File CANCEL NOTA Concatenated")
            else:
                st.write("No dataframes to concatenate.")

            cn['TOTAL BILL'] = cn['TOTAL BILL'].astype('float')
            cn['TANGGAL'] = cn['TANGGAL'].fillna('0').astype('int').astype('str')

            
            subfolders = all_cab
            dfinv = []
            st.write('GOJEK 1')
            main_folder = f'{tmpdirname}/_bahan'
            combined_dataframes = []
            
            for subfolder in subfolders:
                # Glob pattern to get all CSV files in the subfolder
                files = glob(os.path.join(main_folder, subfolder, 'Mie_Gacoan_*'))
            
                # Check if there are CSV files in the subfolder
                if files:
                    # Concatenate CSV files within each subfolder
                    for file in files:
                        df = pd.read_csv(file)
                        df = df.rename(columns={'Gross Sales':'Gross Amount'})
                        # Add a new column for the folder name
                        df['Folder'] = subfolder
                        combined_dataframes.append(df)
                else:
                    print(f"File in subfolder: {subfolder} does not exist. Please double check")
        
            if combined_dataframes:
                df_gojek1 = pd.concat(combined_dataframes)
              
                st.write("File GOJEK 1 Concatenated")
            else:
                st.write("No dataframes to concatenate.")  
                
            if 'df_gojek1' in locals():
                df_gojek1     =       df_gojek1.loc[:,['Waktu Transaksi',
                                                    'Folder',
                                                    'Nomor Pesanan',
                                                    'Gross Amount']].rename(columns={'Waktu Transaksi' : 'DATETIME',
                                                                                    'Folder' : 'CAB',
                                                                                    'Nomor Pesanan' : 'ID',
                                                                                    'Gross Amount' : 'NOM'}).fillna('')
                df_gojek1['DATETIME'] = df_gojek1['DATETIME'].str.replace('Apr', 'April')
                df_gojek1['DATETIME'] = df_gojek1['DATETIME'].str.replace('Jun', 'June')            
            
                # Parse datetime column
                df_gojek1['DATETIME']    =   pd.to_datetime(df_gojek1['DATETIME'], utc=True)
            
                df_gojek1['DATE']        =   df_gojek1['DATETIME'].dt.strftime('%d/%m/%Y')
                df_gojek1['TIME']        =   df_gojek1['DATETIME'].dt.time
                del df_gojek1['DATETIME']
            
                df_gojek1['NOM']         =   pd.to_numeric(df_gojek1['NOM']).astype(int)
            
                df_gojek1['CODE']        =   ''
            
                df_gojek1['KAT']         =   'GO RESTO'
                df_gojek1['SOURCE']      =   'INVOICE'
            
                # re-order columns
                df_gojek1        =   df_gojek1[['CAB', 'DATE', 'TIME', 'CODE', 'ID', 'NOM', 'KAT', 'SOURCE']]
                dfinv.append(df_gojek1)
                df_gojek1 = None
                st.write(f"File GOJEK 1 processed and saved")
            
            st.write('GOJEK 2')            
            # List to store concatenated dataframes
            combined_dataframes = []
            
            # Iterate over each subfolder
            for subfolder in subfolders:
                # Glob pattern to get all CSV files in the subfolder
                files = glob(os.path.join(main_folder, subfolder, 'Laporan Transaksi GoFood*'))
                dfs = []
                # Concatenate CSV files within each subfolder
                for file in files:
                    df = pd.read_csv(file)
                    df = df.rename(columns={'Gross Sales':'Gross Amount'})
                    dfs.append(df)   
                if dfs:
                    df = pd.concat(dfs)
                    # Add a new column for the folder name
                    df['Folder'] = subfolder
                    combined_dataframes.append(df)
                else:
                    print(f"No CSV files found in subfolder: {subfolder}")
            
            # Check if there are any dataframes to concatenate
            if combined_dataframes:
                # Concatenate dataframes from all subfolders
                df_gojek2 = pd.concat(combined_dataframes)
                
                st.write("File GOJEK 2 Concatenated")
            else:
                st.write("No dataframes to concatenate.")
                            
            if 'df_gojek2' in locals():
                #Read data merge GOJEK 2
                df_gojek2      =       df_gojek2.fillna('')
            
                #Rename columns to match the database schema
                df_gojek2     =       df_gojek2.loc[:,['Waktu Transaksi',
                                                    'Folder',
                                                    'Nomor Pesanan',
                                                    'Gross Amount']].rename(columns={'Waktu Transaksi' : 'DATETIME',
                                                                            'Folder' : 'CAB',
                                                                            'Nomor Pesanan' : 'ID',
                                                                            'Gross Amount' : 'NOM'}).fillna('')
                df_gojek2['DATETIME'] = df_gojek2['DATETIME'].str.replace('T', ' ').str.slice(0, 19)
                df_gojek2['DATETIME'] = df_gojek2['DATETIME'].str.replace('Apr', 'April')
                df_gojek2['DATETIME'] = df_gojek2['DATETIME'].str.replace('Jun', 'June')
                # Parse datetime column
                df_gojek2['DATETIME']    =   pd.to_datetime(df_gojek2['DATETIME'], utc=True)
            
                df_gojek2['DATE']        =   df_gojek2['DATETIME'].dt.strftime('%d/%m/%Y')
                df_gojek2['TIME']        =   df_gojek2['DATETIME'].dt.time
                del df_gojek2['DATETIME']
            
                df_gojek2['NOM']         =   pd.to_numeric(df_gojek2['NOM']).astype(int)
            
                df_gojek2['CODE']        =   ''
            
                df_gojek2['KAT']         =   'GO RESTO'
                df_gojek2['SOURCE']      =   'INVOICE'
            
                # re-order columns
                df_gojek2        =   df_gojek2[['CAB', 'DATE', 'TIME', 'CODE', 'ID', 'NOM', 'KAT', 'SOURCE']]
                dfinv.append(df_gojek2)
                df_gojek2 = None
                
                st.write(f"File GOJEK 2 processed and saved")

                
            st.write('GOJEK 3')
            main_folder = f'{tmpdirname}/_bahan/GOJEK 3/'
                        
            # Initialize an empty list to store dataframes
            dfs = []
            
            combined_dataframes = []
            # Iterate over each file in the folder
            for filename in os.listdir(main_folder):
                if filename.endswith('.csv'):  # Assuming all files are CSV format, adjust if needed
                    file_path = os.path.join(main_folder, filename)
                    # Read each file into a dataframe and append to the list
                    dfs.append(pd.read_csv(file_path))
                if filename.endswith('.xlsx'):  # Assuming all files are CSV format, adjust if needed
                    file_path = os.path.join(main_folder, filename)
                    # Read each file into a dataframe and append to the list
                    dfs.append(pd.read_excel(file_path))
            # Check if there are any dataframes to concatenate
            if dfs:
                # Concatenate all dataframes in the list into one dataframe
                concatenated_df = pd.concat(dfs, ignore_index=True)
            
                # Lookup
                storename = pd.read_excel(f'{tmpdirname}/_bahan/bahan/Store Name GOJEK.xlsx')
            
                for subfolder in storename['CAB'].unique():
                    df = concatenated_df[concatenated_df['Outlet name']==storename[storename['CAB']==subfolder]['Outlet name'].values[0]]
                    df['CAB'] = subfolder
                    combined_dataframes.append(df)
            
                # Export the concatenated dataframe to CSV in the specified path
                df_gojek3 = pd.concat(combined_dataframes)
            
                st.write("File GOJEK 3 Concatenated")
            else:
                st.write("No dataframes to concatenate.")
                
            if 'df_gojek3' in locals():
                # Read data merge GOJEK 3
                df_gojek3 = df_gojek3.fillna('')
            
                # Rename columns to match the database schema
                df_gojek3 = df_gojek3.loc[:, ['Transaction time', 'Order ID', 'Amount', 'CAB']].rename(
                    columns={'Transaction time': 'DATETIME', 'Order ID': 'ID', 'Amount': 'NOM'}).fillna('')
            
                #df_gojek3['DATETIME'] = df_gojek3['DATETIME'].str.replace('T', ' ').str.slice(0, 19)
                #df_gojek3['DATETIME'] = df_gojek3['DATETIME'].str.replace('Apr', 'April')
                #df_gojek3['DATETIME'] = df_gojek3['DATETIME'].str.replace('Jun', 'June')
                df_gojek3['ID'] = df_gojek3['ID'].str.replace("'", '').str.slice(0, 19)
            
                # Parse datetime column
                df_gojek3['DATETIME'] = pd.to_datetime(df_gojek3['DATETIME'], utc=True)
            
                df_gojek3['DATE'] = df_gojek3['DATETIME'].dt.strftime('%d/%m/%Y')
                df_gojek3['TIME'] = df_gojek3['DATETIME'].dt.time
                del df_gojek3['DATETIME']
            
                df_gojek3['NOM'] = pd.to_numeric(df_gojek3['NOM']).astype(int)
            
                df_gojek3['CODE'] = ''
            
                df_gojek3['KAT'] = 'GO RESTO'
                df_gojek3['SOURCE'] = 'INVOICE'
            
                # Re-order columns
                df_gojek3 = df_gojek3[['CAB', 'DATE', 'TIME', 'CODE', 'ID', 'NOM', 'KAT', 'SOURCE']]
                dfinv.append(df_gojek3)
                df_gojek3 = None
                st.write(f"File GOJEK 3 processed and saved")
            
            st.write('SHOPEE FOOD')
            main_folder = f'{tmpdirname}/_bahan'
            
            # List to store concatenated dataframes
            combined_dataframes = []
            
            # Iterate over each subfolder
            for subfolder in subfolders:
                # Glob pattern to get all CSV files in the subfolder
                files = glob(os.path.join(main_folder, subfolder, 'Shopeefood_Income_Details*'))
            
                # Concatenate CSV files within each subfolder
                dfs = [pd.read_csv(file) for file in files]
                if dfs:
                    df = pd.concat(dfs)
                    # Add a new column for the folder name
                    df['Folder'] = subfolder
                    combined_dataframes.append(df)
                else:
                    print(f"File in subfolder: {subfolder} does not exist. Please double check")
            
            # Check if there are any dataframes to concatenate
            if combined_dataframes:
                # Concatenate dataframes from all subfolders
                df_shopee = pd.concat(combined_dataframes, ignore_index=True)
                st.write("File SHOPEE FOOD Concatenated")
            else:
                st.write("No dataframes to concatenate.")
                
            if 'df_shopee' in locals():
                # Read data merge Shopee Food
                df_shopee = df_shopee.fillna('')
            
                #Rename columns to match the database schema
                df_shopee   =   df_shopee.loc[:,['Order Pick up ID',
                                                        'Folder',
                                                        'Order Complete/Cancel Time',
                                                        'Order Amount',
                                                        'Order Status']].rename(columns={'Order Pick up ID' : 'ID',
                                                                                        'Folder' : 'CAB',
                                                                                        'Order Complete/Cancel Time' : 'DATETIME',
                                                                                        'Order Amount' : 'NOM',
                                                                                        'Order Status' : 'Status'}).fillna('')
            
                #df_shopee['DATETIME'] = df_shopee['DATETIME'].str.replace('Apr', 'April')
                #df_shopee['DATETIME'] = df_shopee['DATETIME'].str.replace('Jun', 'June')            
                df_shopee['DATETIME']    =   pd.to_datetime(df_shopee['DATETIME'], format='%d/%m/%Y %H:%M:%S')
                df_shopee['DATE']        =   df_shopee['DATETIME'].dt.strftime('%d/%m/%Y')
                df_shopee['TIME']        =   df_shopee['DATETIME'].dt.time
                del df_shopee['DATETIME']
                df_shopee = df_shopee[df_shopee['NOM']!='']
                df_shopee['NOM']         =   pd.to_numeric(df_shopee['NOM']).astype(int)
                df_shopee                =  df_shopee.drop(df_shopee[df_shopee['Status'] == 'Cancelled'].index)
            
                df_shopee['CODE']        =   ''
            
                df_shopee['KAT']         =   'SHOPEEPAY'
                df_shopee['SOURCE']      =   'INVOICE'
            
                # re-order columns
                df_shopee                =   df_shopee[['CAB', 'DATE', 'TIME', 'CODE', 'ID', 'NOM', 'KAT', 'SOURCE']]
                dfinv.append(df_shopee)
                df_shopee = None
                st.write(f"File SHOPEE FOOD processed and saved")


            st.write('GRAB')
            # Set the directory containing the files
            folder_path = f'{tmpdirname}/_bahan/GRAB/csv'
            
            # Initialize an empty list to store dataframes
            dfs = []
            
            # Iterate over each file in the folder
            for filename in os.listdir(folder_path):
                if filename.endswith('.csv'):  # Assuming all files are CSV format, adjust if needed
                    file_path = os.path.join(folder_path, filename)
                    # Read each file into a dataframe and append to the list
                    dfs.append(pd.read_csv(file_path))
            
            # Check if there are any dataframes to concatenate
            if dfs:
                # Concatenate all dataframes in the list into one dataframe
                df_grab = pd.concat(dfs, ignore_index=True)
            
                # Lookup
                storename = pd.read_excel(f'{tmpdirname}/_bahan/bahan/Store Name GRAB.xlsx')

                df_grab = pd.merge(df_grab, storename, how='left', on='Store Name').fillna('')
                df_grab = df_grab[df_grab['CAB'] != '']
           
                st.write("File GRAB *csv Concatenated")
            else:
                st.write("There are no files GRAB *csv to concatenate.")
            
            # Specify the directory where the files are located
            folder_path = f'{tmpdirname}/_bahan/GRAB/xls'
            
            # Initialize a list to store DataFrames from each file
            dataframes = []
            
            # Loop through each file in the folder
            for file_name in os.listdir(folder_path):
                if file_name.endswith('.xls'):  # Make sure only files with .xls extension are processed
                    file_path = os.path.join(folder_path, file_name)
                    try:
                        # Attempt to read the file as CSV first
                        df = pd.read_csv(file_path, encoding='utf-8')
                        dataframes.append(df)
                    except Exception as csv_exception:
                        st.write(f"Error reading {file_path} as CSV: {csv_exception}")
                        try:
                            # If reading as CSV fails, try reading it as an Excel file
                            df = pd.read_excel(file_path, engine='xlrd')
                            dataframes.append(df)
                        except Exception as excel_exception:
                            st.write(f"Error reading {file_path} as Excel: {excel_exception}")
            
            # Check if any files were processed
            if dataframes:
                # Concatenate all DataFrames into one DataFrame
                df_grab2 = pd.concat(dataframes, ignore_index=True)
            
                # Lookup
                storename = pd.read_excel(f'{tmpdirname}/_bahan/bahan/Store Name GRAB.xlsx')
                df_grab2 = pd.merge(df_grab2, storename, how='left', on='Store Name').fillna('')
                df_grab2 = df_grab2[df_grab2['CAB'] != '']
            
                st.write("File GRAB *xls Concatenated")
            else:
                st.write("No dataframes GRAB *xls to concatenate.")
                
            # Process based on the existence of files
            if ('df_grab' in locals()) or ('df_grab2' in locals()):
                # Initialize an empty list to hold dataframes
                dfs = []
            
                # Read the existing files
                if 'df_grab' in locals():
                    dfs.append(df_grab)
                if 'df_grab2' in locals():
                    dfs.append(df_grab2)
            
                # Concatenate all dataframes in the list
                if dfs:
                    df_grab = pd.concat(dfs, ignore_index=True)
            
                    # Rename columns to match the database schema
                    df_grab = df_grab.loc[:, ['CAB', 'Updated On', 'Category', 'Status', 'Short Order ID', 'Amount', 'Net Sales']].rename(
                        columns={'Store Name': 'CAB', 'Updated On': 'DATETIME', 'Status': 'Status', 'Short Order ID': 'ID', 'Net Sales': 'NOM1'}).fillna('')
            
                    def parse_datetime(date_str):
                        formats = ['%d %b %Y %I:%M %p', '%d/%m/%Y %H:%M']
                        for fmt in formats:
                            try:
                                return pd.to_datetime(date_str, format=fmt)
                            except (ValueError, TypeError):
                                continue
                        return None  # Return None if no format matches
            
                    # Apply the custom parsing function to the DATETIME column
                    df_grab['DATETIME'] = df_grab['DATETIME'].apply(parse_datetime)

                    # Extract DATE and TIME from DATETIME, then delete the DATETIME column
                    df_grab['DATE'] = df_grab['DATETIME'].dt.strftime('%d/%m/%Y')
                    df_grab['TIME'] = df_grab['DATETIME'].dt.time
                    del df_grab['DATETIME']
            
                    # Convert 'NOM' and 'Amount' columns to numeric, handling non-numeric issues
                    df_grab['NOM1'] = pd.to_numeric(df_grab['NOM1']).astype(float)
                    #df_grab['Amount'] = pd.to_numeric(df_grab['Amount'].astype('str').str.replace('.', ''), errors='coerce').astype(float)
            
                    # Drop rows where 'Category' is 'Cancelled'
                    df_grab = df_grab[df_grab['Category'] != 'Cancelled']
            
                    # Define conditions and choices for 'NOM'
                    df_grabcon = [
                        (df_grab['Category'] == 'Adjustment'),
                        (df_grab['Category'] == 'Payment'),
                    ]
                    pilih = [df_grab['Amount'], df_grab['NOM1']]
                    df_grab['NOM'] = np.select(df_grabcon, pilih, default='Cek')
            
                    # Define conditions and choices for 'ID'
                    df_grabcon2 = [
                        (df_grab['Category'] == 'Adjustment'),
                        (df_grab['Category'] == 'Payment'),
                    ]
                    pilih2 = [df_grab['ID'] + 'Adj', df_grab['ID']]
                    df_grab['ID'] = np.select(df_grabcon2, pilih2, default='Cek')
            
                    # Additional processing
                    df_grab['CODE'] = ''
                    df_grab['KAT'] = 'GRAB FOOD'
                    df_grab['SOURCE'] = 'INVOICE'
            
                    df_grab = df_grab[['CAB', 'DATE', 'TIME', 'CODE', 'ID', 'NOM', 'KAT', 'SOURCE']]
            
                    # Filter CAB
                    df_grab = df_grab[df_grab['CAB'] != '']
            
                    # Save the final result to a new CSV file
                    dfinv.append(df_grab)
                    df_grab = None
                    st.write(f"File GRAB processed and saved")
                        
            
            st.write('QRIS SHOPEE')
            combined_dataframes = []
            
            # Iterate over each subfolder
            for subfolder in subfolders:
                # Glob pattern to get all CSV files in the subfolder
                files = glob(os.path.join(main_folder, subfolder, 'settlement_report*'))
                dfs = []
                # Concatenate CSV files within each subfolder
                for file in files:
                    try:
                        # Try reading the file as a CSV
                        df = pd.read_csv(file)
                        if len(df.columns)<3:
                            df = pd.read_csv(file,sep=';',dtype=str)
                        df['Folder'] = subfolder
                        dfs.append(df)
                        
                    except ParserError or ValueError:
                        try:
                            # If reading as CSV fails, try reading it as an Excel file
                            df = pd.read_csv(file,sep=';',dtype=str)
                            df['Folder'] = subfolder
                            dfs.append(df)
                        except Exception as ex:
                            # If both CSV and Excel reading fail, raise an error
                            print(f"Failed to read file. Error: {ex}")
                
                if dfs:
                    df = pd.concat(dfs)
                    # Add a new column for the folder name
                    #df['Folder'] = subfolder
                    combined_dataframes.append(df)
                    

            
            # Check if there are any dataframes to concatenate
            if combined_dataframes:
                # Concatenate dataframes from all subfolders
                df_qris = pd.concat(combined_dataframes, ignore_index=True)
                try:
                    df_qris['Update Time'] = pd.to_datetime(df_qris['Update Time'], format='%d/%m/%Y %H:%M', errors='coerce').fillna(pd.to_datetime(df_qris['Update Time'],format='%Y-%m-%d %H:%M:%S', errors='ignore'))
                    df_qris['DATE'] = df_qris['Update Time'].dt.strftime('%d/%m/%Y')
                    df_qris['TIME'] = df_qris['Update Time'].dt.time
                except Exception as e:
                    print(f"Error formatting time: {e}")
                st.write("File QRIS SHOPEE Concatenated")
            else:
                st.write("No dataframes to concatenate.")
            if 'df_qris' in locals():
                # Read data merge QRIS Shopee
                df_qris = df_qris[~df_qris['Transaction ID'].isna()]
                df_qris = df_qris.fillna('')
                # Rename columns to match the database schema
                df_qris = df_qris.loc[:, ['Folder', 'Transaction ID', 'DATE', 'TIME', 'Transaction Amount', 'Transaction Type']].rename(
                    columns={'Folder': 'CAB', 'Transaction ID': 'ID', 'Transaction Amount': 'NOM'}).fillna('')
                df_qris['DATE'] = df_qris['DATE'].str.replace('Apr', 'April')          
                df_qris['DATE'] = df_qris['DATE'].str.replace('Jun', 'June')
            
                df_qris['DATE'] = pd.to_datetime(df_qris['DATE'], format='%d/%m/%Y')
                df_qris['DATE'] = df_qris['DATE'].dt.strftime('%d/%m/%Y')
                df_qris['TIME'] = pd.to_datetime(df_qris['TIME'], format='%H:%M:%S')
                df_qris['TIME'] = df_qris['TIME'].dt.time
            
                df_qris['NOM'] = pd.to_numeric(df_qris['NOM']).astype(float)
            
                df_qris['CODE'] = ''
                df_qris['KAT'] = 'QRIS SHOPEE'
                df_qris['SOURCE'] = 'INVOICE'
            
                # Filter out 'Withdrawal' transactions
                df_qris = df_qris[df_qris['Transaction Type'] != 'Withdrawal']
            
                # Re-order columns
                df_qris = df_qris[['CAB', 'DATE', 'TIME', 'CODE', 'ID', 'NOM', 'KAT', 'SOURCE']]
                dfinv.append(df_qris)
                df_qris = None
                st.write(f"File QRIS SHOPEE processed and saved")

            
            st.write('QRIS IA')
            #Specify the directory where the HTML files are located
            dataframes = []
            
            # Iterate over each subfolder
            for subfolder in subfolders:
                # Glob pattern to get all CSV files in the subfolder
                files = glob(os.path.join(main_folder, subfolder, 'QRIS-id*'))
                # Concatenate CSV files within each subfolder
                for file in files:
                        try:
                            # Read the HTML tables into a list of DataFrames
                            html_tables = pd.read_html(file, header=0, encoding='ISO-8859-1')  # Specify header as 0
                            # If there are tables in the HTML content
                            if html_tables:
                                # Iterate through each DataFrame in the list
                                for df in html_tables:
                                    # Add a new column with the subfolder name
                                    df['Folder'] = subfolder
                                    dataframes.append(df)
                        except Exception as e:
                            ptint(f"Error reading {file_path}: {e}")
            
            if dataframes:
                # Concatenate all DataFrames into one DataFrame
                df_qrisia = pd.concat(dataframes, ignore_index=True)
            
                df_qrisia = df_qrisia[df_qrisia['ID Transaksi']      !=      "Summary"]
              
                st.write("File QRIS TELKOM Concatenated")
            else:
                st.write("No dataframes to concatenate.")

            if 'df_qrisia' in locals():
                # Read data merge QRIS Telkom
                df_qrisia = df_qrisia.fillna('')
            
                # Rename columns to match the database schema
                df_qrisia = df_qrisia.loc[:, ['Folder', 'Waktu Transaksi', 'Nama Customer', 'Nominal (termasuk Tip)']].rename(
                    columns={'Folder': 'CAB', 'Waktu Transaksi': 'DATETIME', 'Nama Customer': 'ID', 'Nominal (termasuk Tip)': 'NOM'}).fillna('')
                df_qrisia['DATETIME'] = df_qrisia['DATETIME'].str.replace('Apr', 'April')            
                df_qrisia['DATETIME'] = df_qrisia['DATETIME'].str.replace('Jun', 'June')
            
                # Convert 'DATETIME' column to datetime
                df_qrisia['DATETIME'] = pd.to_datetime(df_qrisia['DATETIME'])
            
                # Extract date and time into new columns
                df_qrisia['DATE'] = df_qrisia['DATETIME'].dt.strftime('%d/%m/%Y')
                df_qrisia['TIME'] = df_qrisia['DATETIME'].dt.time
                del df_qrisia['DATETIME']
            
                df_qrisia['CODE'] = ''
                df_qrisia['KAT'] = 'QRIS TELKOM'
                df_qrisia['SOURCE'] = 'INVOICE'
            
                # Re-order columns
                df_qrisia = df_qrisia[['CAB', 'DATE', 'TIME', 'CODE', 'ID', 'NOM', 'KAT', 'SOURCE']]
                dfinv.append(df_qrisia)
                df_qrisia = None
                st.write(f"File QRIS TELKOM processed and saved")


            st.write('QRIS ESB')
            # Specify the directory where the HTML files are located
            folder_path = f'{tmpdirname}/_bahan/QRIS_ESB/'
            
            # Initialize a list to store DataFrames from each file
            dataframes = []
            
            # Loop through each file in the folder
            for file_name in os.listdir(folder_path):
                if file_name.endswith('.xlsx'):  # Make sure only HTML files are processed
                    file_path = os.path.join(folder_path, file_name)
                    df = pd.read_excel(file_path, header=12)
                    df = df[~(df['Tanggal Transaksi'].isna()) & (df['Payment Method Name']!='CASH')].loc[:,['Branch name','Tanggal Transaksi','POS Sales Number','Grand Total']]
                    dataframes.append(df)
            if dataframes:
                df_esb = pd.concat(dataframes, ignore_index=True)
                # Save the merged DataFrame to a CSV file without row index

                st.write("FIle QRIS ESB Concatenated")
            else:
                st.write("No dataframes to concatenate.")     

            # Check if the file exists
            if 'df_esb' in locals():
                # Read the CSV file
                df_esb = df_esb.fillna('')
            
                # Add new columns with default values
                df_esb['SOURCE'] = 'INVOICE'
                df_esb['CODE'] = ''
                df_esb['KAT'] = 'QRIS ESB'
            
                # Convert 'Transaction Date' to datetime and extract date and time components
                df_esb['Tanggal Transaksi'] = pd.to_datetime(df_esb['Tanggal Transaksi'], format='%Y-%m-%d %H:%M:%S')
                df_esb['DATE'] = df_esb['Tanggal Transaksi'].dt.strftime('%d/%m/%Y')
                df_esb['TIME'] = df_esb['Tanggal Transaksi'].dt.time
                        
                # Extract text after the dot in the 'CAB' column
                df_esb['CAB'] = df_esb['Branch name'].str.split('.').str[1]
            
                # Rename columns to match the database schema
                df_esb = df_esb.rename(columns={'POS Sales Number': 'ID', 'Grand Total': 'NOM'}).fillna('')
            
                # Select and sort the relevant columns
                df_esb = df_esb.loc[:, ['CAB', 'DATE', 'TIME', 'CODE', 'ID', 'NOM', 'KAT', 'SOURCE']].sort_values('DATE', ascending=False)
            
                dfinv.append(df_esb)
                df_esb = None
                st.write("File QRIS ESB processed and saved")
    
            
            st.write('WEB')
            # Specify the directory where the HTML files are located
            folder_path = main_folder+'/WEB/'
            
            # Initialize a list to store DataFrames from each file
            dataframes = []
            
            # Loop through each file in the folder
            for file_name in os.listdir(folder_path):
                if file_name.endswith('.xls'):  # Make sure only HTML files are processed
                    file_path = os.path.join(folder_path, file_name)
                    try:
                        html_file = pd.read_html(file_path, encoding='ISO-8859-1')
                        # Get the DataFrame corresponding to each file
                        if html_file:
                            df = html_file[0].iloc[1:]  # Remove the first row
                            df.columns = df.iloc[0,:]
                            if 'BILL' in df.columns:
                                df = df.drop(columns='TOTAL').rename(columns={'BILL':'TOTAL'})
                            dataframes.append(df)
                    except Exception as e:
                        st.write(f"Error reading {file_path}: {e}")
                        
                if file_name.endswith('.xlsx'):
                    file_path = os.path.join(folder_path, file_name)
                    try:
                        df = pd.read_excel(file_path)
                        # Get the DataFrame corresponding to each file
                        df.columns = df.iloc[0,:]
                        if 'BILL' in df.columns:
                            df = df.drop(columns='TOTAL').rename(columns={'BILL':'TOTAL'})
                        df = df[~df['DATE'].isin(['DATE','TOTAL'])]
                        df['DATE'] = df['DATE'].astype(str).str[:10]
                        dataframes.append(df)
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
                        
            # Check if any HTML files were processed
            if dataframes:
                # Concatenate all DataFrames into one DataFrame
                dfweb = pd.concat(dataframes, ignore_index=True)
                #dfweb.columns= dfweb.iloc[0,:]
            
                st.write("FIle WEB Concatenated")
            else:
                st.write("No dataframes to concatenate.")           

            if 'dfweb' in locals(): 
                #dfweb['DATE'] = dfweb['DATE'].str.replace('Apr', 'April')            
                #dfweb['DATE'] = dfweb['DATE'].str.replace('Jun', 'June')
                
                dfweb['SOURCE']     =   'WEB'
                
                #Rename columns to match the database schema
                dfweb       =       dfweb.rename(columns={'CO':'TIME','TOTAL':'NOM2','KATEGORI':'KAT','CUSTOMER':'ID'}).fillna('')
                
                dfweb         =   dfweb[dfweb['DATE'].isin(all_date)]
                dfweb['DATE'] = pd.to_datetime(dfweb['DATE'])
                dfweb['DATE'] = dfweb['DATE'].dt.strftime('%d/%m/%Y')
                dfweb = dfweb[dfweb['CAB'].isin(all_cab)]

                dfweb       =       dfweb.loc[:,['CAB','DATE','TIME','CODE','ID','NOM2','DISC','KAT','SOURCE']]#.sort_values('DATE', ascending=[False])
                
                dfweb       =       dfweb[dfweb['TIME']     !=      'TOTAL']
                dfweb       =       dfweb[dfweb['TIME']     !=      'CO']
                
                
                def convert_time(x):
                    try:
                        return pd.to_datetime(x).strftime('%H:%M:%S')
                    except ValueError:
                        try:
                            return pd.to_datetime(x, format='%H:%M:%S').strftime('%H:%M:%S')
                        except ValueError as e:
                            return pd.NaT
                            
                #dfweb['TIME'] = dfweb['TIME'].apply(convert_time)
                dfweb['TIME'] = pd.to_datetime(dfweb['TIME'], errors='coerce').fillna(pd.to_datetime(dfweb['TIME'], format='%H:%M:%S',errors='coerce')).dt.strftime('%H:%M:%S')
                dfweb['DISC'] = dfweb['DISC'].replace('',0).fillna(0)
                #st.write(dfweb)
                dfweb['NOM'] = dfweb.apply(lambda row: float(row['NOM2'])+float(row['DISC']) if (str(row['NOM2']).isnumeric()) else '',axis=1)
                dfweb = dfweb.drop(columns='DISC')

                dfweb['KAT'] = dfweb['KAT'].replace({'SHOPEE PAY': 'SHOPEEPAY', 'SHOPEEFOOD INT': 'SHOPEEPAY', 'GORESTO': 'GO RESTO','GOFOOD':'GO RESTO' ,'GRAB': 'GRAB FOOD', 'QRIS ESB ORDER':'QRIS ESB'})

            dfinv = pd.concat(dfinv, ignore_index = True).fillna('')
            dfinv = dfinv[['CAB', 'DATE', 'TIME', 'CODE', 'ID', 'NOM', 'KAT', 'SOURCE']]
            dfinv = dfinv[(dfinv['CAB'].isin(all_cab))]
            dfinv = dfinv[dfinv['DATE']     !=      '']
            dfinv['DATE'] = pd.to_datetime(dfinv['DATE'], format='%d/%m/%Y')
            dfinv   =   dfinv[dfinv['DATE'].isin(all_date)] #CHANGE
            dfinv['DATE'] = dfinv['DATE'].dt.strftime('%d/%m/%Y')
            final_merge = pd.concat([dfinv,dfweb.drop(columns='NOM').rename(columns={'NOM2':'NOM'})])
            
            st.markdown('### Processing')
            all_kat = ['GOJEK', 'QRIS SHOPEE', 'GRAB','SHOPEEPAY', 'QRIS ESB','QRIS TELKOM','EDC']
            ket = ''
            time_go = 150
            time_qs = 5
            time_gf = 150
            time_sp = 150
            time_qe = 150
            time_qt = 150
            
            
            dfinv['DATE'] = pd.to_datetime(dfinv['DATE'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
            dfinv['DATE'] = pd.to_datetime(dfinv['DATE'], format='%Y-%m-%d')
            
            try:
                dfweb['DATE'] = pd.to_datetime(dfweb['DATE'], format='%d/%m/%Y')
            except ValueError:
                try:
                    dfweb['DATE'] = pd.to_datetime(dfweb['DATE'], format='%Y-%m-%d')
                except ValueError as e:
                    print(f"Error dalam mengonversi tanggal: {e}")

            dfweb['TIME'] = pd.to_datetime(dfweb['DATE'].dt.strftime('%Y-%m-%d') + ' ' + dfweb['TIME'])
            dfinv['TIME'] = pd.to_datetime(dfinv['DATE'].dt.strftime('%Y-%m-%d') + ' ' + dfinv['TIME'].astype(str))
            
            dfinv = dfinv[~(dfinv['NOM']=='Cek')]
            
            dfinv['NOM'] = pd.to_numeric(dfinv['NOM'])
            dfweb['NOM'] = pd.to_numeric(dfweb['NOM'])
            
            dfinv = dfinv[dfinv['NOM']!=0]
            dfweb = dfweb[dfweb['NOM']!=0]
            
            dfinv['KET']   =   ""
            dfweb['KET']   =   ""
            dfinv['HELP']   =   ""
            dfweb['HELP']   =   ""
            
            dfweb['KAT'] = dfweb['KAT'].str.upper()
            cash = dfweb[dfweb['KAT']=='CASH']
            
            for wib in dfinv['CAB'].unique():
                if wib in ['MKSAHM', 'BPPHAR', 'MKSPER', 'MKSTUN', 'MKSPOR', 'MKSPET', 'MKSRAT','SMRYAM', 'SMRAHM']:
                    dfinv.loc[dfinv[dfinv['CAB']==wib].index, 'TIME'] = dfinv.loc[dfinv[dfinv['CAB']==wib].index, 'TIME'] + dt.timedelta(hours=1,minutes=1)
                    
            def difference(value1, value2):
                diff = float(value1) - float(value2)
                return f' (+{str(int(diff))})'
            def label_1(x):
                if 'Selisih' in x:
                    return 'Selisih IT'
                if 'Balance' in x:
                    return 'Balance'
                else:
                    return x
            
            for cab in all_cab:
                st.write(cab)
                for date in all_date:
                    st.write(date)

                    if not ((dfinv[(dfinv['KAT']  ==  "GO RESTO") & (dfinv['CAB']  ==  cab) & (dfinv['DATE']==date)].empty) or
                         (dfweb[(dfweb['KAT']  ==  "GO RESTO") & (dfweb['CAB']  ==  cab) & (dfweb['DATE']==date)].empty)) :
                        goi   =   dfinv[dfinv['KAT']  ==  "GO RESTO"]
                        gow   =   dfweb[dfweb['KAT']  ==  "GO RESTO"]
                        goi   =   goi[goi['CAB']  ==  cab]
                        gow   =   gow[gow['CAB']  ==  cab]
                        goi = goi[goi['DATE']==date]
                        gow = gow[gow['DATE']==date]
            
                        goi = goi.sort_values(by=['CAB', 'NOM', 'TIME'], ascending=[True, True, False]).reset_index(drop=True)
                        gow = gow.sort_values(by=['CAB', 'NOM', 'TIME'], ascending=[True, True, False]).reset_index(drop=True)
                        
                        goi.drop_duplicates(inplace=True)
                        gow['ID2'] = gow['ID'].apply(lambda x: x.split(' - ')[-1] if ' - ' in x else '')
                        goi['ID2'] = goi['ID']
                        for i in cn[(cn['TANGGAL']==str(int(re.findall(r'\d+', date)[-1]))) & (cn['CAB']==cab) & (cn['TYPE BAYAR']=='GO RESTO')].index:
                                x = gow[(gow['DATE']==date) & (gow['NOM']==cn.loc[i,'TOTAL BILL'])].index
                                if len(x)>=1:
                                    gow.loc[gow.loc[x,'ID'].apply(lambda x: fuzz.ratio(re.sub(r'\d+', '', str(x).upper()), re.sub(r'\d+', '', str(cn.loc[i,'NAMA TAMU']).upper()))).sort_values().index[-1],'KET'] = 'Cancel Nota'
                                    cn.loc[i, 'KET'] = 'Done'
                        goi['KET'] = goi['ID']
                        gow2 = gow[gow['ID2']!=''].reset_index(drop=True)
                        gow = gow[gow['ID2']==''].reset_index(drop=True)
                        def compare_time(df_i, df_w, time):
                            for i in range(0,df_w.shape[0]):
                                    if df_w.loc[i,'KET']=='':
                                        list_ind = df_i[(df_i['ID2']==df_w.loc[i,'ID2'])
                                                    & (df_i['HELP']=='')].index
                                        for x in list_ind:
                                            if (float(df_i.loc[x,'NOM'])-float(df_w.loc[i,'NOM2']))==0:
                                                df_w.loc[i,'KET'] = 'Balance '+ str(df_i.loc[x,'ID'])
                                                df_i.loc[x,'KET'] = 'Balance '+ str(df_i.loc[x,'ID'])
                                                df_i.loc[x,'HELP'] = str(df_w.loc[i,'CODE'])
                                                break
                                            else:
                                                df_w.loc[i,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],df_w.loc[i,'NOM2'])
                                                df_i.loc[x,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],df_w.loc[i,'NOM2'])
                                                df_i.loc[x,'HELP'] = str(df_w.loc[i,'CODE'])
                                                break 
                                                
                            for i in df_w[df_w['KET']==''].index :
                                    df_w.loc[i,'KET'] = 'Tidak Ada Invoice Ojol'
                                
                        compare_time(goi, gow2, time_go)
                        goi2 = goi[goi['HELP']!=''].reset_index(drop=True)
                        goi = goi[goi['HELP']==''].reset_index(drop=True)
                        
                        def compare_time(df_i, df_w, time):
                            for i in range(0,df_w.shape[0]):
                                if df_w.loc[i,'KET']=='' :
                                    list_ind = df_i[((df_i['NOM'] - df_w.loc[i,'NOM'])<=200) & ((df_i['NOM']-df_w.loc[i,'NOM'])>=0) & (df_i['HELP']=='')].index
                                    for x in list(list_ind):
                                        if ((df_i.loc[x,'TIME']) - df_w.loc[i,'TIME']  >= dt.timedelta(minutes=0)):
                                            if ((df_i.loc[x,'TIME']) - df_w.loc[i,'TIME'] < dt.timedelta(minutes=time)):
                                                if ((df_i.loc[x,'NOM']-float(df_w.loc[i,'NOM2']))==0):
                                                    df_w.loc[i,'KET'] = 'Balance '+ df_i.loc[x,'ID']
                                                    df_i.loc[x,'KET'] = 'Balance '+ df_i.loc[x,'ID']
                                                    df_i.loc[x,'HELP'] = df_w.loc[i,'CODE']
                                                    break
                                                else:
                                                    df_w.loc[i,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],float(df_w.loc[i,'NOM2']))
                                                    df_i.loc[x,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],float(df_w.loc[i,'NOM2']))
                                                    df_i.loc[x,'HELP'] = df_w.loc[i,'CODE']
                                                    break                              
                                        if ((df_i.loc[x,'TIME']) - df_w.loc[i,'TIME']  < dt.timedelta(minutes=0)):
                                            if ((df_w.loc[i,'TIME']) - df_i.loc[x,'TIME'] < dt.timedelta(minutes=3)):
                                                if (df_i.loc[x,'NOM']-float(df_w.loc[i,'NOM2']))==0:
                                                    df_w.loc[i,'KET'] = 'Balance '+ df_i.loc[x,'ID']
                                                    df_i.loc[x,'KET'] = 'Balance '+ df_i.loc[x,'ID']
                                                    df_i.loc[x,'HELP'] = df_w.loc[i,'CODE']
                                                    break
                                                else:
                                                    df_w.loc[i,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],float(df_w.loc[i,'NOM2']))
                                                    df_i.loc[x,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],float(df_w.loc[i,'NOM2']))
                                                    df_i.loc[x,'HELP'] = df_w.loc[i,'CODE']
                                                    break   
                                                                        
            
                            for i in df_w[df_w['KET']==''].index :
                                if df_w.loc[i,'TIME'] > pd.to_datetime('23:00:00' , format='%H:%M:%S'):
                                    df_w.loc[i,'KET'] = 'Invoice Beda Hari'
                                else:
                                    df_w.loc[i,'KET'] = 'Tidak Ada Invoice Ojol'
            
                            for i in df_i[df_i['HELP']==''].index :
                                if df_i.loc[i,'TIME'] < pd.to_datetime('01:00:00' , format='%H:%M:%S'):
                                    df_i.loc[i,'KET'] = 'Transaksi Kemarin'
                                    df_i.loc[i,'HELP'] = 'Transaksi Kemarin'
                                else:
                                    df_i.loc[i,'KET'] = 'Tidak Ada Transaksi di Web'   
                                    df_i.loc[i,'HELP'] = 'Tidak Ada Transaksi di Web'  
                                    
                        compare_time(goi, gow, time_go)
                        goi.loc[goi[~(goi['KET']=='Transaksi Kemarin')].index,'KET'] = goi.loc[goi[~(goi['KET']=='Cancel Nota')].index, 'ID']
                        gow.loc[gow[~(gow['KET']=='Cancel Nota')].index, 'KET'] = ''
                        goi.loc[goi[~(goi['KET']=='Transaksi Kemarin')].index,'HELP'] = ''
                        gow.loc[gow[~(gow['KET']=='Cancel Nota')].index, 'HELP'] =''
            
                        goi = goi.sort_values(by=['TIME'], ascending=[True]).reset_index(drop=True)
                        gow = gow.sort_values(by=['TIME'], ascending=[True]).reset_index(drop=True)
            
                        compare_time(goi, gow, time_go)
            
                        goi.loc[goi[(goi['KET'].str.contains('F')) & ~(goi['KET'].str.contains('Balance'))].index,'KET'] = goi.loc[goi[(goi['KET'].str.contains('F')) & ~(goi['KET'].str.contains('Balance'))].index, 'ID']
                        gow.loc[gow[~(gow['KET'].str.contains('Cancel Nota')) & ~(gow['KET'].str.contains('Balance'))].index, 'KET'] = ''
                        goi.loc[goi[(goi['KET'].str.contains('F')) & ~(goi['KET'].str.contains('Balance'))].index,'HELP'] = ''
            
                        goi = goi.sort_values(by=['TIME'], ascending=[True]).reset_index(drop=True)
                        gow = gow.sort_values(by=['TIME'], ascending=[True]).reset_index(drop=True)
                        compare_time(goi, gow, time_go)
            
                        all = pd.concat([gow,goi]).sort_values(['CAB','DATE','KET', 'SOURCE','NOM'],ascending=[True,True,True,False,True])
                        all_1 = all[(all['KET'].str.contains('F'))].reset_index(drop=True)
                        all_2 = all[~(all['KET'].str.contains('F')) & ~(all['KET'].isin(['Cancel Nota']))].reset_index(drop=True)
            
                        for c in range(0,2000):
                            step=0
                            for i in all_2.index:  
                                if all_2.loc[i,'SOURCE'] =='WEB':
                                                source = 'INVOICE'
                                                tab =  all_1[(all_1['TIME'] > (all_2.loc[i,'TIME'] - dt.timedelta(minutes=5)
                                        )) & (all_1['SOURCE']==source) & (abs(all_1['NOM']-all_2.loc[i,'NOM'])<=200)]
                                if all_2.loc[i,'SOURCE'] =='INVOICE':
                                                source = 'WEB'
                                                tab =  all_1[((all_2.loc[i,'TIME'] + pd.Timedelta(minutes=15)) > all_1['TIME']) 
                                                & (all_1['SOURCE']==source) & (abs(all_2.loc[i,'NOM']-all_1['NOM'])<=200)]
                                if tab.shape[0]>0:
                                                x = abs(tab['TIME'] - all_2.loc[i,'TIME']).sort_values().index[0]
                                                if all_2.loc[i,'SOURCE'] =='WEB':
                                                    y = x-1
                                                if all_2.loc[i,'SOURCE'] =='INVOICE':
                                                    y = x+1
                                                if abs(all_2.loc[i,'TIME'] - all_1.loc[x,'TIME']) < abs(all_1.loc[y,'TIME'] - all_1.loc[x,'TIME']):
                                                    step = step + 1
                                                    temp_row_a = all_2.loc[i,['TIME','CODE','ID','NOM']].copy()
                                                    temp_row_b = all_1.loc[y,['TIME','CODE','ID','NOM']].copy()
                        
                                                    all_2.loc[i,['TIME','CODE','ID','NOM']] = temp_row_b
                                                    all_1.loc[y,['TIME','CODE','ID','NOM']] = temp_row_a
                        
                                                    if float(all_1.loc[y,'NOM2'] if all_1.loc[y,'SOURCE']=='WEB' else all_1.loc[y,'NOM']) == float(all_1.loc[x,'NOM2'] if all_1.loc[x,'SOURCE']=='WEB' else all_1.loc[x,'NOM']):
                                                        if all_2.loc[i,'SOURCE'] =='WEB':
                                                            all_1.loc[y,'KET'] = 'Balance '+ all_1.loc[x,'ID']
                                                            all_1.loc[x,'KET'] = 'Balance '+ all_1.loc[x,'ID']
                                                        if all_2.loc[i,'SOURCE'] =='INVOICE':
                                                            all_1.loc[y,'KET'] = 'Balance '+ all_1.loc[y,'ID']
                                                            all_1.loc[x,'KET'] = 'Balance '+ all_1.loc[y,'ID']                                            
                                                    else: #if all_1.loc[y,'NOM'] != all_1.loc[x,'NOM']:
                                                        if all_2.loc[i,'SOURCE'] =='WEB':
                                                            all_1.loc[y,'KET'] =  'Selisih '+ str(all_1.loc[x,'ID']) + difference(all_1.loc[x,'NOM'],float(all_1.loc[y,'NOM2']))
                                                            all_1.loc[x,'KET'] =  'Selisih '+ str(all_1.loc[x,'ID']) + difference(all_1.loc[x,'NOM'],float(all_1.loc[y,'NOM2']))
                                                        else:
                                                            all_1.loc[y,'KET'] =  'Selisih '+ str(all_1.loc[y,'ID']) + difference(all_1.loc[y,'NOM'],float(all_1.loc[x,'NOM2']))
                                                            all_1.loc[x,'KET'] =  'Selisih '+ str(all_1.loc[y,'ID']) + difference(all_1.loc[y,'NOM'],float(all_1.loc[x,'NOM2']))
              
                            if step == 0:
                                break
                        print(step)
            
                        for i in all_2[all_2['SOURCE']=='WEB'].index:
                                            list_ind = all_2[(all_2['SOURCE']=='INVOICE') & (abs(all_2['NOM'] - all_2.loc[i,'NOM'])<=200) & (all_2['HELP']!='')
                                                        & (((((all_2['TIME']-all_2.loc[i,'TIME'])) < dt.timedelta(minutes=150)) & ((all_2['TIME']-all_2.loc[i,'TIME'])>=dt.timedelta(minutes=0)))
                                                           | ((((all_2.loc[i,'TIME']-all_2['TIME'])) < dt.timedelta(minutes=15)) & (((all_2.loc[i,'TIME']-all_2['TIME'])) >= dt.timedelta(minutes=0)) ))].index
                        
                                            if len(list_ind)>0:
                                                x = (abs(all_2.loc[i,'TIME'] - all_2.loc[list_ind, 'TIME'])).sort_values().index[0]
                                                if ((all_2.loc[x,'NOM']-float(all_2.loc[i,'NOM2']))==0):
                                                                        all_2.loc[i,'KET'] = 'Balance '+ all_2.loc[x,'ID']
                                                                        all_2.loc[x,'KET'] = 'Balance '+ all_2.loc[x,'ID']
                                                                        all_2.loc[x,'HELP'] = ''
                                                                        
                                                else:
                                                                        all_2.loc[i,'KET'] = 'Selisih '+ str(all_2.loc[x,'ID']) + difference(all_2.loc[x,'NOM'],float(all_2.loc[i,'NOM2']))
                                                                        all_2.loc[x,'KET'] = 'Selisih '+ str(all_2.loc[x,'ID']) + difference(all_2.loc[x,'NOM'],float(all_2.loc[i,'NOM2']))
                                                                        all_2.loc[x,'HELP'] = '' 
                            
                        all = pd.concat([all[all['KET'].isin(['Cancel Nota'])],all_1,all_2,gow2,goi2]).sort_values(['CAB','DATE','KET', 'SOURCE','NOM'],ascending=[True,True,True,False,True])
                        if ket == 'selisih':
                            all = all[~(all['KET'].str.contains('Balance'))]
                        all['HELP'] = all['KET'].apply(lambda x: label_1(x))
                        all['KET'] = all['KET'].apply(lambda x:x if (('Selisih' in x) | ('Balance' in x)) else '')
                        #all['DATE'] = all['DATE'].dt.strftime('%d/%m/%Y')
                        #all['TIME'] = all['TIME'].dt.strftime('%H:%M:%S')
                        all.to_csv(f'{tmpdirname}/_bahan/GOJEK_{cab}_{date}.csv', index=False)
                        st.write('GOJEK', ': File processed')
                        
                    if not ((dfinv[(dfinv['KAT']  ==  "QRIS SHOPEE") & (dfinv['CAB']  ==  cab) & (dfinv['DATE']==date)].empty) or
                         (dfweb[(dfweb['KAT']  ==  "QRIS SHOPEE") & (dfweb['CAB']  ==  cab) & (dfweb['DATE']==date)].empty)):
                        qsi   =   dfinv[dfinv['KAT']  ==  "QRIS SHOPEE"]
                        qsw   =   dfweb[dfweb['KAT']  ==  "QRIS SHOPEE"]
                        qsi   =   qsi[qsi['CAB']  ==  cab]
                        qsw   =   qsw[qsw['CAB']  ==  cab]
                        qsi = qsi[qsi['DATE'] == date]
                        qsw = qsw[qsw['DATE'] == date]
            
                        qsi = qsi.sort_values(by=['CAB', 'NOM', 'TIME'], ascending=[True, True, True]).reset_index(drop=True)
                        qsw = qsw.sort_values(by=['CAB', 'NOM', 'TIME'], ascending=[True, True, True]).reset_index(drop=True)
            
                        qsi.drop_duplicates(inplace=True)
            
                        for i in cn[(cn['TANGGAL']==str(int(re.findall(r'\d+', date)[-1]))) & (cn['CAB']==cab) & (cn['TYPE BAYAR']=='QRIS SHOPEE')].index:
                            x = qsw[(qsw['DATE']==date) & (qsw['NOM']==cn.loc[i,'TOTAL BILL'])].index
                            qsw.loc[qsw.loc[x,'ID'].apply(lambda x: fuzz.ratio(str(x).upper(), str(cn.loc[i,'NAMA TAMU']).upper())).sort_values().index[-1],'KET'] = 'Cancel Nota'
                            cn.loc[i, 'KET'] = 'Done'
                        qsi['KET'] = qsi['ID']
            
                        def compare_time(df_i, df_w, time):
                            for i in range(0,df_w.shape[0]):
                                if df_w.loc[i,'KET']=='' :
                                    list_ind = df_i[((df_i['NOM'] == df_w.loc[i,'NOM'])) & (df_i['HELP']=='')].index
                                    for x in list(list_ind):
                                        if ((df_i.loc[x,'TIME']) - df_w.loc[i,'TIME']  >= dt.timedelta(minutes=0)):
                                            if ((df_i.loc[x,'TIME']) - df_w.loc[i,'TIME'] < dt.timedelta(minutes=time)):
                                                if ((df_i.loc[x,'NOM']-df_w.loc[i,'NOM'])==0):
                                                    df_w.loc[i,'KET'] = 'Balance '+ str(df_i.loc[x,'ID'])
                                                    df_i.loc[x,'KET'] = 'Balance '+ str(df_i.loc[x,'ID'])
                                                    df_i.loc[x,'HELP'] = df_w.loc[i,'CODE']
                                                    break                           
                                        if ((df_i.loc[x,'TIME']) - df_w.loc[i,'TIME']  < dt.timedelta(minutes=0)):
                                            if ((df_w.loc[i,'TIME']) - df_i.loc[x,'TIME'] < dt.timedelta(minutes=time)):
                                                if ((df_i.loc[x,'NOM']-df_w.loc[i,'NOM']))==0:
                                                    df_w.loc[i,'KET'] = 'Balance '+ str(df_i.loc[x,'ID'])
                                                    df_i.loc[x,'KET'] = 'Balance '+ str(df_i.loc[x,'ID'])
                                                    df_i.loc[x,'HELP'] = df_w.loc[i,'CODE']
                                                    break
            
                            for c in range (0,50):
                                step = 0
                                for i in df_w[df_w['KET']==''].index:
                                    list_ind = df_i[(df_i['NOM']==df_w.loc[i,'NOM'])
                                                & ((abs(df_w.loc[i,'TIME'] - df_i['TIME'])) < dt.timedelta(minutes=5))
                                                    ].index
                                    if len(list_ind)>0:
                                            x = (abs(df_w.loc[i,'TIME'] - df_i.loc[list_ind,'TIME'])).sort_values().index[0]
                                            if abs(df_w.loc[i,'TIME'] - df_i.loc[x,'TIME']) < abs(df_w.loc[df_w[df_w['KET']==df_i.loc[x,'KET']].index[0],'TIME'] - df_i.loc[x,'TIME']):
                                                df_w.loc[df_w[df_w['KET']==df_i.loc[x,'KET']].index, 'KET'] = ''
                                                df_w.loc[i,'KET'] = df_i.loc[x,'KET']
                                                step+=1
                                if step == 0:
                                    break
                                            
            
                            for i in df_i[df_i['HELP']==''].sort_values('TIME').index:
                                    if df_i.loc[i,'HELP']=='':
                                        id = df_w[(df_w['KET']=='') & (((df_w['TIME']) - df_i.loc[i,'TIME'] + dt.timedelta(minutes=1)) >= dt.timedelta(minutes=0))].sort_values('TIME').index
                                        z=0
                                        for x in range(0, len(id)-1):
                                            z=+1
                                            if df_i.loc[i,'HELP'] == '':
                                                for y in range(z, len(id)):
                                                    if ((df_i.loc[i,'NOM']==(df_w.loc[id[x],'NOM']+df_w.loc[id[y],'NOM']))
                                                        & (df_w.loc[id[x],'KET']=='') & (df_w.loc[id[y],'KET']=='')
                                                        & ((df_w.loc[id[x],'TIME'] - df_i.loc[i,'TIME'])  <= dt.timedelta(minutes=3))
                                                        & ((df_w.loc[id[y],'TIME'] - df_i.loc[i,'TIME'])  <= dt.timedelta(minutes=3))):
                                                        df_i.loc[i,'KET'] = df_i.loc[i,'ID']
                                                        df_w.loc[id[x],'KET'] = df_i.loc[i,'ID']
                                                        df_w.loc[id[y],'KET'] = df_i.loc[i,'ID']
                                                        df_w.loc[id[x],'HELP'] = 'Bayar 1 Kali - Banyak Struk (QRIS)'
                                                        df_w.loc[id[y],'HELP'] = 'Bayar 1 Kali - Banyak Struk (QRIS)'
                                                        df_i.loc[i,'HELP'] = 'Bayar 1 Kali - Banyak Struk (QRIS)'
                                                    break
                                                
                            for i in df_w[df_w['KET']==''].sort_values('TIME', ascending=False).index:
                                    if df_w.loc[i,'KET']=='':
                                        id = df_i[(df_i['HELP']=='') & ((df_w.loc[i,'TIME'] - df_i['TIME'] + dt.timedelta(minutes=1)) >= dt.timedelta(minutes=0))].sort_values('TIME',ascending=False).index
                                        z=0
                                        for x in range(0, len(id)-1):
                                            z=+1
                                            if df_w.loc[i,'KET'] == '':
                                                for y in range(z, len(id)):
                                                    if ((df_w.loc[i,'NOM']==(df_i.loc[id[x],'NOM']+df_i.loc[id[y],'NOM']))
                                                        & (df_i.loc[id[x],'HELP']=='') & (df_i.loc[id[y],'HELP']=='')
                                                        & ((df_w.loc[i,'TIME'] - df_i.loc[id[x],'TIME'])  <= dt.timedelta(minutes=3))
                                                        & ((df_w.loc[i,'TIME'] - df_i.loc[id[y],'TIME'])  <= dt.timedelta(minutes=3))
                                                        & (df_i.loc[id[x],'ID']!=df_i.loc[id[y],'ID'])):
                                                        df_w.loc[i,'KET'] = str(df_i.loc[id[x],'ID']) + ' & ' + str(df_i.loc[id[y],'ID'])
                                                        df_i.loc[id[x],'KET'] = str(df_i.loc[id[x],'ID']) + ' & ' + str(df_i.loc[id[y],'ID'])
                                                        df_i.loc[id[y],'KET'] = str(df_i.loc[id[x],'ID']) + ' & ' + str(df_i.loc[id[y],'ID'])
                                                        df_w.loc[i,'HELP'] = 'Bayar Lebih dari 1 Kali - 1 Struk (QRIS)'
                                                        df_i.loc[id[x],'HELP'] = 'Bayar Lebih dari 1 Kali - 1 Struk (QRIS)'
                                                        df_i.loc[id[y],'HELP'] = 'Bayar Lebih dari 1 Kali - 1 Struk (QRIS)'
                                                    break
                                                                        
                            for i in df_w[df_w['KET']==''].index :
                                list_ind = df_w[(df_w['NOM']-df_w.loc[i,'NOM'])==0].index
                                for x in list_ind:
                                    if ((df_w.loc[i,'TIME'] - df_w.loc[x,'TIME']) < dt.timedelta(minutes=2)) & ((df_w.loc[i,'TIME'] - df_w.loc[x,'TIME']) > dt.timedelta(seconds=0)):
                                        df_w.loc[i,'KET'] = 'Double Input'
            
            
                            for i in df_i[df_i['HELP']==''].index :
                                cash_ind = cash[(cash['CAB']==df_i.loc[i,'CAB']) & (cash['DATE']==df_i.loc[i,'DATE']) & (cash['NOM']==df_i.loc[i,'NOM'])].index
                                for x in cash_ind:
                                    if (((df_i.loc[i,'TIME'] - cash.loc[x,'TIME']) < dt.timedelta(minutes=2)) & ((df_i.loc[i,'TIME'] - cash.loc[x,'TIME']) >= dt.timedelta(minutes=0))):
                                        df_i.loc[i,'KET'] = 'QRIS to Cash(' + str(cash.loc[x,'CODE']) + ')'
                                        df_i.loc[i,'HELP'] = 'QRIS to Cash(' + str(cash.loc[x,'CODE']) + ')'
                                        break   
                                if df_i.loc[i,'HELP'] == '':
                                    if df_i.loc[i,'TIME'] < pd.to_datetime('01:00:00' , format='%H:%M:%S'):
                                        df_i.loc[i,'KET'] = 'Transaksi Kemarin'
                                    else:
                                        df_i.loc[i,'KET'] = 'Tidak Ada Transaksi di Web' 
            
                            for i in df_w[df_w['KET']==''].index :
                                if df_w.loc[i,'TIME'] > pd.to_datetime('23:00:00' , format='%H:%M:%S'):
                                    df_w.loc[i,'KET'] = 'Invoice Beda Hari'
                                else:
                                    df_w.loc[i,'KET'] = 'Tidak Ada Invoice QRIS'  
            
                        compare_time(qsi, qsw, time_qs)
                        all = pd.concat([qsw,qsi]).sort_values(['CAB','DATE','KET', 'SOURCE','NOM'],ascending=[True,True,True,False,True]).reset_index(drop=True)
                        if ket == 'selisih':
                            all = all[~(all['KET'].str.contains('Balance'))].sort_values(['TIME','KET','SOURCE'])
                        all.loc[all[~all['HELP'].astype(str).str.contains('Bayar')].index,'HELP'] = all.loc[all[~all['HELP'].astype(str).str.contains('Bayar')].index,'KET'].apply(lambda x: label_1(x))
                        all.loc[all[~all['HELP'].astype(str).str.contains('Bayar')].index,'KET'] = all.loc[all[~all['HELP'].astype(str).str.contains('Bayar')].index,'KET'].apply(lambda x:x if (('Balance' in x)) else '')
                        #all['DATE'] = all['DATE'].dt.strftime('%d/%m/%Y')
                        #all['TIME'] = all['TIME'].dt.strftime('%H:%M:%S')
                        all.to_csv(f'{tmpdirname}/_bahan/QRIS SHOPEE_{cab}_{date}.csv', index=False)
                        st.write('QRIS SHOPEE', ': File processed')
                        
                    if not ((dfinv[(dfinv['KAT']  ==  "GRAB FOOD") & (dfinv['CAB']  ==  cab) & (dfinv['DATE']==date)].empty) or
                         (dfweb[(dfweb['KAT']  ==  "GRAB FOOD") & (dfweb['CAB']  ==  cab) & (dfweb['DATE']==date)].empty)) :  
                             
                        gfi   =   dfinv[dfinv['KAT']  ==  "GRAB FOOD"]
                        gfw   =   dfweb[dfweb['KAT']  ==  "GRAB FOOD"]
                        gfi   =   gfi[gfi['CAB']  ==  cab]
                        gfw   =   gfw[gfw['CAB']  ==  cab]
                        gfi = gfi[gfi['DATE']==date]
                        gfw = gfw[gfw['DATE']==date]
            
                        gfi = gfi.sort_values(by=['CAB', 'NOM', 'ID', 'TIME'], ascending=[True, True, True, False]).reset_index(drop=True)
                        gfw = gfw.sort_values(by=['CAB', 'NOM', 'ID', 'TIME'], ascending=[True, True, True, False]).reset_index(drop=True)
            
                        gfi.drop_duplicates(inplace=True)
            
                        gfw.loc[gfw[gfw['ID'].isna()].index,'ID'] = ''
                        gfw['ID2'] = gfw['ID'].apply(lambda x: re.findall(r'\d+', x)[-1] if re.findall(r'\d+', x) else 0)
                        gfi['ID2'] = gfi['ID'].apply(lambda x: re.findall(r'\d+', x)[-1] if re.findall(r'\d+', x) else 0)
            
                        gfw.loc[gfw[gfw['ID'].isna()].index,'ID'] = ''
                        for i in cn[(cn['TANGGAL']==str(int(re.findall(r'\d+', date)[-1]))) & (cn['CAB']==cab) & (cn['TYPE BAYAR']=='GRAB FOOD')].index:
                            x = gfw[(gfw['ID2']==str(re.findall(r'\d+', cn.loc[i,'NAMA TAMU'])[-1])) & (gfw['NOM']==cn.loc[i,'TOTAL BILL'])].index
                            if len(x) >= 1:
                                gfw.loc[x[0], 'KET']='Cancel Nota'
                                cn.loc[i, 'KET'] = 'Done'
            
                        gfi['KET'] = gfi['ID']

                        def compare_time(df_i, df_w, time):
                            for i in range(0,df_w.shape[0]):
                                if df_w.loc[i,'KET']=='':
                                    list_ind = df_i[(abs(float(df_w.loc[i,'NOM2'])-df_i['NOM'])<=50) 
                                                & (df_i['ID2']==df_w.loc[i,'ID2'])
                                                & (df_i['HELP']=='')].index
                                    for x in list_ind:
                                            if ((df_i.loc[x,'TIME'] - df_w.loc[i,'TIME'])  >= dt.timedelta(minutes=0)):
                                                if ((df_i.loc[x,'TIME'] - df_w.loc[i,'TIME']) < dt.timedelta(minutes=time)):
                                                    if (float(df_i.loc[x,'NOM'])-float(df_w.loc[i,'NOM2']))==0:
                                                        df_w.loc[i,'KET'] = 'Balance '+ df_i.loc[x,'ID']
                                                        df_i.loc[x,'KET'] = 'Balance '+ df_i.loc[x,'ID']
                                                        df_i.loc[x,'HELP'] = df_w.loc[i,'CODE']
                                                        break
                                                    else:
                                                        df_w.loc[i,'KET'] = 'Promo Marketing/Adjustment'
                                                        df_i.loc[x,'KET'] = 'Promo Marketing/Adjustment'
                                                        df_i.loc[x,'HELP'] = df_w.loc[i,'CODE']
                                                        break                              
                                            if ((df_i.loc[x,'TIME']) - df_w.loc[i,'TIME']  < dt.timedelta(minutes=0)):
                                                if ((df_w.loc[i,'TIME']) - df_i.loc[x,'TIME'] < dt.timedelta(minutes=time)):
                                                    if (float(df_i.loc[x,'NOM'])-float(df_w.loc[i,'NOM2']))==0:
                                                        df_w.loc[i,'KET'] = 'Balance '+ df_i.loc[x,'ID']
                                                        df_i.loc[x,'KET'] = 'Balance '+ df_i.loc[x,'ID']
                                                        df_i.loc[x,'HELP'] = df_w.loc[i,'CODE']
                                                        break
                                                    else:
                                                        df_w.loc[i,'KET'] = 'Promo Marketing/Adjustment'
                                                        df_i.loc[x,'KET'] = 'Promo Marketing/Adjustment'
                                                        df_i.loc[x,'HELP'] = df_w.loc[i,'CODE']
                                                        break 
                                                        
                            for x in df_i[(df_i['ID'].apply(lambda x: len(re.findall(r'\bGF-\d{3}\b', x)))>=2) & (df_i['HELP']=='')].index:
                                if len(df_w[df_w['ID2'].astype(str).isin([str(x) for x in df_i.loc[x,'KET'].replace('GF-','').split(', ')])].index) >=2:
                                    i = df_w[df_w['ID2'].astype(str).isin([str(x) for x in df_i.loc[x,'KET'].replace('GF-','').split(', ')])].index
                                    if abs(df_i.loc[x,'NOM'] - df_w.loc[i,'NOM2'].astype(float).sum())< 5:
                                        df_w.loc[i[0],'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],df_w.loc[i,'NOM'].astype(float).sum())
                                        df_w.loc[i[1],'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],df_w.loc[i,'NOM'].astype(float).sum())
                                        df_w.loc[i[0],'ID2'] = df_i.loc[x,'KET'].replace('GF-','').split(', ')[0]
                                        df_w.loc[i[1],'ID2'] = df_i.loc[x,'KET'].replace('GF-','').split(', ')[0]
                                        df_i.loc[x,'HELP'] = df_i.loc[x,'KET'].replace('GF-','')
                                        df_i.loc[x,'ID2'] = df_i.loc[x,'KET'].replace('GF-','').split(', ')[0]
                                        df_i.loc[x,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],df_w.loc[i,'NOM'].astype(float).sum())
                                        
                            for i in df_w[df_w['KET']==''].index :
                                if df_w.loc[i,'TIME'] > pd.to_datetime('23:00:00' , format='%H:%M:%S'):
                                    df_w.loc[i,'KET'] = 'Invoice Beda Hari'
                                else:
                                    df_w.loc[i,'KET'] = 'Tidak Ada Invoice Ojol'
            
                            for i in df_i[df_i['HELP']==''].index :
                                if df_i.loc[i,'TIME'] < pd.to_datetime('01:00:00' , format='%H:%M:%S'):
                                    df_i.loc[i,'KET'] = 'Transaksi Kemarin'
                                else:
                                    df_i.loc[i,'KET'] = 'Tidak Ada Transaksi di Web'                       
            
                        compare_time(gfi, gfw, time_gf)
            
                        all = pd.concat([gfw,gfi]).sort_values(['CAB','DATE','KET', 'ID2','SOURCE','NOM'],ascending=[True,True, True,True,False,True])
                        if ket == 'selisih':
                            all = all[~(all['KET'].str.contains('Balance'))]
                        all['HELP'] = all['KET'].apply(lambda x: label_1(x))
                        all['KET'] = all['KET'].apply(lambda x:x if (('Selisih' in x) | ('Balance' in x)) else '')
                        #all['DATE'] = all['DATE'].dt.strftime('%d/%m/%Y')
                        #all['TIME'] = all['TIME'].dt.strftime('%H:%M:%S')
                        all.to_csv(f'{tmpdirname}/_bahan/GRAB_{cab}_{date}.csv', index=False)
                        st.write('GRAB FOOD', ': File processed')
                        
                    if not ((dfinv[(dfinv['KAT']  ==  "SHOPEEPAY") & (dfinv['CAB']  ==  cab) & (dfinv['DATE']==date)].empty) or
                         (dfweb[(dfweb['KAT']  ==  "SHOPEEPAY") & (dfweb['CAB']  ==  cab) & (dfweb['DATE']==date)].empty)) :
                        spi   =   dfinv[dfinv['KAT']  ==  "SHOPEEPAY"]
                        spw   =   dfweb[dfweb['KAT']  ==  "SHOPEEPAY"]
                        spi   =   spi[spi['CAB']  ==  cab]
                        spw   =   spw[spw['CAB']  ==  cab]
                        spi = spi[spi['DATE']==date]
                        spw = spw[spw['DATE']==date]
                        
                        spi = spi.sort_values(by=['CAB', 'NOM', 'ID', 'TIME'], ascending=[True, True, True, True]).reset_index(drop=True)
                        spw = spw.sort_values(by=['CAB', 'NOM', 'ID', 'TIME'], ascending=[True, True, True, False]).reset_index(drop=True)
                        
            
                        spi.drop_duplicates(inplace=True)
                        spw['ID'] = spw['ID'].str.upper()
                        spw.loc[spw[spw['ID'].isna()].index,'ID'] = ''
                        spw['ID2'] = spw['ID'].apply(lambda x: x.split(' - ')[0] if ' - ' in x else x).apply(lambda x: '#'+str(int(re.search(r'\d+$', x[:re.search(r'\d(?!.*\d)', x).end()] if re.search(r'\d(?!.*\d)', x) else x).group())) if re.search(r'\d+$',  x[:re.search(r'\d(?!.*\d)', x).end()] if re.search(r'\d(?!.*\d)', x) else x) else x)
                        spi['ID2'] = spi['ID']
            
                        spw.loc[spw[spw['ID'].isna()].index,'ID'] = ''
                        for i in cn[(cn['TANGGAL']==str(int(re.findall(r'\d+', date)[-1]))) & (cn['CAB']==cab) & (cn['TYPE BAYAR']=='SHOPEEPAY')].index:
                            x = spw[(spw['ID2']=='#'+(str(int(re.search(r'\d+$', cn.loc[i,'NAMA TAMU']).group())) if re.search(r'\d+$', cn.loc[i,'NAMA TAMU']) else cn.loc[i,'NAMA TAMU']))
                                    & (spw['NOM']==cn.loc[i,'TOTAL BILL'])].index
                            if len(x) >= 1:
                                spw.loc[x[0], 'KET']='Cancel Nota'
                                cn.loc[i, 'KET'] = 'Done'
            
                        spi['KET'] = spi['ID']
            
                        def compare_time(df_i, df_w, time):
                            for i in range(0,df_w.shape[0]):
                                    if df_w.loc[i,'KET']=='':
                                        list_ind = df_i[((((df_i['NOM']-df_w.loc[i,'NOM'])<=500) & ((df_i['NOM']-df_w.loc[i,'NOM'])>=0))
                                                         | (((df_w.loc[i,'NOM']-df_i['NOM'])<=200) & ((df_w.loc[i,'NOM']-df_i['NOM'])>=0))) 
                                                    & (df_i['ID2']==df_w.loc[i,'ID2'])
                                                    & (df_i['HELP']=='')].index
                                        for x in list_ind:
                                                if ((df_i.loc[x,'TIME'] - df_w.loc[i,'TIME'])  >= dt.timedelta(minutes=0)):
                                                    if ((df_i.loc[x,'TIME'] - df_w.loc[i,'TIME']) < dt.timedelta(minutes=150)):
                                                        if (float(df_i.loc[x,'NOM'])-float(df_w.loc[i,'NOM2']))==0:
                                                            df_w.loc[i,'KET'] = 'Balance '+ str(df_i.loc[x,'ID'])
                                                            df_i.loc[x,'KET'] = 'Balance '+ str(df_i.loc[x,'ID'])
                                                            df_i.loc[x,'HELP'] = str(df_w.loc[i,'CODE'])
                                                            break
                                                        else:
                                                            df_w.loc[i,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],df_w.loc[i,'NOM2'])
                                                            df_i.loc[x,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],df_w.loc[i,'NOM2'])
                                                            df_i.loc[x,'HELP'] = str(df_w.loc[i,'CODE'])
                                                            break                              
                                                if ((df_i.loc[x,'TIME']) - df_w.loc[i,'TIME']  < dt.timedelta(minutes=0)):
                                                    if ((df_w.loc[i,'TIME']) - df_i.loc[x,'TIME'] < dt.timedelta(minutes=150)):
                                                        if (float(df_i.loc[x,'NOM'])-float(df_w.loc[i,'NOM2']))==0:
                                                            df_w.loc[i,'KET'] = 'Balance '+ str(df_i.loc[x,'ID'])
                                                            df_i.loc[x,'KET'] = 'Balance '+ str(df_i.loc[x,'ID'])
                                                            df_i.loc[x,'HELP'] = str(df_w.loc[i,'CODE'])
                                                            break
                                                        else:
                                                            df_w.loc[i,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],df_w.loc[i,'NOM2'])
                                                            df_i.loc[x,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],df_w.loc[i,'NOM2'])
                                                            df_i.loc[x,'HELP'] = str(df_w.loc[i,'CODE'])
                                                            break 
            
                            for i in df_w[df_w['KET']==''].index :
                                    list_ind_i = df_i[(df_i['HELP']=='') & ((df_i['NOM']-df_w.loc[i,'NOM'])==0) 
                                                      & (df_i['ID2']==df_w.loc[i,'ID2'])].index
                                    for x in list_ind_i:
                                        if ((df_i.loc[x,'TIME'] - df_w.loc[i,'TIME']) < dt.timedelta(minutes=120)) & ((df_i.loc[x,'TIME'] - df_w.loc[i,'TIME']) > dt.timedelta(seconds=0)):
                                            if (df_i.loc[x,'NOM']==df_w.loc[i,'NOM']):
                                                df_w.loc[i,'KET'] = 'Balance '+ str(df_i.loc[x,'ID'])
                                                df_i.loc[x,'KET'] = 'Balance '+ str(df_i.loc[x,'ID'])
                                                df_i.loc[x,'HELP'] = str(df_w.loc[i,'CODE'])
                                                break
                                            else:
                                                df_w.loc[i,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],df_w.loc[i,'NOM2'])
                                                df_i.loc[x,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],df_w.loc[i,'NOM2'])
                                                df_i.loc[x,'HELP'] = str(df_w.loc[i,'CODE'])
                                                break    
                                                  
                                        
                            for i in df_w[df_w['KET']==''].index :
                                    if df_w.loc[i,'TIME'] > pd.to_datetime('23:00:00' , format='%H:%M:%S'):
                                        df_w.loc[i,'KET'] = 'Invoice Beda Hari'
                                    else:
                                        df_w.loc[i,'KET'] = 'Tidak Ada Invoice Ojol'
            
                            for i in df_i[df_i['HELP']==''].index :
                                    if df_i.loc[i,'TIME'] < pd.to_datetime('01:00:00' , format='%H:%M:%S'):
                                        df_i.loc[i,'KET'] = 'Transaksi Kemarin'
                                        df_i.loc[i,'HELP'] = 'Transaksi Kemarin'
                                    if df_i[df_i['ID2']==df_i.loc[i,'ID2']]['ID2'].duplicated().nunique()>=2:
                                        df_i.loc[i,'KET'] = 'Transaksi Kemarin'
                                        df_i.loc[i,'HELP'] = 'Transaksi Kemarin'
                                    if df_i.loc[i,'HELP']=='':
                                        df_i.loc[i,'KET'] = 'Tidak Ada Transaksi di Web'   
                        
                        compare_time(spi, spw, time_sp)
                        all = pd.concat([spw,spi]).sort_values(['CAB','DATE','KET', 'SOURCE','NOM','TIME'],ascending=[True,True,True,False,True,True])
                        if ket == 'selisih':
                            all = all[~(all['KET'].str.contains('Balance'))]
                        all['HELP'] = all['KET'].apply(lambda x: label_1(x))
                        all['KET'] = all['KET'].apply(lambda x:x if (('Selisih' in x) | ('Balance' in x)) else '')
                        #all['DATE'] = all['DATE'].dt.strftime('%d/%m/%Y')
                        #all['TIME'] = all['TIME'].dt.strftime('%H:%M:%S')
                        all.to_csv(f'{tmpdirname}/_bahan/SHOPEEPAY_{cab}_{date}.csv', index=False)
                        st.write('SHOPEEPAY', ': File processed')
                        
                    if not ((dfinv[((dfinv['KAT']  ==  "QRIS ESB") | (dfinv['KAT']  ==  "QRIS ESB ORDER")) & (dfinv['CAB']  ==  cab) & (dfinv['DATE']==date)].empty) or
                         (dfweb[((dfweb['KAT']  ==  "QRIS ESB") | (dfweb['KAT']  ==  "QRIS ESB ORDER")) & (dfweb['CAB']  ==  cab) & (dfweb['DATE']==date)].empty)) :
                        qei   =   dfinv[(dfinv['KAT']  ==  "QRIS ESB") | (dfinv['KAT']  ==  "QRIS ESB ORDER")]
                        qew   =   dfweb[(dfweb['KAT']  ==  "QRIS ESB") | (dfweb['KAT']  ==  "QRIS ESB ORDER")]
                        qei   =   qei[qei['CAB']  ==  cab]
                        qew   =   qew[qew['CAB']  ==  cab]
                        qei = qei[qei['DATE']==date]
                        qew = qew[qew['DATE']==date]
            
                        qei = qei.sort_values(by=['CAB', 'NOM', 'ID', 'TIME'], ascending=[True, True, True, False]).reset_index(drop=True)
                        qew = qew.sort_values(by=['CAB', 'NOM', 'ID', 'TIME'], ascending=[True, True, True, False]).reset_index(drop=True)
            
                        qei.drop_duplicates(inplace=True)
                        for i in cn[(cn['TANGGAL']==str(int(re.findall(r'\d+', date)[-1]))) & (cn['CAB']==cab) & (cn['TYPE BAYAR']=='QRIS qew')].index:
                            x = qew[(qew['ID']==re.findall(r'\d+', cn.loc[i,'NAMA TAMU'])[-1]) 
                                    & (qew['NOM']==cn.loc[i,'TOTAL BILL'])].index
                            if len(x) >= 1:
                                qew.loc[x[0], 'KET']='Cancel Nota'
                                cn.loc[i, 'KET'] = 'Done'
            
                        qei['KET'] = qei['ID']
            
                        def compare_time(df_i, df_w, time):
                            for i in range(0,df_w.shape[0]):
                                if df_w.loc[i,'KET']=='':
                                    list_ind = df_i[((df_w.loc[i,'NOM']-df_i['NOM'])<=10) & ((df_w.loc[i,'NOM']-df_i['NOM'])>=0) 
                                                & (df_i['ID']==df_w.loc[i,'CODE'])
                                                & (df_i['HELP']=='')].index
                                    for x in list_ind:
                                            if ((df_i.loc[x,'TIME'] - df_w.loc[i,'TIME'])  >= dt.timedelta(minutes=0)):
                                                if ((df_i.loc[x,'TIME'] - df_w.loc[i,'TIME']) < dt.timedelta(minutes=time)):
                                                    if ((df_i.loc[x,'NOM']-df_w.loc[i,'NOM'])==0):
                                                        df_w.loc[i,'KET'] = 'Balance '+ df_i.loc[x,'ID']
                                                        df_i.loc[x,'KET'] = 'Balance '+ df_i.loc[x,'ID']
                                                        df_i.loc[x,'HELP'] = df_w.loc[i,'CODE']
                                                        break
                                                    else:
                                                        df_w.loc[i,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],df_w.loc[i,'NOM'])
                                                        df_i.loc[x,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],df_w.loc[i,'NOM'])
                                                        df_i.loc[x,'HELP'] = df_w.loc[i,'CODE']
                                                        break                              
                                            if ((df_i.loc[x,'TIME']) - df_w.loc[i,'TIME']  < dt.timedelta(minutes=0)):
                                                if ((df_w.loc[i,'TIME']) - df_i.loc[x,'TIME'] < dt.timedelta(minutes=time)):
                                                    if ((df_i.loc[x,'NOM']-df_w.loc[i,'NOM']))==0:
                                                        df_w.loc[i,'KET'] = 'Balance '+ df_i.loc[x,'ID']
                                                        df_i.loc[x,'KET'] = 'Balance '+ df_i.loc[x,'ID']
                                                        df_i.loc[x,'HELP'] = df_w.loc[i,'CODE']
                                                        break
                                                    else:
                                                        df_w.loc[i,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],df_w.loc[i,'NOM'])
                                                        df_i.loc[x,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],df_w.loc[i,'NOM'])
                                                        df_i.loc[x,'HELP'] = df_w.loc[i,'CODE']
                                                        break 
            
                            for i in df_w[df_w['KET']==''].index :
                                if df_w.loc[i,'TIME'] > pd.to_datetime('23:00:00' , format='%H:%M:%S'):
                                    df_w.loc[i,'KET'] = 'Invoice Beda Hari'
                                else:
                                    df_w.loc[i,'KET'] = 'Tidak Ada Invoice Ojol'
            
                            for i in df_i[df_i['HELP']==''].index :
                                if df_i.loc[i,'TIME'] < pd.to_datetime('01:00:00' , format='%H:%M:%S'):
                                    df_i.loc[i,'KET'] = 'Transaksi Kemarin'
                                else:
                                    df_i.loc[i,'KET'] = 'Tidak Ada Invoice Ojol'                       
                        
                        compare_time(qei, qew, time_qe)
            
                        all = pd.concat([qew,qei]).sort_values(['CAB','DATE','KET', 'SOURCE','NOM','TIME'],ascending=[True,True,True,False,True,True])
                        if ket == 'selisih':
                            all = all[~(all['KET'].str.contains('Balance'))]
                        all['HELP'] = all['KET'].apply(lambda x: label_1(x))
                        all['KET'] = all['KET'].apply(lambda x:x if (('Selisih' in x) | ('Balance' in x)) else '')
                        #all['DATE'] = all['DATE'].dt.strftime('%d/%m/%Y')
                        #all['TIME'] = all['TIME'].dt.strftime('%H:%M:%S')
                        all['KAT'] = 'QRIS ESB'
                        all.to_csv(f'{tmpdirname}/_bahan/QRIS ESB_{cab}_{date}.csv', index=False)
                        st.write('QRIS ESB', ': File processed')
                             
                    if not ((dfinv[(dfinv['KAT']  ==  "QRIS TELKOM") & (dfinv['CAB']  ==  cab) & (dfinv['DATE']==date)].empty) or
                         (dfweb[(dfweb['KAT']  ==  "QRIS TELKOM") & (dfweb['CAB']  ==  cab) & (dfweb['DATE']==date)].empty)) :
                        qti   =   dfinv[(dfinv['KAT']  ==  "QRIS TELKOM")]
                        qtw   =   dfweb[(dfweb['KAT']  ==  "QRIS TELKOM")]
                        qti   =   qti[qti['CAB']  ==  cab]
                        qtw   =   qtw[qtw['CAB']  ==  cab]
                        qti = qti[qti['DATE']==date]
                        qtw = qtw[qtw['DATE']==date]
            
                        qti = qti.sort_values(by=['CAB', 'NOM', 'TIME'], ascending=[True, True, True]).reset_index(drop=True)
                        qtw = qtw.sort_values(by=['CAB', 'NOM', 'TIME'], ascending=[True, True, True]).reset_index(drop=True)
            
                        qti.drop_duplicates(inplace=True)
            
                        qtw.loc[qtw[qtw['ID'].isna()].index,'ID'] = ''
                        for i in cn[(cn['TANGGAL']==str(int(re.findall(r'\d+', date)[-1]))) & (cn['CAB']==cab) & (cn['TYPE BAYAR']=='QRIS TELKOM')].index:
                                    x = qtw[(qtw['ID']==cn.loc[i,'NAMA TAMU']) 
                                            & (qtw['NOM']==cn.loc[i,'TOTAL BILL'])].index
                                    if len(x) >= 1:
                                        qtw.loc[x[0], 'KET']='Cancel Nota'
                                        cn.loc[i, 'KET'] = 'Done'
            
                        qtw['KET'] = qtw['CODE']
            
                        def compare_time(df_w, df_i, time):
                            for i in range(0,df_i.shape[0]):
                                if df_i.loc[i,'KET']=='' :
                                    list_ind = df_w[((df_w['NOM'] - df_i.loc[i,'NOM'])==0) & ((df_w['NOM']-df_i.loc[i,'NOM'])>=0) & (df_w['HELP']=='')].index
                                    for x in list(list_ind):
                                        if ((df_w.loc[x,'TIME']) - df_i.loc[i,'TIME']  >= dt.timedelta(minutes=0)):
                                            if ((df_w.loc[x,'TIME']) - df_i.loc[i,'TIME'] < dt.timedelta(minutes=time)):
                                                if ((df_w.loc[x,'NOM']-df_i.loc[i,'NOM'])==0):
                                                    df_i.loc[i,'KET'] = 'Balance '+ str(df_w.loc[x,'CODE'])
                                                    df_w.loc[x,'KET'] = 'Balance '+ str(df_w.loc[x,'CODE'])
                                                    df_w.loc[x,'HELP'] = df_w.loc[x,'CODE']
                                                    break                          
                                        if ((df_w.loc[x,'TIME']) - df_i.loc[i,'TIME']  < dt.timedelta(minutes=0)):
                                            if ((df_i.loc[i,'TIME']) - df_w.loc[x,'TIME'] < dt.timedelta(minutes=time)):
                                                if ((df_w.loc[x,'NOM']-df_i.loc[i,'NOM']))==0:
                                                    df_i.loc[i,'KET'] = 'Balance '+ str(df_w.loc[x,'CODE'])
                                                    df_w.loc[x,'KET'] = 'Balance '+ str(df_w.loc[x,'CODE'])
                                                    df_w.loc[x,'HELP'] = df_w.loc[x,'CODE']
                                                    break
                                                                        
            
                            for i in df_i[df_i['KET']==''].index :
                                if df_i.loc[i,'TIME'] > pd.to_datetime('23:00:00' , format='%H:%M:%S'):
                                    df_i.loc[i,'KET'] = 'Invoice Beda Hari'
                                else:
                                    df_i.loc[i,'KET'] = 'Tidak Ada Invoice Ojol'
            
                            for i in df_w[df_w['HELP']==''].index :
                                if df_w.loc[i,'TIME'] < pd.to_datetime('01:00:00' , format='%H:%M:%S'):
                                    df_w.loc[i,'KET'] = 'Transaksi Kemarin'
                                else:
                                    df_w.loc[i,'KET'] = 'Tidak Ada Invoice Ojol' 
                        compare_time(qtw, qti, time_qt)
            
                        all = pd.concat([qtw, qti,]).sort_values(['CAB','DATE','KET', 'SOURCE','NOM','TIME'],ascending=[True,True,True,False,True,True]).drop(columns='HELP')
                        if ket == 'selisih':
                            all = all[~(all['KET'].str.contains('Balance'))]
                        all['HELP'] = all['KET'].apply(lambda x: label_1(x))
                        all['KET'] = all['KET'].apply(lambda x:x if (('Selisih' in x) | ('Balance' in x)) else '')
                        #all['DATE'] = all['DATE'].dt.strftime('%d/%m/%Y')
                        #all['TIME'] = all['TIME'].dt.strftime('%H:%M:%S')
                        all['KAT'] = 'QRIS TELKOM'
                        all.to_csv(f'{tmpdirname}/_bahan/QRIS TELKOM_{cab}_{date}.csv', index=False)
                        st.write('QRIS TELKOM', ': File processed')
                             
                    if not ((dfinv[(dfinv['KAT'].str.contains('EDC')) & (dfinv['CAB']  ==  cab) & (dfinv['DATE2']==date)].empty) or
                            (dfweb[(dfweb['KAT'].str.contains('EDC')) & (dfweb['CAB']  ==  cab) & (dfweb['DATE']==date)].empty)) :
                        edi   =   dfinv[dfinv['KAT'].str.contains('EDC')]
                        edw   =   dfweb[dfweb['KAT'].str.contains('EDC')]
                        edi   =   edi[edi['CAB']  ==  cab]
                        edw   =   edw[edw['CAB']  ==  cab]
                        edi = edi[edi['DATE2']==date]
                        edw = edw[edw['DATE']==date]
                    
                                                
                        edi = edi.sort_values(by=['CAB', 'NOM', 'DATE'], ascending=[True, True, True]).reset_index(drop=True)
                        edw = edw.sort_values(by=['CAB', 'NOM', 'TIME'], ascending=[True, True, True]).reset_index(drop=True)
                        
                    
                        edi.drop_duplicates(inplace=True)
                        edw['ID'] = edw['ID'].str.upper()
                        edw.loc[edw[edw['ID'].isna()].index,'ID'] = ''
                        for i in cn[(cn['TANGGAL']==str(int(re.findall(r'\d+', date)[-1]))) & (cn['CAB']==cab) & (cn['TYPE BAYAR']=='EDC')].index:
                                    x = edw[(edw['ID']==cn.loc[i,'NAMA TAMU']) 
                                            & (edw['NOM']==cn.loc[i,'TOTAL BILL'])].index
                                    if len(x) >= 1:
                                        edw.loc[x[0], 'KET']='Cancel Nota'
                                        cn.loc[i, 'KET'] = 'Done'
                                        
                        edi['ID2'] = edi['ID']                     
                        edw['KET'] = edw['CODE']
                    
                        def compare_time(df_w, df_i):
                            for i in range(0,df_i.shape[0]):
                                if df_i.loc[i,'KET']=='' :
                                    list_ind = df_w[(df_w['NOM'] == df_i.loc[i,'NOM']) & (df_w['HELP']=='')].index
                                    for x in list(list_ind):
                                        if (df_i.loc[i,'DATE'] - df_w.loc[x,'DATE']) == dt.timedelta(days=0):
                                                if ((df_w.loc[x,'NOM']-df_i.loc[i,'NOM'])==0):
                                                    df_i.loc[i,'KET'] = 'Balance '+ str(df_w.loc[x,'CODE'])
                                                    df_w.loc[x,'KET'] = 'Balance '+ str(df_w.loc[x,'CODE'])
                                                    df_w.loc[x,'HELP'] = df_w.loc[x,'CODE']
                                                    break        
                                        elif (df_i.loc[i,'DATE'] - df_w.loc[x,'DATE']) == dt.timedelta(days=1):
                                                if ((df_w.loc[x,'NOM']-df_i.loc[i,'NOM'])==0):
                                                    df_i.loc[i,'KET'] = 'Transaksi Kemarin'
                                                    df_w.loc[x,'KET'] = 'Invoice Beda Hari'
                                                    df_w.loc[x,'HELP'] = df_w.loc[x,'CODE']
                                                break
                    
                            for i in df_i[df_i['KET']==''].index :
                                    df_i.loc[i,'KET'] = 'Tidak Ada Transaksi di Web'
                    
                            for i in df_w[df_w['HELP']==''].index :
                                    df_w.loc[i,'KET'] = 'Tidak Ada Invoice Ojol' 
                        compare_time(edw, edi)
                    
                        all = pd.concat([edw, edi]).sort_values(['CAB','DATE','KET', 'SOURCE','NOM','TIME'],ascending=[True,True,True,False,True,True]).drop(columns='HELP')
                        if ket == 'selisih':
                            all = all[~(all['KET'].str.contains('Balance'))]
                        all['HELP'] = all['KET'].apply(lambda x: label_1(x))
                        all['KET'] = all['KET'].apply(lambda x:x if (('Selisih' in x) | ('Balance' in x)) else '')
                        #all['DATE'] = all['DATE'].dt.strftime('%d/%m/%Y')
                        #all['TIME'] = all['TIME'].dt.strftime('%H:%M:%S')
                        all.to_csv(f'{tmpdirname}/_bahan/EDC_{cab}_{date}.csv', index=False)
                        st.write('EDC', ': File processed')
                                    

            combined_dataframes = []
            files = []
            for cab in all_cab:
                 for date in all_date:
                    for ojol in all_kat:
                        if os.path.exists(f'{tmpdirname}/_bahan/{ojol}_{cab}_{date}.csv'):
                            file = pd.read_csv(f'{tmpdirname}/_bahan/{ojol}_{cab}_{date}.csv')
                            if not file.empty:
                                #file['TIME'] = pd.to_datetime(file['TIME']).dt.strftime('%H:%M:%S')
                                files.append(file)
            
                    # Concatenate CSV files within each subfolder
            df_all = pd.concat(files)
            df_concat = []
            for cab in all_cab:
                for kat in ['GO RESTO', 'QRIS SHOPEE', 'GRAB FOOD','SHOPEEPAY', 'QRIS ESB','QRIS TELKOM','EDC']:
                    if not df_all[(df_all['CAB'] == cab) & (df_all['KAT'].str.contains(kat))].empty:
                        df_all2 = df_all[(df_all['CAB'] == cab) & (df_all['KAT']==kat)].reset_index(drop=True)
                        df_all3 = df_all2.loc[df_all2[(df_all2['KET'].isna()) & (df_all2['HELP'].str.contains('|'.join(['Transaksi Kemarin','Tidak Ada','Invoice Beda Hari'])))].index,].copy()
                        df_all3.loc[:,'HELP'] = ''
                        for i in df_all3[(df_all3['HELP']=='')].index:
                            if (df_all3.loc[i,'SOURCE']=='WEB') & (df_all3.loc[i,'HELP']==''):
                                if kat in ['SHOPEEPAY','GRAB FOOD']:
                                    x = df_all3[(df_all3['DATE']==(pd.to_datetime(df_all3.loc[i,'DATE'])+ dt.timedelta(days=1)).strftime('%Y-%m-%d')) 
                                        & (df_all3['ID2'] == df_all3.loc[i,'ID2'])
                                        & (abs(df_all3.loc[i,'NOM'] - df_all3['NOM']) <=200)
                                        & (df_all3['SOURCE']=='INVOICE') & (df_all3['HELP']=='')
                                        & (abs(pd.to_datetime(str(pd.to_datetime(df_all3.loc[i,'TIME']) - pd.to_datetime(df_all3['TIME'])))) <= dt.timedelta(minutes=150))].index
                                if kat in ['GO RESTO', 'QRIS SHOPEE', 'QRIS TELKOM']:
                                    x = df_all3[(df_all3['DATE']==(pd.to_datetime(df_all3.loc[i,'DATE'])+ dt.timedelta(days=1)).strftime('%Y-%m-%d')) 
                                        & (abs(df_all3.loc[i,'NOM'] - df_all3['NOM']) <=200)
                                        & (df_all3['SOURCE']=='INVOICE') & (df_all3['HELP']=='')
                                        & (abs(pd.to_datetime(str(pd.to_datetime(df_all3.loc[i,'TIME']) - pd.to_datetime(df_all3['TIME'])))) <= dt.timedelta(minutes=150))].index                                                        
                                if kat in ['QRIS ESB']:
                                    x = df_all3[(df_all3['DATE']==(pd.to_datetime(df_all3.loc[i,'DATE'])+ dt.timedelta(days=1)).strftime('%Y-%m-%d')) 
                                        & (df_all3['ID'] == df_all3.loc[i,'CODE'])
                                        & (abs(df_all3.loc[i,'NOM'] - df_all3['NOM']) <=200)
                                        & (df_all3['SOURCE']=='INVOICE') & (df_all3['HELP']=='')
                                        & (abs(pd.to_datetime(pd.to_datetime(df_all3.loc[i,'TIME']) - pd.to_datetime(df_all3['TIME']))) <= dt.timedelta(minutes=150))].index                                                        
                                if len(x)>=1:
                                    x = abs(pd.to_datetime(pd.to_datetime(df_all3.loc[i,'TIME']) - pd.to_datetime(df_all3['TIME']))).sort_values().index[-1]
                                    if kat in ['GRAB FOOD']:
                                        df_all3.loc[i, 'HELP'] = 'Invoice Beda Hari'
                                        df_all3.loc[x, 'HELP'] = 'Transaksi Kemarin'       
                                    else:
                                        if (float(df_all3.loc[i,'NOM2'])-float(df_all3.loc[x,'NOM']))==0:
                                            df_all3.loc[i, 'HELP'] = 'Invoice Beda Hari'
                                            df_all3.loc[x, 'HELP'] = 'Transaksi Kemarin'
                                        else:
                                            df_all3.loc[i, 'HELP'] = 'Selisih IT'
                                            df_all3.loc[i, 'KET'] = 'Selisih '+ str(df_all3.loc[x,'ID']) + difference(df_all3.loc[x,'NOM'],df_all3.loc[i,'NOM2'])
                                            df_all3.loc[x, 'HELP'] = 'Selisih IT' 
                                            df_all3.loc[x, 'KET'] = 'Selisih '+ str(df_all3.loc[x,'ID']) + difference(df_all3.loc[x,'NOM'],df_all3.loc[i,'NOM2'])   
                            if (df_all3.loc[i, 'HELP'] == '') & (df_all3.loc[i, 'SOURCE']=='WEB'):
                                df_all3.loc[i, 'HELP'] = f"Tidak Ada Invoice {'Ojol' if kat in ['GO RESTO','GRAB FOOD','SHOPEEPAY'] else 'QRIS'}" 
                            if (df_all3.loc[i, 'HELP'] == '') & (df_all3.loc[i, 'SOURCE']=='INVOICE'):
                                df_all3.loc[i, 'HELP'] = 'Tidak Ada Transaksi di Web'
                        all = pd.concat([df_all2.loc[df_all2[~((df_all2['KET'].isna()) & (df_all2['HELP'].str.contains('|'.join(['Transaksi Kemarin','Tidak Ada','Invoice Beda Hari']))))].index,],df_all3]).sort_values(['CAB','DATE'])
                        all['DATE'] = pd.to_datetime(all['DATE']).dt.strftime('%d/%m/%Y')
                        
                        
                        df_concat.append(all)
                        #pd.to_datetime(str(df_all3.loc[i,'DATE'].strftime('%Y-%m-%d')) + ' ' + str(df_all3.loc[i,'TIME']))
            
            #combined_dataframes.append(df_all)
            final_df = pd.concat(df_concat, ignore_index=True)
            for cab in final_df['CAB'].unique():
                if cab in ['MKSAHM', 'BPPHAR', 'MKSPER', 'MKSTUN', 'MKSPOR', 'MKSPET', 'MKSRAT','SMRYAM', 'SMRAHM']:
                    final_df.loc[(final_df[final_df['SOURCE']=='INVOICE') & (final_df[final_df['CAB']==cab)].index,'TIME'] = pd.to_datetime(final_df.loc[(final_df[final_df['SOURCE']=='INVOICE') & (final_df[final_df['CAB']==cab)].index,'TIME']) - dt.timedelta (hours=1, minutes=1)
            final_df['NOM'] = final_df.apply(lambda row: row['NOM'] if row['SOURCE']=='INVOICE' else row['NOM2'],axis=1)
            if 'ID2' not in final_df.columns:
                final_df =  final_df[['CAB','DATE','TIME','CODE','ID','NOM','KAT','SOURCE','KET','HELP']]
            else:
                final_df =  final_df[['CAB','DATE','TIME','CODE','ID','NOM','KAT','SOURCE','KET','HELP','ID2']]
            final_df['TIME'] = pd.to_datetime(final_df['TIME']).dt.strftime('%H:%M:%S')
            time_now = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            st.markdown('### Output')
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                zip_file.writestr(f'MERGE_{time_now}.csv', final_merge.sort_values(['CAB','DATE','TIME']).to_csv(index=False))
                zip_file.writestr(f'BREAKDOWN_{time_now}.csv', final_df.to_csv(index=False))
            
            # Pastikan buffer ZIP berada di awal
            zip_buffer.seek(0)
            
            # Tombol untuk mengunduh file ZIP
            st.download_button(
                label="Download all Files",
                data=zip_buffer,
                file_name=f'ABO_{time_now}.zip',
                mime='application/zip',
            )  
            


                    

    
