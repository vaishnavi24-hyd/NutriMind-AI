import streamlit as st
import json

def render_meal_analysis(meal):
    """
    Renders the detailed AI analysis for a given meal.
    Preserves the ultra-premium typography and layout scaling.
    """
    analysis_data = {}
    try:
        analysis_data = json.loads(meal.nutrition_summary)
    except Exception:
        analysis_data = {"summary": meal.nutrition_summary, "recommendation": ""}
        
    with st.container(border=True):
        st.success("Analysis Complete")
        
        st.markdown("#### 🔍 Detected Food Items")
        foods = analysis_data.get("foods", [])
        
        if not foods:
            st.markdown(f"**{meal.food_name}**")
        else:
            for food in foods:
                with st.container(border=True):
                    f_col1, f_col2 = st.columns([3, 1])
                    with f_col1:
                        st.markdown(f"**{food.get('name', 'Unknown')}** ({food.get('portion', 'Unknown portion')})")
                        st.markdown(f"<small style='color:#A0AEC0;'>Calories: {food.get('calories', 0)} | Protein: {food.get('protein', 0)}g | Carbs: {food.get('carbs', 0)}g | Fat: {food.get('fat', 0)}g</small>", unsafe_allow_html=True)
                    with f_col2:
                        st.markdown(f"<div style='text-align: right; color: #00f0ff; font-weight: bold;'>{food.get('confidence', 0)}% Match</div>", unsafe_allow_html=True)
        
        st.markdown("#### 📊 Total Estimated Nutrition")
        
        # Using a 2x2 grid to ensure the massive fonts do not clip on smaller screens
        macro_col1, macro_col2 = st.columns(2)
        macro_col3, macro_col4 = st.columns(2)
        
        with macro_col1:
            st.metric("Calories", f"{meal.calories} kcal")
        with macro_col2:
            st.metric("Protein", f"{meal.protein}g")
        with macro_col3:
            st.metric("Carbs", f"{meal.carbs}g")
        with macro_col4:
            st.metric("Fat", f"{meal.fats}g")
        
        st.markdown("---")
        st.markdown("#### 💡 Health Summary")
        
        summary_text = analysis_data.get("summary", meal.nutrition_summary)
        rec_text = analysis_data.get("recommendation", "")
        
        if "Excellent" in summary_text:
            st.info(summary_text)
        else:
            st.write(summary_text)
            
        if rec_text:
            st.markdown(f"**Recommendation:** {rec_text}")
            
        score_col1, score_col2 = st.columns(2)
        with score_col1:
            st.markdown(f"**Overall Health Score:** {meal.health_score}/100")
        with score_col2:
            confidence = getattr(meal, 'confidence_score', 0)
            st.markdown(f"**Overall AI Confidence:** {confidence}/100")
