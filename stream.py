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

            st.markdown('### Cleaning')
            st.write('CANCEL NOTA')
            main_folder = f'{tmpdirname}/_bahan/CANCEL_NOTA'
            
            # Get the list of subfolders within the main folder
            subfolders = [folder for folder in os.listdir(main_folder) if os.path.isdir(os.path.join(main_folder, folder))]
            
            # List to store concatenated dataframes
            combined_dataframes = []
            
            # Iterate over each subfolder
            for subfolder in subfolders:
                # Glob pattern to get all CSV files in the subfolder
                files = glob(os.path.join(main_folder, subfolder, '*.xlsx'))
                # Concatenate CSV files within each subfolder
                dfs = []
                for file in files:
                    try:
                        df = pd.read_excel(file,sheet_name='Rekap nota cancel & salah input', header=0)
                        df = df.loc[:,df.columns[:9]].dropna(subset=['Unnamed: 2']).reset_index(drop=True)
                        df.columns = df.loc[0,:].values
                        df = df.loc[1:,]
                        df = df[df['TANGGAL']!='TANGGAL']
                        df['TOTAL BILL'] = df['TOTAL BILL'].astype('float')
                        df['CAB'] = subfolder
                        df['KET'] = ''
                        df = df[df['TOTAL BILL']>0]
                        df['TOTAL BILL'] = df['TOTAL BILL'].astype('float')
                        df['TANGGAL'] = df['TANGGAL'].fillna('0').astype('int').astype('str')
                        combined_dataframes.append(df)
                    except Exception as excel_exception:
                        st.write(f"Error process {file} as Excel: {excel_exception}")
            
            # Check if there are any dataframes to concatenate
            if combined_dataframes:
                # Concatenate dataframes from all subfolders
                final_df = pd.concat(combined_dataframes)
                
                # Optionally, you can save the final dataframe to a CSV file
                final_df.to_csv(f'{tmpdirname}/_merge/merge_cancel_nota.csv', index=False)
            
                st.write("File CANCEL NOTA Concatenated")
            else:
                st.write("No dataframes to concatenate.")

            cn = final_df.reset_index(drop=True)
            cn['TOTAL BILL'] = cn['TOTAL BILL'].astype('float')
            cn['TANGGAL'] = cn['TANGGAL'].fillna('0').astype('int').astype('str')
            
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
                    for file in files:
                        df = pd.read_csv(file)
                        df = df.rename(columns={'Gross Sales':'Gross Amount'})
                        # Add a new column for the folder name
                        df['Folder'] = subfolder
                        combined_dataframes.append(df)
                else:
                    print(f"File in subfolder: {subfolder} does not exist. Please double check")
        
            if combined_dataframes:
                final_df = pd.concat(combined_dataframes)
                final_df.to_csv(f'{tmpdirname}/_merge/merge_Gojek 1.csv', index=False)
                st.write("File GOJEK 1 Concatenated")
            else:
                st.write("No dataframes to concatenate.")  
    
            st.write('GOJEK 2')
            # Path to the folder containing the subfolders
            main_folder = f'{tmpdirname}/_bahan/GOJEK 2'
            
            # Get the list of subfolders within the main folder
            subfolders = [folder for folder in os.listdir(main_folder) if os.path.isdir(os.path.join(main_folder, folder))]
            
            # List to store concatenated dataframes
            combined_dataframes = []
            
            # Iterate over each subfolder
            for subfolder in subfolders:
                # Glob pattern to get all CSV files in the subfolder
                files = glob(os.path.join(main_folder, subfolder, '*.csv'))
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
                final_df = pd.concat(combined_dataframes)
                
                # Optionally, you can save the final dataframe to a CSV file
                final_df.to_csv(f'{tmpdirname}/_merge/merge_Gojek 2.csv', index=False)
                st.write("File Gojek 2 Concatenated")
            else:
                st.write("No dataframes to concatenate.")

            st.write('GOJEK 3')
            main_folder = f'{tmpdirname}/_bahan/GOJEK 3/'
            
            subfolders = [folder for folder in os.listdir(main_folder) if os.path.isdir(os.path.join(main_folder, folder))]
            
            # Initialize an empty list to store dataframes
            dfs = []
            
            combined_dataframes = []
            # Iterate over each file in the folder
            for filename in os.listdir(main_folder):
                if filename.endswith('.csv'):  # Assuming all files are CSV format, adjust if needed
                    file_path = os.path.join(main_folder, filename)
                    # Read each file into a dataframe and append to the list
                    dfs.append(pd.read_csv(file_path))
            
            # Check if there are any dataframes to concatenate
            if dfs:
                # Concatenate all dataframes in the list into one dataframe
                concatenated_df = pd.concat(dfs, ignore_index=True)
            
                # Lookup
                storename = pd.read_csv(f'{tmpdirname}/_bahan/bahan/Store Name GOJEK.csv')
            
                for subfolder in subfolders:
                    df = concatenated_df[concatenated_df['Outlet name']==storename[storename['CAB']==subfolder]['Outlet name'].values[0]]
                    df['CAB'] = subfolder
                    combined_dataframes.append(df)
            
                # Export the concatenated dataframe to CSV in the specified path
                pd.concat(combined_dataframes).to_csv(f'{tmpdirname}/_merge/merge_Gojek 3.csv', index=False)
            
                st.write("File GOJEK 3 Concatenated")
            else:
                st.write("No dataframes to concatenate.")
    
            st.write('SHOPEE FOOD')
            main_folder = f'{tmpdirname}/_bahan/SHOPEE FOOD'
            
            # List to store concatenated dataframes
            combined_dataframes = []
            
            # Iterate over each subfolder
            for subfolder in os.listdir(main_folder):
                folder_path = os.path.join(main_folder, subfolder)
                if os.path.isdir(folder_path):
                    # Glob pattern to get all CSV files in the subfolder
                    files = glob(os.path.join(folder_path, '*.csv'))
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
                final_df = pd.concat(combined_dataframes, ignore_index=True)
                final_df.to_csv(f'{tmpdirname}/_merge/merge_Shopee Food.csv', index=False)
                st.write("File SHOPEE FOOD Concatenated")
            else:
                st.write("No dataframes to concatenate.")
            
            st.write('SHOPEE FOOD 2')
            main_folder = f'{tmpdirname}/_bahan/SHOPEE FOOD 2'
            
            # List to store concatenated dataframes
            combined_dataframes = []
            
            # Iterate over each subfolder
            for subfolder in os.listdir(main_folder):
                folder_path = os.path.join(main_folder, subfolder)
                if os.path.isdir(folder_path):
                    # Glob pattern to get all CSV files in the subfolder
                    files = glob(os.path.join(folder_path, '*.csv'))
                    # Concatenate CSV files within each subfolder
                    dfs = [pd.read_csv(file) for file in files]
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
                final_df = pd.concat(combined_dataframes, ignore_index=True).fillna("TO")
                final_df = final_df[final_df['Store Name'] !=  'TO']
            
                # Optionally, you can save the final dataframe to a CSV file
                final_df.to_csv(f'{tmpdirname}/_merge/merge_Shopee Food 2.csv', index=False)
            
                st.write("File SHOPEE FOOD 2 Concatenated")
            else:
                st.write("There are no files to concatenate.")
            
            st.write('GRAB *csv')
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
                concatenated_df = pd.concat(dfs, ignore_index=True)
            
                # Lookup
                storename = pd.read_csv(f'{tmpdirname}/_bahan/bahan/Store Name GRAB.csv')
                concatenated_df = pd.merge(concatenated_df, storename, how='left', on='Store Name').fillna('')
                concatenated_df = concatenated_df[concatenated_df['CAB'] != '']
                # Export the concatenated dataframe to CSV in the specified path
                output_path = f'{tmpdirname}/_merge/merge_Grab 1.csv'
                concatenated_df.to_csv(output_path, index=False)
            
                st.write("File GRAB *csv Concatenated")
            else:
                st.write("There are no files to concatenate.")
            
            st.write('GRAB *xls')
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
                merged_df = pd.concat(dataframes, ignore_index=True)
            
                # Lookup
                storename = pd.read_csv(f'{tmpdirname}/_bahan/bahan/Store Name GRAB.csv')
                merged_df = pd.merge(merged_df, storename, how='left', on='Store Name').fillna('')
            
                # Save the merged DataFrame to a CSV file without row index
                output_file = f'{tmpdirname}/_merge/merge_Grab 2.csv'
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                merged_df.to_csv(output_file, index=False)
            
                st.write("File GRAB *xls Concatenated")
            else:
                st.write("No dataframes to concatenate.")
            
            
            # Function to preprocess each DataFrame
            def preprocess_dataframe(df):
                # Specify the column to split and the separator
                column_to_split = "Merchant Host,Partner Merchant ID,Merchant/Store Name,Transaction Type,Merchant Scope,Transaction ID,Reference ID,Parent ID,External Reference ID,Issuer Identifier,Transaction Amount,Fee (MDR),Settlement Amount,Terminal ID,Create Time,Update Time,Adjustment Reason,Entity ID,Fee (Cofunding),Reward Amount,Reward Type,Promo Type,Payment Method,Currency Code,Voucher Promotion Event Name,Fee (Withdrawal),Fee (Handling)"
                separator = ","
            
                # Split the specified column by the separator and expand it into separate columns
                split_columns = df[column_to_split].str.split(separator, expand=True)
            
                # Rename the split columns
                split_columns.columns = column_to_split.split(",")
            
                # Concatenate the new columns with the original DataFrame
                df = pd.concat([df, split_columns], axis=1)
            
                # Drop the original column which was split
                df.drop(columns=[column_to_split], inplace=True)
            
                # Drop 'Unnamed: 0' if it exists
                df.drop(columns=['Unnamed: 0'], errors='ignore', inplace=True)
            
                # Take out unnecessary data
                df = df[df['Transaction Type'] == 'Payment']
            
                return df
            
            st.write('QRIS SHOPEE *,')
            # Path to the folder containing the subfolders
            main_folder = f'{tmpdirname}/_bahan/QRIS_SHOPEE/QRIS A (Separator ,)/'
            
            # Get the list of subfolders within the main folder
            subfolders = [folder for folder in os.listdir(main_folder) if os.path.isdir(os.path.join(main_folder, folder))]
            
            # List to store concatenated dataframes
            combined_dataframes = []
            
            # Iterate over each subfolder
            for subfolder in subfolders:
                folder_path = os.path.join(main_folder, subfolder)
                # Concatenate CSV files within each subfolder after preprocessing
                files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]
                if files:
                    df_subfolder = pd.concat([preprocess_dataframe(pd.read_csv(os.path.join(folder_path, file))) for file in files])
                    # Add a new column for the folder name
                    df_subfolder['Folder'] = subfolder
                    combined_dataframes.append(df_subfolder)
                else:
                    print(f"File in subfolder: {subfolder} does not exist. Please double check")
            
            # Check if there are any dataframes to concatenate
            if combined_dataframes:
                # Concatenate dataframes from all subfolders
                final_df = pd.concat(combined_dataframes)
            
                # Format Time
                final_df['Update Time'] = pd.to_datetime(final_df['Update Time'], format='%Y-%m-%d %H:%M:%S')
                final_df['DATE'] = final_df['Update Time'].dt.strftime('%d/%m/%Y')
                final_df['TIME'] = final_df['Update Time'].dt.time
            
                # Save the final dataframe to a CSV file
                output_path = f'{tmpdirname}/_bahan/QRIS_SHOPEE/merge/merge_QRIS S_A.csv'
                final_df.to_csv(output_path, index=False)
            
                st.write("File QRIS SHOPEE *, Concatenated")
            else:
                st.write("No dataframes to concatenate.")
            
            
            st.write('QRIS SHOPEE *;')
            # Define the base folder path
            base_folder_path = f'{tmpdirname}/_bahan/QRIS_SHOPEE/QRIS B (Separator ;)'
            
            # Function to remove separator "," from a CSV file and export to a new file
            def remove_separator_from_csv(file_path):
                with open(file_path, 'r', newline='') as input_file:
                    reader = csv.reader(input_file)
                    rows = [','.join(row).replace(',', '') for row in reader]
            
                with open(file_path, 'w', newline='') as output_file:
                    writer = csv.writer(output_file)
                    for row in rows:
                        writer.writerow([row])
            
            # Initialize a variable to track if any CSV files were processed
            csv_processed = False
            
            # Traverse through all subdirectories and remove separators from CSV files
            for dirpath, dirnames, filenames in os.walk(base_folder_path):
                for filename in filenames:
                    if filename.endswith('.csv'):
                        file_path = os.path.join(dirpath, filename)
                        remove_separator_from_csv(file_path)
                        print(f"Removed separator from {file_path}")
                        # Set the flag indicating CSV files were processed
                        csv_processed = True
            
                # st.write a message if no CSV files are found in a subfolder
                if not filenames:
                    print(f"File in subfolder: {subfolder} does not exist. Please double check")
    
            
            base_folder_path = f'{tmpdirname}/_bahan/QRIS_SHOPEE/QRIS B (Separator ;)'
            
            # Function to recursively find all CSV files in a directory and its subdirectories
            def find_csv_files(directory):
                csv_files = []
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file.endswith('.csv'):
                            csv_files.append(os.path.relpath(os.path.join(root, file), directory))
                return csv_files
            
            def read_csv_files(files, directory):
                dfs = []
                for file in files:
                    try:
                        file_path = os.path.join(directory, file)
                        folder = os.path.basename(os.path.dirname(file_path))
                        df = pd.read_csv(file_path, delimiter=';')
                        try:
                            df['Update Time'] = pd.to_datetime(df['Update Time'], format='%d/%m/%Y %H:%M')
                            df['DATE'] = df['Update Time'].dt.strftime('%d/%m/%Y')
                            df['TIME'] = df['Update Time'].dt.time
                        except Exception:
                            try:
                                df['Update Time'] = pd.to_datetime(df['Update Time'], format='%m/%d/%Y %H:%M')
                                df['DATE'] = df['Update Time'].dt.strftime('%d/%m/%Y')
                                df['TIME'] = df['Update Time'].dt.time
                            except Exception as e:
                                print(f"Error formatting time: {e}")
                        df['Folder'] = folder
                        dfs.append(df)
                    except Exception as e:
                        print(f"Error reading {file}: {e}")
                return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
            
            # Find all CSV files in the base folder and its subfolders
            csv_files = find_csv_files(base_folder_path)
            
            # Read all CSV files into a single DataFrame and add "Folder" column
            if csv_files:
                df = read_csv_files(csv_files, base_folder_path)
            else:
                print("No CSV files found.")
                df = pd.DataFrame()
            
            # Only proceed if the DataFrame is not empty
            if not df.empty:
                # Export DataFrame to CSV
                output_file_path = f"{tmpdirname}/_bahan/QRIS_SHOPEE/merge/merge_QRIS S_B.csv"
                df.to_csv(output_file_path, index=False)
                st.write("File QRIS SHOPEE *; Concatenated")
            else:
                st.write("No dafaframes to concatenate.")
            
            st.write('QRIS SHOPEE')
            # Define the folder path
            folder_path = f'{tmpdirname}/_bahan/QRIS_SHOPEE/QRIS C (Normal)'
            output_path = f'{tmpdirname}/_bahan/QRIS_SHOPEE/merge/merge_QRIS S_C.csv'
            
            # Function to add the "Folder" column to a CSV file
            def add_folder_column(csv_file_path, folder_name):
                # Read the CSV file
                df = pd.read_csv(csv_file_path)
                # Add the "Folder" column with the folder name
                df['Folder'] = folder_name
                # Return the modified DataFrame
                return df
            
            # Initialize an empty list to store DataFrames
            dfs = []
            
            # Iterate through each directory and subdirectory
            for root, dirs, files in os.walk(folder_path):
                # Iterate through each file
                for file in files:
                    # Check if the file is a CSV file
                    if file.endswith('.csv'):
                        # Get the full path of the CSV file
                        csv_file_path = os.path.join(root, file)
                        # Get the name of the parent folder
                        folder_name = os.path.basename(root)
                        # Add the "Folder" column to the CSV file and append to the list
                        df = add_folder_column(csv_file_path, folder_name)
                        dfs.append(df)
            
            # Check if any CSV files were processed
            if dfs:
                # Concatenate all DataFrames in the list
                merged_df = pd.concat(dfs, ignore_index=True)
            
                # Format Time
                try:
                    merged_df['Update Time'] = pd.to_datetime(merged_df['Update Time'], format='%d/%m/%Y %H:%M', errors='coerce').fillna(pd.to_datetime(merged_df['Update Time'],format='%Y-%m-%d %H:%M:%S', errors='ignore'))
                    merged_df['DATE'] = merged_df['Update Time'].dt.strftime('%d/%m/%Y')
                    merged_df['TIME'] = merged_df['Update Time'].dt.time
                except Exception as e:
                    print(f"Error formatting time: {e}")
            
                # Save the merged DataFrame to a CSV file
                merged_df.to_csv(output_path, index=False)
                print("File QRIS SHOPEE Concatenated")
            else:
                print("No dataframes to concatenate.")
            
            
            # Define the directory containing the CSV files
            directory = f'{tmpdirname}/_bahan/QRIS_SHOPEE/merge'
            
            # Initialize an empty list to store DataFrames
            dfs = []
            
            # Iterate over each file in the directory
            for filename in os.listdir(directory):
                if filename.endswith('.csv'):
                    filepath = os.path.join(directory, filename)
                    try:
                        # Read each CSV file into a DataFrame and append to the list
                        dfs.append(pd.read_csv(filepath))
                    except Exception as e:
                        st.write(f"Error reading {filepath}: {e}")
            
            # Check if any CSV files were processed
            if dfs:
                # Concatenate all DataFrames in the list along axis 0 (rows)
                concatenated_df = pd.concat(dfs, ignore_index=True)
            
                # Export the concatenated DataFrame to a CSV file
                output_file = f'{tmpdirname}/_merge/merge_QRIS Shopee.csv'
                concatenated_df.to_csv(output_file, index=False)
            
                st.write('File QRIS SHOPEE Concatenated')
            else:
                st.write("No dataframes to concatenate.")
            
            st.write('QRIS IA')
             #Specify the directory where the HTML files are located
            folder_path = f'{tmpdirname}/_bahan/QRIS_IA/'
            
             #Initialize a list to store DataFrames from each file
            dataframes = []
            
             #Walk through all directories and subdirectories
            for root, dirs, files in os.walk(folder_path):
                for file_name in files:
                    if file_name.endswith('.xls'):  # Make sure only Excel files are processed
                        file_path = os.path.join(root, file_name)
                        try:
                            # Read the HTML tables into a list of DataFrames
                            html_tables = pd.read_html(file_path, header=0, encoding='ISO-8859-1')  # Specify header as 0
                            # If there are tables in the HTML content
                            if html_tables:
                                # Iterate through each DataFrame in the list
                                for df in html_tables:
                                    # Extract the subfolder name
                                    subfolder_name = os.path.basename(os.path.dirname(file_path))
                                    # Add a new column with the subfolder name
                                    df['Folder'] = subfolder_name
                                    dataframes.append(df)
                        except Exception as e:
                            ptint(f"Error reading {file_path}: {e}")
            
            if dataframes:
                # Concatenate all DataFrames into one DataFrame
                merged_qris_ia = pd.concat(dataframes, ignore_index=True)
            
                merged_qris_ia = merged_qris_ia[merged_qris_ia['ID Transaksi']      !=      "Summary"]
            
                # Save the merged DataFrame to a CSV file without row index
                output_file = f'{tmpdirname}/_merge/merge_QRIS IA.csv'
                merged_qris_ia.to_csv(output_file, index=False)
                st.write("File QRIS TELKOM Concatenated")
            else:
                st.write("No dafaframes to concatenate.")

            st.write('QRIS ESB')
            # Specify the directory where the HTML files are located
            folder_path = f'{tmpdirname}/_bahan/QRIS_ESB/'
            
            # Initialize a list to store DataFrames from each file
            dataframes = []
            
            # Loop through each file in the folder
            for file_name in os.listdir(folder_path):
                if file_name.endswith('.xlsx'):  # Make sure only HTML files are processed
                    file_path = os.path.join(folder_path, file_name)
                    df = pd.read_excel(file_path)
                    df = df[~df.loc[:,'Unnamed: 2'].isna()].reset_index(drop=True)
                    # Remove the first row
                    df.columns = df.loc[0,:].values
                    df = df.loc[1:,]
                    dataframes.append(df)
            if dataframes:
                merged_web = pd.concat(dataframes, ignore_index=True)
                # Save the merged DataFrame to a CSV file without row index
                output_file = f'{tmpdirname}/_merge/merge_ESB.csv'
                merged_web.to_csv(output_file, index=False)
                st.write("FIle QRIS ESB Concatenated")
            else:
                st.write("No dataframes to concatenate.")     
            
            
            st.write('WEB')
            # Specify the directory where the HTML files are located
            folder_path = f'{tmpdirname}/_bahan/WEB/'
            
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
                            dataframes.append(df)
                    except Exception as e:
                        st.write(f"Error reading {file_path}: {e}")
            
            # Check if any HTML files were processed
            if dataframes:
                # Concatenate all DataFrames into one DataFrame
                merged_web = pd.concat(dataframes, ignore_index=True)
            
                # Save the merged DataFrame to a CSV file without row index
                output_file = f'{tmpdirname}/_merge/merge_WEB.csv'
                merged_web.to_csv(output_file, index=False)
            
                # Read the CSV file skipping the first row
                final_web = pd.read_csv(output_file, skiprows=[0])
            
                # Filter out rows where the 'DATE' column contains "DATE" or "TOTAL"
                final_web = final_web[~final_web['DATE'].str.contains('DATE|TOTAL')]
            
                # Save the DataFrame without row index to a new CSV file
                final_web.to_csv(output_file, index=False)
            
                st.write("FIle WEB Concatenated")
            else:
                st.write("No dataframes to concatenate.")           
    
            st.markdown('### Preparing')

            gojek1_path       = f'{tmpdirname}/_merge/merge_Gojek 1.csv'
            outputgojek1_path = f'{tmpdirname}/_final/Final Gojek 1.csv'
            
            st.write('GOJEK 1')
            if os.path.exists(gojek1_path):
                #Read data merge GOJEK 1
                df_go1      =       pd.read_csv(gojek1_path).fillna('')
                loc_go1     =       df_go1.loc[:,['Waktu Transaksi',
                                                  'Folder',
                                                  'Nomor Pesanan',
                                                  'Gross Amount']].rename(columns={'Waktu Transaksi' : 'DATETIME',
                                                                                  'Folder' : 'CAB',
                                                                                  'Nomor Pesanan' : 'ID',
                                                                                  'Gross Amount' : 'NOM'}).fillna('')
                loc_go1['DATETIME'] = loc_go1['DATETIME'].str.replace('Apr', 'April')
                loc_go1['DATETIME'] = loc_go1['DATETIME'].str.replace('Jun', 'June')            
            
                # Parse datetime column
                loc_go1['DATETIME']    =   pd.to_datetime(loc_go1['DATETIME'], utc=True)
            
                loc_go1['DATE']        =   loc_go1['DATETIME'].dt.strftime('%d/%m/%Y')
                loc_go1['TIME']        =   loc_go1['DATETIME'].dt.time
                del loc_go1['DATETIME']
            
                loc_go1['NOM']         =   pd.to_numeric(loc_go1['NOM']).astype(int)
            
                loc_go1['CODE']        =   ''
            
                loc_go1['KAT']         =   'GO RESTO'
                loc_go1['SOURCE']      =   'INVOICE'
            
                # re-order columns
                loc_go1        =   loc_go1[['CAB', 'DATE', 'TIME', 'CODE', 'ID', 'NOM', 'KAT', 'SOURCE']]
            
                # Save the final result to a new CSV file
                loc_go1.to_csv(outputgojek1_path, index=False)
                st.write(f"File GOJEK 1 processed and saved")
            else:
                st.write("File does not exist. Please double check")
            
            gojek2_path       = f'{tmpdirname}/_merge/merge_Gojek 2.csv'
            outputgojek2_path = f'{tmpdirname}/_final/Final Gojek 2.csv'
            
            st.write('GOJEK 2')
            if os.path.exists(gojek2_path):
                #Read data merge GOJEK 2
                df_go2      =       pd.read_csv(gojek2_path).fillna('')
            
                #Rename columns to match the database schema
                loc_go2     =       df_go2.loc[:,['Waktu Transaksi',
                                                  'Folder',
                                                  'Nomor Pesanan',
                                                  'Gross Amount']].rename(columns={'Waktu Transaksi' : 'DATETIME',
                                                                            'Folder' : 'CAB',
                                                                            'Nomor Pesanan' : 'ID',
                                                                            'Gross Amount' : 'NOM'}).fillna('')
                loc_go2['DATETIME'] = loc_go2['DATETIME'].str.replace('T', ' ').str.slice(0, 19)
                loc_go2['DATETIME'] = loc_go2['DATETIME'].str.replace('Apr', 'April')
                loc_go2['DATETIME'] = loc_go2['DATETIME'].str.replace('Jun', 'June')
                # Parse datetime column
                loc_go2['DATETIME']    =   pd.to_datetime(loc_go2['DATETIME'], utc=True)
            
                loc_go2['DATE']        =   loc_go2['DATETIME'].dt.strftime('%d/%m/%Y')
                loc_go2['TIME']        =   loc_go2['DATETIME'].dt.time
                del loc_go2['DATETIME']
            
                loc_go2['NOM']         =   pd.to_numeric(loc_go2['NOM']).astype(int)
            
                loc_go2['CODE']        =   ''
            
                loc_go2['KAT']         =   'GO RESTO'
                loc_go2['SOURCE']      =   'INVOICE'
            
                # re-order columns
                loc_go2        =   loc_go2[['CAB', 'DATE', 'TIME', 'CODE', 'ID', 'NOM', 'KAT', 'SOURCE']]
            
            
                # Save the final result to a new CSV file
                loc_go2.to_csv(outputgojek2_path, index=False)
                st.write(f"File GOJEK 2 processed and saved")
            else:
                st.write("File does not exist. Please double check")
            
            gojek3_path       = f'{tmpdirname}/_merge/merge_Gojek 3.csv'
            outputgojek3_path = f'{tmpdirname}/_final/Final Gojek 3.csv'
            
            st.write('GOJEK 3')
            if os.path.exists(gojek3_path):
                # Read data merge GOJEK 3
                df_go3 = pd.read_csv(gojek3_path).fillna('')
            
                # Rename columns to match the database schema
                loc_go3 = df_go3.loc[:, ['Transaction time', 'Order ID', 'Amount', 'CAB']].rename(
                    columns={'Transaction time': 'DATETIME', 'Order ID': 'ID', 'Amount': 'NOM'}).fillna('')
            
                loc_go3['DATETIME'] = loc_go3['DATETIME'].str.replace('T', ' ').str.slice(0, 19)
                loc_go3['DATETIME'] = loc_go3['DATETIME'].str.replace('Apr', 'April')
                loc_go3['DATETIME'] = loc_go3['DATETIME'].str.replace('Jun', 'June')
                loc_go3['ID'] = loc_go3['ID'].str.replace("'", '').str.slice(0, 19)
            
                # Parse datetime column
                loc_go3['DATETIME'] = pd.to_datetime(loc_go3['DATETIME'], utc=True)
            
                loc_go3['DATE'] = loc_go3['DATETIME'].dt.strftime('%d/%m/%Y')
                loc_go3['TIME'] = loc_go3['DATETIME'].dt.time
                del loc_go3['DATETIME']
            
                loc_go3['NOM'] = pd.to_numeric(loc_go3['NOM']).astype(int)
            
                loc_go3['CODE'] = ''
            
                loc_go3['KAT'] = 'GO RESTO'
                loc_go3['SOURCE'] = 'INVOICE'
            
                # Re-order columns
                loc_go3 = loc_go3[['CAB', 'DATE', 'TIME', 'CODE', 'ID', 'NOM', 'KAT', 'SOURCE']]
            
                # Save the final result to a new CSV file
                loc_go3.to_csv(outputgojek3_path, index=False)
                st.write(f"File GOJEK 3 processed and saved")
            else:
                st.write("File does not exist. Please double check")
            
            shopee_path       = f'{tmpdirname}/_merge/merge_Shopee Food.csv'
            outputshopee_path = f'{tmpdirname}/_final/Final Shopee Food.csv'
            
            st.write('SHOPEE FOOD')
            if os.path.exists(shopee_path):
                # Read data merge Shopee Food
                df_shopee = pd.read_csv(shopee_path).fillna('')
            
                #Rename columns to match the database schema
                loc_shopee   =   df_shopee.loc[:,['Order Pick up ID',
                                                      'Folder',
                                                      'Order Complete/Cancel Time',
                                                      'Order Amount',
                                                      'Order Status']].rename(columns={'Order Pick up ID' : 'ID',
                                                                                      'Folder' : 'CAB',
                                                                                      'Order Complete/Cancel Time' : 'DATETIME',
                                                                                      'Order Amount' : 'NOM',
                                                                                      'Order Status' : 'Status'}).fillna('')
            
                #loc_shopee['DATETIME'] = loc_shopee['DATETIME'].str.replace('Apr', 'April')
                #loc_shopee['DATETIME'] = loc_shopee['DATETIME'].str.replace('Jun', 'June')            
                loc_shopee['DATETIME']    =   pd.to_datetime(loc_shopee['DATETIME'], format='%d/%m/%Y %H:%M:%S')
                loc_shopee['DATE']        =   loc_shopee['DATETIME'].dt.strftime('%d/%m/%Y')
                loc_shopee['TIME']        =   loc_shopee['DATETIME'].dt.time
                del loc_shopee['DATETIME']
                loc_shopee = loc_shopee[loc_shopee['NOM']!='']
                loc_shopee['NOM']         =   pd.to_numeric(loc_shopee['NOM']).astype(int)
                loc_shopee                =  loc_shopee.drop(loc_shopee[loc_shopee['Status'] == 'Cancelled'].index)
            
                loc_shopee['CODE']        =   ''
            
                loc_shopee['KAT']         =   'SHOPEEPAY'
                loc_shopee['SOURCE']      =   'INVOICE'
            
                # re-order columns
                loc_shopee                =   loc_shopee[['CAB', 'DATE', 'TIME', 'CODE', 'ID', 'NOM', 'KAT', 'SOURCE']]
            
                # Save the final result to a new CSV file
                loc_shopee.to_csv(outputshopee_path, index=False)
                st.write(f"File SHOPEE FOOD processed and saved")
            else:
                st.write("File does not exist. Please double check")

            shopee_path2       = f'{tmpdirname}/_merge/merge_Shopee Food 2.csv'
            outputshopee_path2 = f'{tmpdirname}/_final/Final Shopee Food 2.csv'
            st.write('SHOPEE FOOD 2')
            if os.path.exists(shopee_path2):
                #Read data merge Shopee Food
                df_shopee2 = pd.read_csv(f'{tmpdirname}/_merge/merge_Shopee Food 2.csv').fillna('')
                #Rename columns to match the database schema
                loc_shopee2   =   df_shopee2.loc[:,["Folder", "Order Complete Time", "Transaction ID (Order ID)", "Food Original Price", "Status"]].rename(columns={"Folder" : "CAB",
                                                                                                                                                    "Order Complete Time" : "DATETIME",
                                                                                                                                                    "Transaction ID (Order ID)" : "ID",
                                                                                                                                                    "Food Original Price" : "NOM"}).fillna("")
            
                loc_shopee2['DATETIME']    =   pd.to_datetime(loc_shopee2['DATETIME'], format='%d %m %Y %H:%M')
                loc_shopee2['DATE']        =   loc_shopee2['DATETIME'].dt.strftime('%d/%m/%Y')
                loc_shopee2['TIME']        =   loc_shopee2['DATETIME'].dt.time
                del loc_shopee2['DATETIME']
            
                loc_shopee2['NOM']         =   pd.to_numeric(loc_shopee2['NOM']).astype(int)
                loc_shopee2                =   loc_shopee2.drop(loc_shopee2[loc_shopee2['Status'] == 'Cancelled'].index)
            
                loc_shopee2['CODE']        =   ""
            
                loc_shopee2['KAT']         =   "SHOPEEPAY"
                loc_shopee2['SOURCE']      =   "INVOICE"
            
                loc_shopee2                =   loc_shopee2[loc_shopee2['Status'] == 'Completed']
            
                # re-order columns
                loc_shopee2                =   loc_shopee2[["CAB", "DATE", "TIME", "CODE", "ID", "NOM", "KAT", "SOURCE"]]
            
                # Save the final result to a new CSV file
                loc_shopee2.to_csv(outputshopee_path2, index=False)
                st.write(f"File SHOPEE FOOD 2 processed and saved")
            else:
                st.write("File does not exist. Please double check")
            
            outputgrab_path   = f'{tmpdirname}/_final/Final Grab.csv'
            grab1_path        = f'{tmpdirname}/_merge/merge_Grab 1.csv'
            grab2_path        = f'{tmpdirname}/_merge/merge_Grab 2.csv'
            
            # Check for the existence of grab files
            grab1_exists = os.path.exists(grab1_path)
            grab2_exists = os.path.exists(grab2_path)
    
            st.write('GRAB')
            # Process based on the existence of files
            if grab1_exists or grab2_exists:
                # Initialize an empty list to hold dataframes
                dfs = []
            
                # Read the existing files
                if grab1_exists:
                    df_grab1 = pd.read_csv(grab1_path).fillna('')
                    dfs.append(df_grab1)
                if grab2_exists:
                    df_grab2 = pd.read_csv(grab2_path).fillna('')
                    dfs.append(df_grab2)
            
                # Concatenate all dataframes in the list
                if dfs:
                    df_grab = pd.concat(dfs, ignore_index=True)
            
                    # Rename columns to match the database schema
                    loc_grab = df_grab.loc[:, ['CAB', 'Updated On', 'Category', 'Status', 'Short Order ID', 'Amount', 'Net Sales']].rename(
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
                    loc_grab['DATETIME'] = loc_grab['DATETIME'].apply(parse_datetime)
            
                    # Extract DATE and TIME from DATETIME, then delete the DATETIME column
                    loc_grab['DATE'] = loc_grab['DATETIME'].dt.strftime('%d/%m/%Y')
                    loc_grab['TIME'] = loc_grab['DATETIME'].dt.time
                    del loc_grab['DATETIME']
            
                    # Convert 'NOM' and 'Amount' columns to numeric, handling non-numeric issues
                    loc_grab['NOM1'] = pd.to_numeric(loc_grab['NOM1']).astype(float)
                    #loc_grab['Amount'] = pd.to_numeric(loc_grab['Amount'].astype('str').str.replace('.', ''), errors='coerce').astype(float)
            
                    # Drop rows where 'Category' is 'Canceled'
                    loc_grab = loc_grab[loc_grab['Category'] != 'Canceled']
            
                    # Define conditions and choices for 'NOM'
                    loc_grabcon = [
                        (loc_grab['Category'] == 'Adjustment'),
                        (loc_grab['Category'] == 'Payment'),
                    ]
                    pilih = [loc_grab['Amount'], loc_grab['NOM1']]
                    loc_grab['NOM'] = np.select(loc_grabcon, pilih, default='Cek')
            
                    # Define conditions and choices for 'ID'
                    loc_grabcon2 = [
                        (loc_grab['Category'] == 'Adjustment'),
                        (loc_grab['Category'] == 'Payment'),
                    ]
                    pilih2 = [loc_grab['ID'] + 'Adj', loc_grab['ID']]
                    loc_grab['ID'] = np.select(loc_grabcon2, pilih2, default='Cek')
            
                    # Additional processing
                    loc_grab['CODE'] = ''
                    loc_grab['KAT'] = 'GRAB FOOD'
                    loc_grab['SOURCE'] = 'INVOICE'
            
                    loc_grab = loc_grab[['CAB', 'DATE', 'TIME', 'CODE', 'ID', 'NOM', 'KAT', 'SOURCE']]
            
                    # Filter CAB
                    loc_grab = loc_grab[loc_grab['CAB'] != '']
            
                    # Save the final result to a new CSV file
                    loc_grab.to_csv(outputgrab_path, index=False)
                    st.write(f"File GRAB processed and saved")
            else:
                st.write("File does not exist. Please double check")
            
            
            qrisshopee_path       = f'{tmpdirname}/_merge/merge_QRIS Shopee.csv'
            outputqrishopee_path  = f'{tmpdirname}/_final/Final QRIS Shopee.csv'
            st.write('QRIS SHOPEE')
            if os.path.exists(qrisshopee_path):
                # Read data merge QRIS Shopee
                df_shopee = pd.read_csv(qrisshopee_path).fillna('')
            
                # Rename columns to match the database schema
                loc_qrisshopee = df_shopee.loc[:, ['Folder', 'Transaction ID', 'DATE', 'TIME', 'Transaction Amount', 'Transaction Type']].rename(
                    columns={'Folder': 'CAB', 'Transaction ID': 'ID', 'Transaction Amount': 'NOM'}).fillna('')
                loc_qrisshopee['DATE'] = loc_qrisshopee['DATE'].str.replace('Apr', 'April')          
                loc_qrisshopee['DATE'] = loc_qrisshopee['DATE'].str.replace('Jun', 'June')
            
                loc_qrisshopee['DATE'] = pd.to_datetime(loc_qrisshopee['DATE'], format='%d/%m/%Y')
                loc_qrisshopee['DATE'] = loc_qrisshopee['DATE'].dt.strftime('%d/%m/%Y')
                loc_qrisshopee['TIME'] = pd.to_datetime(loc_qrisshopee['TIME'], format='%H:%M:%S')
                loc_qrisshopee['TIME'] = loc_qrisshopee['TIME'].dt.time
            
                loc_qrisshopee['NOM'] = pd.to_numeric(loc_qrisshopee['NOM']).astype(float)
            
                loc_qrisshopee['CODE'] = ''
                loc_qrisshopee['KAT'] = 'QRIS SHOPEE'
                loc_qrisshopee['SOURCE'] = 'INVOICE'
            
                # Filter out 'Withdrawal' transactions
                loc_qrisshopee = loc_qrisshopee[loc_qrisshopee['Transaction Type'] != 'Withdrawal']
            
                # Re-order columns
                loc_qrisshopee = loc_qrisshopee[['CAB', 'DATE', 'TIME', 'CODE', 'ID', 'NOM', 'KAT', 'SOURCE']]
            
                # Save the final result to a new CSV file
                loc_qrisshopee.to_csv(outputqrishopee_path, index=False)
                st.write(f"File QRIS SHOPEE processed and saved")
            else:
                st.write("File does not exist. Please double check")
            
            qristelekom_path        = f'{tmpdirname}/_merge/merge_QRIS IA.csv'
            outputqristelekom_path  = f'{tmpdirname}/_final/Final QRIS Telkom.csv'
            st.write('QRIS TELKOM')
            if os.path.exists(qristelekom_path):
                # Read data merge QRIS Telkom
                df_qristelkom = pd.read_csv(qristelekom_path).fillna('')
            
                # Rename columns to match the database schema
                loc_qristelkom = df_qristelkom.loc[:, ['Folder', 'Waktu Transaksi', 'Nama Customer', 'Nominal (termasuk Tip)']].rename(
                    columns={'Folder': 'CAB', 'Waktu Transaksi': 'DATETIME', 'Nama Customer': 'ID', 'Nominal (termasuk Tip)': 'NOM'}).fillna('')
                loc_qristelkom['DATETIME'] = loc_qristelkom['DATETIME'].str.replace('Apr', 'April')            
                loc_qristelkom['DATETIME'] = loc_qristelkom['DATETIME'].str.replace('Jun', 'June')
            
                # Convert 'DATETIME' column to datetime
                loc_qristelkom['DATETIME'] = pd.to_datetime(loc_qristelkom['DATETIME'])
            
                # Extract date and time into new columns
                loc_qristelkom['DATE'] = loc_qristelkom['DATETIME'].dt.strftime('%d/%m/%Y')
                loc_qristelkom['TIME'] = loc_qristelkom['DATETIME'].dt.time
                del loc_qristelkom['DATETIME']
            
                loc_qristelkom['CODE'] = ''
                loc_qristelkom['KAT'] = 'QRIS TELKOM'
                loc_qristelkom['SOURCE'] = 'INVOICE'
            
                # Re-order columns
                loc_qristelkom = loc_qristelkom[['CAB', 'DATE', 'TIME', 'CODE', 'ID', 'NOM', 'KAT', 'SOURCE']]
            
                # Save the final result to a new CSV file
                loc_qristelkom.to_csv(outputqristelekom_path, index=False)
                st.write(f"File QRIS TELKOM processed and saved")
            else:
                st.write("File does not exist. Please double check")
            
            
            # Path to the CSV file
            file_path = f'{tmpdirname}/_merge/merge_ESB.csv'
            st.write('QRIS ESB')
            # Check if the file exists
            if os.path.exists(file_path):
                # Read the CSV file
                df_esb = pd.read_csv(file_path)
            
                # Add new columns with default values
                df_esb['SOURCE'] = 'INVOICE'
                df_esb['CODE'] = ''
                df_esb['KAT'] = 'QRIS ESB'
            
                # Convert 'Transaction Date' to datetime and extract date and time components
                #df_esb['DATE'] = df_esb['DATE'].str.replace('Jun', 'June')
                df_esb['Transaction Date'] = pd.to_datetime(df_esb['Transaction Date'], format='%Y-%m-%d %H:%M:%S')
                df_esb['DATE'] = df_esb['Transaction Date'].dt.strftime('%d/%m/%Y')
                df_esb['TIME'] = df_esb['Transaction Date'].dt.time
            
                # Filter rows where 'Payment Transaction Status' is 'settlement'
                df_esb = df_esb[df_esb['Payment Transaction Status'] == 'settlement']
                df_esb = df_esb[(df_esb['Source'].str.contains('Dine In')) | (df_esb['Source'].str.contains('Take Away'))]
            
                # Extract text after the dot in the 'CAB' column
                df_esb['CAB'] = df_esb['Branch Name'].str.split('.').str[1]
            
                # Rename columns to match the database schema
                df_esb = df_esb.rename(columns={'POS Sales Number': 'ID', 'Amount': 'NOM'}).fillna('')
            
                # Select and sort the relevant columns
                df_esb = df_esb.loc[:, ['CAB', 'DATE', 'TIME', 'CODE', 'ID', 'NOM', 'KAT', 'SOURCE']].sort_values('DATE', ascending=False)
            
                # Save the final result to a new CSV file
                df_esb.to_csv(f'{tmpdirname}/_final/Final ESB.csv', index=False)
                st.write("File QRIS ESB processed and saved")
            else:
                # st.write a message if the file is not found
                st.write("File does not exist. Please double check")
    
            #Read data merge WEB
            df_web       =   pd.read_csv(f'{tmpdirname}/_merge/merge_WEB.csv')
            df_web['DATE'] = df_web['DATE'].str.replace('Apr', 'April')            
            df_web['DATE'] = df_web['DATE'].str.replace('Jun', 'June')
            
            df_web['SOURCE']     =   'WEB'
            
            #Rename columns to match the database schema
            df_web       =       df_web.rename(columns={'CO':'TIME','TOTAL':'NOM','KATEGORI':'KAT','CUSTOMER':'ID'}).fillna('')
            df_web       =       df_web.loc[:,['CAB','DATE','TIME','CODE','ID','NOM','KAT','SOURCE']].sort_values('DATE', ascending=[False])
            
            final_web       =       df_web.to_csv(f'{tmpdirname}/_final/WEB Akhir.csv', index=False)
            web_final       =       pd.read_csv(f'{tmpdirname}/_final/WEB Akhir.csv')
            
            web_final       =       web_final[web_final['TIME']     !=      'TOTAL']
            web_final       =       web_final[web_final['TIME']     !=      'CO']
    
    
            def convert_time(x):
                try:
                    return pd.to_datetime(x).strftime('%H:%M:%S')
                except ValueError:
                    try:
                        return pd.to_datetime(x, format='%H:%M:%S').strftime('%H:%M:%S')
                    except ValueError as e:
                        return pd.NaT
                        
            web_final['TIME'] = web_final['TIME'].apply(convert_time)
            web_final         =   web_final[web_final['DATE'].isin(all_date)]
            web_final['DATE'] = pd.to_datetime(web_final['DATE'])
            web_final['DATE'] = web_final['DATE'].dt.strftime('%d/%m/%Y')
            web_final = web_final[web_final['CAB'].isin(all_cab)]
            web_final['KAT'] = web_final['KAT'].replace({'SHOPEE PAY': 'SHOPEEPAY', 'GORESTO': 'GO RESTO', 'GRAB': 'GRAB FOOD', 'QRIS ESB ORDER':'QRIS ESB'})
            web_final.to_csv(f'{tmpdirname}/_final/ALL/WEB.csv', index=False)

            invoice_final = pd.concat([pd.read_csv(f, dtype=str) for f in glob(f'{tmpdirname}/_final/Final*')], ignore_index = True).fillna('')
            invoice_final = invoice_final[['CAB', 'DATE', 'TIME', 'CODE', 'ID', 'NOM', 'KAT', 'SOURCE']]
            invoice_final = invoice_final[(invoice_final['CAB'].isin(all_cab))]
            invoice_final = invoice_final[invoice_final['DATE']     !=      '']
            invoice_final['DATE'] = pd.to_datetime(invoice_final['DATE'], format='%d/%m/%Y')
            invoice_final   =   invoice_final[invoice_final['DATE'].isin(all_date)] #CHANGE
            invoice_final['DATE'] = invoice_final['DATE'].dt.strftime('%d/%m/%Y')
            invoice_final.to_csv(f'{tmpdirname}/_final/ALL/INVOICE.csv', index=False) #CHANGE

            st.markdown('### Processing')
            all_kat = ['GOJEK', 'QRIS SHOPEE', 'GRAB','SHOPEEPAY', 'QRIS ESB','QRIS TELKOM']
            ket = ''
            time_go = 150
            time_qs = 5
            time_gf = 150
            time_sp = 150
            time_qe = 150
            time_qt = 150
            
            dfinv   =   pd.read_csv(f'{tmpdirname}/_final/ALL/INVOICE.csv')
            dfweb   =   pd.read_csv(f'{tmpdirname}/_final/ALL/WEB.csv')
            
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
            dfinv['TIME'] = pd.to_datetime(dfinv['DATE'].dt.strftime('%Y-%m-%d') + ' ' + dfinv['TIME'] )
            
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
                if wib in ['MKSAHM', 'BPPHAR', 'MKSPER', 'MKSTUN', 'MKSPOR', 'MKSPET', 'MKSRAT']:
                    dfinv.loc[dfinv[dfinv['CAB']==wib].index, 'TIME'] = dfinv.loc[dfinv[dfinv['CAB']==wib].index, 'TIME'] + dt.timedelta(hours=1,minutes=1)
                    
            def difference(value1, value2):
                diff = value1 - value2
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

                    if 'GOJEK' in all_kat:
                        goi   =   dfinv[dfinv['KAT']  ==  "GO RESTO"]
                        gow   =   dfweb[dfweb['KAT']  ==  "GO RESTO"]
                        goi   =   goi[goi['CAB']  ==  cab]
                        gow   =   gow[gow['CAB']  ==  cab]
                        goi = goi[goi['DATE']==date]
                        gow = gow[gow['DATE']==date]
            
                        goi = goi.sort_values(by=['CAB', 'NOM', 'TIME'], ascending=[True, True, False]).reset_index(drop=True)
                        gow = gow.sort_values(by=['CAB', 'NOM', 'TIME'], ascending=[True, True, False]).reset_index(drop=True)
            
                        goi.drop_duplicates(inplace=True)
                        for i in cn[(cn['TANGGAL']==str(int(re.findall(r'\d+', date)[-1]))) & (cn['CAB']==cab) & (cn['TYPE BAYAR']=='GO RESTO')].index:
                                x = gow[(gow['DATE']==date) & (gow['NOM']==cn.loc[i,'TOTAL BILL'])].index
                                if len(x)>=1:
                                    gow.loc[gow.loc[x,'ID'].apply(lambda x: fuzz.ratio(re.sub(r'\d+', '', str(x).upper()), re.sub(r'\d+', '', str(cn.loc[i,'NAMA TAMU']).upper()))).sort_values().index[-1],'KET'] = 'Cancel Nota'
                                    cn.loc[i, 'KET'] = 'Done'
                        goi['KET'] = goi['ID']
            
                        def compare_time(df_i, df_w, time):
                            for i in range(0,df_w.shape[0]):
                                if df_w.loc[i,'KET']=='' :
                                    list_ind = df_i[((df_i['NOM'] - df_w.loc[i,'NOM'])<=200) & ((df_i['NOM']-df_w.loc[i,'NOM'])>=0) & (df_i['HELP']=='')].index
                                    for x in list(list_ind):
                                        if ((df_i.loc[x,'TIME']) - df_w.loc[i,'TIME']  >= dt.timedelta(minutes=0)):
                                            if ((df_i.loc[x,'TIME']) - df_w.loc[i,'TIME'] < dt.timedelta(minutes=time)):
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
                                            if ((df_w.loc[i,'TIME']) - df_i.loc[x,'TIME'] < dt.timedelta(minutes=3)):
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
                        
                                                    if all_1.loc[y,'NOM'] == all_1.loc[x,'NOM']:
                                                        if all_2.loc[i,'SOURCE'] =='WEB':
                                                            all_1.loc[y,'KET'] = 'Balance '+ all_1.loc[x,'ID']
                                                            all_1.loc[x,'KET'] = 'Balance '+ all_1.loc[x,'ID']
                                                        if all_2.loc[i,'SOURCE'] =='INVOICE':
                                                            all_1.loc[y,'KET'] = 'Balance '+ all_1.loc[y,'ID']
                                                            all_1.loc[x,'KET'] = 'Balance '+ all_1.loc[y,'ID']                                            
                                                    if all_1.loc[y,'NOM'] != all_1.loc[x,'NOM']:
                                                        if all_2.loc[i,'SOURCE'] =='WEB':
                                                            all_1.loc[y,'KET'] =  'Selisih '+ str(all_1.loc[x,'ID']) + difference(all_1.loc[x,'NOM'],all_1.loc[y,'NOM'])
                                                            all_1.loc[x,'KET'] =  'Selisih '+ str(all_1.loc[x,'ID']) + difference(all_1.loc[x,'NOM'],all_1.loc[y,'NOM'])
                                                        else:
                                                            all_1.loc[y,'KET'] =  'Selisih '+ str(all_1.loc[y,'ID']) + difference(all_1.loc[y,'NOM'],all_1.loc[x,'NOM'])
                                                            all_1.loc[x,'KET'] =  'Selisih '+ str(all_1.loc[y,'ID']) + difference(all_1.loc[y,'NOM'],all_1.loc[x,'NOM'])
              
                            if step == 0:
                                break
                        print(step)
            
                        for i in all_2[all_2['SOURCE']=='WEB'].index:
                                            list_ind = all_2[(all_2['SOURCE']=='INVOICE') & (abs(all_2['NOM'] - all_2.loc[i,'NOM'])<=200) & (all_2['HELP']!='')
                                                        & (((((all_2['TIME']-all_2.loc[i,'TIME'])) < dt.timedelta(minutes=150)) & ((all_2['TIME']-all_2.loc[i,'TIME'])>=dt.timedelta(minutes=0)))
                                                           | ((((all_2.loc[i,'TIME']-all_2['TIME'])) < dt.timedelta(minutes=15)) & (((all_2.loc[i,'TIME']-all_2['TIME'])) >= dt.timedelta(minutes=0)) ))].index
                        
                                            if len(list_ind)>0:
                                                x = (abs(all_2.loc[i,'TIME'] - all_2.loc[list_ind, 'TIME'])).sort_values().index[0]
                                                if ((all_2.loc[x,'NOM']-all_2.loc[i,'NOM'])==0):
                                                                        all_2.loc[i,'KET'] = 'Balance '+ all_2.loc[x,'ID']
                                                                        all_2.loc[x,'KET'] = 'Balance '+ all_2.loc[x,'ID']
                                                                        all_2.loc[x,'HELP'] = ''
                                                                        
                                                else:
                                                                        all_2.loc[i,'KET'] = 'Selisih '+ str(all_2.loc[x,'ID']) + difference(all_2.loc[x,'NOM'],all_2.loc[i,'NOM'])
                                                                        all_2.loc[x,'KET'] = 'Selisih '+ str(all_2.loc[x,'ID']) + difference(all_2.loc[x,'NOM'],all_2.loc[i,'NOM'])
                                                                        all_2.loc[x,'HELP'] = '' 
                            
                        all = pd.concat([all[all['KET'].isin(['Cancel Nota'])],all_1,all_2]).sort_values(['CAB','DATE','KET', 'SOURCE','NOM'],ascending=[True,True,True,False,True])
                        if ket == 'selisih':
                            all = all[~(all['KET'].str.contains('Balance'))]
                        all['HELP'] = all['KET'].apply(lambda x: label_1(x))
                        all['KET'] = all['KET'].apply(lambda x:x if (('Selisih' in x) | ('Balance' in x)) else '')
                        #all['DATE'] = all['DATE'].dt.strftime('%d/%m/%Y')
                        #all['TIME'] = all['TIME'].dt.strftime('%H:%M:%S')
                        all.to_csv(f'{tmpdirname}/_final/GOJEK/{cab}/GOJEK_{cab}_{date}.csv', index=False)
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
                                                    df_w.loc[i,'KET'] = 'Balance '+ df_i.loc[x,'ID']
                                                    df_i.loc[x,'KET'] = 'Balance '+ df_i.loc[x,'ID']
                                                    df_i.loc[x,'HELP'] = df_w.loc[i,'CODE']
                                                    break                           
                                        if ((df_i.loc[x,'TIME']) - df_w.loc[i,'TIME']  < dt.timedelta(minutes=0)):
                                            if ((df_w.loc[i,'TIME']) - df_i.loc[x,'TIME'] < dt.timedelta(minutes=time)):
                                                if ((df_i.loc[x,'NOM']-df_w.loc[i,'NOM']))==0:
                                                    df_w.loc[i,'KET'] = 'Balance '+ df_i.loc[x,'ID']
                                                    df_i.loc[x,'KET'] = 'Balance '+ df_i.loc[x,'ID']
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
                                                        df_w.loc[i,'KET'] = df_i.loc[id[x],'ID'] + '& ' + df_i.loc[id[y],'ID']
                                                        df_i.loc[id[x],'KET'] = df_i.loc[id[x],'ID'] + '& ' + df_i.loc[id[y],'ID']
                                                        df_i.loc[id[y],'KET'] = df_i.loc[id[x],'ID'] + '& ' + df_i.loc[id[y],'ID']
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
                        all.to_csv(f'{tmpdirname}/_final/QRIS SHOPEE/{cab}/QRIS SHOPEE_{cab}_{date}.csv', index=False)
                        st.write('QRIS SHOPEE', ': File processed')
                        
                    if 'GRAB' in all_kat:
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
                            x = gfw[(gfw['ID2']==re.findall(r'\d+', cn.loc[i,'NAMA TAMU'])[-1]) & (gfw['NOM']==cn.loc[i,'TOTAL BILL'])].index
                            if len(x) >= 1:
                                gfw.loc[x[0], 'KET']='Cancel Nota'
                                cn.loc[i, 'KET'] = 'Done'
            
                        gfi['KET'] = gfi['ID']
                        def compare_time(df_i, df_w, time):
                            for i in range(0,df_w.shape[0]):
                                if df_w.loc[i,'KET']=='':
                                    list_ind = df_i[(abs(df_w.loc[i,'NOM']-df_i['NOM'])<=50) 
                                                & (df_i['ID2']==df_w.loc[i,'ID2'])
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
                                                        df_w.loc[i,'KET'] = 'Promo Marketing/Adjustment'
                                                        df_i.loc[x,'KET'] = 'Promo Marketing/Adjustment'
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
                                                        df_w.loc[i,'KET'] = 'Promo Marketing/Adjustment'
                                                        df_i.loc[x,'KET'] = 'Promo Marketing/Adjustment'
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
                                    df_i.loc[i,'KET'] = 'Tidak Ada Transaksi di Web'                       
            
                        compare_time(gfi, gfw, time_gf)
            
                        all = pd.concat([gfw,gfi]).sort_values(['CAB','DATE','KET', 'ID2','SOURCE','NOM'],ascending=[True,True, True,True,False,True])
                        if ket == 'selisih':
                            all = all[~(all['KET'].str.contains('Balance'))]
                        all['HELP'] = all['KET'].apply(lambda x: label_1(x))
                        all['KET'] = all['KET'].apply(lambda x:x if (('Selisih' in x) | ('Balance' in x)) else '')
                        #all['DATE'] = all['DATE'].dt.strftime('%d/%m/%Y')
                        #all['TIME'] = all['TIME'].dt.strftime('%H:%M:%S')
                        all.to_csv(f'{tmpdirname}/_final/GRAB/{cab}/GRAB_{cab}_{date}.csv', index=False)
                        st.write('GRAB FOOD', ': File processed')
                        
                    if 'SHOPEEPAY' in all_kat:
                        spi   =   dfinv[dfinv['KAT']  ==  "SHOPEEPAY"]
                        spw   =   dfweb[dfweb['KAT']  ==  "SHOPEEPAY"]
                        spi   =   spi[spi['CAB']  ==  cab]
                        spw   =   spw[spw['CAB']  ==  cab]
                        spi = spi[spi['DATE']==date]
                        spw = spw[spw['DATE']==date]
            
                        spi = spi.sort_values(by=['CAB', 'NOM', 'ID', 'TIME'], ascending=[True, True, True, True]).reset_index(drop=True)
                        spw = spw.sort_values(by=['CAB', 'NOM', 'ID', 'TIME'], ascending=[True, True, True, True]).reset_index(drop=True)
            
            
                        spi.drop_duplicates(inplace=True)
                        spw['ID'] = spw['ID'].str.upper()
                        spw.loc[spw[spw['ID'].isna()].index,'ID'] = ''
                        spw['ID2'] = spw['ID'].apply(lambda x: '#'+str(int(re.search(r'\d+$', x[:re.search(r'\d(?!.*\d)', x).end()] if re.search(r'\d(?!.*\d)', x) else x).group())) if re.search(r'\d+$',  x[:re.search(r'\d(?!.*\d)', x).end()] if re.search(r'\d(?!.*\d)', x) else x) else x)
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
                                                        if ((df_i.loc[x,'NOM']-df_w.loc[i,'NOM'])==0):
                                                            df_w.loc[i,'KET'] = 'Balance '+ str(df_i.loc[x,'ID'])
                                                            df_i.loc[x,'KET'] = 'Balance '+ str(df_i.loc[x,'ID'])
                                                            df_i.loc[x,'HELP'] = str(df_w.loc[i,'CODE'])
                                                            break
                                                        else:
                                                            df_w.loc[i,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],df_w.loc[i,'NOM'])
                                                            df_i.loc[x,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],df_w.loc[i,'NOM'])
                                                            df_i.loc[x,'HELP'] = str(df_w.loc[i,'CODE'])
                                                            break                              
                                                if ((df_i.loc[x,'TIME']) - df_w.loc[i,'TIME']  < dt.timedelta(minutes=0)):
                                                    if ((df_w.loc[i,'TIME']) - df_i.loc[x,'TIME'] < dt.timedelta(minutes=150)):
                                                        if ((df_i.loc[x,'NOM']-df_w.loc[i,'NOM']))==0:
                                                            df_w.loc[i,'KET'] = 'Balance '+ str(df_i.loc[x,'ID'])
                                                            df_i.loc[x,'KET'] = 'Balance '+ str(df_i.loc[x,'ID'])
                                                            df_i.loc[x,'HELP'] = str(df_w.loc[i,'CODE'])
                                                            break
                                                        else:
                                                            df_w.loc[i,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],df_w.loc[i,'NOM'])
                                                            df_i.loc[x,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],df_w.loc[i,'NOM'])
                                                            df_i.loc[x,'HELP'] = str(df_w.loc[i,'CODE'])
                                                            break 
            
                            for i in df_w[df_w['KET']==''].index :
                                    list_ind_i = df_i[(df_i['HELP']=='') & ((df_i['NOM']-df_w.loc[i,'NOM'])==0) 
                                                      & (df_i['ID2']==df_w.loc[i,'ID2'])].index
                                    for x in list_ind_i:
                                        if ((df_i.loc[x,'TIME'] - df_w.loc[i,'TIME']) < dt.timedelta(minutes=120)) & ((df_i.loc[x,'TIME'] - df_w.loc[i,'TIME']) > dt.timedelta(seconds=0)):
                                            if ((df_i.loc[x,'NOM']-df_w.loc[i,'NOM'])==0):
                                                df_w.loc[i,'KET'] = 'Balance '+ str(df_i.loc[x,'ID'])
                                                df_i.loc[x,'KET'] = 'Balance '+ str(df_i.loc[x,'ID'])
                                                df_i.loc[x,'HELP'] = str(df_w.loc[i,'CODE'])
                                                break
                                            else:
                                                df_w.loc[i,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],df_w.loc[i,'NOM'])
                                                df_i.loc[x,'KET'] = 'Selisih '+ str(df_i.loc[x,'ID']) + difference(df_i.loc[x,'NOM'],df_w.loc[i,'NOM'])
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
                        all.to_csv(f'{tmpdirname}/_final/SHOPEEPAY/{cab}/SHOPEEPAY_{cab}_{date}.csv', index=False)
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
                        all.to_csv(f'{tmpdirname}/_final/QRIS ESB/{cab}/QRIS ESB_{cab}_{date}.csv', index=False)
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
                                    x = qtw[(qtw['ID']==re.findall(r'\d+', cn.loc[i,'NAMA TAMU'])[-1]) 
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
                                                    df_w.loc[x,'HELP'] = df_i.loc[i,'CODE']
                                                    break                          
                                        if ((df_w.loc[x,'TIME']) - df_i.loc[i,'TIME']  < dt.timedelta(minutes=0)):
                                            if ((df_i.loc[i,'TIME']) - df_w.loc[x,'TIME'] < dt.timedelta(minutes=time)):
                                                if ((df_w.loc[x,'NOM']-df_i.loc[i,'NOM']))==0:
                                                    df_i.loc[i,'KET'] = 'Balance '+ str(df_w.loc[x,'CODE'])
                                                    df_w.loc[x,'KET'] = 'Balance '+ str(df_w.loc[x,'CODE'])
                                                    df_w.loc[x,'HELP'] = df_i.loc[i,'CODE']
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
                        all.to_csv(f'{tmpdirname}/_final/QRIS TELKOM/{cab}/QRIS TELKOM_{cab}_{date}.csv', index=False)
                        st.write('QRIS TELKOM', ': File processed')
                             
            combined_dataframes = []
            files = []
            for cab in all_cab:
                 for date in all_date:
                    for ojol in all_kat:
                        if os.path.exists(f'{tmpdirname}/_final/{ojol}/{cab}/{ojol}_{cab}_{date}.csv'):
                            file = pd.read_csv(f'{tmpdirname}/_final/{ojol}/{cab}/{ojol}_{cab}_{date}.csv')
                            if not file.empty:
                                if file['CAB'].unique()[0] in ['MKSAHM', 'BPPHAR', 'MKSPER', 'MKSTUN', 'MKSPOR', 'MKSPET', 'MKSRAT']:
                                    file.loc[file[file['SOURCE']=='INVOICE'].index,'TIME'] = pd.to_datetime(file.loc[file[file['SOURCE']=='INVOICE'].index,'TIME']) - dt.timedelta (hours=1, minutes=1)
                                file['TIME'] = pd.to_datetime(file['TIME']).dt.strftime('%H:%M:%S')
                                files.append(file)
            
                    # Concatenate CSV files within each subfolder
            df_all = pd.concat(files)
            df_concat = []
            for cab in all_cab:
                for kat in ['GO RESTO', 'QRIS SHOPEE', 'GRAB FOOD','SHOPEEPAY', 'QRIS ESB','QRIS TELKOM']:
                    if not df_all[(df_all['CAB'] == cab) & (df_all['KAT']==kat)].empty:
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
                                        & ( abs(pd.to_datetime(str(pd.to_datetime(df_all3.loc[i,'DATE']).strftime('%Y-%m-%d')) + ' ' +df_all3.loc[i,'TIME']) - pd.to_datetime((pd.to_datetime(df_all3['DATE']).dt.strftime('%Y-%m-%d')) + ' ' + df_all3['TIME'])) <= dt.timedelta(minutes=150))].index
                                if kat in ['GO RESTO', 'QRIS SHOPEE', 'QRIS TELKOM']:
                                    x = df_all3[(df_all3['DATE']==(pd.to_datetime(df_all3.loc[i,'DATE'])+ dt.timedelta(days=1)).strftime('%Y-%m-%d')) 
                                        & (abs(df_all3.loc[i,'NOM'] - df_all3['NOM']) <=200)
                                        & (df_all3['SOURCE']=='INVOICE') & (df_all3['HELP']=='')
                                        & ( abs(pd.to_datetime(str(pd.to_datetime(df_all3.loc[i,'DATE']).strftime('%Y-%m-%d')) + ' ' +df_all3.loc[i,'TIME']) - pd.to_datetime((pd.to_datetime(df_all3['DATE']).dt.strftime('%Y-%m-%d')) + ' ' + df_all3['TIME'])) <= dt.timedelta(minutes=150))].index                                                        
                                if kat in ['QRIS ESB']:
                                    x = df_all3[(df_all3['DATE']==(pd.to_datetime(df_all3.loc[i,'DATE'])+ dt.timedelta(days=1)).strftime('%Y-%m-%d')) 
                                        & (df_all3['ID'] == df_all3.loc[i,'CODE'])
                                        & (abs(df_all3.loc[i,'NOM'] - df_all3['NOM']) <=200)
                                        & (df_all3['SOURCE']=='INVOICE') & (df_all3['HELP']=='')
                                        & ( abs(pd.to_datetime(str(pd.to_datetime(df_all3.loc[i,'DATE']).strftime('%Y-%m-%d')) + ' ' +df_all3.loc[i,'TIME']) - pd.to_datetime((pd.to_datetime(df_all3['DATE']).dt.strftime('%Y-%m-%d')) + ' ' + df_all3['TIME'])) <= dt.timedelta(minutes=150))].index                                                        
                                if len(x)>=1:
                                    x = abs(pd.to_datetime(str(pd.to_datetime(df_all3.loc[i,'DATE']).strftime('%Y-%m-%d')) + ' ' +df_all3.loc[i,'TIME']) - pd.to_datetime((pd.to_datetime(df_all3.loc[x,'DATE']).dt.strftime('%Y-%m-%d')) + ' ' + df_all3.loc[x,'TIME'])).sort_values().index[-1]
                                    if kat in ['GRAB FOOD']:
                                        df_all3.loc[i, 'HELP'] = 'Invoice Beda Hari'
                                        df_all3.loc[x, 'HELP'] = 'Transaksi Kemarin'       
                                    else:
                                        if df_all3.loc[i,'NOM']==df_all3.loc[x,'NOM']:
                                            df_all3.loc[i, 'HELP'] = 'Invoice Beda Hari'
                                            df_all3.loc[x, 'HELP'] = 'Transaksi Kemarin'
                                        else:
                                            df_all3.loc[i, 'HELP'] = 'Selisih IT'
                                            df_all3.loc[i, 'KET'] = 'Invoice Beda Hari Selisih '+ str(df_all3.loc[x,'ID']) + difference(df_all3.loc[x,'NOM'],df_all3.loc[i,'NOM'])
                                            df_all3.loc[x, 'HELP'] = 'Selisih IT' 
                                            df_all3.loc[x, 'KET'] = 'Transaksi Kemarin Selisih '+ str(df_all3.loc[x,'ID']) + difference(df_all3.loc[x,'NOM'],df_all3.loc[i,'NOM'])   
                            if (df_all3.loc[i, 'HELP'] == '') & (df_all3.loc[i, 'SOURCE']=='WEB'):
                                df_all3.loc[i, 'HELP'] = f"Tidak Ada Invoice {'Ojol' if kat in ['GO RESTO','GRAB FOOD','SHOPEEPAY'] else 'QRIS'}" 
                            if (df_all3.loc[i, 'HELP'] == '') & (df_all3.loc[i, 'SOURCE']=='INVOICE'):
                                df_all3.loc[i, 'HELP'] = 'Tidak Ada Transaksi di Web'
                        all = pd.concat([df_all2.loc[df_all2[~((df_all2['KET'].isna()) & (df_all2['HELP'].str.contains('|'.join(['Transaksi Kemarin','Tidak Ada','Invoice Beda Hari']))))].index,],df_all3]).sort_values(['CAB','DATE'])
                        all['DATE'] = pd.to_datetime(all['DATE']).dt.strftime('%d/%m/%Y')
                        df_concat.append(all)
                        #pd.to_datetime(str(df_all3.loc[i,'DATE'].strftime('%Y-%m-%d')) + ' ' + str(df_all3.loc[i,'TIME']))
            
            #combined_dataframes.append(df_all)
            final_df = pd.concat(df_concat)
            time_now = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            st.markdown('### Output')
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                zip_file.writestr(f'MERGE_{time_now}.csv', pd.concat([invoice_final,web_final]).sort_values(['CAB','DATE','TIME']).to_csv(index=False))
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
            


                    

    
