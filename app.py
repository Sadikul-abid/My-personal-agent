import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from groq import Groq

# 📄 ১. পেজ কনফিগারেশন
st.set_page_config(
    page_title="Decathlon Footwear Production OS",
    page_icon="👟",
    layout="wide"
)

# 🎨 🛠️ ADVANCED WRAPPER CSS FOR FORCED SCROLLBAR
# এটি পুরো টেবিলের প্যারেন্ট কন্টেইনারকে স্ক্রিনের ভেতরে আটকে না রেখে ডানে প্রসারিত হতে সাহায্য করবে
st.markdown("""
    <style>
        /* Force the inner wrapper of Streamlit data components to show horizontal scrollbar always */
        [data-testid="stDataFrameTotalContainer"] {
            overflow-x: auto !important;
            display: block !important;
        }
        .element-container iframe, div[data-testid="stDataEditor"] {
            width: 100% !important;
            overflow-x: auto !important;
        }
        /* Style the physical scrollbar track and thumb to ensure it is thick and visible */
        ::-webkit-scrollbar {
            height: 14px !important;
            width: 14px !important;
            display: block !important;
        }
        ::-webkit-scrollbar-track {
            background: #f1f3f5 !important;
            border-radius: 4px !important;
        }
        ::-webkit-scrollbar-thumb {
            background: #adb5bd !important;
            border-radius: 4px !important;
            border: 2px solid #f1f3f5 !important;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #6c757d !important;
        }
    </style>
""", unsafe_allow_html=True)

# 🔐 Groq API কী চেকিং
GROQ_API_KEY = os.environ.get('GROQ_API_KEY') or st.sidebar.text_input("Enter Groq API Key:", type="password")

