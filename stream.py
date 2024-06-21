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

selected_options = st.multiselect('Pilih Cabang', list_cab)
# Tampilkan widget untuk memilih rentang tanggal
start_date = st.date_input("Pilih Tanggal Awal")
end_date = st.date_input("Pilih Tanggal Akhir")

# Jika tombol ditekan untuk memproses rentang tanggal
if (start_date is not None) & (end_date is not None):
    date_range = []
    current_date = start_date
    while current_date <= end_date:
        date_range.append(current_date.strftime('%Y-%m-%d'))
        current_date += dt.timedelta(days=1)

st.markdown('### Upload file *Zip')
uploaded_file = st.file_uploader("Pilih file ZIP", type="zip")

if uploaded_file is not None:
    st.write('File berhasil diupload')
    # Baca konten zip file
    zip_contents = uploaded_file.read()

    # Simpan zip file sementara
    with open("temp.zip", "wb") as f:
        f.write(zip_contents)

    # Ekstrak zip file
    with zipfile.ZipFile("temp.zip", "r") as zip_ref:
        zip_ref.extractall("1. ABO")

    # Hapus file zip sementara
    os.remove("temp.zip")

    if st.button('Process'):
        st.markdown('### Cleaning')
        st.write('GOJEK 1')
        main_folder = '1. ABO/_bahan/GOJEK 1'
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
                st.write(f"No CSV files found in subfolder: {subfolder}")
    
        if combined_dataframes:
            final_df = pd.concat(combined_dataframes)
            final_df.to_csv('1. ABO/_merge/merge_Gojek 1.csv', index=False)
            st.write("Concatenated GOJEK 1 Exported to:", '_merge/merge_Gojek 1.csv')
        else:
            st.write("No dataframes to concatenate.")  

        st.write('GOJEK 2')
        main_folder = '1. ABO/_bahan/GOJEK 2'
        
        # Get the list of subfolders within the main folder
        subfolders = [folder for folder in os.listdir(main_folder) if os.path.isdir(os.path.join(main_folder, folder))]
        
        # List to store concatenated dataframes
        combined_dataframes = []
        
        # Iterate over each subfolder
        for subfolder in subfolders:
            # Glob pattern to get all CSV files in the subfolder
            files = glob(os.path.join(main_folder, subfolder, '*.csv'))
            # Concatenate CSV files within each subfolder
            dfs = [pd.read_csv(file) for file in files]
            if dfs:
                df = pd.concat(dfs)
                # Add a new column for the folder name
                df['Folder'] = subfolder
                combined_dataframes.append(df)
            else:
                st.write(f"No CSV files found in subfolder: {subfolder}")
        
        # Check if there are any dataframes to concatenate
        if combined_dataframes:
            # Concatenate dataframes from all subfolders
            final_df_ = pd.concat(combined_dataframes)
            final_df.to_csv('1. ABO/_merge/merge_Gojek 2.csv', index=False)
            st.write("Concatenated GOJEK 2 Exported to:", '_merge/merge_Gojek 2.csv')
        else:
            st.write("No dataframes to concatenate.")    

        st.write('GOJEK 3')
        folder_path = '1. ABO/_bahan/GOJEK 3/'
        
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
            storename = pd.read_csv('1. ABO/_bahan/bahan/Store Name GOJEK.csv')
            concatenated_df = pd.merge(concatenated_df, storename, how='left', on='Outlet name').fillna('')
            concatenated_df.to_csv('1. ABO/_merge/merge_Gojek 3.csv', index=False)
            st.write("Concatenated GOJEK 3 Exported to:", output_path)
        else:
            st.write("There are no files to concatenate.")

        st.write('SHOPEE FOOD')
        main_folder = '1. ABO/_bahan/SHOPEE FOOD'
        
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
                    st.write(f"No CSV files found in subfolder: {subfolder}")
        
        # Check if there are any dataframes to concatenate
        if combined_dataframes:
            # Concatenate dataframes from all subfolders
            final_df = pd.concat(combined_dataframes, ignore_index=True)
            final_df.to_csv('1. ABO/_merge/merge_Shopee Food.csv', index=False)
            st.write("Concatenated SHOPEE FOOD Exported to:", '_merge/merge_Shopee Food.csv')
        else:
            st.write("No dataframes to concatenate.")

        
        st.write('GRAB *csv')
        # Set the directory containing the files
        folder_path = '1. ABO/_bahan/GRAB/csv'
        
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
            storename = pd.read_csv('1. ABO/_bahan/bahan/Store Name GRAB.csv')
            concatenated_df = pd.merge(concatenated_df, storename, how='left', on='Store Name').fillna('')
        
            # Export the concatenated dataframe to CSV in the specified path
            output_path = '1. ABO/_merge/merge_Grab 1.csv'
            concatenated_df.to_csv(output_path, index=False)
        
            st.write("Concatenated GRAB Exported to:", output_path)
        else:
            st.write("There are no files to concatenate.")
        
        st.write('GRAB *xls')
        # Specify the directory where the files are located
        folder_path = '1. ABO/_bahan/GRAB/xls'
        
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
            storename = pd.read_csv('1. ABO/_bahan/bahan/Store Name GRAB.csv')
            merged_df = pd.merge(merged_df, storename, how='left', on='Store Name').fillna('')
        
            # Save the merged DataFrame to a CSV file without row index
            output_file = '1. ABO/_merge/merge_Grab 2.csv'
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            merged_df.to_csv(output_file, index=False)
        
            st.write("Concatenated DataFrame Exported to:", output_file)
        else:
            st.write("There are no files to process.")
        
        
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
        main_folder = '1. ABO/_bahan/QRIS_SHOPEE/QRIS A (Separator ,)/'
        
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
                st.write(f"No CSV files found in subfolder: {subfolder}")
        
        # Check if there are any dataframes to concatenate
        if combined_dataframes:
            # Concatenate dataframes from all subfolders
            final_df = pd.concat(combined_dataframes)
        
            # Format Time
            final_df['Update Time'] = pd.to_datetime(final_df['Update Time'], format='%Y-%m-%d %H:%M:%S')
            final_df['DATE'] = final_df['Update Time'].dt.strftime('%d/%m/%Y')
            final_df['TIME'] = final_df['Update Time'].dt.time
        
            # Save the final dataframe to a CSV file
            output_path = '1. ABO/_bahan/QRIS_SHOPEE/merge/merge_QRIS S_A.csv'
            final_df.to_csv(output_path, index=False)
        
            st.write("Concatenated QRIS S_A Exported to:", output_path)
        else:
            st.write("There are no files to concatenate.")
        
        
        st.write('QRIS SHOPEE *;')
        # Define the base folder path
        base_folder_path = '1. ABO/_bahan/QRIS_SHOPEE/QRIS B (Separator ;)'
        
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
                    st.write(f"Removed separator from {file_path}")
                    # Set the flag indicating CSV files were processed
                    csv_processed = True
        
            # st.write a message if no CSV files are found in a subfolder
            if not filenames:
                st.write(f"No CSV files found in subfolder: {dirpath}")
        
        # Check if any CSV files were processed
        if csv_processed:
            st.write("All CSV files processed.")
        else:
            st.write("No CSV files found for processing.")
        
        base_folder_path = '1. ABO/_bahan/QRIS_SHOPEE/QRIS B (Separator ;)'
        
        # Function to recursively find all CSV files in a directory and its subdirectories
        def find_csv_files(directory):
            csv_files = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.csv'):
                        csv_files.append(os.path.relpath(os.path.join(root, file), directory))
            return csv_files
        
        # Function to read CSV files with ';' delimiter
        def read_csv_files(files, directory):
            dfs = []
            for file in files:
                try:
                    file_path = os.path.join(directory, file)
                    folder = os.path.basename(os.path.dirname(file_path))
                    df = pd.read_csv(file_path, delimiter=';')
                    df['Folder'] = folder
                    dfs.append(df)
                except Exception as e:
                    st.write(f"Error reading {file}: {e}")
            return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
        
        # Find all CSV files in the base folder and its subfolders
        csv_files = find_csv_files(base_folder_path)
        
        # Read all CSV files into a single DataFrame and add "Folder" column
        if csv_files:
            df = read_csv_files(csv_files, base_folder_path)
        else:
            st.write("No CSV files found.")
            df = pd.DataFrame()
        
        # Only proceed if the DataFrame is not empty
        if not df.empty:
            # Format Time
            try:
                df['Update Time'] = pd.to_datetime(df['Update Time'], format='%d/%m/%Y %H:%M')
                df['DATE'] = df['Update Time'].dt.strftime('%d/%m/%Y')
                df['TIME'] = df['Update Time'].dt.time
            except KeyError:
                st.write("The column 'Update Time' does not exist in the data.")
            except Exception as e:
                st.write(f"Error formatting time: {e}")
        
            # Export DataFrame to CSV
            output_file_path = '1. ABO/_bahan/QRIS_SHOPEE/merge/merge_QRIS S_B.csv'
            df.to_csv(output_file_path, index=False)
            st.write(f"DataFrame exported to {output_file_path}")
        else:
            st.write("No data to export. DataFrame is empty.")
        
        st.write('QRIS SHOPEE')
        # Define the folder path
        folder_path = '1. ABO/_bahan/QRIS_SHOPEE/QRIS C (Normal)'
        output_path = '1. ABO/_bahan/QRIS_SHOPEE/merge/merge_QRIS S_C.csv'
        
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
                merged_df['Update Time'] = pd.to_datetime(merged_df['Update Time'], format='%Y-%m-%d %H:%M:%S')
                merged_df['DATE'] = merged_df['Update Time'].dt.strftime('%d/%m/%Y')
                merged_df['TIME'] = merged_df['Update Time'].dt.time
            except Exception as e:
                st.write(f"Error formatting time: {e}")
        
            # Save the merged DataFrame to a CSV file
            merged_df.to_csv(output_path, index=False)
            st.write("Merged CSV file has been created:", output_path)
        else:
            st.write("There are no CSV files to merge.")
        
        
        # Define the directory containing the CSV files
        directory = '1. ABO/_bahan/QRIS_SHOPEE/merge'
        
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
            output_file = '1. ABO/_merge/merge_QRIS Shopee.csv'
            concatenated_df.to_csv(output_file, index=False)
        
            st.write("Concatenated CSV file saved to:", output_file)
        else:
            st.write("There are no CSV files to concatenate.")
        
        st.write('QRIS IA')
         #Specify the directory where the HTML files are located
        folder_path = '1. ABO/_bahan/QRIS_IA/'
        
         #Initialize a list to store DataFrames from each file
        dataframes = []
        
         #Walk through all directories and subdirectories
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                if file_name.endswith('.xls'):  # Make sure only Excel files are processed
                    file_path = os.path.join(root, file_name)
                    try:
                        # Read the HTML tables into a list of DataFrames
                        html_tables = pd.read_html(file_path, header=0)  # Specify header as 0
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
                        st.write(f"Error reading {file_path}: {e}")
        
        if dataframes:
            # Concatenate all DataFrames into one DataFrame
            merged_qris_ia = pd.concat(dataframes, ignore_index=True)
        
            merged_qris_ia = merged_qris_ia[merged_qris_ia['ID Transaksi']      !=      "Summary"]
        
            # Save the merged DataFrame to a CSV file without row index
            output_file = '1. ABO/_merge/merge_QRIS IA.csv'
            merged_qris_ia.to_csv(output_file, index=False)
            st.write("Merged CSV file saved to:", output_file)
        else:
            st.write("There are no QRIS TELKOM files to process. No CSV file generated.")
        
        st.write('WEB')
        # Specify the directory where the HTML files are located
        folder_path = '1. ABO/_bahan/WEB/'
        
        # Initialize a list to store DataFrames from each file
        dataframes = []
        
        # Loop through each file in the folder
        for file_name in os.listdir(folder_path):
            if file_name.endswith('.xls'):  # Make sure only HTML files are processed
                file_path = os.path.join(folder_path, file_name)
                try:
                    html_file = pd.read_html(file_path)
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
            output_file = '1. ABO/_merge/merge_WEB.csv'
            merged_web.to_csv(output_file, index=False)
        
            # Read the CSV file skipping the first row
            final_web = pd.read_csv(output_file, skiprows=[0])
        
            # Filter out rows where the 'DATE' column contains "DATE" or "TOTAL"
            final_web = final_web[~final_web['DATE'].str.contains('DATE|TOTAL')]
        
            # Save the DataFrame without row index to a new CSV file
            final_web.to_csv(output_file, index=False)
        
            st.write("Concatenated WEB Exported to:", output_file)
        else:
            st.write("There are no HTML files to process.")           

        
        gojek1_path       = '1. ABO/_merge/merge_Gojek 1.csv'
        outputgojek1_path = '1. ABO/_final/Final Gojek 1.csv'
        
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
            st.write(f"File processed and saved as {outputgojek1_path}")
        else:
            st.write("File does not exist. Please double check")
        
        gojek2_path       = '1. ABO/_merge/merge_Gojek 2.csv'
        outputgojek2_path = '1. ABO/_final/Final Gojek 2.csv'
        
        if os.path.exists(gojek1_path):
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
            final_go2      =   loc_go2.to_csv('1. ABO/_final/Final Gojek 2.csv', index=False)
        
            # Save the final result to a new CSV file
            loc_go2.to_csv(outputgojek2_path, index=False)
            st.write(f"File processed and saved as {outputgojek2_path}")
        else:
            st.write("File does not exist. Please double check")
        
        gojek3_path       = '1. ABO/_merge/merge_Gojek 3.csv'
        outputgojek3_path = '1. ABO/_final/Final Gojek 3.csv'
        
        if os.path.exists(gojek3_path):
            # Read data merge GOJEK 3
            df_go3 = pd.read_csv(gojek3_path).fillna('')
        
            # Rename columns to match the database schema
            loc_go3 = df_go3.loc[:, ['Transaction time', 'Order ID', 'Amount', 'CAB']].rename(
                columns={'Transaction time': 'DATETIME', 'Order ID': 'ID', 'Amount': 'NOM'}).fillna('')
        
            loc_go3['DATETIME'] = loc_go3['DATETIME'].str.replace('T', ' ').str.slice(0, 19)
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
            st.write(f"File processed and saved as {outputgojek3_path}")
        else:
            st.write("File does not exist. Please double check")
        
        shopee_path       = '1. ABO/_merge/merge_Shopee Food.csv'
        outputshopee_path = '1. ABO/_final/Final Shopee Food.csv'
        
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
        
            #loc_shopee['DATETIME'] = loc_shopee['DATETIME'].str.replace('Jun', 'June')
        
            loc_shopee['DATETIME']    =   pd.to_datetime(loc_shopee['DATETIME'], format='%d/%m/%Y %H:%M:%S')
            loc_shopee['DATE']        =   loc_shopee['DATETIME'].dt.strftime('%d/%m/%Y')
            loc_shopee['TIME']        =   loc_shopee['DATETIME'].dt.time
            del loc_shopee['DATETIME']
        
            loc_shopee['NOM']         =   pd.to_numeric(loc_shopee['NOM']).astype(int)
            loc_shopee                =  loc_shopee.drop(loc_shopee[loc_shopee['Status'] == 'Cancelled'].index)
        
            loc_shopee['CODE']        =   ''
        
            loc_shopee['KAT']         =   'SHOPEEPAY'
            loc_shopee['SOURCE']      =   'INVOICE'
        
            # re-order columns
            loc_shopee                =   loc_shopee[['CAB', 'DATE', 'TIME', 'CODE', 'ID', 'NOM', 'KAT', 'SOURCE']]
        
            # Save the final result to a new CSV file
            loc_shopee.to_csv(outputshopee_path, index=False)
            st.write(f"File processed and saved as {outputshopee_path}")
        else:
            st.write("File does not exist. Please double check")
        
        outputgrab_path   = '1. ABO/_final/Final Grab.csv'
        grab1_path        = '1. ABO/_merge/merge_Grab 1.csv'
        grab2_path        = '1. ABO/_merge/merge_Grab 2.csv'
        
        # Check for the existence of grab files
        grab1_exists = os.path.exists(grab1_path)
        grab2_exists = os.path.exists(grab2_path)
        
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
                loc_grab['NOM1'] = pd.to_numeric(loc_grab['NOM1'], errors='coerce').astype(float)
                loc_grab['Amount'] = pd.to_numeric(loc_grab['Amount'].str.replace('.', ''), errors='coerce').astype(float)
        
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
                pilih2 = [loc_grab['ID'] + 'A', loc_grab['ID']]
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
                st.write(f"File processed and saved as {outputgrab_path}")
        else:
            st.write("File Grab1 and Grab2 does not exist. Please double check")
        
        
        qrisshopee_path       = '1. ABO/_merge/merge_QRIS Shopee.csv'
        outputqrishopee_path  = '1. ABO/_final/Final QRIS Shopee.csv'
        
        if os.path.exists(qrisshopee_path):
            # Read data merge QRIS Shopee
            df_shopee = pd.read_csv(qrisshopee_path).fillna('')
        
            # Rename columns to match the database schema
            loc_qrisshopee = df_shopee.loc[:, ['Folder', 'Transaction ID', 'DATE', 'TIME', 'Transaction Amount', 'Transaction Type']].rename(
                columns={'Folder': 'CAB', 'Transaction ID': 'ID', 'Transaction Amount': 'NOM'}).fillna('')
        
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
            st.write(f"File processed and saved as {outputqrishopee_path}")
        else:
            st.write("File does not exist. Please double check")
        
        qristelekom_path        = '1. ABO/_merge/merge_QRIS IA.csv'
        outputqristelekom_path  = '1. ABO/_final/Final QRIS Telkom.csv'
        
        if os.path.exists(qristelekom_path):
            # Read data merge QRIS Telkom
            df_qristelkom = pd.read_csv(qristelekom_path).fillna('')
        
            # Rename columns to match the database schema
            loc_qristelkom = df_qristelkom.loc[:, ['Folder', 'Waktu Transaksi', 'Nama Customer', 'Nominal (termasuk Tip)']].rename(
                columns={'Folder': 'CAB', 'Waktu Transaksi': 'DATETIME', 'Nama Customer': 'ID', 'Nominal (termasuk Tip)': 'NOM'}).fillna('')
        
            loc_qristelkom['DATETIME'] = loc_qristelkom['DATETIME'].str.replace('Jun', 'June')
        
            # Convert 'DATETIME' column to datetime
            loc_qristelkom['DATETIME'] = pd.to_datetime(loc_qristelkom['DATETIME'])
        
            # Extract date and time into new columns
            loc_qristelkom['DATE'] = loc_qristelkom['DATETIME'].dt.strftime('%d/%m/%Y')
            loc_qristelkom['TIME'] = loc_qristelkom['DATETIME'].dt.time
            del loc_qristelkom['DATETIME']
        
            loc_qristelkom['CODE'] = ''
            loc_qristelkom['KAT'] = 'QRIS Telkom'
            loc_qristelkom['SOURCE'] = 'INVOICE'
        
            # Re-order columns
            loc_qristelkom = loc_qristelkom[['CAB', 'DATE', 'TIME', 'CODE', 'ID', 'NOM', 'KAT', 'SOURCE']]
        
            # Save the final result to a new CSV file
            loc_qristelkom.to_csv(outputqristelekom_path, index=False)
            st.write(f"File processed and saved as {outputqristelekom_path}")
        else:
            st.write("File does not exist. Please double check")
        
        import pandas as pd
        import os
        
        # Path to the CSV file
        file_path = '1. ABO/_merge/merge_ESB.csv'
        
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
        
            # Extract text after the dot in the 'CAB' column
            df_esb['CAB'] = df_esb['Branch Name'].str.split('.').str[1]
        
            # Rename columns to match the database schema
            df_esb = df_esb.rename(columns={'POS Sales Number': 'ID', 'Amount': 'NOM'}).fillna('')
        
            # Select and sort the relevant columns
            df_esb = df_esb.loc[:, ['CAB', 'DATE', 'TIME', 'CODE', 'ID', 'NOM', 'KAT', 'SOURCE']].sort_values('DATE', ascending=False)
        
            # Save the final result to a new CSV file
            df_esb.to_csv('1. ABO/_final/Final ESB.csv', index=False)
        else:
            # st.write a message if the file is not found
            st.write("File does not exist. Please double check")
        
        #Read data merge WEB
        df_web       =   pd.read_csv('1. ABO/_merge/merge_WEB.csv')
        
        df_web['DATE'] = df_web['DATE'].str.replace('Jun', 'June')
        
        df_web['SOURCE']     =   'WEB'
        
        #Rename columns to match the database schema
        df_web       =       df_web.rename(columns={'CO':'TIME','TOTAL':'NOM','KATEGORI':'KAT','CUSTOMER':'ID'}).fillna('')
        df_web       =       df_web.loc[:,['CAB','DATE','TIME','CODE','ID','NOM','KAT','SOURCE']].sort_values('DATE', ascending=[False])
        
        final_web       =       df_web.to_csv('1. ABO/_final/WEB Akhir.csv', index=False)
        web_final       =       pd.read_csv('1. ABO/_final/WEB Akhir.csv')
        
        web_final       =       web_final[web_final['TIME']     !=      'TOTAL']
        web_final       =       web_final[web_final['TIME']     !=      'CO']
        
        web_final['TIME'] = pd.to_datetime(web_final['TIME'])
        web_final['DATE'] = pd.to_datetime(web_final['DATE'])
        web_final         =   web_final[web_final['DATE'].isin([all_date])]
        web_final['TIME'] = web_final['TIME'].dt.strftime('%H:%M:%S')
        web_final['DATE'] = web_final['DATE'].dt.strftime('%d/%m/%Y')
        web_final = web_final[(web_final['CAB'].str.isin(all_cab))]
        web_final['KAT'] = web_final['KAT'].replace({'SHOPEE PAY': 'SHOPEEPAY', 'GORESTO': 'GO RESTO', 'GRAB': 'GRAB FOOD'})
        web_exp          =       web_final.to_csv('1. ABO/_final/ALL/WEB {saveas}.csv', index=False)
        
        df_concat = pd.concat([pd.read_csv(f, dtype=str) for f in glob.glob('1. ABO/_final/Final*')], ignore_index = True).fillna('')
        df_concat = df_concat[['CAB', 'DATE', 'TIME', 'CODE', 'ID', 'NOM', 'KAT', 'SOURCE']]
        df_concat = df_concat[(df_concat['CAB'].str.isin(all_cab))]
        df_concat = df_concat[df_concat['DATE']     !=      '']
        df_concat['DATE'] = pd.to_datetime(df_concat['DATE'], format='%d/%m/%Y')
        df_concat   =   df_concat[df_concat['DATE'].isin(all_date)] #CHANGE
        df_concat['DATE'] = df_concat['DATE'].dt.strftime('%d/%m/%Y')
        df_concatx  =   df_concat.to_csv('1. ABO/_final/ALL/INVOICE {saveas}.csv', index=False) #CHANGE
        st.write(web_final)
        st.write(df_concat)


        
        
        
