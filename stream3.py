import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import streamlit as st

# Sample data with numeric columns for gradient application
data = {
    "Name": ["John", "Alice", "Bob", "Eve"],
    "January 2024": [1000, 1200, 1100, 1050],
    "February 2024": [1050, 1150, 1080, 1000]
}
df = pd.DataFrame(data)

# Create grid options
gb = GridOptionsBuilder.from_dataframe(df)

# Render the grid with the styled DataFrame
AgGrid(styled_df, gridOptions=gb.build())
