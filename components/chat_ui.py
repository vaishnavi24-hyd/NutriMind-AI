import streamlit as st
import datetime
from services.chat_service import ChatService

def render_chat_interface():
    """Renders the AI Nutrition Coach chat interface."""
    st.title("🤖 AI Nutrition Coach")
    st.markdown("Chat with your personalized AI coach for diet advice, meal planning, and answering nutrition questions.")
    
    # Header controls (Clear Chat)
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
            
    # Initialize chat history
    if "messages" not in st.session_state or not st.session_state.messages:
        # Add an initial onboarding message
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi there! 👋 I'm your AI Nutrition Coach. I'm here to help you hit your macros, plan your meals, and achieve your health goals. (Note: I am an AI, not a medical doctor). How can I help you today?", "timestamp": datetime.datetime.now().strftime("%I:%M %p")}
        ]
        
    # Quick Prompts
    st.markdown("**Quick Suggestions:**")
    prompt_cols = st.columns(5)
    
    prompts = [
        "High protein breakfast ideas",
        "Healthy Indian lunch",
        "Weight loss meal suggestions",
        "Muscle gain foods",
        "Low calorie snacks"
    ]
    
    # Store the selected quick prompt
    selected_prompt = None
    for i, prompt in enumerate(prompts):
        with prompt_cols[i]:
            if st.button(prompt, key=f"prompt_{i}", use_container_width=True):
                selected_prompt = prompt

    st.markdown("---")
    
    # Container for chat messages to keep input at bottom
    chat_container = st.container(height=500)
    
    with chat_container:
        # Display chat messages from history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                st.markdown(f"<small style='color: #718096;'>{message['timestamp']}</small>", unsafe_allow_html=True)
                
    # Accept user input (from chat_input or quick prompt)
    user_input = st.chat_input("Ask me about nutrition, meal plans, or healthy recipes...")
    
    if selected_prompt:
        user_input = selected_prompt
        
    if user_input:
        # 1. Add user message to state
        timestamp = datetime.datetime.now().strftime("%I:%M %p")
        st.session_state.messages.append({"role": "user", "content": user_input, "timestamp": timestamp})
        
        # 2. Render user message in UI immediately
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)
                st.markdown(f"<small style='color: #718096;'>{timestamp}</small>", unsafe_allow_html=True)
                
            # 3. Render typing indicator and generate response
            with st.chat_message("assistant"):
                with st.spinner("Coach is typing..."):
                    response = ChatService.generate_response(user_input, st.session_state.messages)
                    resp_timestamp = datetime.datetime.now().strftime("%I:%M %p")
                    
                st.markdown(response)
                st.markdown(f"<small style='color: #718096;'>{resp_timestamp}</small>", unsafe_allow_html=True)
                
        # 4. Save response to state
        st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": resp_timestamp})
        
        # Rerun to clear the selected_prompt state if a button was clicked
        if selected_prompt:
            st.rerun()
