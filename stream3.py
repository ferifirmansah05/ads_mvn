import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import streamlit as st

# Membuat DataFrame contoh
data = {
    "Nama": ["John", "Alice", "Bob", "Eve", "Michael", "Jane", "Tom", "Sue", "Anna", "Max"],
    "Januari 2024": [1000, 1200, 1100, 1050, 900, 850, 780, 760, 720, 700],
    "Februari 2024": [1050, 1150, 1080, 1000, 950, 800, 770, 740, 690, 710],
    "Maret 2024": [1100, 1250, 1120, 1020, 970, 890, 780, 750, 710, 730]
}

df = pd.DataFrame(data)

# Konfigurasi GridOptionsBuilder untuk AgGrid
gb = GridOptionsBuilder.from_dataframe(df)

# Styling untuk kolom 'Januari 2024', 'Februari 2024', dan 'Maret 2024' agar menggunakan background gradient
# Menggunakan CSS background gradient pada kolom numerik (penjualan)
gb.configure_column("Januari 2024", cellStyle='background: linear-gradient(to right, #ffcccc 0%, #ff6666 100%);')
gb.configure_column("Februari 2024", cellStyle='background: linear-gradient(to right, #ffff99 0%, #ffcc00 100%);')
gb.configure_column("Maret 2024", cellStyle='background: linear-gradient(to right, #99ff99 0%, #66cc66 100%);')

# Membuat gridOptions untuk AgGrid
grid_options = gb.build()

# Menampilkan AgGrid dengan style dan gridOptions yang sudah dikonfigurasi
AgGrid(
    df,
    gridOptions=grid_options,
    height=400,
    allow_unsafe_jscode=True
)
