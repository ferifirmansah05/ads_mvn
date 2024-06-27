import requests
import subprocess

# URL file GitHub
url = 'https://raw.githubusercontent.com/username/repository/branch/filename.py'

# Download file dari GitHub
response = requests.get(url)

# Simpan file ke direktori lokal
with open('filename.py', 'wb') as file:
    file.write(response.content)

# Jalankan file yang telah didownload
subprocess.run(['python', 'filename.py'])
