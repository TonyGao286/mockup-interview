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
col1, col2 = st.columns([3, 1])
with col2:
    app_lang = st.radio("Language / 语言", ["English", "中文"], horizontal=True, label_visibility="collapsed")

# --- 4. Bilingual Dictionary & Prompt Templates ---
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
        # 纯英文的底层 Prompt
        "prompt_template": """
You are an elite US Boarding School Admissions Coach. You are tough but deeply encouraging.
A 14-year-old applicant answered this question:
Question: "{question}"
Applicant's Answer: "{answer}"

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

Please write your ENTIRE response in ENGLISH.
"""
    },
    "中文": {
        "title": "🎓 AI 招生面试教练",
        "subtitle": "全真模拟美高面试。获取即时、犀利的反馈与头脑风暴指导。",
        "q_label": "##### 🗣️ 面试问题：",
        "hint_label": "需要提示吗？招生官到底想听到什么？",
        "btn_shuffle": "🔄 换一道题",
        "ans_label": "你的回答（可以用中文或英文，大胆尝试）：",
        "btn_submit": "提交并获取 AI 深度反馈",
        "msg_short": "请提供更多细节（至少一两句话），这样我才能更好地帮你分析和扩展！",
        "msg_loading": "正在以顶尖美高标准分析并生成反馈...",
        "msg_success": "✅ 评估与辅导已就绪！",
        # 纯中文的底层 Prompt（彻底解决英文顽固输出的问题）
        "prompt_template": """
你是一位顶尖的美国寄宿高中招生面试教练。你非常严格，但也充满鼓励。
一位14岁的申请者回答了以下面试问题：
问题："{question}"
申请者的回答："{answer}"

请评估这个回答并引导他们改进。请严格按照以下格式输出你的全部内容（必须全部使用中文）：

### 📊 教练深度评估

**1. 真实度与细节深度 (评分: X/10):**
*反馈:* 诚实地评价这听起来像是一个真实的、有血有肉的14岁少年，还是一个背诵中介模板的机器人。指出它是否缺乏真实的个人故事（Show, don't tell）。

**2. 错失的机会与红旗警告:**
*反馈:* 这个回答最核心的弱点是什么？哪一部分会让招生官失去兴趣？

### 🧠 头脑风暴 (如何绝地反击)
为了让这个回答令人过目不忘，请向申请者提出3个启发式的追问。引导他们从中挑选一个来重写答案：
* [提出一个具体的引导性问题，帮他们挖掘记忆中的细节]
* [提出第二个引导性问题，关注个人的挣扎或成长]
* [提出第三个引导性问题，关注他们对周围人或社区的影响]

重要：你的所有输出（包括标题、正文和建议）必须100%使用流畅专业的简体中文。
"""
    }
}
t = ui[app_lang]

# --- 5. Bilingual Question Bank ---
QUESTIONS = [
    {
        "en": "How would your best friend describe you in three words, and why?",
        "zh": "你的好朋友会用哪三个词来形容你？为什么？",
        "intent_en": "💡 **What they are really asking:** Are you self-aware? What role do you play in your peer group?",
        "intent_zh": "💡 **潜台词：** 你有自我认知吗？你在朋友圈里扮演什么角色？"
    },
    {
        "en": "Tell me about a time you failed at something or made a mistake. What did you learn?",
        "zh": "告诉我一次你失败或犯错的经历。你学到了什么？",
        "intent_en": "💡 **What they are really asking:** How resilient are you? Do you blame others, or do you take responsibility?",
        "intent_zh": "💡 **潜台词：** 你的抗挫折能力如何？你会推卸责任吗？行动胜于空谈。"
    },
    {
        "en": "What is something you’ve changed your mind about recently?",
        "zh": "最近有什么事情让你改变了原有的看法？",
        "intent_en": "💡 **What they are really asking:** Are you open-minded and capable of intellectual growth?",
        "intent_zh": "💡 **潜台词：** 你的思想开放吗？具备心智成长的能力吗？"
    }
]

# --- 6. Session State ---
if 'current_q_idx' not in st.session_state:
    st.session_state.current_q_idx = random.randint(0, len(QUESTIONS)-1)

def generate_new_question():
    st.session_state.current_q_idx = random.randint(0, len(QUESTIONS)-1)

q_obj = QUESTIONS[st.session_state.current_q_idx]
current_question_text = q_obj['en'] if app_lang == 'English' else q_obj['zh']

# --- 7. Main UI Rendering ---
st.markdown(f"<h3 style='text-align: center; color: #1e293b;'>{t['title']}</h3>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #64748b;'>{t['subtitle']}</p>", unsafe_allow_html=True)

st.markdown(t['q_label'])
st.info(f"**{current_question_text}**")

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
            
            # 直接调用对应语言的 Prompt 模板，并注入问题和回答
            final_prompt = t['prompt_template'].format(question=current_question_text, answer=user_answer)
            
            try:
                response = model.generate_content(final_prompt)
                st.success(t['msg_success'])
                st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
