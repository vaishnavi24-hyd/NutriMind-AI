import streamlit as st
from database.database import get_db
from services.profile_service import ProfileService
from services.analytics_service import AnalyticsService

def render_profile():
    st.title("👤 My Profile")
    st.markdown("Set your physiological data and fitness goals to personalize your AI Nutrition experience.")
    
    with get_db() as db:
        user = ProfileService.get_user_profile(db)
        
        # Determine mode
        if "edit_profile" not in st.session_state:
            st.session_state.edit_profile = user is None
            
        if st.session_state.edit_profile:
            st.markdown("### Edit Profile")
            with st.form("profile_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    age = st.number_input("Age", min_value=10, max_value=100, value=user.age if user else 30)
                    gender = st.selectbox("Gender", ["Male", "Female"], index=0 if not user or user.gender == "Male" else 1)
                    weight_kg = st.number_input("Weight (kg)", min_value=30.0, max_value=250.0, value=user.weight_kg if user else 70.0)
                    height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=user.height_cm if user else 170.0)
                    
                with col2:
                    activity_level = st.selectbox(
                        "Activity Level", 
                        ["Sedentary", "Light", "Moderate", "Active", "Very Active"],
                        index=["Sedentary", "Light", "Moderate", "Active", "Very Active"].index(user.activity_level) if user else 2
                    )
                    fitness_goal = st.selectbox(
                        "Fitness Goal",
                        ["Weight Loss", "Maintenance", "Muscle Gain"],
                        index=["Weight Loss", "Maintenance", "Muscle Gain"].index(user.fitness_goal) if user else 1
                    )
                    
                submit = st.form_submit_button("Save Profile", use_container_width=True)
                
                if submit:
                    ProfileService.save_user_profile(
                        db=db,
                        age=age,
                        gender=gender,
                        weight_kg=weight_kg,
                        height_cm=height_cm,
                        activity_level=activity_level,
                        fitness_goal=fitness_goal
                    )
                    st.session_state.edit_profile = False
                    st.success("Profile saved successfully!")
                    st.rerun()
                    
        else:
            # View Mode
            metrics = ProfileService.calculate_metrics(user)
            df = AnalyticsService.get_analytics_dataframe(db)
            insights = ProfileService.generate_health_insights(user, metrics, df)
            
            # Header
            col_head, col_btn = st.columns([4, 1])
            with col_head:
                st.markdown(f"### Current Goal: **{user.fitness_goal}**")
            with col_btn:
                if st.button("✏️ Edit Profile", use_container_width=True):
                    st.session_state.edit_profile = True
                    st.rerun()
                    
            # KPI Cards
            st.markdown("#### Personalized Targets")
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            
            with kpi1:
                st.markdown(f"""
                <div class="metric-card" style="text-align:center;">
                    <div class="metric-title">Target Calories</div>
                    <div class="metric-value">{metrics['target_calories']}</div>
                    <div class="metric-subtext">kcal / day</div>
                </div>
                """, unsafe_allow_html=True)
            with kpi2:
                st.markdown(f"""
                <div class="metric-card" style="text-align:center;">
                    <div class="metric-title">Protein</div>
                    <div class="metric-value">{metrics['target_protein']}g</div>
                    <div class="metric-subtext">Daily</div>
                </div>
                """, unsafe_allow_html=True)
            with kpi3:
                st.markdown(f"""
                <div class="metric-card" style="text-align:center;">
                    <div class="metric-title">Carbs</div>
                    <div class="metric-value">{metrics['target_carbs']}g</div>
                    <div class="metric-subtext">Daily</div>
                </div>
                """, unsafe_allow_html=True)
            with kpi4:
                st.markdown(f"""
                <div class="metric-card" style="text-align:center;">
                    <div class="metric-title">Fats</div>
                    <div class="metric-value">{metrics['target_fats']}g</div>
                    <div class="metric-subtext">Daily</div>
                </div>
                """, unsafe_allow_html=True)
                
            # Stats & Insights
            col_stats, col_insights = st.columns([1, 1], gap="large")
            
            with col_stats:
                with st.container(border=True):
                    st.markdown("#### Your Stats")
                    st.markdown(f"- **BMI:** `{metrics['bmi']}` ({metrics['bmi_category']})")
                    st.markdown(f"- **BMR:** `{metrics['bmr']} kcal`")
                    st.markdown(f"- **TDEE:** `{metrics['tdee']} kcal`")
                    st.markdown(f"- **Weight:** `{user.weight_kg} kg`")
                    st.markdown(f"- **Height:** `{user.height_cm} cm`")
                    
            with col_insights:
                with st.container(border=True):
                    st.markdown("#### Health Insights")
                    if not insights:
                        st.info("You're on track! Keep up the good work.")
                    else:
                        for insight in insights:
                            st.markdown(insight)
