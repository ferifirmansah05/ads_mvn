import streamlit as st

# Judul aplikasi
st.title('Unggah Multiple File di Streamlit')

# Widget untuk mengunggah multiple file
uploaded_files = st.file_uploader("Pilih file Excel", type=['xlsx', 'xls'], accept_multiple_files=True)

if uploaded_files is not None:
    for file in uploaded_files:
        # Memuat file ke dalam dataframe pandas
        df = pd.read_excel(file, engine='openpyxl')

        # Menampilkan nama file
        st.write(f"Nama file: {file.name}")

        # Menampilkan dataframe
        st.write(df)