if not GROQ_API_KEY:
    st.warning("⚠️ Please provide a Groq API Key to activate the Master Router Agent.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# 💾 ২. স্ট্রীমলিট স্টেট ম্যানেজমেন্ট (মেমোরি ডেটাবেস)
if 'master_template' not in st.session_state:
    st.session_state.master_template = [
        {"SL No": 1.0, "Task Name": "Project Initiation", "Fixed Days": 0.0},
        {"SL No": 2.0, "Task Name": "Consumption, CBD (sharing)\n", "Fixed Days": 0.0},
        {"SL No": 3.0, "Task Name": "Sample Order: Raw Materials", "Fixed Days": 30.0},
        {"SL No": 4.0, "Task Name": "Sample Received: Raw Materials", "Fixed Days": 7.0},
        {"SL No": 5.0, "Task Name": "Sample Order: Threads/Packing Materials", "Fixed Days": 15.0},
        {"SL No": 6.0, "Task Name": "Sample Received: Threads/Packing Materials", "Fixed Days": 7.0},
        {"SL No": 12.0, "Task Name": "BOM: DKT Validation", "Fixed Days": 7.0},
        {"SL No": "", "Task Name": "Bulk Material: Order", "Fixed Days": 90.0},
        {"SL No": "", "Task Name": "Bulk Material: ETA", "Fixed Days": 7.0},
        {"SL No": 21.0, "Task Name": "Sample Mold: Order", "Fixed Days": 42.0},
        {"SL No": 23.0, "Task Name": "Samlpe Mold: ETA", "Fixed Days": 7.0},
        {"SL No": 24.0, "Task Name": "Sample Mold: Validation", "Fixed Days": 0.0},
        {"SL No": 16.0, "Task Name": "Proto: Start", "Fixed Days": 7.0},
        {"SL No": 17.0, "Task Name": "Proto: End", "Fixed Days": 7.0},
        {"SL No": 18.0, "Task Name": "Proto: Validation", "Fixed Days": 0.0},
        {"SL No": 26.0, "Task Name": "FSR Mold: Order", "Fixed Days": 70.0},
        {"SL No": 28.0, "Task Name": "FSR Mold: ETA", "Fixed Days": 7.0},
        {"SL No": 29.0, "Task Name": "FSR Mold: Validation", "Fixed Days": 0.0},
        {"SL No": 30.0, "Task Name": "FSR Sample: Start", "Fixed Days": 7.0},
        {"SL No": 31.0, "Task Name": "FSR Sample: End", "Fixed Days": 21.0},
        {"SL No": 32.0, "Task Name": "FSR Sample:Validation", "Fixed Days": 0.0},
        {"SL No": 37.0, "Task Name": "CFM Sample: Start", "Fixed Days": 6.0},
        {"SL No": 39.0, "Task Name": "CFM Sample: ETD", "Fixed Days": 14.0},
        {"SL No": 40.0, "Task Name": "CFM Sample: Validation", "Fixed Days": 0.0},
        {"SL No": 42.0, "Task Name": "Go Indus: Start", "Fixed Days": 21.0},
        {"SL No": 44.0, "Task Name": "Go Indus: Passed", "Fixed Days": 2.0},
        {"SL No": 45.0, "Task Name": "Go prod", "Fixed Days": 27.0},
        {"SL No": 46.0, "Task Name": "Go ship", "Fixed Days": 56.0},
        {"SL No": 19.0, "Task Name": "CDD", "Fixed Days": 0.0},
        {"SL No": 7.0, "Task Name": "Sample Materials: Approval", "Fixed Days": 0.0},
        {"SL No": 8.0, "Task Name": "Duplibox: Ask", "Fixed Days": 28.0},
        {"SL No": 9.0, "Task Name": "Duplibox: Received", "Fixed Days": 7.0},
        {"SL No": 10.0, "Task Name": "Duplibox: Evaluation", "Fixed Days": 7.0},
        {"SL No": 11.0, "Task Name": "BOM: Preparation for validation", "Fixed Days": 7.0},
        {"SL No": 13.0, "Task Name": "BOM: OMC BOM", "Fixed Days": 1.0},
        {"SL No": 14.0, "Task Name": "Trim Card: Start", "Fixed Days": 1.0},
        {"SL No": 15.0, "Task Name": "Trim Card: End: Approval", "Fixed Days": 3.0},
        {"SL No": 19.0, "Task Name": "DCR Evaluation: Start", "Fixed Days": 0.0},
        {"SL No": 25.0, "Task Name": "Sample size proto trial", "Fixed Days": 0.0},
        {"SL No": 33.0, "Task Name": "CTF & PVP Test: Start", "Fixed Days": 30.0},
        {"SL No": 34.0, "Task Name": "CTF & PVP Test: Report", "Fixed Days": 7.0},
        {"SL No": 35.0, "Task Name": "Tooling Ready: Start", "Fixed Days": 7.0},
        {"SL No": 36.0, "Task Name": "Tooling Ready: End", "Fixed Days": 7.0},
        {"SL No": 41.0, "Task Name": "RTI:CDCT file: Start", "Fixed Days": 5.0},
        {"SL No": 20.0, "Task Name": "Commercialization meeting", "Fixed Days": 0.0}
    ]

if 'article_sheets' not in st.session_state:
    st.session_state.article_sheets = {}

def calculate_forward_timeline(initiation_date):
    tasks_list = []
    current_date = initiation_date
    
    for task_info in st.session_state.master_template:
        current_date = current_date + timedelta(days=int(task_info["Fixed Days"]))
        wk_no = current_date.isocalendar()[1]
        
        status = "Not Started"
        if task_info["Task Name"] == "Project Initiation":
            status = "Done"
            
        tasks_list.append({
            "SL No": task_info["SL No"],
            "Task Name": task_info["Task Name"].strip(),
            "Fixed Days": task_info["Fixed Days"],
            "Target Date": current_date.strftime('%Y-%m-%d'),
            "WK No": f"Wk {wk_no}",
            "Status": status
        })
    return pd.DataFrame(tasks_list)

# --- 🧠 ৩. সেন্ট্রাল মাস্টার এজেন্ট এবং স্পেশালিস্ট গেটওয়ে ---
MASTER_ROUTER_PROMPT = """
You are the "Master AI Agent". Your job is to analyze the user's request and intelligently delegate it to the correct Specialist Agent:
1. PLANNER_SPECIALIST: Use this for timelines, production critical paths, milestones, running/overdue tasks, sheet lookups, or date shift logic.
2. WORKPLACE_EXECUTION: Use this for Bills of Materials (BOM) management, material consumption formulas, and waste calculations.
3. KNOWLEDGE_BASE: Use this for Decathlon Footwear SOPs, quality assurance rules, and compliance standards.

Output exactly ONE word in uppercase: PLANNER_SPECIALIST, WORKPLACE_EXECUTION, or KNOWLEDGE_BASE.
"""

def route_request_to_agent(user_input):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "system", "content": MASTER_ROUTER_PROMPT}, {"role": "user", "content": user_input}],
        temperature=0.0, max_tokens=15
    )
    return completion.choices[0].message.content.strip().upper()

