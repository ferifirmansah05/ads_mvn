import pandas as pd
import numpy as np
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from matplotlib.colors import LinearSegmentedColormap, to_hex
import matplotlib.pyplot as plt

# 1. Fungsi untuk membuat skema warna pastel menggunakan LinearSegmentedColormap
def create_pastel_cmap():
    pastel_cmap = LinearSegmentedColormap.from_list(
        "pastel_gradient",
        [
            (0, (1.0, 1.0, 1.0)),  # Putih
            (1, (1.0, 0.7, 0.7))   # Merah pastel
        ]
    )
    return pastel_cmap

# 2. Fungsi untuk mengonversi nilai ke warna pastel
def get_pastel_color(value, vmin, vmax, cmap):
    norm_value = (value - vmin) / (vmax - vmin) if vmax > vmin else 0
    rgba_color = cmap(norm_value)  # Ambil warna RGBA dari colormap
    hex_color = to_hex(rgba_color)  # Konversi ke HEX
    return hex_color

# 3. Contoh DataFrame
np.random.seed(0)
data = {
    "Nama": ["John", "Alice", "Bob", "Eve", "Michael"],
    "Jan": np.random.randint(100, 500, size=5),
    "Feb": np.random.randint(100, 500, size=5),
    "Mar": np.random.randint(100, 500, size=5),
    "Apr": np.random.randint(100, 500, size=5),
}
df = pd.DataFrame(data)

# 4. Membuat skema warna pastel
pastel_cmap = create_pastel_cmap()

# 5. Menambahkan kolom warna berdasarkan nilai di setiap baris
df_colors = df.copy()
vmin = df.iloc[:, 1:].min().min()  # Nilai minimum
vmax = df.iloc[:, 1:].max().max()  # Nilai maksimum

for col in df.columns[1:]:  # Kolom numerik
    df_colors[col] = df[col].apply(lambda x: get_pastel_color(x, vmin, vmax, pastel_cmap))

# 6. Mengatur GridOptionsBuilder dengan warna pastel
gb = GridOptionsBuilder.from_dataframe(df)

# Menambahkan cellStyle untuk setiap kolom numerik
for col in df.columns[1:]:
    js_code = JsCode(f"""
    function(params) {{
        return {{
            'backgroundColor': '{df_colors.at[params.rowIndex, col]}',
            'color': 'black'
        }};
    }}
    """)
    gb.configure_column(col, cellStyle=js_code)

grid_options = gb.build()

# 7. Menampilkan tabel di Streamlit
st.title("AgGrid dengan Gradient Pastel Horizontal")
AgGrid(df, gridOptions=grid_options, height=400, allow_unsafe_jscode=True)
