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

def initialize_firebase():
    # Path ke file service account JSON yang diunduh dari Firebase Console
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'gs://abov1-2d892.appspot.com'
    })

def get_storage_bucket():
    if not firebase_admin._apps:
        initialize_firebase()
    return storage.bucket()

# Fungsi untuk mengunggah file ke Firebase Storage
def upload_file_to_firebase(file, blob_name):
    bucket = get_storage_bucket()
    blob = bucket.blob(blob_name)
    blob.upload_from_file(file)
    return blob.public_url

# Fungsi untuk mendapatkan IP publik pengguna
def get_public_ip():
    try:
        response = requests.get('https://api64.ipify.org?format=json')
        ip = response.json()['ip']
        return ip
    except Exception as e:
        st.error(f"Error mendapatkan IP publik: {e}")
        return "unknown"

# Aplikasi Streamlit
def main():
    st.title("Upload dan Ekstrak File ZIP ke Firebase Storage dengan Path Unik")
    
    # Unggah file ZIP menggunakan Streamlit
    uploaded_zip = st.file_uploader("Pilih file ZIP yang ingin diunggah dan diekstrak", type="zip")
    
    if uploaded_zip is not None:
        # Tampilkan preview file yang diunggah
        st.write("File details:")
        st.write(f"Filename: {uploaded_zip.name}")
        st.write(f"File type: {uploaded_zip.type}")
        st.write(f"File size: {uploaded_zip.size} bytes")
        
        # Dapatkan IP publik pengguna
        user_ip = get_public_ip()
        st.write(f"IP publik pengguna: {user_ip}")
        
        # Gunakan direktori sementara
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Ekstrak file ZIP ke direktori sementara
            with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
                zip_ref.extractall(tmpdirname)
                st.write(f"Ekstrak file ke {tmpdirname}")

                # Menampilkan daftar file yang diekstrak
                for root, dirs, files in os.walk(tmpdirname):
                    for file in files:
                        st.write(f"File diekstrak: {file}")
                        file_path = os.path.join(root, file)
                        with open(file_path, 'rb') as f:
                            # Menyusun path penyimpanan unik dengan IP pengguna
                            blob_name = f"{user_ip}/{os.path.relpath(file_path, tmpdirname)}"
                            public_url = upload_file_to_firebase(f, blob_name)
                            st.success(f"File {blob_name} berhasil diunggah! URL publik: {public_url}")

if __name__ == "__main__":
    main()
