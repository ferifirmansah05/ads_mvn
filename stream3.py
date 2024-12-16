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
gb.configure_grid_options(domLayout='autoHeight') 
grid_options = gb.build()
# Tampilkan AgGrid
st.markdown("""
    <style>
        .stAgGrid {
            margin-bottom: 0; /* Menghapus margin di bawah tabel */
            padding-bottom: 0; /* Menghapus padding di bawah tabel */
        }
        .ag-root-wrapper {
            border: none !important; /* Opsional: Hilangkan border jika diperlukan */
        }
    </style>
    """, unsafe_allow_html=True)

st.write("Tabel dengan kolom pertama dibekukan:")
AgGrid(df, gridOptions=grid_options,fit_columns_on_grid_load=True)

