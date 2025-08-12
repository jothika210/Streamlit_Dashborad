import streamlit as st
import sqlalchemy
from sqlalchemy.engine import URL
import pandas as pd
from base64 import b64encode
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*experimental_get_query_params.*")
import streamlit.components.v1 as components
from header import render_header


def get_base64_image(image_path):
    with open(image_path, "rb") as file:
        return b64encode(file.read()).decode()

logo_path = r"C:\Users\CITPL\Desktop\streamlit project\image\citpl2.png"
logo_base64 = get_base64_image(logo_path)

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
        
def fetch_activity_data1():
    total_query = """
        SELECT DISTINCT sm_name,sm_number from pathway.salesHierarchy
    """
    total_data1 = load_data_from_db(total_query)
    total_count1 = len(total_data1)
 
    completed_query = """
    SELECT DISTINCT sh.sm_name,rs.sm_number
        FROM pathway.response_summary rs
        LEFT JOIN pathway.response r ON rs.survey_submitted_id = r.survey_submitted_id
        LEFT JOIN pathway.response_image ri ON r.survey_submitted_id = ri.survey_submitted_id
        LEFT JOIN pathway.user_data ud ON rs.userid = ud.empcode
        LEFT JOIN pathway.saleshierarchy sh ON rs.rs_code = sh.rs_code AND rs.asm_code = sh.asm_emp_id AND rs.sm_number = sh.sm_number where r.q_id in (35) ANd rs.sm_number is not null
    """
    completed_data1 = load_data_from_db(completed_query)
    completed_count1 = len(completed_data1)
 
    pending_count1 = total_count1 - completed_count1
    completion_percentage1 = (completed_count1 / total_count1) * 100 if total_count1 else 0
    pending_percentage1 = (pending_count1 / total_count1) * 100 if total_count1 else 0
    return total_count1, completed_count1, pending_count1, completion_percentage1, pending_percentage1
 
def generate_liquid_fill_chart1(total_count1, completed_count1, pending_count1):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/echarts/dist/echarts.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/echarts-liquidfill/dist/echarts-liquidfill.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>      
        .card-container {{
            display: flex;
            gap: 50px;
            margin: 30px auto;
            flex-wrap: wrap;
        }}
        .card {{
            display: flex;
            flex-direction: column;
            background: #1E293B;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
            width: 298px;
            padding: 15px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
        }}
        .header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
        }}
        .header h3 {{
            margin: 0;
            font-size: 16px;
            color: #E2E8F0;
            font-weight: bold;
        }}
        .header p {{
            margin: 0;
            font-size: 20px;
            color: #73B9EE;
            font-weight: bold;
        }}
        .icon {{
            font-size: 24px;
            color: #73B9EE;
            margin-right: 10px;
            animation: pulse 2s infinite;
        }}
        .chart-wrapper {{
            width: 120px;
            height: 120px;
            margin: 0 auto;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4);
        }}
        .button {{
            margin-top: 20px;
            padding: 10px 74px;
            background-color:#73B9EE;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            text-align: center;
        }}
        .button:hover {{
            background-color: #10B981;
        }}
        @keyframes pulse {{
            0% {{
                transform: scale(1);
            }}
            50% {{
                transform: scale(1.1);
            }}
            100% {{
                transform: scale(1);
            }}
        }}
    </style>
    </head>
    <body>
            <div class="card-container">
                <div class="card">
                    <div class="header">
                        <div style="display: flex; align-items: center;">
                            <i class="fa-solid fa-chart-pie icon"></i>
                            <h3>Total Surveys</h3>
                        </div>
                        <p>{total_count1}</p>
                    </div>
                    <div class="chart-wrapper" id="chart1"></div>
                </div>
                <div class="card">
                    <div class="header">
                        <div style="display: flex; align-items: center;">
                            <i class="fa-solid fa-check-circle icon" style="color: #10B981;"></i>
                            <h3>Completed Surveys</h3>
                        </div>
                        <p>{completed_count1}</p>
                    </div>
                    <div class="chart-wrapper" id="chart2"></div>
                   
                </div>
                <div class="card">
                    <div class="header">
                        <div style="display: flex; align-items: center;">
                            <i class="fa-solid fa-clock icon" style="color: #FCA746;"></i>
                            <h3>Pending Surveys</h3>
                        </div>
                        <p>{pending_count1}</p>
                    </div>
                    <div class="chart-wrapper" id="chart3"></div>
                   
                </div>
            </div>
       
        <script>
            var chart1 = echarts.init(document.getElementById('chart1'));
            var chart2 = echarts.init(document.getElementById('chart2'));
            var chart3 = echarts.init(document.getElementById('chart3'));
 
            function getLiquidOption(percentage, color) {{
                return {{
                    series: [{{
                        type: 'liquidFill',
                        data: [percentage / 100],
                        waveAnimation: true,
                        amplitude: 8,
                        radius: '90%',
                        color: [color],
                        outline: {{
                            show: true,
                            borderDistance: 5,
                            itemStyle: {{
                                borderWidth: 2,
                                borderColor: color
                            }}
                        }},
                        label: {{
                            normal: {{
                                formatter: function() {{
                                    return (percentage).toFixed(2) + '%';  // Properly display percentage
                                }},
                                textStyle: {{
                                    fontSize: 18,
                                    color: '#FFFFFF',
                                    fontWeight: 'bold'
                                }}
                            }}
                        }},
                        backgroundStyle: {{
                            color: '#334155'
                        }}
                    }}]
                }};
            }}
 
            chart1.setOption(getLiquidOption(100, '#73B9EE'));
            chart2.setOption(getLiquidOption({completed_count1 / total_count1 * 100}, '#10B981'));
            chart3.setOption(getLiquidOption({pending_count1 / total_count1 * 100}, '#FCA746'));
        </script>
    </body>
    </html>
    """
    return html_content
 
def display_button(title, color, action_url):
        st.markdown(
        f"""
        <form action="#" method="get">
            <button
                type="submit"
                style="
                    background-color: {color};
                    color: #FFFFFF;
                    padding: 8px 15px;
                    font-size: 16px;
                    border-radius: 5px;
                    border: none;
                    cursor: pointer;
                    width: 100%;
                "
                name="action"
                value="{action_url}">
                {title}
            </button>
        </form>
        """,
        unsafe_allow_html=True,
    )


def salesman_dashboard():
    render_header()
    total_count1, completed_count1, pending_count1, completion_percentage1, pending_percentage1 = fetch_activity_data1()
    completion_percentage1 = round(completion_percentage1, 2)
    pending_percentage1 = round(pending_percentage1, 2)
 
    st.title("Salesman Dashboard")
   
    col1, col2, col3 = st.columns(3)
 
    with col1:
        display_button(
            title="Total Surveys",
            color="#73B9EE",
            action_url="total_surveys1"
        )
    with col2:
        display_button(
            title="Completed Surveys",
            color="#10B981",
            action_url="completed_survey1"
        )
    with col3:
        display_button(
            title="Pending Surveys",
            color="#FCA746",
            action_url="pending_surveys1"
        )
   
    html_content = generate_liquid_fill_chart1(total_count1, completed_count1, pending_count1)

    components.html(html_content, height=400, width=1100)
