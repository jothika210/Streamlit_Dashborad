import streamlit as st
from base64 import b64encode


def get_base64_image(image_path):
    with open(image_path, "rb") as file:
        return b64encode(file.read()).decode()

logo_path = r"C:\Users\CITPL\Desktop\streamlit project\image\citpl2.png"  
logo_base64 = get_base64_image(logo_path)

score_path = r"C:\Users\CITPL\Desktop\Stremlit !\score_card_icon.jpg"
scorecard_image_base64 = get_base64_image(score_path)


def render_header():
    st.markdown(
        f"""
        <div class="custom-top-header">
            <div class="header-left">
                <img src="data:image/png;base64,{logo_base64}" alt="Logo">
                <span><b>Survey Analytics</b></span>
            </div>
            <div class="header-right">
                <form action="#" method="get">
                    <button class="header-image-button" name="action" value="scorecard" title="Score Card">
                        <img src="data:image/png;base64,{scorecard_image_base64}" alt="Score Card">
                    </button>
                    <div class="dropdown">
                        <button class="header-button dropdown-button">Dashboard</button>
                            <div class="dropdown-content">
                                <form action="#" method="get">
                                    <button class="dropdown-link" type="submit" name="action" value="distributor_dashboard">Distributor Dashboard </button>
                                </form>
                                <form action="#" method="get">
                                    <button class="dropdown-link" type="submit" name="action" value="salesman_dashboard">Salesman Dashboard </button>
                                </form>
                            </div>
                    </div>
                    <form action="#" method="get">
                        <button class="header-button" type="submit" name="action" value="Distributor">Distributor</button>
                        <button class="header-button" type="submit" name="action" value="Salesman">Salesman</button>
                    </form>
                </form>
            </div>
        </div>
        <div class="main-content">
        """,
        unsafe_allow_html=True,
    )
   
    st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}  /* Hide Streamlit menu */
        footer {visibility: hidden;}     /* Hide footer */
        header {visibility: hidden;}     /* Hide header */
       .stSidebar {
            background: #219ebc;/* Gradient from top to bottom */
        }
        .custom-top-header {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background: #219ebc;
            color: white;
            padding: 10px 20px;
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .header-left {
            display: flex;
            align-items: center;
        }
        .header-left img {
            height: 40px;
            margin-right: 10px;
        }
        .header-right {
            display: flex;
            gap: 4px;
        }
        .header-button, .dropdown-link{
            background-color: white;
            color: #219ebc;
            border: none;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold
        }
        .header-button:hover, .dropdown-link:hover {
            background-color: #f1f1f1;
        }
        .header-image-button {
            background-color: transparent;
            border: none;
            cursor: pointer;
            padding: 0;
            margin: 0;
        }
        .header-image-button img {
            height: 40px;
            width: 40px;
            border-radius: 4px;
        }
        .header-image-button:hover img {
            filter: brightness(0.9);
        }
       
        .dropdown {
                position: relative;
                display: inline-block;
        }
        .dropdown-content button {
            background-color: white;
            color: black;
            border: none;
            padding: 10px;
            width: 100%;
            text-align: left;
            cursor: pointer;
        }
        .dropdown:hover .dropdown-content {
                display: block;
        }
        .dropdown-content {
                display: none;
                position: absolute;
                background-color: white;
                box-shadow: 0px 8px 16px rgba(0,0,0,0.2);
                z-index: 1000;
                min-width: 200px;
                border-radius: 4px;
                overflow: hidden;
        }
        .dropdown-content a {
                color:rgb(26, 28, 28);
                text-decoration: none;
                display: block;
                padding: 8px 16px;
        }
        .dropdown-content button:hover {
                background-color: #219ebc;
        }
 
        .main-content {
            margin-top: 1px;
            padding: 1px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)