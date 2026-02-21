import streamlit as st
import google.generativeai as genai
import random

# --- 1. Page Configuration ---
st.set_page_config(page_title="AI Mock Interviewer", page_icon="🎓", layout="centered")

# --- 2. Secure Backend API Initialization ---
# 这里直接读取服务器后端的密码，用户完全无感
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ System Offline: Developer API Key missing in backend secrets.")
    st.stop()

# --- 3. Top Boarding School Question Bank ---
QUESTIONS = [
    "How would your best friend describe you in three words, and why?",
    "If you had a free afternoon with no homework and no screens allowed, what would you do?",
    "Tell me about a time you failed at something or made a mistake. What did you learn?",
    "What is something you’ve changed your mind about recently?",
    "If you could create a new club at our school, what would it be?",
    "What book, movie, or article has deeply influenced how you see the world?",
    "Tell me about a time you had to work with someone you didn't agree with.",
    "If you had to teach a class on any subject to your peers, what would you teach?",
    "What is a problem in your local community or the world that you genuinely want to solve?"
]

# --- 4. Session State ---
if 'current_question' not in st.session_state:
    st.session_state.current_question = random.choice(QUESTIONS)

def generate_new_question():
    st.session_state.current_question = random.choice(QUESTIONS)

# --- 5. Clean UI ---
st.markdown("<h3 style='text-align: center; color: #1e293b;'>🎓 AI Admissions Officer</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b;'>Practice your boarding school interview. Get instant, tough feedback.</p>", unsafe_allow_html=True)

st.markdown("##### 🗣️ Interview Question:")
st.info(f"**{st.session_state.current_question}**")

st.button("🔄 Shuffle Question", on_click=generate_new_question)

st.write("")
user_answer = st.text_area("Your Answer (Be authentic and specific):", height=150, placeholder="Well, I think...")

# --- 6. AI Evaluation ---
if st.button("Submit for AI Feedback", type="primary", use_container_width=True):
    if len(user_answer.strip()) < 20:
        st.warning("Please provide a more detailed answer for meaningful feedback (at least a few sentences).")
    else:
        with st.spinner("Analyzing your response with Top 30 Boarding School standards..."):
            model = genai.GenerativeModel(model_name="gemini-2.5-flash")
            
            prompt = f"""
            You are a seasoned, tough Director of Admissions at a top-tier US Boarding School (e.g., Groton, Andover).
            A 14-year-old applicant has just answered this interview question:
            Question: "{st.session_state.current_question}"
            Applicant's Answer: "{user_answer}"
            
            Critique this answer strictly. Do not be overly nice. 
            Format exactly as follows:
            
            ### 📊 Admissions Evaluation
            **1. Authenticity Score (Out of 10):** [Score]
            *Critique:* Does this sound like a real teenager or a memorized consultant script? Point out any clichés.
            
            **2. Depth & Detail Score (Out of 10):** [Score]
            *Critique:* Did they "show" instead of "tell"? Did they provide a specific anecdote?
            
            **3. Red Flags:**
            *Critique:* What part of this answer would make an admissions officer lose interest? 
            
            **4. The Pivot (How to fix it):**
            *Advice:* Give ONE actionable tip to make this answer unforgettable.
            """
            
            try:
                response = model.generate_content(prompt)
                st.success("✅ Feedback Ready!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
