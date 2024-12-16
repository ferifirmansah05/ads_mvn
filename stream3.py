import pandas as pd
import numpy as np
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

# Contoh DataFrame
np.random.seed(0)
data = {
    "Nama": ["John", "Alice", "Bob", "Eve", "Michael"],
    "Jan": np.random.randint(100, 500, size=5),
    "Feb": np.random.randint(100, 500, size=5),
    "Mar": np.random.randint(100, 500, size=5),
    "Apr": np.random.randint(100, 500, size=5),
}
df = pd.DataFrame(data)

# Hitung nilai min dan max untuk setiap baris
df['RowMin'] = df.iloc[:, 1:].min(axis=1)
df['RowMax'] = df.iloc[:, 1:].max(axis=1)

# Membuat GridOptions dengan AgGrid
gb = GridOptionsBuilder.from_dataframe(df.drop(columns=["RowMin", "RowMax"]))

# Definisikan cellStyle untuk gradient horizontal
js_code = JsCode("""
function(params) {
    const rowMin = params.data.RowMin;
    const rowMax = params.data.RowMax;

    if (params.value == null || rowMin == rowMax) {
        return {'backgroundColor': 'white', 'color': 'black'};
    }

    const value = params.value;
    const ratio = (value - rowMin) / (rowMax - rowMin);
    const red = Math.min(255, Math.max(0, 255 * (1 - ratio)));
    const green = Math.min(255, Math.max(0, 255 * ratio));
    const color = `rgb(${red}, ${green}, 0)`;

    return {'backgroundColor': color, 'color': 'black'};
}
""")

# Terapkan cellStyle pada kolom data (bukan kolom pertama)
for col in df.columns[1:-2]:  # Kolom data saja, kecuali "Nama" dan kolom tambahan
    gb.configure_column(
        col,
        cellStyle=js_code,
    )

# Atur GridOptions
grid_options = gb.build()

# Tampilkan AgGrid dengan gradient horizontal
st.title("AgGrid dengan Gradient Horizontal Per Baris")
AgGrid(
    df, 
    gridOptions=grid_options, 
    height=400, 
    allow_unsafe_jscode=True
)
