import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import re
from groq import Groq

# 📄 ১. পেজ এবং থিম কনফিগারেশন
st.set_page_config(
    page_title="Footwear AI OS",
    page_icon="👟",
    layout="wide"
)

# 🔐 Groq API কী চেকিং
GROQ_API_KEY = os.environ.get('GROQ_API_KEY') or st.sidebar.text_input("Enter Groq API Key:", type="password")

if not GROQ_API_KEY:
    st.warning("⚠️ Please provide a Groq API Key to activate the Master Agent.")
    st.stop()

# Groq ক্লায়েন্ট ইনিশিয়েট করা
client = Groq(api_key=GROQ_API_KEY)

# 💾 ২. স্ট্রীমলিট স্টেট ম্যানেজমেন্ট (এক্সেল ব্যাকএন্ড ডাটাবেস)
if 'projects' not in st.session_state:
    st.session_state.projects = {}

# ফিক্সড মাস্টার লিড টাইম লজিক (মাস্টার টেমপ্লেট)
TASK_LEAD_TIMES = [
    ("Go ship", 0),  
    ("Go prod", -27),
    ("Go Indus: Passed", -29),
    ("Go Indus: Start", -50),
    ("CFM Sample: Validation", -50),
    ("CFM Sample: ETD", -64),
    ("CFM Sample: Start", -72),
    ("F&R sample:Validation", -72),
    ("F&R sample: End", -93),
    ("F&R sample: Start", -100),
    ("F&R Mold: Validation", -100),
    ("F&R Mold: ETA", -107),
    ("F&R Mold: Order", -177),
    ("Proto: Validation", -177),
    ("Proto: End", -184),
    ("Proto: Start", -191),
    ("Bulk Material: ETA", -198),
    ("Bulk Material: Order", -288),
    ("BOM: DKT Validation", -295),
    ("Sample Mold: Validation", -295),
    ("Sample Mold: ETA", -302),
    ("Sample Mold: Order", -344),
    ("Sample Received: Raw Materials", -351),
    ("Sample Order: Raw Materials", -381),
    ("Consumption, CBD (sharing)", -381),
    ("Project Initiation", -381)
]

# ব্যাকওয়ার্ড ক্যালকুলেশন ইঞ্জিন
def generate_timeline_df(base_date):
    tasks_list = []
    for task, days in reversed(TASK_LEAD_TIMES):
        target_date = base_date + timedelta(days=days)
        wk_no = target_date.isocalendar()[1]
        
        status = "Pending"
        if "Initiation" in task or "Sharing" in task.lower() or "consumption" in task.lower():
            status = "Done"
            
        tasks_list.append({
            "Task Name": task,
            "Target Date": target_date.strftime('%Y-%m-%d'),
            "WK No": f"Wk {wk_no}",
            "Status": status
        })
    return pd.DataFrame(tasks_list)

# --- 🧠 ৩. স্পেশালাইজড এজেন্ট: 80/20 PLANNER AGENT (AI) ---
PLANNER_SYSTEM_PROMPT = """
You are the "Footwear Production 80/20 Planner". Your job is to act as a highly experienced PPC Manager.
Analyze the user's input, project details, or questions regarding their footwear production timelines. 
Focus heavily on the top 20% high-leverage milestones (like Material Orders, Sample ETD, BOM Validation) that prevent line stoppage.
Respond professionally using clear bullet points.
"""

def run_80_20_planner(user_input):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        temperature=0.3
    )
    return completion.choices[0].message.content

# --- 🧠 ৪. মাস্টার রাউটার প্রম্পট (Router Logic) ---
MASTER_ROUTER_PROMPT = """
You are the "Master AI OS Router". Classify the user's request into exactly ONE category:
1. PLANNER (Choose this for anything related to timelines, schedules, 80/20 updates, tracking sheets, or dates)
2. WORKPLACE_EXECUTION (Choose this for technical calculations, BOM audits, or wastage analysis)
3. KNOWLEDGE_BASE (Choose this for Decathlon SOP, specifications, or reference lookups)

CRITICAL: Output ONLY the word 'PLANNER', 'WORKPLACE_EXECUTION', or 'KNOWLEDGE_BASE'. Do not add any punctuation.
"""

def route_request(user_input):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": MASTER_ROUTER_PROMPT},
            {"role": "user", "content": user_input}
        ],
        temperature=0.0,
        max_tokens=10
    )
    return completion.choices[0].message.content.strip().upper()


# ========================================================
# 💻 ৫. STREAMLIT VISUAL UI WITH INTEGRATED MASTER AGENT
# ========================================================

st.title("👟 Footwear AI OS — Intelligent Workspace")
st.markdown("---")

# 🧠 সেকশন ১: সেন্ট্রাল মাস্টার এজেন্ট ইন্টারফেস
st.write("### 🤖 Interact with Master AI Agent")
user_query = st.text_area("Ask anything (e.g., 'What are the critical tasks for a style?', 'Calculate leather wastage...', 'Show Decathlon SOP')", height=80, placeholder="Type your query here...")
submit_query = st.button("Send to Master Router", type="primary")

