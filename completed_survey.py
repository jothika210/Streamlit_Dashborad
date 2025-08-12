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




def render_completed_survey_page():
        render_header()
        image_path = r'C:\Users\CITPL\Desktop\streamlit project\image\citpl2.png'
        st.sidebar.image(image_path, caption="Survey Analytics")
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
        st.subheader("Completed Survey data")
     
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
   
        completed_df = load_data_from_db(completed_query)
       
 
        completed_rs_names = completed_df['rs_name'].unique().tolist()
       
        selected_rs_name = st.sidebar.selectbox("Distributor Name", completed_rs_names, index=None, placeholder="Select the Distributor Name")
 
        if selected_rs_name:
            distributor_query = f"""
            SELECT DISTINCT sh.cluster, sh.rs_name, sh.rs_code, sh.asm_emp_id,
                sh.asm_name, sh.rs_district, rs.userid, sh.sm_name, sh.sm_number, sh.route_name, 
                rs.survey_submitted_id, rs.survey_submittedon, ud.username
                FROM pathway.response_summary rs
                LEFT JOIN pathway.salesHierarchy sh ON rs.rs_code = sh.rs_code
                LEFT JOIN pathway.response rp ON rs.survey_submitted_id = rp.survey_submitted_id
                LEFT JOIN pathway.response_image ri ON rs.survey_submitted_id = ri.survey_submitted_id
                LEFT JOIN pathway.user_data ud ON rs.userid = ud.empcode
                WHERE rp.q_id in(9,11,13,16) AND sh.rs_name = '{selected_rs_name}'
                """
            distributor_df = load_data_from_db(distributor_query)
 
            if not distributor_df.empty:
                salesman_list = distributor_df['sm_name'].dropna().unique().tolist()
                selected_sm_name = st.sidebar.selectbox("Salesman Name", salesman_list, index=None, placeholder="Select the Salesman Name")
 
                if selected_sm_name:
                    filtered_df = distributor_df[distributor_df['sm_name'] == selected_sm_name]
 
                    route_list = filtered_df['route_name'].dropna().unique().tolist()
                    selected_route_name = st.sidebar.selectbox("Route Name", route_list, index=None, placeholder="Select the Route Name")
 
                    if selected_route_name:
                        final_filtered_df = filtered_df[filtered_df['route_name'] == selected_route_name]
                    else:
                        final_filtered_df = filtered_df
 
                    salesman_query = f"""
                    SELECT sh.rs_name, sh.sm_name, sh.route_name, sh.outlet_code, sh.outlet_name, sh.outlet_type, sh.outlet_latitude , sh.outlet_longitude
                    FROM pathway.response_summary rs
                    LEFT JOIN pathway.salesHierarchy sh ON rs.rs_code = sh.rs_code
                    LEFT JOIN pathway.response rp ON rs.survey_submitted_id = rp.survey_submitted_id
                    LEFT JOIN pathway.response_image ri ON rs.survey_submitted_id = ri.survey_submitted_id
                    LEFT JOIN pathway.user_data ud ON rs.userid = ud.empcode
                    WHERE rp.q_id in(9,11,13,16) AND sh.rs_name = '{selected_rs_name}' AND sh.sm_name = '{selected_sm_name}'
                    """
                    additional_columns_df = load_data_from_db(salesman_query)
                    final_filtered_df = pd.merge(final_filtered_df, additional_columns_df, on=['rs_name', 'sm_name', 'route_name'], how='left')
 
                else:
                    final_filtered_df = distributor_df
 
                st.write(f"**Data for Distributor: {selected_rs_name}**")
                total_records = len(final_filtered_df)
                st.write(f"Total Records: {total_records}")
                st.dataframe(final_filtered_df)
            else:
                st.write("No data found for the selected Distributor.")
        else:
            st.write("**Please select the Distributor Name**")


