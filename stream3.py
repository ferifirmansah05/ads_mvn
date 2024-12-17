import pandas as pd
import numpy as np
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from matplotlib.colors import LinearSegmentedColormap, to_hex

# 1. Fungsi untuk membuat colormap gradasi putih ke merah pastel
def create_white_to_red_cmap():
    pastel_cmap = LinearSegmentedColormap.from_list(
        "white_red",
        [(0, (1.0, 1.0, 1.0)),  # Putih
         (1, (1.0, 0.5, 0.5))]  # Merah pastel
    )
    return pastel_cmap

# 2. Fungsi untuk mengonversi nilai ke warna
def get_color(value, vmin, vmax, cmap):
    norm_value = (value - vmin) / (vmax - vmin) if vmax > vmin else 0
    rgba_color = cmap(norm_value)  # Ambil warna RGBA dari colormap
    return to_hex(rgba_color)      # Konversi ke HEX

# 3. DataFrame Contoh
np.random.seed(42)
data = {
    "Nama": ["John", "Alice", "Bob", "Eve", "Michael"],
    "Jan": np.random.randint(100, 500, size=5),
    "Feb": np.random.randint(100, 500, size=5),
    "Mar": np.random.randint(100, 500, size=5),
}
df = pd.DataFrame(data)

# 4. Membuat colormap
cmap = create_white_to_red_cmap()

# 5. Buat DataFrame warna untuk setiap nilai di sel
df_colors = df.copy()
vmin = df.iloc[:, 1:].min().min()  # Nilai minimum
vmax = df.iloc[:, 1:].max().max()  # Nilai maksimum

for col in df.columns[1:]:
    df_colors[col] = df[col].apply(lambda x: get_color(x, vmin, vmax, cmap))

# 6. Konfigurasi AgGrid
gb = GridOptionsBuilder.from_dataframe(df)

# Menambahkan cellStyle untuk setiap kolom numerik
for col in df.columns[1:]:
    gb.configure_column(
        col,
        cellStyle=JsCode(f"""
        function(params) {{
            let value = params.value;
            if (value !== undefined && value !== null) {{
                return {{
                    'backgroundColor': '{df_colors.at[0, col]}',
                    'color': 'black',
                    'textAlign': 'center'
                }};
            }}
            return {{}};
        }}
        """)
    )

grid_options = gb.build()

# 7. Tampilkan AgGrid di Streamlit
st.title("AgGrid dengan Gradasi Warna Putih ke Merah")
AgGrid(df, gridOptions=grid_options, allow_unsafe_jscode=True)
