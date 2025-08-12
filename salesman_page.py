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

def fetch_distinct_sm_names():
    query = """
        SELECT DISTINCT sh.sm_name
        FROM pathway.response_summary rs
        LEFT JOIN pathway.response r ON rs.survey_submitted_id = r.survey_submitted_id 
        LEFT JOIN pathway.response_image ri ON r.survey_submitted_id = ri.survey_submitted_id
        LEFT JOIN pathway.user_data ud ON rs.userid = ud.empcode
        LEFT JOIN pathway.saleshierarchy sh ON rs.rs_code = sh.rs_code AND rs.asm_code = sh.asm_emp_id AND rs.sm_number = sh.sm_number where r.q_id in (35) ANd rs.sm_number is not null
    """
    return load_data_from_db(query)['sm_name'].tolist()
 
def fetch_sales_hierarchy1(selected_sm_name):
    query = f"""
        SELECT DISTINCT sh.sm_name, rs.sm_number, sh.cluster, sh.rs_name, rs.rs_code, rs.asm_code,
                        sh.asm_name, sh.rs_district, rs.userid,
                        rs.survey_submitted_id, rs.survey_submittedon, ud.username
       FROM pathway.response_summary rs
        LEFT JOIN pathway.response r ON rs.survey_submitted_id = r.survey_submitted_id 
        LEFT JOIN pathway.response_image ri ON r.survey_submitted_id = ri.survey_submitted_id
        LEFT JOIN pathway.user_data ud ON rs.userid = ud.empcode
        LEFT JOIN pathway.saleshierarchy sh ON rs.rs_code = sh.rs_code AND rs.asm_code = sh.asm_emp_id AND rs.sm_number = sh.sm_number where r.q_id in (35) ANd rs.sm_number is not null AND sh.sm_name = '{selected_sm_name}'
    """
    return load_data_from_db(query)

def fetch_distinct_asm_names1():
    query = """
        SELECT DISTINCT sh.asm_name
       FROM pathway.response_summary rs
        LEFT JOIN pathway.response r ON rs.survey_submitted_id = r.survey_submitted_id 
        LEFT JOIN pathway.response_image ri ON r.survey_submitted_id = ri.survey_submitted_id
        LEFT JOIN pathway.user_data ud ON rs.userid = ud.empcode
        LEFT JOIN pathway.saleshierarchy sh ON rs.rs_code = sh.rs_code AND rs.asm_code = sh.asm_emp_id AND rs.sm_number = sh.sm_number where r.q_id in (35) ANd rs.sm_number is not null 
    """
    return load_data_from_db(query)['asm_name'].tolist()

def fetch_sales_hierarchy_by_asm1(selected_asm_name):
    query = f"""
        SELECT DISTINCT  sh.asm_name, rs.asm_code, sh.sm_name, rs.sm_number, sh.cluster, sh.rs_name, rs.rs_code, 
                sh.rs_district, rs.userid, rs.survey_submitted_id,
               rs.survey_submittedon, ud.username
                FROM pathway.response_summary rs
        LEFT JOIN pathway.response r ON rs.survey_submitted_id = r.survey_submitted_id 
        LEFT JOIN pathway.response_image ri ON r.survey_submitted_id = ri.survey_submitted_id
        LEFT JOIN pathway.user_data ud ON rs.userid = ud.empcode
        LEFT JOIN pathway.saleshierarchy sh ON rs.rs_code = sh.rs_code AND rs.asm_code = sh.asm_emp_id AND rs.sm_number = sh.sm_number where r.q_id in (35) ANd rs.sm_number is not null AND sh.asm_name = '{selected_asm_name}'
    """
    return load_data_from_db(query)

def fetch_response_details1(survey_submitted_id):
    query = f"SELECT userid, q_name, ans  FROM pathway.response  WHERE survey_submitted_id = '{survey_submitted_id}'"
    return load_data_from_db(query)
 
def fetch_matching_images1(survey_id, user_id):
    query = f"SELECT blob_storage_filename  FROM pathway.response_image WHERE survey_submitted_id = '{survey_id}' AND userid = '{user_id}'"
    return load_data_from_db(query)
 
