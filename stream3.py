import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import streamlit as st
from streamlit.components.v1 import html
import JsCode
# DataFrame contoh
data = {
    "Nama": ["John", "Alice", "Bob", "Eve"],
    "Januari 2024": [1000, 1200, 1100, 1050],
    "Februari 2024": [1500, 1400, 1350, 1450],
    "Maret 2024": [900, 850, 780, 760],
}

df = pd.DataFrame(data)

# Konfigurasi GridOptionsBuilder untuk AgGrid
gb = GridOptionsBuilder.from_dataframe(df)

# Menambahkan background gradient pada kolom kedua hingga akhir
gradient_css = JsCode("""
    function(params) {
        const value = params.value;
        const min = 700; // Sesuaikan dengan minimum data Anda
        const max = 1500; // Sesuaikan dengan maksimum data Anda
        const ratio = (value - min) / (max - min);
        const red = Math.min(255, Math.round(255 * (1 - ratio)));
        const green = Math.min(255, Math.round(255 * ratio));
        return {
            backgroundColor: `rgb(${red}, ${green}, 150)`, // Gradient dari merah ke hijau
            color: 'black'  // Warna teks
        };
    }
""")
# Terapkan fungsi CSS ke kolom kedua hingga terakhir
for col in df.columns[1:]:
    gb.configure_column(col, cellStyle=gradient_css)

# Membuat gridOptions
grid_options = gb.build()

# Menampilkan AgGrid dengan styling gradien
AgGrid(
    df,
    gridOptions=grid_options,
    height=400,
    allow_unsafe_jscode=True,  # Izinkan penggunaan JS untuk styling
)
