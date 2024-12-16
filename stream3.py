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
st.markdown("""
    <style>
        .stAgGrid {
            margin: 0;  /* Hilangkan margin */
            padding: 0; /* Hilangkan padding */
        }
        .ag-root-wrapper {
            border: none !important; /* Hilangkan border luar */
        }
        .ag-header {
            border-bottom: none !important; /* Opsional: Hilangkan border bawah header */
        }
        .ag-row {
            border-bottom: none !important; /* Opsional: Hilangkan garis antar baris */
        }
    </style>
    """, unsafe_allow_html=True)
st.write("Tabel dengan kolom pertama dibekukan:")
AgGrid(df, gridOptions=grid_options,fit_columns_on_grid_load=True, height=None)

