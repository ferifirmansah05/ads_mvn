import streamlit as st
import pandas as pd
import zipfile
import io
import os
from glob import glob
import csv
def run_install_script():
    result = subprocess.run(['python', 'install_packages.py'], check=True)
    if result.returncode == 0:

if __name__ == "__main__":
    run_install_script() 
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
                
        
        
        
        
        