if submit_query and user_query:
    with st.spinner("Master Agent is routing your request..."):
        decision = route_request(user_query)
        st.write(f"**🎯 Master Router Decision:** `{decision}`")
        st.markdown("---")
        
        if "PLANNER" in decision:
            st.markdown("#### 📊 Specialist Agent: **[80/20 Footwear Planner Agent]**")
            
            # এআই প্ল্যানারের রেসপন্স শো করা
            ai_analysis = run_80_20_planner(user_query)
            st.info(ai_analysis)
            
            # টেক্সট ইনপুটের ভেতর যদি কোনো ডেট এবং নিউ স্টাইল ডিটেক্ট হয়, তবে অটো শিট ক্রিয়েশন প্রম্পট দেবে
            date_match = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2})|(\d{2}[-/]\d{2}[-/]\d{4})', user_query)
            if date_match and ("new" in user_query.lower() or "sheet" in user_query.lower()):
                st.success("💡 **System Note:** এটি একটি নতুন প্ল্যানিং রিকোয়েস্ট। নিচে **'Specialist Planner Sheet Engine'** ব্যবহার করে সরাসরি আপনার এক্সেল ডাটাবেসে শিটটি যুক্ত করে নিন।")
                
        elif "WORKPLACE_EXECUTION" in decision:
            st.markdown("#### 🤖 Specialist Agent: **[Workplace Execution Agent]**")
            st.warning("👟 [Workplace Execution Module]: এটি পরবর্তী ধাপে আপনার BOM list অডিট এবং Consumption ক্যালকুলেটরের সাথে যুক্ত হবে।")
            
        elif "KNOWLEDGE_BASE" in decision:
            st.markdown("#### 📚 Specialist Agent: **[Knowledge Base Agent]**")
            st.warning("📚 [Knowledge Base Module]: এটি পরবর্তী ধাপে Decathlon SOP নির্দেশিকার সাথে কানেক্ট হবে।")
            
        st.markdown("---")

# 📊 সেকশন ২: আপনার এক্সেল প্ল্যানিং ড্যাশবোর্ড (Specialist Planner Sheet Engine)
st.write("## 🛠️ Specialist Planner Sheet Engine (Excel Dashboard Clone)")

# নেভিগেশন ট্যাব
tab_dashboard, tab_new_article, tab_all_sheets = st.tabs([
    "📊 Central Dashboard", 
    "➕ Add New Article (New Sheet)", 
    "📁 View/Edit Article Sheets"
])

# ---- TAB 1: CENTRAL DASHBOARD ----
with tab_dashboard:
    if not st.session_state.projects:
        st.info("💡 বর্তমানে কোনো অ্যাক্টিভ প্রজেক্ট শিট নেই। 'Add New Article' ট্যাব থেকে প্রথম শিট তৈরি করুন।")
    else:
        total_articles = len(st.session_state.projects)
        st.metric("Total Running Articles (Sheets)", total_articles)
        
        dashboard_summary = []
        for name, df in st.session_state.projects.items():
            xf_date = df[df["Task Name"] == "Go ship"]["Target Date"].values[0]
            prod_date = df[df["Task Name"] == "Go prod"]["Target Date"].values[0]
            
            done_tasks = len(df[df["Status"] == "Done"])
            total_tasks = len(df)
            progress = int((done_tasks / total_tasks) * 100)
            
            dashboard_summary.append({
                "Article/Style Name": name,
                "Go Prod Date": prod_date,
                "Final XF Date": xf_date,
                "Progress": f"{progress}%",
                "Total Tasks": total_tasks
            })
            
        st.write("### 📋 Active Style Master List")
        st.dataframe(pd.DataFrame(dashboard_summary), use_container_width=True, hide_index=True)

# ---- TAB 2: ADD NEW ARTICLE (NEW SHEET) ----
with tab_new_article:
    st.write("### ➕ Launch New Footwear Style Sheet")
    
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        new_style_name = st.text_input("Style / Article Name:", placeholder="e.g., 380148 - PLAY 100", key="new_style_name_input")
    with col_input2:
        new_xf_date = st.date_input("Proposed XF Date (Shipment Date):", datetime.now() + timedelta(days=365), key="new_xf_date_input")
        
    if st.button("🚀 Create Article Sheet & Generate Timeline", type="secondary"):
        if not new_style_name.strip():
            st.error("⚠️ অনুগ্রহ করে একটি সঠিক আর্টিকেলের নাম দিন।")
        elif new_style_name in st.session_state.projects:
            st.warning(f"⚠️ '{new_style_name}' নামে অলরেডি একটি শিট রয়েছে!")
        else:
            base_datetime = datetime.combine(new_xf_date, datetime.min.time())
            generated_df = generate_timeline_df(base_datetime)
            
            # মেমরিতে নতুন এক্সেল শিট পুশ
            st.session_state.projects[new_style_name] = generated_df
            st.success(f"🎉 সাফল্যজনক! '{new_style_name}' শিটটি সফলভাবে যুক্ত হয়েছে।")

# ---- TAB 3: VIEW ARTICLE SHEETS ----
with tab_all_sheets:
    if not st.session_state.projects:
        st.info("কোনো ডাটা শিট পাওয়া যায়নি।")
    else:
        selected_style = st.selectbox("🎯 Select Active Sheet to View/Edit:", list(st.session_state.projects.keys()))
        
        if selected_style:
            st.write(f"### 📑 Worksheet for Style: `{selected_style}`")
            current_df = st.session_state.projects[selected_style]
            
            st.markdown("💡 *Status পরিবর্তন করতে কলামে ডাবল ক্লিক করুন:*")
            
            # এক্সেলের মতো ইন্টারঅ্যাক্টিভ গ্রিড এডিটর
            edited_df = st.data_editor(
                current_df,
                column_config={
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["Pending", "Running", "Done", "Delayed"],
                        required=True,
                    ),
                    "Target Date": st.column_config.TextColumn(disabled=True),
                    "Task Name": st.column_config.TextColumn(disabled=True),
                    "WK No": st.column_config.TextColumn(disabled=True),
                },
                hide_index=True,
                use_container_width=True,
                key=f"editor_{selected_style}"
            )
            
            if st.button(f"💾 Save Changes to {selected_style} Sheet"):
                st.session_state.projects[selected_style] = edited_df
                st.success(f"✅ {selected_style} শিটের স্ট্যাটাস আপডেট সেভ করা হয়েছে!")
