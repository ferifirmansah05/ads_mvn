import streamlit as st
import pandas as pd
import zipfile
import io
import os
from glob import glob

st.title('Unggah dan Gabungkan File CSV dari ZIP')

uploaded_file = st.file_uploader("Pilih file ZIP", type="zip")


if st.button('Process'):
    with zipfile.ZipFile(uploaded_file, 'r') as z:
      z.extractall()

    main_folder = '/content/1. ABO/_bahan/GOJEK 1'


    # Get the list of subfolders within the main folder
    subfolders = [folder for folder in os.listdir(main_folder) if os.path.isdir(os.path.join(main_folder, folder))]
    st.write(glob(os.path.join(main_folder, subfolders[0], '*.csv')))
    # List to store concatenated dataframes
    combined_dataframes = []

    # Iterate over each subfolder
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

    # Check if there are any dataframes to concatenate
    if combined_dataframes:
        # Concatenate dataframes from all subfolders
        final_df = pd.concat(combined_dataframes)
        # Streamlit app
        st.title('Download CSV File Example')

        def convert_df(df):
          return df.to_csv(index=False).encode('utf-8')

        csv = convert_df(final_df)

        st.download_button(
          "Press to Download",
          csv,
          "file.csv",
          "text/csv",
          key='download-csv'
      )






