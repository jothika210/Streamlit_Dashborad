import streamlit as st
import streamlit as st
import sqlalchemy
from sqlalchemy.engine import URL
import pandas as pd
from urllib.parse import quote
from base64 import b64encode
from header import render_header



def get_base64_image(image_path):
    with open(image_path, "rb") as file:
        return b64encode(file.read()).decode()






config = {
    "UID": "pathway_app_user",
    "PASSWORD": "9x4@L4eXm",
    "SERVER": "citplcia.database.windows.net",
    "DATABASE": "mhauditapp"
}
 
connection_url = URL.create(
    "mssql+pyodbc",
    username=config.get("UID"),
    password=config.get("PASSWORD"),
    host=config.get("SERVER"),
    database=config.get("DATABASE"),
    query={"driver": "ODBC Driver 17 for SQL Server", "autocommit": "True"},
)
 
engine = sqlalchemy.create_engine(
    connection_url, pool_size=0, pool_pre_ping=True, pool_recycle=3600
).execution_options(isolation_level="AUTOCOMMIT")
 
@st.cache_data(show_spinner=False)
def load_data_from_db(query):
    with st.spinner("Loading data...Please Wait"):
        with engine.connect() as conn:
            return pd.read_sql(query, conn)
   

def render_total_surveys_page():
    render_header()
    image_path = r'C:\Users\CITPL\Desktop\streamlit project\image\citpl2.png'
    st.sidebar.image(image_path, caption="Survey Analytics")
    st.subheader("Total Survey Data")
    st.markdown(
        """
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}    
            header {visibility: hidden;}
            .main-content {
                margin-top: 0px;  
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
 
    total_query = """
        SELECT DISTINCT rs_name, rs_code
        FROM pathway.salesHierarchy
    """
    total_df = load_data_from_db(total_query)
   
    if total_df.empty:
        st.write("No data available.")
        return
   
    total_rs_names = total_df['rs_name'].dropna().unique().tolist()
   
    total1_rs_names = st.sidebar.selectbox(
        "Distributor Name",
        options=["Select Distributor"] + total_rs_names,
        index=0,
        key="total_survey_distributor"
    )
   
    if total1_rs_names != "Select Distributor":
 
        filtered_total_df = total_df[total_df['rs_name'] == total1_rs_names]
       
        details_query = f"""
            SELECT rs_name, rs_code, cluster, asm_emp_id, asm_name, sm_name, sm_number, route_name, outlet_name, outlet_code, outlet_type, rs_district
            FROM pathway.salesHierarchy
            WHERE rs_name = '{total1_rs_names}'
        """
        details_df = load_data_from_db(details_query)
       
        detailed_filtered_df = pd.merge(
            filtered_total_df,
            details_df,
            on=['rs_name', 'rs_code'],
            how='left'
        )
       
        st.write(f"**Data for Distributor: {total1_rs_names}**")
        st.dataframe(detailed_filtered_df)
    else:
        st.write("**Please select a valid Distributor Name.**")


def render_total_surveys_page1():
    render_header()
    image_path = r'C:\Users\CITPL\Desktop\streamlit project\image\citpl2.png'
    st.sidebar.image(image_path, caption="Survey Analytics")
    st.subheader("Total Survey Data")
    st.markdown(
        """
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}    
            header {visibility: hidden;}
            .main-content {
                margin-top: 0px;  
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
 
    total_query = """
        select distinct sm_name,sm_number from pathway.salesHierarchy
    """
    total_df = load_data_from_db(total_query)
   
    if total_df.empty:
        st.write("No data available.")
        return
   
    total_sm_names = total_df['sm_name'].dropna().unique().tolist()
   
    total1_sm_names = st.sidebar.selectbox(
        "Salesman Name",
        options=["Select Salesman"] + total_sm_names,
        index=0,
        key="total_survey_salesman"
    )
   
    if total1_sm_names != "Select Salesman":
 
        filtered_total_df = total_df[total_df['sm_name'] == total1_sm_names]
       
        details_query = f"""
            SELECT rs_name, rs_code, cluster, asm_emp_id, asm_name, sm_name, sm_number, route_name, outlet_name, outlet_code, outlet_type, rs_district
            FROM pathway.salesHierarchy
            WHERE sm_name = '{total1_sm_names}'
        """
        details_df = load_data_from_db(details_query)
       
        detailed_filtered_df = pd.merge(
            filtered_total_df,
            details_df,
            on=['sm_name', 'sm_number'],
            how='left'
        )
       
        st.write(f"**Data for Salesman: {total1_sm_names}**")
        st.dataframe(detailed_filtered_df)
    else:
        st.write("**Please select a valid Salesman Name.**")