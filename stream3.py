from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
import streamlit as st

# Data contoh
data = {
    "Nama": ["John", "Alice", "Bob", "Eve"],
    "Umur": [25, 30, 22, 29],
    "Kota": ["Jakarta", "Bandung", "Surabaya", "Medan"],
    "Penjualan": [1000, 1200, 1100, 1050]
}

df = pd.DataFrame(data)

# Konfigurasi AgGrid
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True, resizable=True)
gb.configure_column("Nama", pinned="left")  # Membekukan kolom pertama
gb.configure_grid_options(domLayout='autoHeight', autoSizeColumns=True)
grid_options = gb.build()
# Tampilkan AgGrid
st.write("Tabel dengan kolom pertama dibekukan:")
AgGrid(df, gridOptions=grid_options, height=None, fit_columns_on_grid_load=True, theme='streamlit')

