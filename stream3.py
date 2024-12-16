import pandas as pd
from st_aggrid import AgGrid
import streamlit as st

# Sample data with numeric columns for gradient application
data = {
    "Name": ["John", "Alice", "Bob", "Eve"],
    "January 2024": [1000, 1200, 1100, 1050],
    "February 2024": [1050, 1150, 1080, 1000]
}
df = pd.DataFrame(data)

# Apply background gradient to numeric columns
st.write("Sample AgGrid with Background Gradient:")
AgGrid(df.style.background_gradient(cmap='Blues', subset=["January 2024", "February 2024"]))
