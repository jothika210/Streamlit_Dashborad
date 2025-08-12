import streamlit as st
import sqlalchemy
from sqlalchemy.engine import URL
import pandas as pd
from base64 import b64encode
import warnings
import plotly.express as px
import plotly.graph_objects as go
import branca.colormap as cm
import folium
from streamlit_folium import folium_static
import geopandas as gpd
import numpy as np
import time


st.set_page_config(layout="wide", page_title="Dashboard", page_icon="📊")

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*experimental_get_query_params.*")

from total_surveys import render_total_surveys_page, render_total_surveys_page1
from completed_survey import render_completed_survey_page, render_completed_survey_page1
from pending_surveys import render_pending_surveys_page, render_pending_surveys_page1
from distributor_page import display_distributor_section
from salesman_page import display_salesman_section
from distributor_dashboard import distributor_dashboard
from salesman_dashboard import salesman_dashboard
from scorecard import render_score_card
from header import render_header

def get_base64_image(image_path):
    with open(image_path, "rb") as file:
        return b64encode(file.read()).decode()

config = {
    "UID": "pathway_app_user",
    "PASSWORD": "999999999",
    "SERVER": "database.net",
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
        
def load_geojson():
    geojson_path = r"C:\Users\CITPL\Desktop\Stremlit !\india_district (1).geojson"
    return gpd.read_file(geojson_path)

def get_district_data():
    completed_query = """
    SELECT sh.rs_district AS district, COUNT(DISTINCT sh.rs_name) AS response_count
    FROM pathway.response_summary rs
    LEFT JOIN pathway.salesHierarchy sh ON rs.rs_code = sh.rs_code
    LEFT JOIN pathway.response rp ON rs.survey_submitted_id = rp.survey_submitted_id
    LEFT JOIN pathway.response_image ri ON rs.survey_submitted_id = ri.survey_submitted_id
    LEFT JOIN pathway.user_data ud ON rs.userid = ud.empcode
    WHERE rp.q_id IN (9, 11, 13, 16)
    GROUP BY sh.rs_district
    """
    return load_data_from_db(completed_query)


def get_distributor_data(selected_district, from_date, to_date):
    from_date_str = from_date.strftime('%Y-%m-%d') if from_date else '1900-01-01'
    to_date_str = to_date.strftime('%Y-%m-%d') if to_date else '2100-12-31'

    data = f"""
    SELECT sh.rs_district AS district, sh.rs_name AS distributor_name, COUNT(DISTINCT rs.survey_submitted_id) AS survey_completed
    FROM pathway.response_summary rs
    LEFT JOIN pathway.salesHierarchy sh ON rs.rs_code = sh.rs_code
    LEFT JOIN pathway.response rp ON rs.survey_submitted_id = rp.survey_submitted_id
    LEFT JOIN pathway.response_image ri ON rs.survey_submitted_id = ri.survey_submitted_id
    LEFT JOIN pathway.user_data ud ON rs.userid = ud.empcode
    WHERE rp.q_id IN (9, 11, 13, 16)
    AND sh.rs_district = '{selected_district}'  
    AND rs.survey_submittedon BETWEEN '{from_date_str}' AND '{to_date_str}'  
    GROUP BY sh.rs_district, sh.rs_name
    """
    
    df = load_data_from_db(data)
    return df


def render_dashboard():
    render_header()
    if "map_rendered" not in st.session_state:
        st.session_state.map_rendered = False
        st.session_state.map_object = None
        
    def render_map():
        st.subheader("District-wise Distributor Data")
        gdf = load_geojson()
        district_data = get_district_data()
        gdf = gdf.merge(district_data, left_on="NAME_2", right_on="district", how="left")
        gdf["response_count"] = gdf["response_count"].fillna(0)
        colormap = cm.LinearColormap(
            colors=["lightblue", "darkgreen"],
            vmin=1,
            vmax=gdf["response_count"].max(),
        )
        m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
        
        
        with st.spinner("Loading map..."):
            folium.GeoJson(
                gdf,
                name="districts",
                tooltip=folium.features.GeoJsonTooltip(
                    fields=["NAME_2", "response_count"], aliases=["District", "Distributor Count"]
                ),
                style_function=lambda feature: {
                    "fillColor": colormap(feature["properties"]["response_count"])
                    if feature["properties"]["response_count"] > 0
                    else "transparent",
                    "color": "grey",
                    "weight": 1,
                    "fillOpacity": 0.8 if feature["properties"]["response_count"] > 0 else 0,
                },
            ).add_to(m)
            colormap.caption = "Distributor Count"
            colormap.add_to(m)  
        st.session_state.map_object = m
        st.session_state.map_rendered = True
        folium_static(m, width=500, height=350)
        
        
    def render_data_analysis():
        st.subheader("Data Analysis")
        district_list = get_district_data()
        col1, col2, col3 = st.columns([2, 2, 2])  
        with col1:
            selected_district = st.selectbox("Select District", district_list, index=None, placeholder="select the district name")
        with col2:
            from_date = st.date_input("From Date", key="from_date", value=None)
        with col3:
            to_date = st.date_input("To Date", key="to_date", value=None)
        with st.container():
            
            if selected_district:
                distributor_data = get_distributor_data(selected_district, from_date, to_date)
                if not distributor_data.empty:
                    fig = px.bar(
                        distributor_data,
                        x="distributor_name",
                        y="survey_completed",
                        labels={"distributor_name": "Distributor", "survey_completed": "Surveys Completed"},
                        title=f"Survey Completion in {selected_district}",
                        color="survey_completed",
                        color_continuous_scale="Blues",
                    )
                    fig.update_layout(
                            height=400,  
                            width=600,   
                            xaxis=dict(
                                tickmode='linear', 
                                tick0=1,           
                                dtick=1,           
                                range=[0, 5]       
                            ),
                            yaxis=dict(
                                tickmode='linear',  
                                tick0=1,           
                                dtick=1,          
                                range=[0, 5]   
                            )
                        )
 
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No data available for this district.")
                    empty_chart = px.bar(pd.DataFrame(columns=["distributor_name", "survey_completed"]), x="distributor_name", y="survey_completed")
                    empty_chart.update_layout(height=300, width=600,)
                    st.plotly_chart(empty_chart, use_container_width=True)
            else:
                empty_chart = px.bar(pd.DataFrame(columns=["distributor_name", "survey_completed"]), x="distributor_name", y="survey_completed")
                empty_chart.update_layout(height=300, width=600,)
                st.plotly_chart(empty_chart, use_container_width=True)
            
    col1, col2 = st.columns([1, 1])  
    with col1:
        if not st.session_state.map_rendered:
            render_map()
        else:
            st.subheader("District-wise Distributor Data")
            folium_static(st.session_state.map_object,width=500, height=350)
    
    with col2:
        render_data_analysis()
        
        
    query = """
    SELECT rp.q_id, rp.q_name, rp.ans
    FROM pathway.response rp
    WHERE rp.q_id IN (9, 11, 13, 16)
    """

    df = load_data_from_db(query)

    def get_q_id():
        if df.empty:
            st.warning("No data found for the selected survey questions.")
        else:
            st.markdown(
                """
                <style>
                .custom-card {
                    background-color: #f0f0f0;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
                    margin-bottom: 20px;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            col1, col2, col3, col4 = st.columns(4)

            def animate_bar_chart(data, title, color):
                placeholder = st.empty()  
                steps = 20  
                max_y = max(data.values) if not data.empty else 1  

                for i in np.linspace(0, 1, steps):  
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=data.index,
                        y=data.values * i,  
                        marker=dict(color=color)
                    ))

                    fig.update_layout(
                        title=title,
                        xaxis_title="Response",
                        yaxis_title="Count",
                        showlegend=False
                    )

                    placeholder.plotly_chart(fig, use_container_width=True)
                    time.sleep(0.05)  

            with col1:
                hygiene_dist = df[df["q_id"] == 9]["ans"].value_counts()
                animate_bar_chart(hygiene_dist, "Godown Hygiene & Upkeep", "steelblue")

            with col2:
                stacking_dist = df[df["q_id"] == 11]["ans"].value_counts()
                animate_bar_chart(stacking_dist, "Stacking Norms Followed", "seagreen")

            with col3:
                fifo_dist = df[df["q_id"] == 13]["ans"].value_counts()
                animate_bar_chart(fifo_dist, "Stock Rotation (FIFO) Followed", "tomato")

            with col4:
                tat_dist = df[df["q_id"] == 16]["ans"].value_counts()
                animate_bar_chart(tat_dist, "Delivery TAT Followed", "goldenrod")

    get_q_id()
        

def page_redirect():
    action = st.query_params.get_all('action')
    if not action:
        action = ['dashboard']
         
    with st.container():
        if action[0] == 'Distributor':
            display_distributor_section()
        elif action[0] == 'Salesman':
            display_salesman_section()
        elif action[0] == 'distributor_dashboard':
            distributor_dashboard()
        elif action[0] == 'salesman_dashboard':
            salesman_dashboard()
        elif action[0] == 'scorecard':
            render_score_card()
        elif action[0] == "completed_survey":
            render_completed_survey_page()  
        elif action[0] == "total_surveys":
            render_total_surveys_page()
        elif action[0] == "pending_surveys":
            render_pending_surveys_page()
        elif action[0] == "completed_survey1":
            render_completed_survey_page1()  
        elif action[0] == "total_surveys1":
            render_total_surveys_page1()
        elif action[0] == "pending_surveys1":
            render_pending_surveys_page1()
        else:
            render_dashboard()

if __name__ == "__main__":
    with st.container():
        page_redirect()

