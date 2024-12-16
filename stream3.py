import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import streamlit as st
import streamlit.components.v1 as components

# Contoh DataFrame
data = {
    "Nama": ["John", "Alice", "Bob", "Eve"],
    "Januari 2024": [1000, 1200, 1100, 1050],
    "Februari 2024": [1500, 1400, 1350, 1450],
    "Maret 2024": [900, 850, 780, 760],
}

df = pd.DataFrame(data)

# Fungsi untuk menghitung warna horizontal per row
def calculate_row_colors(row):
    row_min = row.min()
    row_max = row.max()
    return [
        f"rgb({int(255 * (1 - (value - row_min) / (row_max - row_min)))},"
        f"{int(255 * ((value - row_min) / (row_max - row_min)))},150)"
        for value in row
    ]

# Fungsi untuk menentukan cellStyle
def set_row_style(params):
    row_index = params['rowIndex']
    column_name = params['colDef']['field']
    if row_index is None or column_name == "Nama":
        return {'backgroundColor': 'white', 'color': 'black'}
    
    # Ambil warna berdasarkan row
    row_colors = calculate_row_colors(df.iloc[row_index, 1:])
    col_index = df.columns.get_loc(column_name) - 1  # Kolom mulai dari kolom ke-2
    if col_index >= 0:
        return {'backgroundColor': row_colors[col_index], 'color': 'black', 'fontWeight': 'bold'}
    return {'backgroundColor': 'white', 'color': 'black'}

# Konfigurasi AgGrid
gb = GridOptionsBuilder.from_dataframe(df)

# Terapkan cellStyle ke semua kolom mulai dari kolom ke-2
for col in df.columns[1:]:
    gb.configure_column(col, cellStyle=set_row_style)

# Bangun opsi AgGrid
grid_options = gb.build()

# Tampilkan tabel di Streamlit
AgGrid(
    df,
    gridOptions=grid_options,
    height=400,
    allow_unsafe_jscode=False  # Tidak menggunakan JS
)
