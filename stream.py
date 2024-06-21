import streamlit as st
import pandas as pd
import zipfile
import io
import os
from glob import glob

st.title('Upload File *Zip')

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
            st.write("Concatenated GOJEK 1")
        else:
            st.write("No dataframes GOJEK 1 to concatenate.")   

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
            st.write("Concatenated GOJEK 2")
        else:
            st.write("No dataframes GOJEK 2 to concatenate.")

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
            st.write("Concatenated GOJEK 3")
        else:
            st.write("No dataframes GOJEK 3 to concatenate.")

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
            st.write("Concatenated SHOPEE FOOD")
        else:
            st.write("No dataframes SHOPEE FOOD to concatenate.")
        
        





