import pandas as pd
import numpy as np
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from matplotlib.colors import LinearSegmentedColormap, to_hex

# 1. Fungsi untuk membuat colormap putih ke merah pastel
def create_white_to_red_cmap():
    pastel_cmap = LinearSegmentedColormap.from_list(
        "white_red",
        [(0, (1.0, 1.0, 1.0)),  # Putih
         (1, (1.0, 0.5, 0.5))]  # Merah pastel
    )
    return pastel_cmap

# 2. Fungsi untuk menghitung warna berdasarkan nilai
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

# 4. Membuat colormap
cmap = create_white_to_red_cmap()

# 5. Menyiapkan GridOptionsBuilder dengan cellStyle dinamis
gb = GridOptionsBuilder.from_dataframe(df)

# Menambahkan cellStyle untuk setiap kolom numerik (hanya menghitung vmin dan vmax dari kolom itu)
for col in df.columns[1:]:
    gb.configure_column(
        col,
        cellStyle=JsCode(f"""
        function(params) {{
            const value = params.value;
            const vmin = Math.min(...params.columnApi.getAllDisplayedColumns().map(c => 
                params.api.getDisplayedRowAtIndex(0).data[c.colId]));
            const vmax = Math.max(...params.columnApi.getAllDisplayedColumns().map(c => 
                params.api.getDisplayedRowAtIndex(0).data[c.colId]));
            
            const norm = (value - vmin) / (vmax - vmin);
            const color = `rgb(255, ${255 - Math.round(255 * norm)}, ${255 - Math.round(255 * norm)})`;
            
            return {{
                'backgroundColor': color,
                'color': 'black',
                'textAlign': 'center'
            }};
        }}
        """)
    )

grid_options = gb.build()

# 6. Tampilkan AgGrid di Streamlit
st.title("AgGrid dengan Gradasi Horizontal Dinamis")
AgGrid(df, gridOptions=grid_options, allow_unsafe_jscode=True)
