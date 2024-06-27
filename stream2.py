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

# Menjalankan file yang diunduh
with open(local_filename, 'r') as f:
    exec(f.read())

