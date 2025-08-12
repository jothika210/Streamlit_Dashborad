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
    
def render_pending_surveys_page():
    render_header()
    image_path = r'C:\Users\CITPL\Desktop\streamlit project\image\citpl2.png'
    st.sidebar.image(image_path, caption="Survey Analytics")
    st.subheader("Pending Survey Data")

    st.markdown(
        """
        <style>
            #MainMenu {visibility: hidden;}  /* Hide Streamlit menu */
            footer {visibility: hidden;}     /* Hide footer */
            header {visibility: hidden;}
            .main-content {
                margin-top: 0px;  
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    completed_query = """
       SELECT DISTINCT sh.cluster, sh.rs_name, sh.rs_code, sh.asm_emp_id,
                        sh.asm_name, sh.rs_district, rs.userid,
                        rs.survey_submitted_id, rs.survey_submittedon, ud.username
       FROM pathway.response_summary rs
       LEFT JOIN pathway.salesHierarchy sh ON rs.rs_code = sh.rs_code
       LEFT JOIN pathway.response rp ON rs.survey_submitted_id = rp.survey_submitted_id
       LEFT JOIN pathway.response_image ri ON rs.survey_submitted_id = ri.survey_submitted_id
       LEFT JOIN pathway.user_data ud ON rs.userid = ud.empcode
       WHERE rp.q_id in(9,11,13,16) 
    """

    total_query = """
        SELECT DISTINCT rs_name, rs_code, rs_district
        FROM pathway.salesHierarchy
    """

    completed_df = load_data_from_db(completed_query)
    total_df = load_data_from_db(total_query)

    pending_df = total_df[~total_df["rs_code"].isin(completed_df["rs_code"])]

    districts = pending_df["rs_district"].unique().tolist()
    selected_district = st.sidebar.selectbox(
        "Select District", districts, index=None, placeholder="Select a District"
    )

    if selected_district:
        district_filtered_df = pending_df[pending_df["rs_district"] == selected_district]

        st.write(f"**Pending Data for District: {selected_district}**")
        st.dataframe(district_filtered_df)

        pending_rs_names = district_filtered_df["rs_name"].tolist()
        
        pending_count = len(pending_rs_names)
        st.write(f"Total Records: {pending_count}")
        
        selected_pending_rs_name = st.sidebar.selectbox(
            "Select Distributor Name",
            pending_rs_names,
            index=None,
            placeholder="Select the Distributor Name"
        )

        if selected_pending_rs_name:
            filtered_pending_df = district_filtered_df[district_filtered_df['rs_name'] == selected_pending_rs_name]
            st.write(f"**Pending Data for Distributor: {selected_pending_rs_name}**")
            st.dataframe(filtered_pending_df)
    else:
        st.write("**Please select a District**")



def render_pending_surveys_page1():
    render_header()
    image_path = r'C:\Users\CITPL\Desktop\streamlit project\image\citpl2.png'
    st.sidebar.image(image_path, caption="Survey Analytics")
    st.subheader("Pending Survey data")
    st.markdown(
        """
        <style>
            #MainMenu {visibility: hidden;}  /* Hide Streamlit menu */
            footer {visibility: hidden;}     /* Hide footer */
            header {visibility: hidden;}
            .main-content {
                margin-top: 0px;  
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
   
    completed_query = """
        SELECT DISTINCT sh.sm_name,rs.sm_number
        FROM pathway.response_summary rs
        LEFT JOIN pathway.response r ON rs.survey_submitted_id = r.survey_submitted_id
        LEFT JOIN pathway.response_image ri ON r.survey_submitted_id = ri.survey_submitted_id
        LEFT JOIN pathway.user_data ud ON rs.userid = ud.empcode
        LEFT JOIN pathway.saleshierarchy sh 
        ON rs.rs_code = sh.rs_code AND rs.asm_code = sh.asm_emp_id AND rs.sm_number = sh.sm_number 
        WHERE r.q_id IN (35) AND rs.sm_number IS NOT NULL
       """
    total_query = """
        select distinct sm_name,sm_number from pathway.salesHierarchy
       
    """  
    completed_df = load_data_from_db(completed_query)
    total_df = load_data_from_db(total_query)
 
    pending_df = total_df[~total_df["sm_name"].isin(completed_df["sm_name"])]
    pending_sm_names = pending_df["sm_name"].tolist()
       
    pending_count = len(pending_sm_names)
    st.write(f"Total Records: {pending_count}")
    selected_pending_sm_name = st.sidebar.selectbox(
        "Salesman Name",
        pending_sm_names,
        index=None,
        placeholder="Select the Salesman Name"
    )
       
    if selected_pending_sm_name:
            filtered_pending_df = pending_df[pending_df['sm_name'] == selected_pending_sm_name]
 
            st.write(f"**Pending Data for Salesman: {selected_pending_sm_name}**")
            st.dataframe(filtered_pending_df)
    else:
            st.write("**Please select the Salesman Name**")