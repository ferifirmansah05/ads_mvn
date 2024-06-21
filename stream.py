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
        main_folder = '1. ABO/_bahan/GOJEK 1'
        subfolders = [folder for folder in os.listdir(main_folder) if os.path.isdir(os.path.join(main_folder, folder))]
        st.write(glob(os.path.join(main_folder, subfolders[0], '*.csv')))
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
            final_df_GOJEK_1 = pd.concat(combined_dataframes)












