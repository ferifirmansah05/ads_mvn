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
    # Create a gradient color from blue to red
    color = f"rgb({int(255 * normalized_value)}, 0, {int(255 * (1 - normalized_value))})"
    return f"background-color: {color};"

# Apply background gradient to numeric columns
st.write("Sample AgGrid with Background Gradient:")

# Create a new DataFrame for styling
styled_df = df.copy()

# Apply gradient style to numeric columns
for column in df.columns[1:]:  # Skip the 'Name' column
    min_value = df[column].min()
    max_value = df[column].max()
    styled_df[column] = styled_df[column].apply(lambda x: gradient_style(x, min_value, max_value))

# Create grid options
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column("Name", cellStyle={"backgroundColor": "white"})  # Keep Name column white
for column in df.columns[1:]:
    gb.configure_column(column, cellStyle={"backgroundColor": "white"})  # Set other columns to white

# Render the grid with the styled DataFrame
AgGrid(styled_df, gridOptions=gb.build(), enable_enterprise_modules=True)
