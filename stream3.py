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
        col, width=150,
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
AgGrid(df, gridOptions=grid_options, fit_columns_on_grid_load=True, allow_unsafe_jscode=True)


# Data sample
data = [
    {"Make": "Toyota", "Model": "Corolla", "Price": 25000},
    {"Make": "Honda", "Model": "Civic", "Price": 22000},
    {"Make": "Ford", "Model": "Focus", "Price": 21000},
    {"Make": "Chevrolet", "Model": "Malibu", "Price": 28000},
    {"Make": "Nissan", "Model": "Altima", "Price": 26000},
]

df = pd.DataFrame(data)

# Menyusun Grid Options
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_pagination(paginationPageSize=10)
gb.configure_column("Make", width=150)
gb.configure_column("Model", width=150)
gb.configure_column("Price", width=120)

# Pengaturan untuk menambahkan baris total
def add_total_row(data):
    total_row = {"Make": "Total", "Model": "", "Price": sum(int(item["Price"]) for item in data)}
    return total_row

# Membuat grid dan menampilkan data dengan baris total
gridOptions = gb.build()
gridOptions["domLayout"] = "autoHeight"  # Agar grid sesuai dengan ukuran data

# Menampilkan AG-Grid dan mendapatkan data terfilter
response = AgGrid(df, gridOptions=gridOptions, height=300, enable_enterprise_modules=True)

# Mengambil data yang difilter melalui API AG-Grid
filtered_data = response['data']

# Menambahkan baris total di bawah data yang ditampilkan
total_row = add_total_row(filtered_data)  # Total berdasarkan data yang terfilter
data_to_display = filtered_data + [total_row]  # Gabungkan data terfilter dengan total

# Menampilkan grid dengan data dan baris total yang terpisah dari proses sorting
AgGrid(data_to_display, gridOptions=gridOptions, height=300)

