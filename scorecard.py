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
        
        
        
def get_distributor_data():
    query = """SELECT distinct distributor_code , distributor_name from pathway.distributor_report"""
    return load_data_from_db(query)['distributor_name'].tolist()
 
def get_all_data(selected_rs_name=None):
    if selected_rs_name:
        query = f"""SELECT * from pathway.distributor_report where distributor_name = '{selected_rs_name}'"""
    else:
        query = """SELECT * FROM pathway.distributor_report"""
    return load_data_from_db(query)
 
def get_cluster_data():
    query = """SELECT distinct cluster from pathway.distributor_report """
    return load_data_from_db(query)['cluster'].tolist()
 
def get_all_data_cluster(selected_cluster=None):
    if selected_cluster:
        query = f"""SELECT * from pathway.distributor_report where cluster = '{selected_cluster}'"""
    else:
        query = """SELECT * FROM pathway.distributor_report"""
    return load_data_from_db(query)
 
def get_district_data():
    query = """SELECT distinct rs_district from pathway.distributor_report """
    return load_data_from_db(query)['rs_district'].tolist()
 
def get_all_data_district(selected_district=None):
    if selected_district:
        query = f"""SELECT * from pathway.distributor_report where rs_district = '{selected_district}'"""
    else:
        query = """SELECT * FROM pathway.distributor_report"""
    return load_data_from_db(query)
 


def render_score_card():
    render_header()
    st.title("🌐 Score Card Data")
    image_path = r'C:\Users\CITPL\Desktop\streamlit project\image\citpl2.png'
    st.sidebar.image(image_path, caption="Survey Analytics")
 
    filter_option = st.sidebar.radio(
        "Select a filter option:",
        ("By Distributor", "By Cluster", "By District")
    )
       
    if filter_option == "By Distributor":
        try:
            distributors = get_distributor_data()
            selected_rs_name = st.sidebar.selectbox("Distributor Name", distributors, index=None, placeholder="Select a Distributor Name")
 
            if selected_rs_name:
                data = get_all_data(selected_rs_name)
                if data.empty:
                    st.info("No data available for the selected distributor.")
                else:
                    st.dataframe(data)
            else:
                all_data = get_all_data()
                if all_data.empty:
                    st.info("No data available for any distributor.")
                else:
                    st.dataframe(all_data)
               
        except Exception as e:
            st.error(f"Error fetching data: {e}")
 
    elif filter_option == "By Cluster":
        try:
            cluster = get_cluster_data()
            selected_cluster = st.sidebar.selectbox("Cluster Name", cluster, index=None, placeholder="Select a Cluster Name")
 
            if selected_cluster:
                data = get_all_data_cluster(selected_cluster)
                if data.empty:
                    st.info("No data available for the selected distributor.")
                else:
                    st.dataframe(data)
            else:
                all_data = get_all_data_cluster()
                if all_data.empty:
                    st.info("No data available for any distributor.")
                else:
                    st.dataframe(all_data)
                   
        except Exception as e:
            st.error(f"Error fetching data: {e}")
           
    elif filter_option == "By District":
        try:
            district = get_district_data()
            selected_district = st.sidebar.selectbox("District Name", district, index=None, placeholder="Select a District Name")
 
            if selected_district:
                data = get_all_data_district(selected_district)
                if data.empty:
                    st.info("No data available for the selected distributor.")
                else:
                    st.dataframe(data)
            else:
                all_data = get_all_data_district()
                if all_data.empty:
                    st.info("No data available for any distributor.")
                else:
                    st.dataframe(all_data)
        except Exception as e:
            st.error(f"Error fetching data: {e}")