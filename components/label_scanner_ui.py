import streamlit as st
import json

def render_label_analysis(scan):
    """
    Renders the futuristic neon UI for food label analysis.
    """
    with st.container(border=True):
        st.markdown("<h3 style='color: #00f0ff;'>🧬 Label Analysis Results</h3>", unsafe_allow_html=True)
        
        score_col1, score_col2 = st.columns(2)
        with score_col1:
            st.metric("Health Score", f"{scan.health_score}/100")
        with score_col2:
            status = "🔴 YES" if scan.is_ultra_processed else "🟢 NO"
            # We use markdown with neon styling instead of metric for text
            st.markdown(f"""
                <div style="background: rgba(15, 18, 28, 0.8); border-radius: 16px; padding: 25px; border: 1px solid rgba(57, 255, 20, 0.3); box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.6), 0 5px 15px rgba(0,0,0,0.3); text-align: center;">
                    <p style="color: #FFFFFF !important; font-size: 1.3rem !important; font-weight: 800 !important; text-transform: uppercase; margin-bottom: 10px !important;">Ultra Processed</p>
                    <p style="color: {'#ff0055' if scan.is_ultra_processed else '#39ff14'} !important; font-size: 2.5rem !important; font-weight: 800 !important;">{status}</p>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown("#### 🚨 Detected Additives & Risks")
        
        try:
            harmful = json.loads(scan.harmful_ingredients) if isinstance(scan.harmful_ingredients, str) else scan.harmful_ingredients
        except:
            harmful = []
            
        if harmful:
            for item in harmful:
                st.markdown(f"""
                <div style="background: rgba(255, 0, 85, 0.1); border-left: 4px solid #ff0055; padding: 10px 20px; border-radius: 4px; margin-bottom: 10px;">
                    <span style="color: #ff0055; font-weight: bold; font-size: 1.1rem;">⚠️ {item}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No harmful additives or high sugar detected.")
            
        st.markdown("#### 🧪 Ingredient Explanation")
        st.info(scan.ingredient_explanation)
        
        st.markdown("#### 📝 Summary")
        st.write(scan.summary)
        
        st.markdown("#### 💡 Healthier Alternatives")
        st.markdown(f"*{scan.healthier_alternatives}*")
