import pandas as pd
import numpy as np
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode,ColumnsAutoSizeMode
from matplotlib.colors import LinearSegmentedColormap, to_hex

# 1. Fungsi untuk membuat colormap putih ke merah pastel
def create_white_to_red_cmap():
    pastel_cmap = LinearSegmentedColormap.from_list(
        "white_red",
        [(0, (1.0, 1.0, 1.0)),  # Putih
         (1, (1.0, 0.5, 0.5))]  # Merah pastel
    )
    return pastel_cmap

# 2. Fungsi untuk mendapatkan warna horizontal
def row_gradient_colors(row, cmap):
    vmin, vmax = row.min(), row.max()  # Nilai min dan max dalam satu baris
    colors = [get_color(value, vmin, vmax, cmap) for value in row]
    return colors

def get_color(value, vmin, vmax, cmap):
    norm_value = (value - vmin) / (vmax - vmin) if vmax > vmin else 0
    rgba_color = cmap(norm_value)  # Ambil warna dari colormap
    return to_hex(rgba_color)      # Konversi ke HEX

# 3. DataFrame Contoh
np.random.seed(42)
data = {
    "Nama": ["John", "Alice", "Bob", "Eve", "Michael"],
    "Jan": np.random.randint(100, 500, size=5),
    "Feb": np.random.randint(100, 500, size=5),
    "Mar": np.random.randint(100, 500, size=5),
    "Apr": np.random.randint(100, 500, size=5),
}
df = pd.DataFrame(data)
df.iloc[:,1:] = df.iloc[:,1:].astype('int')
# 4. Membuat colormap
cmap = create_white_to_red_cmap()

# 5. Menghitung warna horizontal per baris
row_colors = df.iloc[:, 1:].apply(lambda row: row_gradient_colors(row, cmap), axis=1)

# 6. Konfigurasi AgGrid
gb = GridOptionsBuilder.from_dataframe(df)


# Menambahkan cellStyle untuk setiap kolom numerik
for col_idx, col in enumerate(df.columns[1:]):
    gb.configure_column(
        col,
        cellStyle=JsCode(f"""
        function(params) {{
            const colors = {row_colors.apply(lambda x: x[col_idx]).tolist()};
            return {{
                'backgroundColor': colors[params.node.rowIndex],
                'color': 'black',
                'textAlign': 'center'
            }};
        }}
        """)
    )

grid_options = gb.build()


# 7. Tampilkan AgGrid di Streamlit
st.title("AgGrid dengan Gradasi Horizontal Putih ke Merah Pastel")
AgGrid(df, gridOptions=grid_options, allow_unsafe_jscode=True, enable_enterprise_modules=True,width='100%')


# Data untuk grid
data = [
    {'Name': 'Alice', 'Age': 30, 'City': 'New York'},
    {'Name': 'Bob', 'Age': 25, 'City': 'London'},
    {'Name': 'Charlie', 'Age': 35, 'City': 'San Francisco'},
]

# Membuat GridOptionsBuilder dari data
gb = GridOptionsBuilder.from_dataframe(data)

# Menentukan pengaturan khusus untuk kolom pertama
column_defs = [
    {'headerName': 'Name', 'field': 'Name', 'autoSizeColumns': True},  # Kolom pertama: Auto resize
    {'headerName': 'Age', 'field': 'Age', 'width': 150},              # Kolom kedua: Lebar 150px
    {'headerName': 'City', 'field': 'City', 'width': 150},            # Kolom ketiga: Lebar 150px
]

# Mengonfigurasi grid untuk menggunakan columnDefs yang telah diubah
gb.configure_columns(column_defs)

# Menampilkan grid AG-Grid di Streamlit
AgGrid(data, gridOptions=gb.build(), fit_columns_on_grid_load=True)


