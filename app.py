import streamlit as st
import pandas as pd
import datetime
import os
import time
from PIL import Image

# --- DB IMPORTS ---
from database.database import engine, Base, get_db
from models.meal import Meal
from models.food_label import FoodLabelScan
from services.meal_service import MealService
from services.analytics_service import AnalyticsService
from services.nutrition_service import NutritionService
from services.ocr_service import OCRService
from services.ingredient_analysis import IngredientAnalysisService
from services.label_scan_service import LabelScanService
from utils.image_utils import save_uploaded_file, get_image_metadata
from components.chat_ui import render_chat_interface
from components.nutrition_cards import render_meal_analysis
from components.label_scanner_ui import render_label_analysis
import plotly.express as px
import plotly.graph_objects as go

# Initialize database
Base.metadata.create_all(bind=engine)

# --- PAGE CONFIGURATION ---
# Sets up the main page properties, including layout and theme constraints
st.set_page_config(
    page_title="AI Nutrition & Meal Intelligence",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
# Inject custom CSS to enforce a modern, dark-themed, and responsive UI.
# This overrides some of Streamlit's default styling to provide a sleek SaaS look.
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

    /* Global Typography & Colors */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif !important;
    }
    
    .stApp {
        background-color: #05060A;
        background-image: radial-gradient(circle at 50% 0%, #0B0E1B 0%, #05060A 80%);
        color: #F8FAFC;
    }

    /* Headings - Massive Typography */
    h1 { font-size: 3.5rem !important; font-weight: 800 !important; color: #FFFFFF !important; text-shadow: 0 0 30px rgba(0, 240, 255, 0.6); margin-bottom: 1rem !important; letter-spacing: -0.02em !important;}
    h2 { font-size: 2.8rem !important; font-weight: 800 !important; color: #00f0ff !important; margin-top: 1.5rem !important;}
    h3 { font-size: 2.2rem !important; font-weight: 600 !important; color: #39ff14 !important;}
    p, li, span, div { font-size: 1.1rem !important; color: #F8FAFC !important; }
    
    /* Hide Streamlit Header/Footer */
    header[data-testid="stHeader"] { display: none; }
    footer { display: none; }

    /* Sidebar - Glassmorphism & Neon */
    [data-testid="stSidebar"] {
        background: rgba(10, 12, 20, 0.7) !important;
        backdrop-filter: blur(24px) !important;
        border-right: 1px solid rgba(0, 240, 255, 0.2) !important;
    }
    
    /* Sidebar Brand Labeling */
    [data-testid="stSidebar"] h3 {
        font-size: 2.4rem !important;
        text-align: center;
        margin-top: 20px;
        text-shadow: 0 0 20px rgba(57, 255, 20, 0.6);
    }
    
    /* Sidebar Radio Buttons (Navigation) */
    .stRadio div[role="radiogroup"] label {
        background: transparent !important;
        padding: 16px 24px !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
        transition: all 0.3s ease !important;
        border: 1px solid transparent !important;
    }
    
    .stRadio div[role="radiogroup"] label p {
        font-size: 1.3rem !important;
        font-weight: 600 !important;
    }
    
    .stRadio div[role="radiogroup"] label:hover {
        background: rgba(0, 240, 255, 0.08) !important;
        border: 1px solid rgba(0, 240, 255, 0.4) !important;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.15) !important;
    }
    
    .stRadio div[role="radiogroup"] label[data-checked="true"] {
        background: linear-gradient(90deg, rgba(0, 240, 255, 0.2) 0%, transparent 100%) !important;
        border-left: 6px solid #00f0ff !important;
    }
    
    .stRadio div[role="radiogroup"] label[data-checked="true"] p {
        color: #00f0ff !important;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.4);
    }

    /* Glassmorphism Metric Cards */
    .metric-card {
        background: rgba(15, 18, 28, 0.6);
        backdrop-filter: blur(24px);
        border-radius: 20px;
        padding: 35px 25px;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
        margin-bottom: 30px;
        border: 1px solid rgba(0, 240, 255, 0.25);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
        text-align: center;
    }
    
    /* Top neon glow accent for metric card */
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, #00f0ff, #39ff14, transparent);
        opacity: 0.7;
        transition: opacity 0.4s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        border-color: rgba(0, 240, 255, 0.7);
        box-shadow: 0 20px 50px rgba(0, 240, 255, 0.25);
    }
    
    .metric-card:hover::before {
        opacity: 1;
        box-shadow: 0 0 25px #00f0ff;
    }
    
    .metric-title {
        color: #FFFFFF !important;
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        margin-bottom: 15px;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
    }
    
    .metric-value {
        color: #FFFFFF !important;
        font-size: 4rem !important;
        font-weight: 800 !important;
        line-height: 1.1;
        text-shadow: 0 0 25px rgba(255, 255, 255, 0.5);
    }
    
    .metric-subtext {
        color: #39ff14 !important;
        font-size: 1.1rem !important;
        margin-top: 15px;
        font-weight: 600 !important;
        text-shadow: 0 0 10px rgba(57, 255, 20, 0.3);
    }

    /* Analytics Chart Containers */
    .chart-container {
        background: rgba(15, 18, 28, 0.5);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 30px;
        border: 1px solid rgba(0, 240, 255, 0.15);
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .chart-container:hover {
        border-color: rgba(0, 240, 255, 0.5);
        box-shadow: 0 0 40px rgba(0, 240, 255, 0.15), inset 0 0 20px rgba(0, 240, 255, 0.05);
        transform: translateY(-4px);
    }
    
    .chart-title {
        color: #00f0ff !important;
        font-size: 1.6rem !important;
        font-weight: 800 !important;
        margin-bottom: 20px;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Insights Panel */
    .insight-card {
        background: linear-gradient(145deg, rgba(15, 18, 28, 0.8), rgba(20, 25, 40, 0.6));
        backdrop-filter: blur(24px);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 4px solid #39ff14;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
    }
    
    .insight-card.warning {
        border-left: 4px solid #ff0055;
    }
    
    .insight-card.info {
        border-left: 4px solid #00f0ff;
    }

    .insight-card:hover {
        transform: translateX(5px);
        background: linear-gradient(145deg, rgba(20, 25, 40, 0.9), rgba(25, 30, 50, 0.7));
    }
    
    /* Content Blocks */
    .content-card {
        background: rgba(15, 18, 28, 0.6);
        backdrop-filter: blur(24px);
        border-radius: 20px;
        padding: 40px;
        margin-bottom: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .content-card:hover {
        border-color: rgba(57, 255, 20, 0.4);
        box-shadow: 0 0 40px rgba(57, 255, 20, 0.1);
    }
    
    .section-title {
        color: #00f0ff !important;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        margin-bottom: 25px;
        padding-bottom: 20px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Streamlit Containers (e.g. border=True containers) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(15, 18, 28, 0.5) !important;
        backdrop-filter: blur(16px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(0, 240, 255, 0.2) !important;
        transition: all 0.3s ease;
        padding: 20px !important;
    }
    
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(0, 240, 255, 0.5) !important;
        box-shadow: 0 0 30px rgba(0, 240, 255, 0.1) !important;
    }
    
    /* Streamlit Native Metrics */
    [data-testid="stMetric"] {
        background: rgba(15, 18, 28, 0.8);
        border-radius: 16px;
        padding: 25px;
        border: 1px solid rgba(57, 255, 20, 0.3);
        box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.6), 0 5px 15px rgba(0,0,0,0.3);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
        color: #FFFFFF !important;
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 10px !important;
        text-align: center;
    }

    [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
        color: #FFFFFF !important;
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.6);
        line-height: 1.1;
        text-align: center;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00f0ff 0%, #bf00ff 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        padding: 1rem 2rem !important;
        transition: all 0.3s ease !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 10px 25px rgba(0, 240, 255, 0.5) !important;
    }

    /* Chat Bubbles */
    [data-testid="stChatMessage"] {
        background: rgba(15, 18, 28, 0.8) !important;
        backdrop-filter: blur(16px) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        border: 1px solid rgba(0, 240, 255, 0.2) !important;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3) !important;
        margin-bottom: 20px !important;
    }
    
    [data-testid="stChatMessage"][data-baseweb="card"] {
        border-left: 4px solid #39ff14 !important;
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: rgba(15, 18, 28, 0.6) !important;
        border: 2px dashed #00f0ff !important;
        border-radius: 20px !important;
        padding: 40px !important;
        transition: all 0.3s ease !important;
        text-align: center !important;
    }
    
    [data-testid="stFileUploader"]:hover {
        background: rgba(0, 240, 255, 0.1) !important;
        box-shadow: 0 0 30px rgba(0, 240, 255, 0.3) !important;
        border-color: #39ff14 !important;
    }
    
    /* Uploader Typography overrides */
    [data-testid="stFileUploader"] small, [data-testid="stFileUploader"] div {
        font-size: 1.2rem !important;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animated-element {
        animation: fadeIn 0.5s ease forwards;
    }
</style>
"""

# Apply the CSS immediately
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# --- UI COMPONENTS ---
def render_metric_card(title: str, value: str, subtext: str):
    """
    Renders a styled metric card using custom HTML/CSS.
    Useful for KPIs and top-level statistics.
    """
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-subtext">{subtext}</div>
        </div>
    """, unsafe_allow_html=True)

def render_content_card(title: str, placeholder: str):
    """
    Renders a clean container for future complex content (charts, tables, etc.).
    Currently displays a placeholder message.
    """
    st.markdown(f"""
        <div class="content-card">
            <div class="section-title">{title}</div>
            <div class="placeholder-text">{placeholder}</div>
        </div>
    """, unsafe_allow_html=True)




# --- PAGE VIEWS ---
def show_dashboard():
    """Renders the main dashboard page with high-level metrics and summaries."""
    st.title("📊 Dashboard")
    st.markdown("Welcome back! Here is your daily nutrition overview.")
    
    with get_db() as db:
        
        today = datetime.date.today()
        df = AnalyticsService.get_analytics_dataframe(db, start_date=today, end_date=today)
        
        calories_today = int(df["calories"].sum()) if not df.empty else 0
        protein_today = int(df["protein"].sum()) if not df.empty else 0
        meals_logged = len(df) if not df.empty else 0
        avg_health = int(df["health_score"].mean()) if not df.empty else 0
        
    target_cal = "2000 kcal"
    target_pro = "150g"
    
    # 4-column layout for top metrics
    cols = st.columns(4)
    
    with cols[0]:
        render_metric_card("Calories Today", f"{calories_today:,}", f"Target: {target_cal}")
    with cols[1]:
        render_metric_card("Protein Intake", f"{protein_today}g", f"Target: {target_pro}")
    with cols[2]:
        render_metric_card("Meals Logged", f"{meals_logged}", "Today")
    with cols[3]:
        render_metric_card("Avg Health Score", f"{avg_health}", "Today's average")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main content layout: 3/4 width for charts, 1/4 width for feed/insights
    col_main, col_side = st.columns([3, 1], gap="large")
    
    with col_main:
        render_content_card("Weekly Calorie Trend", "📈 [ View full charts in Analytics page ]")
        render_content_card("Today's Macros", "🍩 [ View full charts in Analytics page ]")
        
    with col_side:
        render_content_card("Nutrition Insights", "💡 **Tip:** Ensure your profile is filled out to get personalized targets.")
        render_content_card("Recent Meals", "🍔 [ View your log in Meal History ]")

def show_upload_meal():
    """Renders the meal upload and AI analysis interface."""
    st.title("📸 Upload Meal")
    st.markdown("Snap a picture of your meal and let our AI analyze the nutritional content.")
    
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown("### Image Upload")
        
        # File uploader supports drag-and-drop by default
        uploaded_file = st.file_uploader(
            "Choose a meal image...", 
            type=['jpg', 'jpeg', 'png'],
            help="Drag and drop supported. Max size: 5MB."
        )
        
        if uploaded_file is not None:
            try:
                # Save the image locally using our utility
                file_path, file_name, timestamp, image_bytes = save_uploaded_file(uploaded_file)
                
                # Read image metadata using our utility
                width, height, file_size_kb = get_image_metadata(uploaded_file)
                
                st.success("Image successfully uploaded and saved!")
                
                # Display preview
                img = Image.open(uploaded_file)
                st.image(img, caption="Meal Preview", use_container_width=True)
                
                # Metadata display using standard Streamlit container
                with st.container(border=True):
                    st.markdown("#### Image Metadata")
                    st.markdown(f"- **Filename:** `{file_name}`")
                    st.markdown(f"- **Dimensions:** `{width} x {height} px`")
                    st.markdown(f"- **File Size:** `{file_size_kb:.1f} KB`")
                    formatted_time = datetime.datetime.strptime(timestamp, '%Y%m%d_%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
                    st.markdown(f"- **Uploaded At:** `{formatted_time}`")
                    
            except Exception as e:
                st.error(f"Error processing image: {e}")
            
    with col_right:
        st.markdown("### AI Analysis Results")
        if uploaded_file is not None:
            with st.status("🧠 Initializing AI analysis...", expanded=True) as status:
                st.write("Sending image to local llama3.2-vision model...")
                try:
                    with get_db() as db:
                        # Process and save the meal using the NutritionService orchestrator
                        db_meal, debug_logs = NutritionService.process_and_save_meal(
                            db=db,
                            image_bytes=image_bytes,
                            file_path=file_path,
                            timestamp_str=timestamp
                        )
                        status.update(label="Analysis complete!", state="complete", expanded=False)
                    
                    # Render the analysis using the extracted component
                    render_meal_analysis(db_meal)
                    
                    # Render Debug Log
                    with st.expander("🛠️ Debug: AI Response Log", expanded=False):
                        st.markdown("**Errors / Fallbacks Triggered:**")
                        if debug_logs["errors"]:
                            for err in debug_logs["errors"]:
                                st.error(err)
                        else:
                            st.success("No parsing errors.")
                            
                        st.markdown("**Cleaned JSON Output:**")
                        st.json(debug_logs["cleaned_json"])
                        
                        st.markdown("**Raw Ollama Output:**")
                        st.code(debug_logs["raw_response"], language="json")
                    
                except Exception as e:
                    status.update(label="Analysis failed", state="error", expanded=True)
                    st.error(f"Error during AI inference: {str(e)}")
        else:
            with st.container(border=True):
                st.info("🔍 Upload an image to see AI analysis")

def show_meal_history():
    """Renders the historical log of user meals."""
    st.title("🗓️ Meal History")
    
    # Check if we are viewing a specific meal
    if "view_meal_id" in st.session_state and st.session_state.view_meal_id is not None:
        if st.button("⬅️ Back to History"):
            st.session_state.view_meal_id = None
            st.rerun()
            
        with get_db() as db:
            meal = db.query(Meal).filter(Meal.id == st.session_state.view_meal_id).first()
            if meal:
                col1, col2 = st.columns([1, 1], gap="large")
                with col1:
                    st.subheader("Meal Image")
                    try:
                        img = Image.open(meal.image_path)
                        st.image(img, caption=meal.food_name, use_container_width=True)
                    except Exception as e:
                        st.error("Image not found.")
                with col2:
                    st.subheader("AI Analysis Results")
                    render_meal_analysis(meal)
            else:
                st.error("Meal not found.")
        return

    st.markdown("Review your past meals and nutritional intake.")
    
    # --- FILTERS ---
    with st.expander("🔍 Search & Filters", expanded=True):
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        
        with col_s1:
            search_query = st.text_input("Search food...", "")
        with col_s2:
            date_range = st.date_input("Date Range", value=())
        with col_s3:
            # Setting a max default that makes sense for meals
            min_cal, max_cal = st.slider("Calories Range", 0, 2000, (0, 2000))
        with col_s4:
            sort_by = st.selectbox("Sort By", ["newest", "oldest", "highest_calories", "lowest_calories"])
            
    # Process date range
    start_date = None
    end_date = None
    if len(date_range) == 2:
        start_date, end_date = date_range
    elif len(date_range) == 1:
        start_date = date_range[0]
        end_date = date_range[0]

    # --- FETCH MEALS ---
    with get_db() as db:
        meals = MealService.get_all_meals(
            db=db,
            search_query=search_query if search_query else None,
            start_date=start_date,
            end_date=end_date,
            min_calories=float(min_cal),
            max_calories=float(max_cal),
            sort_by=sort_by
        )
    
    if not meals:
        st.info("No meals found matching your criteria.")
        return
        
    # --- RENDER CARDS ---
    st.markdown("### Logged Meals")
    
    # We display them in a grid (e.g. 3 columns)
    cols = st.columns(3)
    for i, meal in enumerate(meals):
        col = cols[i % 3]
        with col:
            with st.container(border=True):
                try:
                    img = Image.open(meal.image_path)
                    st.image(img, use_container_width=True)
                except Exception:
                    st.markdown("<div style='height:150px; background-color:#2D3139; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#A0AEC0;'>Image not found</div>", unsafe_allow_html=True)
                
                st.markdown(f"**{meal.food_name}**")
                st.markdown(f"🔥 {meal.calories} kcal | 🍗 {meal.protein}g")
                st.markdown(f"<small style='color:#A0AEC0;'>{meal.upload_timestamp.strftime('%Y-%m-%d %H:%M')}</small>", unsafe_allow_html=True)
                
                if st.button("View Analysis", key=f"view_{meal.id}", use_container_width=True):
                    st.session_state.view_meal_id = meal.id
                    st.rerun()

def show_analytics():
    """Renders deep-dive analytics and trends with a premium futuristic UI."""
    st.markdown("<h1 class='animated-element'>📈 AI Analytics Core</h1>", unsafe_allow_html=True)
    st.markdown("<p class='animated-element' style='color:#00f0ff;'>Deep dive into your nutritional trends and AI-driven health patterns.</p>", unsafe_allow_html=True)
    
    # --- DATE FILTERS ---
    filter_col, _ = st.columns([1, 2])
    with filter_col:
        time_range = st.selectbox(
            "Select Time Range",
            ["Last 7 Days", "Last 30 Days", "All Time", "Custom Range"]
        )
        
    start_date = None
    end_date = None
    today = datetime.date.today()
    
    if time_range == "Last 7 Days":
        start_date = today - datetime.timedelta(days=7)
    elif time_range == "Last 30 Days":
        start_date = today - datetime.timedelta(days=30)
    elif time_range == "Custom Range":
        date_range = st.date_input("Custom Range", value=())
        if len(date_range) == 2:
            start_date, end_date = date_range
        elif len(date_range) == 1:
            start_date = date_range[0]
            end_date = date_range[0]
            
    # --- FETCH DATA ---
    with get_db() as db:
        df = AnalyticsService.get_analytics_dataframe(db, start_date=start_date, end_date=end_date)
        
    if df.empty:
        st.info("No meal data found for the selected time range. Please upload some meals!")
        return
        
    # --- KPI CARDS ---
    st.markdown("<h2 class='section-title animated-element'>System Overview</h2>", unsafe_allow_html=True)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    avg_cal = int(df["calories"].mean())
    avg_pro = int(df["protein"].mean())
    total_meals = len(df)
    healthiest = df.loc[df["health_score"].idxmax()]
    
    with kpi1:
        render_metric_card("Avg Calories", f"{avg_cal} kcal", "per meal")
    with kpi2:
        render_metric_card("Avg Protein", f"{avg_pro} g", "per meal")
    with kpi3:
        render_metric_card("Total Meals", f"{total_meals}", "in selected range")
    with kpi4:
        render_metric_card("Peak Health Score", f"{healthiest['health_score']}/100", f"{healthiest['food_name']}")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- PLOTLY THEME CONFIG ---
    template = "plotly_dark"
    neon_cyan = "#00f0ff"
    neon_green = "#39ff14"
    neon_purple = "#bf00ff"
    neon_pink = "#ff0055"
    
    st.markdown("<h2 class='section-title animated-element'>Nutritional Data Streams</h2>", unsafe_allow_html=True)
    
    # Top Row: Calorie Trend & Macro Distribution
    row1_c1, row1_c2 = st.columns([2, 1], gap="large")
    
    with row1_c1:
        st.markdown(f"<div class='chart-container animated-element'><div class='chart-title'>⚡ Calorie Consumption Trend</div>", unsafe_allow_html=True)
        daily_cal = df.groupby("date")["calories"].sum().reset_index()
        fig_cal = px.area(daily_cal, x="date", y="calories", template=template, color_discrete_sequence=[neon_cyan], markers=True)
        fig_cal.update_traces(fillcolor='rgba(0, 240, 255, 0.2)', line=dict(width=3))
        fig_cal.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="", yaxis_title="Calories")
        st.plotly_chart(fig_cal, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with row1_c2:
        st.markdown(f"<div class='chart-container animated-element'><div class='chart-title'>🍩 Macro Distribution</div>", unsafe_allow_html=True)
        avg_macros = pd.DataFrame({
            "Macro": ["Protein", "Carbs", "Fats"],
            "Amount": [df["protein"].mean(), df["carbs"].mean(), df["fats"].mean()]
        })
        fig_macro_pie = px.pie(avg_macros, values="Amount", names="Macro", hole=0.7, 
                               color_discrete_sequence=[neon_green, "#0080ff", neon_purple], template=template)
        fig_macro_pie.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
        fig_macro_pie.update_traces(textposition='outside', textinfo='percent+label')
        st.plotly_chart(fig_macro_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Second Row: Macro Trends & Health Score Trend
    row2_c1, row2_c2 = st.columns(2, gap="large")
    
    with row2_c1:
        st.markdown(f"<div class='chart-container animated-element'><div class='chart-title'>📊 Macronutrient Trends</div>", unsafe_allow_html=True)
        daily_macros = df.groupby("date")[["protein", "carbs", "fats"]].mean().reset_index()
        fig_mac = go.Figure()
        fig_mac.add_trace(go.Bar(x=daily_macros["date"], y=daily_macros["carbs"], name="Carbs", marker_color="#0080ff"))
        fig_mac.add_trace(go.Bar(x=daily_macros["date"], y=daily_macros["protein"], name="Protein", marker_color=neon_green))
        fig_mac.add_trace(go.Bar(x=daily_macros["date"], y=daily_macros["fats"], name="Fats", marker_color=neon_purple))
        fig_mac.update_layout(barmode='stack', template=template, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="", yaxis_title="Grams")
        st.plotly_chart(fig_mac, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with row2_c2:
        st.markdown(f"<div class='chart-container animated-element'><div class='chart-title'>❤️ Health Score Velocity</div>", unsafe_allow_html=True)
        daily_health = df.groupby("date")["health_score"].mean().reset_index()
        fig_health = px.line(daily_health, x="date", y="health_score", template=template, color_discrete_sequence=[neon_pink], markers=True)
        fig_health.update_traces(line=dict(width=3, dash="dot"))
        fig_health.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="", yaxis_title="Score (0-100)", yaxis_range=[0, 100])
        st.plotly_chart(fig_health, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    # Third Row: Weekly Meal Frequency & AI Insights
    row3_c1, row3_c2 = st.columns([1, 1], gap="large")
    
    with row3_c1:
        st.markdown(f"<div class='chart-container animated-element'><div class='chart-title'>📅 Meal Logging Frequency</div>", unsafe_allow_html=True)
        freq_df = df["date"].value_counts().reset_index()
        freq_df.columns = ["date", "count"]
        freq_df = freq_df.sort_values("date")
        fig_freq = px.bar(freq_df, x="date", y="count", template=template, color_discrete_sequence=[neon_purple])
        fig_freq.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="", yaxis_title="Meals Logged")
        st.plotly_chart(fig_freq, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with row3_c2:
        st.markdown("<h2 class='section-title animated-element' style='margin-top:0;'>🧠 AI Intelligence Matrix</h2>", unsafe_allow_html=True)
        insights = AnalyticsService.generate_ai_insights(df)
        for insight in insights:
            if isinstance(insight, dict):
                card_class = f"insight-card {insight.get('type', 'info')}"
                st.markdown(f"""
                <div class="{card_class} animated-element">
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:5px;">
                        <span style="font-size:1.5rem;">{insight.get('icon', '💡')}</span>
                    </div>
                    <div style="color:#F8FAFC;">{insight.get('message', '')}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Fallback for old format
                st.markdown(f"<div class='insight-card info'>{insight}</div>", unsafe_allow_html=True)

def show_food_label_scanner():
    """Renders the Food Label Scanner interface."""
    st.title("🔎 Food Label Scanner")
    st.markdown("Upload a picture of an ingredient label to detect harmful additives and sugar content.")
    
    tab1, tab2 = st.tabs(["Scan New Label", "Scan History"])
    
    with tab1:
        col_left, col_right = st.columns([1, 1], gap="large")
        
        with col_left:
            uploaded_file = st.file_uploader("Upload Label Image", type=['jpg', 'jpeg', 'png'], key="label_uploader")
            
            if uploaded_file is not None:
                file_path, file_name, timestamp, image_bytes = save_uploaded_file(uploaded_file)
                st.success("Image uploaded.")
                img = Image.open(uploaded_file)
                st.image(img, caption="Label Preview", use_container_width=True)
                
        with col_right:
            if uploaded_file is not None:
                with st.status("🔍 Processing label...", expanded=True) as status:
                    st.write("Extracting text via OCR...")
                    try:
                        # 1. OCR
                        ocr_text = OCRService.extract_text_from_image(image_bytes)
                        st.write("Analyzing ingredients with AI...")
                        
                        # 2. AI Analysis
                        analysis = IngredientAnalysisService.analyze_label_text(ocr_text)
                        
                        # 3. Save to DB
                        with get_db() as db:
                            db_scan = LabelScanService.add_scan(db, file_path, ocr_text, analysis)
                            
                        status.update(label="Analysis complete!", state="complete", expanded=False)
                        
                        # 4. Render UI
                        render_label_analysis(db_scan)
                        
                        with st.expander("🛠️ Debug: OCR Output", expanded=False):
                            st.text_area("Raw Text", ocr_text, height=200)
                            st.json(analysis)
                            
                    except Exception as e:
                        status.update(label="Analysis failed", state="error", expanded=True)
                        st.error(f"Error during scan: {str(e)}")
            else:
                with st.container(border=True):
                    st.info("Upload an ingredient label to see analysis.")
                    
    with tab2:
        with get_db() as db:
            scans = LabelScanService.get_all_scans(db)
        if not scans:
            st.info("No label scans found.")
        else:
            for scan in scans:
                with st.expander(f"Scan from {scan.upload_timestamp.strftime('%Y-%m-%d %H:%M')}"):
                    try:
                        st.image(Image.open(scan.image_path), width=200)
                    except:
                        pass
                    render_label_analysis(scan)

def show_ai_coach():
    """Renders the conversational AI assistant interface."""
    render_chat_interface()


# --- MAIN APPLICATION ROUTER ---
def main():
    """Main application entry point that handles sidebar navigation and routing."""
    
    # Sidebar Configuration
    with st.sidebar:
        # App branding
        st.markdown("### 🥗 NutriMind")
        st.markdown("<p style='color: #A0AEC0; font-size: 0.9rem; margin-top: -10px;'>AI Meal Intelligence</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Navigation Menu
        # We use a radio button styled like a menu for standard page routing
        page = st.radio(
            "Navigation",
            [
                "Dashboard", 
                "Upload Meal", 
                "Meal History", 
                "Food Label Scanner",
                "Analytics", 
                "AI Nutrition Coach",
            ],
            label_visibility="collapsed"
        )
        
        # Footer / Extra Options
        st.markdown("---")
        st.button("⚙️ Settings", use_container_width=True)
        
    # Route to the appropriate page based on sidebar selection
    if page == "Dashboard":
        show_dashboard()
    elif page == "Upload Meal":
        show_upload_meal()
    elif page == "Meal History":
        show_meal_history()
    elif page == "Analytics":
        show_analytics()
    elif page == "Food Label Scanner":
        show_food_label_scanner()
    elif page == "AI Nutrition Coach":
        show_ai_coach()


if __name__ == "__main__":
    main()
