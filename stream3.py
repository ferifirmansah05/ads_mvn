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

# Function to create a gradient style
def gradient_style(value, min_value, max_value):
    # Normalize the value to a range between 0 and 1
    normalized_value = (value - min_value) / (max_value - min_value)
    # Create a gradient color from white to red
    color = f"rgb({int(255 * normalized_value)}, 0, 0)"
    return f"background-color: {color};"

# Create grid options
gb = GridOptionsBuilder.from_dataframe(df)

# Apply gradient style to numeric columns
for column in df.columns[1:]:  # Skip the 'Name' column
    min_value = df[column].min()
    max_value = df[column].max()
    # Set cell style for each numeric column
    gb.configure_column(column, cellStyle=lambda value: gradient_style(value, min_value, max_value))

# Render the grid with the styled DataFrame
AgGrid(df, gridOptions=gb.build())
