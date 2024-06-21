import streamlit as st
import pandas as pd
import zipfile
import io
import os
from glob import glob

st.title('Unggah dan Gabungkan File CSV dari ZIP')

uploaded_file = st.file_uploader("Pilih file ZIP", type="zip")

if uploaded_file is not None:
    # Baca konten zip file
    zip_contents = uploaded_file.read()

    # Simpan zip file sementara
    with open("temp.zip", "wb") as f:
        f.write(zip_contents)

    # Ekstrak zip file
    with zipfile.ZipFile("temp.zip", "r") as zip_ref:
        zip_ref.extractall("extracted_files")
    
    st.write("File ABO.zip berhasil diekstrak.")

    # Hapus file zip sementara
    os.remove("temp.zip")

    # Menampilkan daftar file yang diekstrak
    extracted_files = os.listdir("extracted_files")
    st.write("File yang diekstrak:")
    for file in extracted_files:
        st.write(file)






