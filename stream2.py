import streamlit as st
import requests
from streamlit_option_menu import option_menu


# Membuat navigasi bar
option = option_menu(
    menu_title="#FPnA",  # required
    options=["Automate Breakdown Ojol", "Download Invoice"],  # required
    menu_icon="cast",  # optional
    default_index=0,  # optional
    orientation="horizontal",
)

# Fungsi untuk menjalankan file python yang diunduh
def run_stream_script(url):
    # Mengunduh file dari GitHub
    response = requests.get(url)
    if response.status_code == 200:
        # Menjalankan file yang diunduh
        exec(response.text, globals())
    else:
        st.error(f"Failed to download file: {response.status_code}")

# Arahkan ke aplikasi berdasarkan pilihan pengguna
if option == 'Automate Breakdown Ojol':
    stream1_url = 'https://raw.githubusercontent.com/ferifirmansah05/ads_mvn/main/stream.py'
    run_stream_script(stream1_url)
  
elif option == 'Download Invoice':
    stream2_url = 'https://raw.githubusercontent.com/ferifirmansah05/ads_mvn/main/stream3.py'
    run_stream_script(stream2_url)



                    

