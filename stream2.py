import requests
import subprocess

# URL file GitHub
url = 'https://raw.githubusercontent.com/ferifirmansah05/ads_mvn/main/stream.py'

# Download file dari GitHub
response = requests.get(url)

# Simpan file ke direktori lokal
with open('stream.py', 'wb') as file:
    file.write(response.content)

# Jalankan file yang telah didownload
subprocess.run(['python', 'stream.py'])