def render_completed_survey_page1():
    render_header()

    image_path = r'C:\Users\CITPL\Desktop\streamlit project\image\citpl2.png'
    st.sidebar.image(image_path, caption="Survey Analytics")

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

    st.subheader("Completed Survey Data")

    completed_query1 = """
        SELECT DISTINCT sh.sm_name,rs.sm_number
        FROM pathway.response_summary rs
        LEFT JOIN pathway.response r ON rs.survey_submitted_id = r.survey_submitted_id
        LEFT JOIN pathway.response_image ri ON r.survey_submitted_id = ri.survey_submitted_id
        LEFT JOIN pathway.user_data ud ON rs.userid = ud.empcode
        LEFT JOIN pathway.saleshierarchy sh 
        ON rs.rs_code = sh.rs_code AND rs.asm_code = sh.asm_emp_id AND rs.sm_number = sh.sm_number 
        WHERE r.q_id IN (35) AND rs.sm_number IS NOT NULL
    """

    completed_df = load_data_from_db(completed_query1)

    if not completed_df.empty:
        completed_df = completed_df.loc[:, ~completed_df.columns.duplicated()]

    if not completed_df.empty and 'sm_name' in completed_df.columns:
        completed_sm_names = completed_df['sm_name'].unique().tolist()
    else:
        completed_sm_names = []

    selected_sm_name = st.sidebar.selectbox("Salesman Name", completed_sm_names, index=None, placeholder="Select the Salesman")

    if selected_sm_name :
        salesman_query = f"""
            SELECT DISTINCT sh.sm_name,sh.sm_number, sh.cluster, sh.rs_name, sh.rs_code, sh.asm_emp_id,
            sh.asm_name, sh.rs_district, rs.userid,  sh.route_name,
            rs.survey_submitted_id, rs.survey_submittedon, ud.username
            FROM pathway.response_summary rs
            LEFT JOIN pathway.response r ON rs.survey_submitted_id = r.survey_submitted_id
            LEFT JOIN pathway.response_image ri ON r.survey_submitted_id = ri.survey_submitted_id
            LEFT JOIN pathway.user_data ud ON rs.userid = ud.empcode
            LEFT JOIN pathway.saleshierarchy sh 
            ON rs.rs_code = sh.rs_code AND rs.asm_code = sh.asm_emp_id AND rs.sm_number = sh.sm_number 
            WHERE r.q_id IN (35) AND rs.sm_number IS NOT NULL AND sh.sm_name = '{selected_sm_name}'
        """
        salesman_df = load_data_from_db(salesman_query)

        if not salesman_df.empty:
            salesman_df = salesman_df.loc[:, ~salesman_df.columns.duplicated()]

            route_list = salesman_df['route_name'].dropna().unique().tolist()
            selected_route_name = st.sidebar.selectbox("Route Name",  route_list, index=None, placeholder="Select the Routename")

            if selected_route_name:
                final_filtered_df = salesman_df[salesman_df['route_name'] == selected_route_name]
            else:
                final_filtered_df = salesman_df

            additional_query = f"""
                SELECT sh.rs_name, sh.sm_name, sh.route_name, sh.outlet_code, sh.outlet_name, 
                sh.outlet_type, sh.outlet_latitude, sh.outlet_longitude
                FROM pathway.response_summary rs
                LEFT JOIN pathway.response r ON rs.survey_submitted_id = r.survey_submitted_id
                LEFT JOIN pathway.response_image ri ON r.survey_submitted_id = ri.survey_submitted_id
                LEFT JOIN pathway.user_data ud ON rs.userid = ud.empcode
                LEFT JOIN pathway.saleshierarchy sh 
                ON rs.rs_code = sh.rs_code AND rs.asm_code = sh.asm_emp_id AND rs.sm_number = sh.sm_number 
                WHERE r.q_id IN (35) AND rs.sm_number IS NOT NULL AND sh.sm_name = '{selected_sm_name}' 
            """
            additional_columns_df = load_data_from_db(additional_query)

            if not additional_columns_df.empty:
                additional_columns_df = additional_columns_df.loc[:, ~additional_columns_df.columns.duplicated()]

                final_filtered_df = pd.merge(
                    final_filtered_df, additional_columns_df, 
                    on=['rs_name', 'sm_name', 'route_name'], how='left'
                )

            st.write(f"**Data for Salesman: {selected_sm_name}**")
            total_records = len(final_filtered_df)
            st.write(f"Total Records: {total_records}")
            st.dataframe(final_filtered_df)
        else:
            st.write("No data found for the selected Salesman.")
    else:
        st.write("**Please select a valid Salesman Name**")
