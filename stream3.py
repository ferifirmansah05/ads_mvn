import streamlit as st
import plotly.express as px

# Data untuk grafik
df = pd.DataFrame({
    "Category": ["A", "B", "C", "D"],
    "Value": [10, 20, 30, 40]
})

fig = px.bar(df, x="Category", y="Value", title="Sample Bar Chart")
st.plotly_chart(fig)

# Menampilkan metrik di bawah grafik
st.metric(label="Total Sales", value="$40,000", delta="+15%")
