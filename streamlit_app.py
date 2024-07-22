# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
import streamlit.components.v1 as components

# Write directly to the app
st.title("Drift Detection Reports")

# Get the current credentials
session = get_active_session()

# Get available reports
files = session.sql('LS @SIMPLE_ML_DB.SIMPLE_ML_SCHEMA.MONITORING').collect()
files = [file['name'] for file in files]
report_selection = st.selectbox('Select Report File:', files)

@st.cache_data
def get_report():
    file = session.file.get_stream(f'@SIMPLE_ML_DB.SIMPLE_ML_SCHEMA.{report_selection}').read()
    
    # Convert bytes to string
    html_content = file.decode('utf-8')
    return html_content

report = get_report()
components.html(report, width=1000, height=1200, scrolling=True)