def display_salesman_section():
    render_header()
    st.title("🌐 Salesman Data")
    image_path = r'C:\Users\CITPL\Desktop\streamlit project\image\citpl2.png'
    st.sidebar.image(image_path, caption="Survey Analytics")
 
    filter_method = st.sidebar.radio(
        "Choose filter",
        ("By Salesman Name", "By Cluster", "By ASM Name", "By Username")
    )
 
    if filter_method == "By Salesman Name":
        try:
            distinct_sm_names = fetch_distinct_sm_names()
            selected_sm_name = st.sidebar.selectbox("Salesman Name", distinct_sm_names, index=None, placeholder="Select a Salesman Name")
 
            if selected_sm_name:
                data = fetch_sales_hierarchy1(selected_sm_name)
 
                if not data.empty:
                    data['Select'] = False
                    columns_order = ['Select'] + [col for col in data.columns if col != 'Select']
                    data = data[columns_order]
 
                    selected_rows = st.data_editor(
                        data,
                        column_config={'Select': st.column_config.CheckboxColumn(label="Select")},
                        disabled=["cluster", "rs_name", "rs_code", "asm_emp_id", "asm_name", "rs_district", "survey_submitted_id", "survey_submittedon", "userid", "username"],
                        hide_index=True,
                    )
 
                    selected_ids = selected_rows[selected_rows['Select']].survey_submitted_id.tolist()
 
                    for survey_id in selected_ids:
                        details = fetch_response_details1(survey_id)
                        user_id = details['userid'].iloc[0]
                        username_query = f"SELECT username FROM pathway.user_data WHERE empcode = '{user_id}'"
                        username = load_data_from_db(username_query)['username'].iloc[0]
 
                        st.write(f"**Survey Details for {selected_sm_name} - {survey_id} ({username}):**")
 
                        if not details.empty:
                            matching_images = fetch_matching_images1(survey_id, user_id)
 
                            if not matching_images.empty:
                                image_links = []
                                for idx, row in matching_images.iterrows():
                                    blob_filename = row['blob_storage_filename']
                                    blob_filename_encoded = quote(blob_filename)
                                    file_link = (f"https://distributorkpi.cavininfotech.com/api/viewimage/"
                                                 f"Salesman/{blob_filename_encoded}")
                                    image_links.append(f"[Img {idx + 1}]({file_link})")
 
                                st.markdown(f"**Images:** {', '.join(image_links)}", unsafe_allow_html=True)
 
                            st.dataframe(details[['q_name', 'ans']])
                        else:
                            st.write("No matching details found.")
                else:
                    st.write("No data available for the selected distributor.")
            else:
                st.write("**Please Select the Distributor**")
 
        except Exception as e:
            st.error(f"Error fetching data: {e}")
 
    elif filter_method == "By Cluster":
        try:
            cluster_names_query = """
            SELECT DISTINCT  sh.cluster
                FROM pathway.response_summary rs
                LEFT JOIN pathway.response r ON rs.survey_submitted_id = r.survey_submitted_id 
                LEFT JOIN pathway.response_image ri ON r.survey_submitted_id = ri.survey_submitted_id
                LEFT JOIN pathway.user_data ud ON rs.userid = ud.empcode
                LEFT JOIN pathway.saleshierarchy sh ON rs.rs_code = sh.rs_code AND rs.asm_code = sh.asm_emp_id AND rs.sm_number = sh.sm_number where r.q_id in (35) ANd rs.sm_number is not null
                    """
            cluster_name_data = load_data_from_db(cluster_names_query)
            distinct_cluster_names = cluster_name_data['cluster'].tolist()
 
            selected_cluster_name = st.sidebar.selectbox(
                "Cluster Name",
                ["Select a Cluster"] + distinct_cluster_names,
                index=0
            )
 
            if selected_cluster_name != "Select a Cluster":
                query = f"""
                SELECT DISTINCT sh.cluster, sh.sm_name, rs.sm_number, sh.rs_name, rs.rs_code, rs.asm_code,
                       sh.asm_name, sh.rs_district, rs.userid, rs.survey_submitted_id,
                       rs.survey_submittedon, ud.username
                       FROM pathway.response_summary rs
                        LEFT JOIN pathway.response r ON rs.survey_submitted_id = r.survey_submitted_id 
                        LEFT JOIN pathway.response_image ri ON r.survey_submitted_id = ri.survey_submitted_id
                        LEFT JOIN pathway.user_data ud ON rs.userid = ud.empcode
                        LEFT JOIN pathway.saleshierarchy sh ON rs.rs_code = sh.rs_code AND rs.asm_code = sh.asm_emp_id AND rs.sm_number = sh.sm_number where r.q_id in (35) ANd rs.sm_number is not null AND sh.cluster = '{selected_cluster_name}'
                                """
                data = load_data_from_db(query)
                district_list = sorted(data['rs_district'].unique())
                selected_district = st.sidebar.selectbox(
                    "District",
                    ["All"] + district_list,
                    index=0
                )
 
                filtered_data = data.copy()
                if selected_district != "All":
                    filtered_data = filtered_data[filtered_data['rs_district'] == selected_district]
           
                if not filtered_data.empty:
                    filtered_data.reset_index(drop=True, inplace=True)
                    st.write("**Filtered Data Table**")
                    total_records = len(filtered_data)
                    st.write(f"Total Records: {total_records}")
                    st.dataframe(filtered_data)
                else:
                    st.write("No data available for selected filters")
            else:
                st.write("Please select a Cluster.")
        except Exception as e:
            st.error(f"Error fetching data: {e}")
 
    elif filter_method == "By ASM Name":
        try:
            asm_names = fetch_distinct_asm_names1()  
            selected_asm_name = st.sidebar.selectbox("ASM Name", asm_names, index=None, placeholder="Select an ASM Name")
 
            if selected_asm_name:
                data = fetch_sales_hierarchy_by_asm1(selected_asm_name)
                st.dataframe(data)
            else:
                st.write("Please select an ASM Name.")
        except Exception as e:
            st.error(f"Error fetching data: {e}")
 
    elif filter_method == "By Username":
        try:
            user_query = f"""
                SELECT DISTINCT  ud.username
                    FROM pathway.response_summary rs
                    LEFT JOIN pathway.response r ON rs.survey_submitted_id = r.survey_submitted_id 
                    LEFT JOIN pathway.response_image ri ON r.survey_submitted_id = ri.survey_submitted_id
                    LEFT JOIN pathway.user_data ud ON rs.userid = ud.empcode
                    LEFT JOIN pathway.saleshierarchy sh ON rs.rs_code = sh.rs_code AND rs.asm_code = sh.asm_emp_id AND rs.sm_number = sh.sm_number where r.q_id in (35) ANd rs.sm_number is not null """
            usernames = load_data_from_db(user_query)
            distinct_user_names = usernames['username'].tolist()
 
            selected_username = st.sidebar.selectbox(
                "Username", distinct_user_names,
                index=None,
                placeholder="Select a Username"
            )
 
            start_date = st.sidebar.date_input("Start Date", value=None)
            end_date = st.sidebar.date_input("End Date", value=None)
 
            if selected_username :
                query = f"""
                SELECT DISTINCT ud.username, rs.userid, sh.sm_name, rs.sm_number, sh.cluster, sh.rs_name, rs.rs_code, rs.asm_code,
                       sh.asm_name, sh.rs_district,  rs.survey_submitted_id,
                       rs.survey_submittedon
                       FROM pathway.response_summary rs
                        LEFT JOIN pathway.response r ON rs.survey_submitted_id = r.survey_submitted_id 
                        LEFT JOIN pathway.response_image ri ON r.survey_submitted_id = ri.survey_submitted_id
                        LEFT JOIN pathway.user_data ud ON rs.userid = ud.empcode
                        LEFT JOIN pathway.saleshierarchy sh ON rs.rs_code = sh.rs_code AND rs.asm_code = sh.asm_emp_id AND rs.sm_number = sh.sm_number where r.q_id in (35) ANd rs.sm_number is not null AND ud.username = '{selected_username}'
                        """
 
                if start_date and end_date:
                    if start_date > end_date:
                        st.error("End date must be greater than or equal to start date.")
                    else:
                        query += f"""
                        AND CAST(rs.survey_submittedon AS DATE)
                        BETWEEN '{start_date}' AND '{end_date}'
                    """
                        result_data = load_data_from_db(query)
 
                else:
                    result_data = load_data_from_db(query)
 
                if not result_data.empty:
                    st.write(f"**Data for Username: {selected_username}**")
                    total_records = len(result_data)
                    st.write(f"**Total Records: {total_records}**")
                    st.dataframe(result_data)
 
                    if start_date and end_date:
                        result_data['survey_submittedon'] = pd.to_datetime(result_data['survey_submittedon'])
                        date_wise_data = result_data.groupby(result_data['survey_submittedon'].dt.date).size()
                        st.write("**Date-Wise Survey Submissions**")
                        st.bar_chart(date_wise_data)
                else:
                    st.write("No data available for the selected username and/or date range.")
            else:
                st.write("**Please select a Username**")
        except Exception as e:
            st.error(f"Error fetching data: {e}")
         