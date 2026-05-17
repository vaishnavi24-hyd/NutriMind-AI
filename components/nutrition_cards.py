import streamlit as st

def render_meal_analysis(meal):
    """
    Renders the detailed AI analysis for a given meal.
    Preserves the ultra-premium typography and layout scaling.
    """
    with st.container(border=True):
        st.success("Analysis Complete")
        
        st.markdown("#### Detected Food Items")
        st.markdown(f"**{meal.food_name}**")
        
        st.markdown("#### Estimated Nutrition")
        
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
        st.markdown("#### Health Summary")
        if "Excellent" in meal.nutrition_summary:
            st.info(meal.nutrition_summary)
        else:
            st.write(meal.nutrition_summary)
        score_col1, score_col2 = st.columns(2)
        with score_col1:
            st.markdown(f"**Health Score:** {meal.health_score}/100")
        with score_col2:
            confidence = getattr(meal, 'confidence_score', 0)
            st.markdown(f"**AI Confidence:** {confidence}/100")
