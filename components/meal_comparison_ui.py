import streamlit as st
import json
import plotly.graph_objects as go
from PIL import Image
from services.nutrition_service import NutritionService
from services.ollama_service import OllamaService
from utils.image_utils import save_uploaded_file
from database.database import get_db

def render_meal_comparison():
    st.title("⚖️ Meal Comparison")
    st.markdown("Upload two meals to see how they stack up against each other and get AI advice on which to choose.")
    
    col_a, col_b = st.columns(2, gap="large")
    
    meal_a_file = None
    meal_b_file = None
    
    with col_a:
        st.markdown("### Meal A")
        meal_a_file = st.file_uploader("Upload Meal A...", type=['jpg', 'jpeg', 'png'], key="meal_a")
        if meal_a_file:
            st.image(Image.open(meal_a_file), use_container_width=True)
            
    with col_b:
        st.markdown("### Meal B")
        meal_b_file = st.file_uploader("Upload Meal B...", type=['jpg', 'jpeg', 'png'], key="meal_b")
        if meal_b_file:
            st.image(Image.open(meal_b_file), use_container_width=True)
            
    if meal_a_file and meal_b_file:
        if st.button("🚀 Analyze & Compare", use_container_width=True, type="primary"):
            with st.spinner("Analyzing both meals... (This may take a moment)"):
                with get_db() as db:
                    # Save and process Meal A
                    file_path_a, _, ts_a, bytes_a = save_uploaded_file(meal_a_file)
                    meal_a, logs_a = NutritionService.process_and_save_meal(db, bytes_a, file_path_a, ts_a)
                    
                    # Save and process Meal B
                    file_path_b, _, ts_b, bytes_b = save_uploaded_file(meal_b_file)
                    meal_b, logs_b = NutritionService.process_and_save_meal(db, bytes_b, file_path_b, ts_b)
                    
                    try:
                        data_a = json.loads(meal_a.nutrition_summary)
                    except:
                        data_a = {"summary": meal_a.nutrition_summary}
                    
                    try:
                        data_b = json.loads(meal_b.nutrition_summary)
                    except:
                        data_b = {"summary": meal_b.nutrition_summary}
                        
                    st.success("Analysis Complete!")
                    
                    # --- AI COMPARISON VERDICT ---
                    with st.spinner("Generating Final Comparison Verdict..."):
                        verdict_raw = OllamaService.compare_meals(data_a, data_b)
                        try:
                            verdict = json.loads(verdict_raw)
                        except Exception:
                            verdict = {
                                "healthier_meal": "Unknown",
                                "verdict": "Unable to parse comparison verdict. Please review the macros manually.",
                                "recommendation": ""
                            }
                            
                    # --- UI RENDERING ---
                    st.markdown("---")
                    st.markdown("## 🏆 Final Verdict")
                    
                    winner = verdict.get("healthier_meal", "Tie")
                    winner_color = "#ffd700" if winner != "Tie" else "#00f0ff"
                    
                    st.markdown(f"""
                    <div style="
                        border: 2px solid {winner_color};
                        background: linear-gradient(145deg, rgba(255,215,0,0.1) 0%, rgba(0,0,0,0) 100%);
                        padding: 24px;
                        border-radius: 8px;
                        box-shadow: 0px 0px 20px {winner_color}40;
                        text-align: center;
                        margin-bottom: 20px;
                    ">
                        <h2 style="color: {winner_color}; margin-top: 0; text-transform: uppercase;">Healthier Choice: {winner}</h2>
                        <p style="font-size: 1.1em; color: #E2E8F0;">{verdict.get("verdict", "")}</p>
                        <hr style="border-color: rgba(255,255,255,0.1); margin: 16px 0;">
                        <h4 style="color: #00ff88;">Recommendation:</h4>
                        <p style="font-style: italic; color: #A0AEC0;">{verdict.get("recommendation", "")}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # --- SIDE BY SIDE COMPARISON ---
                    st.markdown("## 📊 Macro Comparison")
                    
                    # Charts
                    categories = ['Calories (kcal)', 'Protein (g)', 'Carbs (g)', 'Fat (g)', 'Health Score']
                    val_a = [meal_a.calories, meal_a.protein, meal_a.carbs, meal_a.fats, meal_a.health_score]
                    val_b = [meal_b.calories, meal_b.protein, meal_b.carbs, meal_b.fats, meal_b.health_score]
                    
                    fig = go.Figure(data=[
                        go.Bar(name='Meal A', x=categories, y=val_a, marker_color='#00f0ff'),
                        go.Bar(name='Meal B', x=categories, y=val_b, marker_color='#b800ff')
                    ])
                    fig.update_layout(
                        barmode='group',
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#E2E8F0'),
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Side by Side metrics
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("### Meal A Breakdown")
                        st.metric("Health Score", meal_a.health_score, delta=meal_a.health_score - meal_b.health_score)
                        foods_a = data_a.get("foods", [])
                        if foods_a:
                            st.write("**Detected Foods:**")
                            for f in foods_a:
                                st.markdown(f"- {f.get('name')} ({f.get('portion')})")
                                
                    with c2:
                        st.markdown("### Meal B Breakdown")
                        st.metric("Health Score", meal_b.health_score, delta=meal_b.health_score - meal_a.health_score)
                        foods_b = data_b.get("foods", [])
                        if foods_b:
                            st.write("**Detected Foods:**")
                            for f in foods_b:
                                st.markdown(f"- {f.get('name')} ({f.get('portion')})")
                                
                    # Comparison Sub-Metrics
                    st.markdown("### Additional Insights")
                    c3, c4, c5 = st.columns(3)
                    with c3:
                        st.markdown(f"**Better for Weight Loss:**<br><span style='color:#00ff88;'>{verdict.get('better_for_weight_loss', 'Tie')}</span>", unsafe_allow_html=True)
                    with c4:
                        st.markdown(f"**Better for Muscle Gain:**<br><span style='color:#ffaa00;'>{verdict.get('better_for_muscle_gain', 'Tie')}</span>", unsafe_allow_html=True)
                    with c5:
                        st.markdown(f"**More Processed:**<br><span style='color:#ff003c;'>{verdict.get('more_processed', 'Tie')}</span>", unsafe_allow_html=True)