def run_planner_specialist_agent(user_input):
    prompt = """You are the 'Planner Specialist Agent' working under the Master AI Agent. 
    Your expertise is Decathlon footwear scheduling, target timelines, and critical path analysis. 
    Analyze the user's query and generate a strategic, high-priority 80/20 summary of tasks, focus areas, or potential risks."""
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": user_input}],
        temperature=0.3
    )
    return completion.choices[0].message.content


# ========================================================
# 💻 ৪. UI INTERFACE & AGENT HUB
# ========================================================

st.title("👟 Decathlon Footwear Production OS")
st.markdown("---")

# 🤖 সেন্ট্রাল মাস্টার এজেন্ট উইন্ডো
st.write("### 🤖 Master AI Agent Portal")
user_query = st.text_area("Communicate with Master Agent (e.g., 'Verify overdue tasks on current styles', 'Analyze critical path')", height=70)

if st.button("Query Master Agent", type="primary"):
    with st.spinner("Master Agent routing query to Specialist..."):
        assigned_specialist = route_request_to_agent(user_query)
        st.write(f"**⚡ Master Agent Routing Decision:** `Delegated to {assigned_specialist}`")
        
        if "PLANNER_SPECIALIST" in assigned_specialist:
            st.markdown("#### 📊 Selected Sub-Agent: **[Planner Specialist Agent]**")
            analysis_result = run_planner_specialist_agent(user_query)
            st.info(analysis_result)
        elif "WORKPLACE_EXECUTION" in assigned_specialist:
            st.markdown("#### 🤖 Selected Sub-Agent: **[Workplace Execution Agent]**")
            st.warning("👟 Triggering technical calculations and BOM component evaluations...")
        elif "KNOWLEDGE_BASE" in assigned_specialist:
            st.markdown("#### 📚 Selected Sub-Agent: **[Knowledge Base Agent]**")
            st.warning("📚 Consulting Decathlon Quality SOPs and laboratory validation books...")

st.markdown("---")

# 🎯 ৫. সাইডবার কন্ট্রোল
st.sidebar.header("➕ Create New Article Sheet")
new_article_name = st.sidebar.text_input("New Model / Article Name:", placeholder="e.g., 348793 - PLAY PROTECT")
initiation_date = st.sidebar.date_input("Select Project Initiation Date:", datetime.now())

if st.sidebar.button("🚀 Add Tab / Sheet"):
    if not new_article_name.strip():
        st.sidebar.error("⚠️ Please enter a unique article name.")
    elif new_article_name in st.session_state.article_sheets:
        st.sidebar.warning("⚠️ This article sheet already exists!")
    else:
        base_dt = datetime.combine(initiation_date, datetime.min.time())
        st.session_state.article_sheets[new_article_name] = calculate_forward_timeline(base_dt)
        st.sidebar.success(f"🎉 Tab '{new_article_name}' added successfully!")
        st.rerun()

# 🗂️ ৬. ডাইনামিক ট্যাব জেনারেশন ইঞ্জিন
base_tabs = ["📋 Master_Template", "📊 Dashboard"]
dynamic_article_tabs = list(st.session_state.article_sheets.keys())
all_tabs_list = base_tabs + dynamic_article_tabs

ui_tabs = st.tabs(all_tabs_list)

