import requests
import os

# URL file yang ingin diunduh
url = 'https://raw.githubusercontent.com/ferifirmansah05/ads_mvn/main/stream.py'

# Nama file lokal
local_filename = 'stream.py'

# Mengunduh file dari GitHub
response = requests.get(url)
if response.status_code == 200:
    with open(local_filename, 'wb') as f:
        f.write(response.content)
else:
    print(f"Failed to download file: {response.status_code}")

import subprocess

# Perintah untuk menjalankan Streamlit dengan runOnSave=false
command_run_streamlit = "streamlit stream.py --server.runOnSave=false"
subprocess.run(command_run_streamlit, shell=True)
