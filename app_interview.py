import streamlit as st
import google.generativeai as genai
import random

# --- 1. Page Configuration ---
st.set_page_config(page_title="AI Mock Interviewer", page_icon="🎓", layout="centered")

# --- 2. Secure Backend API Initialization ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ System Offline: Developer API Key missing in backend secrets.")
    st.stop()

# --- 3. UI Language Toggle ---
# 在最顶部加上语言切换开关
col1, col2 = st.columns([3, 1])
with col2:
    app_lang = st.radio("Language / 语言", ["English", "中文"], horizontal=True, label_visibility="collapsed")

# --- 4. Bilingual Dictionary for UI ---
ui = {
    "English": {
        "title": "🎓 AI Admissions Coach",
        "subtitle": "Practice your boarding school interview. Get instant feedback and brainstorming guidance.",
        "q_label": "##### 🗣️ Interview Question:",
        "hint_label": "Need a hint? What is the interviewer actually asking?",
        "btn_shuffle": "🔄 Shuffle Question",
        "ans_label": "Your Answer (Try your best, it doesn't have to be perfect):",
        "btn_submit": "Submit for AI Feedback",
        "msg_short": "Please provide a little more detail (at least a sentence or two) so I can help you expand it!",
        "msg_loading": "Analyzing and preparing brainstorming tips...",
        "msg_success": "✅ Feedback & Coaching Ready!",
        "prompt_lang_instruction": "Please write your ENTIRE evaluation, feedback, and all section headers in ENGLISH."
    },
    "中文": {
        "title": "🎓 AI 招生面试教练",
        "subtitle": "全真模拟美高面试。获取即时、犀利的反馈与头脑风暴指导（支持中英文答题）。",
        "q_label": "##### 🗣️ 面试问题：",
        "hint_label": "需要提示吗？招生官到底想听到什么？",
        "btn_shuffle": "🔄 换一道题",
        "ans_label": "你的回答（可以用中文或英文，大胆尝试）：",
        "btn_submit": "提交并获取 AI 深度反馈",
        "msg_short": "请提供更多细节（至少一两句话），这样我才能更好地帮你分析和扩展！",
        "msg_loading": "正在以顶尖美高标准分析并生成反馈...",
        "msg_success": "✅ 评估与辅导已就绪！",
        "prompt_lang_instruction": "IMPORTANT: Please write your ENTIRE evaluation, feedback, and brainstorming questions in fluent, professional CHINESE (Simplified). The section headers must also be translated into Chinese (e.g., '真实度与深度', '错失的机会', '头脑风暴')."
    }
}
t = ui[app_lang]

# --- 5. Bilingual Question Bank ---
QUESTIONS = [
    {
        "en": "How would your best friend describe you in three words, and why?",
        "zh": "你的好朋友会用哪三个词来形容你？为什么？",
        "intent_en": "💡 **What they are really asking:** Are you self-aware? What role do you play in your peer group? They want to hear specific traits like 'loyal' or 'analytical', backed up by a story.",
        "intent_zh": "💡 **潜台词：** 你有自我认知吗？你在朋友圈里扮演什么角色？他们不想听“聪明”或“善良”，他们想听“忠诚”、“善于分析”等，并需要你用一个具体故事来证明。"
    },
    {
        "en": "Tell me about a time you failed at something or made a mistake. What did you learn?",
        "zh": "告诉我一次你失败或犯错的经历。你学到了什么？",
        "intent_en": "💡 **What they are really asking:** How resilient are you? Do you blame others, or do you take responsibility? The actions you took to fix it matter most.",
        "intent_zh": "💡 **潜台词：** 你的抗挫折能力如何？你会推卸责任吗？他们真正关心的是：在失败后，你采取了什么具体的行动去弥补和改进。"
    },
    {
        "en": "What is something you’ve changed your mind about recently?",
        "zh": "最近有什么事情让你改变了原有的看法？",
        "intent_en": "💡 **What they are really asking:** Are you open-minded and capable of intellectual growth? Focus on *how* and *why* your perspective shifted.",
        "intent_zh": "💡 **潜台词：** 你的思想开放吗？具备心智成长的能力吗？重点描述你的观点是*如何*以及*为什么*发生转变的，展现你的反思能力。"
    }
]

# --- 6. Session State ---
if 'current_q_idx' not in st.session_state:
    st.session_state.current_q_idx = random.randint(0, len(QUESTIONS)-1)

def generate_new_question():
    st.session_state.current_q_idx = random.randint(0, len(QUESTIONS)-1)

q_obj = QUESTIONS[st.session_state.current_q_idx]

# --- 7. Main UI Rendering ---
st.markdown(f"<h3 style='text-align: center; color: #1e293b;'>{t['title']}</h3>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #64748b;'>{t['subtitle']}</p>", unsafe_allow_html=True)

st.markdown(t['q_label'])
st.info(f"**{q_obj['en'] if app_lang == 'English' else q_obj['zh']}**")

with st.expander(t['hint_label']):
    st.markdown(q_obj['intent_en'] if app_lang == 'English' else q_obj['intent_zh'])

st.button(t['btn_shuffle'], on_click=generate_new_question)

st.write("")
user_answer = st.text_area(t['ans_label'], height=150)

# --- 8. AI Evaluation Logic ---
if st.button(t['btn_submit'], type="primary", use_container_width=True):
    if len(user_answer.strip()) < 15:
        st.warning(t['msg_short'])
    else:
        with st.spinner(t['msg_loading']):
            model = genai.GenerativeModel(model_name="gemini-2.5-flash")
            
            prompt = f"""
            You are an elite US Boarding School Admissions Coach. You are tough but deeply encouraging.
            A 14-year-old applicant answered this question:
            Question: "{q_obj['en']}"
            Applicant's Answer: "{user_answer}"
            
            Evaluate this and guide them to a better answer. Format exactly as follows:
            
            ### 📊 Coach's Evaluation
            
            **1. Authenticity & Depth (Score: X/10):**
            *Feedback:* Be honest about whether this sounds like a real, specific teenager or a generic template. Point out if it lacks a personal story.
            
            **2. The Missed Opportunity (Red Flags):**
            *Feedback:* What is the core weakness of this answer?
            
            ### 🧠 Let's Brainstorm (How to fix it)
            To make this answer unforgettable, ask yourself these 3 questions. Try to rewrite your answer by picking ONE of these to focus on:
            * [Ask a specific, guiding question to help them dig into their memory]
            * [Ask a second guiding question focusing on a personal struggle]
            * [Ask a third guiding question focusing on their impact on others]
            
            {t['prompt_lang_instruction']}
            """
            
            try:
                response = model.generate_content(prompt)
                st.success(t['msg_success'])
                st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
