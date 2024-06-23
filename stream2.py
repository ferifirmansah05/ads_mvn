import streamlit as st
import zipfile
import os
import tempfile
import requests
import firebase_admin
from firebase_admin import credentials, storage

def download_file_from_github(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded successfully and saved to {save_path}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")


# URL file model .pkl di GitHub (gunakan URL raw dari file .pkl di GitHub)
url = 'https://raw.githubusercontent.com/ferifirmansah05/ads_mvn/main/serviceAccountKey.json'

# Path untuk menyimpan file yang diunduh
save_path = 'serviceAccountKey.json'

download_file_from_github(url, save_path)


# Fungsi untuk menginisialisasi Firebase dan mendapatkan bucket storage
def get_storage_bucket():
    try:
        cred_path = "serviceAccountKey.json"
        bucket_name = "abov1-2d892.appspot.com"
        # Periksa apakah aplikasi Firebase sudah diinisialisasi
        if not firebase_admin._apps:
            st.write(f"Using credentials from: {cred_path}")
            st.write(f"Using bucket name: {bucket_name}")
            
            # Inisialisasi aplikasi Firebase
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'storageBucket': bucket_name
            })
            
            st.write("Firebase app initialized successfully.")
        
        # Ambil bucket storage
        bucket = storage.bucket(bucket_name)
        st.write("Bucket retrieved successfully.")
        return bucket
    except ValueError as ve:
        st.error(f"ValueError in get_storage_bucket: {ve}")
        raise  # Raise exception to see full traceback
    except firebase_admin.exceptions.FirebaseError as fe:
        st.error(f"FirebaseError in get_storage_bucket: {fe}")
        raise  # Raise exception to see full traceback
    except Exception as e:
        st.error(f"Unexpected error in get_storage_bucket: {e}")
        raise  # Raise exception to see full traceback

# Fungsi untuk mengunggah file ke Firebase Storage
def upload_file_to_firebase(file, blob_name):
    bucket = get_storage_bucket()
    if bucket:
        try:
            blob = bucket.blob(blob_name)
            blob.upload_from_file(file)
            st.write("File uploaded successfully.")
            return blob.public_url
        except Exception as e:
            st.error(f"Error uploading file: {e}")
            return None
    else:
        st.error("Bucket is None. File upload aborted.")
        return None

# Fungsi untuk menguji apakah bucket berhasil diambil
def test_get_storage_bucket():
    bucket = get_storage_bucket()
    if bucket:
        st.success("get_storage_bucket() works correctly.")
    else:
        st.error("get_storage_bucket() does not work correctly.")

# Aplikasi Streamlit untuk menguji fungsi
def main():
    st.title("Test Firebase Storage Bucket")

    test_get_storage_bucket()  # Uji fungsi get_storage_bucket()

    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        blob_name = f"test/{uploaded_file.name}"
        public_url = upload_file_to_firebase(uploaded_file, blob_name)
        if public_url:
            st.success(f"File uploaded successfully. Public URL: {public_url}")

if __name__ == "__main__":
    main()