# --- 📋 TAB 1: MASTER_TEMPLATE ---
with ui_tabs[0]:
    st.subheader("📋 Core Master Template Configuration")
    # মাস্টার ভিউ কন্টেইনারকেও ডাইনামিক এবং ফিক্সড উইডথ দিয়ে রেডি করা হয়েছে
    st.data_editor(
        pd.DataFrame(st.session_state.master_template),
        column_config={
            "SL No": st.column_config.TextColumn("SL No", width=100),
            "Task Name": st.column_config.TextColumn("Task Name", width=400),
            "Fixed Days": st.column_config.NumberColumn("Fixed Days", width=150),
        },
        hide_index=True,
        use_container_width=False,
        key="master_template_editor"
    )

# --- 📊 TAB 2: DASHBOARD ---
with ui_tabs[1]:
    st.subheader("📊 Central Operations Dashboard Radar")
    
    if not st.session_state.article_sheets:
        st.info("💡 বর্তমানে কোনো সক্রিয় মডেল শিট নেই। সাইডবার থেকে প্রজেক্ট ইনপুট দিয়ে নতুন শিট ট্যাব এড করুন।")
    else:
        today_str = datetime.now().strftime('%Y-%m-%d')
        running_tasks = []
        overdue_tasks = []
        
        for p_name, df in st.session_state.article_sheets.items():
            for idx, row in df.iterrows():
                t_date = row["Target Date"]
                status = row["Status"]
                
                if status != "Done":
                    if t_date == today_str:
                        running_tasks.append({"Project / Article": p_name, "Task Name": row["Task Name"], "Target Date": t_date, "Status": status})
                    elif t_date < today_str:
                        overdue_tasks.append({"Project / Article": p_name, "Task Name": row["Task Name"], "Target Date": t_date, "Status": status})
                        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🏃‍♂️ RUNNING TASKS (TODAY)")
            if running_tasks:
                st.dataframe(pd.DataFrame(running_tasks), use_container_width=True, hide_index=True)
            else:
                st.success("✅ আজকে কোনো পেন্ডিং রানিং টাস্ক নেই!")
        with col2:
            st.markdown("#### 🛑 OVERDUE / DELAYED TASKS")
            if overdue_tasks:
                st.dataframe(pd.DataFrame(overdue_tasks), use_container_width=True, hide_index=True)
            else:
                st.success("🎉 চমৎকার! কোনো ব্যাকলগ বা ওভারডিউ টাস্ক নেই।")

# --- 📁 DYNAMIC TABS: INDIVIDUAL ARTICLE SHEETS ---
# এখানে কলামের ফিক্সড টোটাল পিক্সেল উইডথ স্পেসিফিক করে দেওয়া হয়েছে যেন স্ক্রলবার কাজ করতে বাধ্য হয়
for i, article_name in enumerate(dynamic_article_tabs):
    with ui_tabs[i + 2]:
        st.subheader(f"📑 Production Sheet for Style: `{article_name}`")
        df_current = st.session_state.article_sheets[article_name]
        
        st.markdown("💡 *ডানে-বামে সরাতে নিচের স্ক্রলবার ব্যবহার করুন:*")
        
        # টেবিল গ্রিড কনফিগারেশন
        edited_df = st.data_editor(
            df_current,
            column_config={
                "SL No": st.column_config.TextColumn("SL No", width=120, disabled=True),
                "Task Name": st.column_config.TextColumn("Task Name", width=450, disabled=True),
                "Fixed Days": st.column_config.NumberColumn("Fixed Days", width=120, disabled=True),
                "Target Date": st.column_config.TextColumn("Target Date", width=180, disabled=True),
                "WK No": st.column_config.TextColumn("WK No", width=120, disabled=True),
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Not Started", "Running", "Done", "Delayed"],
                    width=160,
                    required=True,
                ),
            },
            hide_index=True,
            use_container_width=False,  # এটিকে False রাখা হয়েছে স্ক্রলবার পপ-আপ করানোর জন্য
            key=f"editor_{article_name}"
        )
        
        if st.button(f"💾 Save Updates to {article_name}", key=f"btn_{article_name}"):
            st.session_state.article_sheets[article_name] = edited_df
            st.success(f"✅ {article_name} শিটের ডেটা সফলভাবে আপডেট করা হয়েছে!")
