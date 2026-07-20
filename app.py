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

# 🔐 Groq API কী চেকিং
GROQ_API_KEY = os.environ.get('GROQ_API_KEY') or st.sidebar.text_input("Enter Groq API Key:", type="password")

if not GROQ_API_KEY:
    st.warning("⚠️ Please provide a Groq API Key to activate the Master Router.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# 💾 ২. স্ট্রীমলিট স্টেট ম্যানেজমেন্ট (এক্সেল শিট মেমোরি ডেটাবেস)
if 'master_template' not in st.session_state:
    # এক্সেল থেকে সংগৃহীত হুবহু ৪৪টি অফিশিয়াল টাস্ক এবং ফিক্সড লিড টাইম কনফিগারেশন
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
    # এখানে ডাইনামিকালি নতুন আর্টিকেল মডেলের শিট ডেটা জমা হবে
    st.session_state.article_sheets = {}

# ফরোয়ার্ড ক্যালকুলেশন লিড টাইম ইঞ্জিন
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

# --- 🧠 ৩. মাস্টার রাউটার লজিক ---
MASTER_ROUTER_PROMPT = """
You are the "Master AI OS Router". Classify the request into exactly ONE category:
1. PLANNER (Timelines, deadlines, dashboard reviews, running tasks, sheet lookups)
2. WORKPLACE_EXECUTION (BOM structures, consumption math, waste calculation)
3. KNOWLEDGE_BASE (Decathlon SOP rules, factory compliance standards)
Output ONLY the single word uppercase.
"""

def route_request(user_input):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "system", "content": MASTER_ROUTER_PROMPT}, {"role": "user", "content": user_input}],
        temperature=0.0, max_tokens=10
    )
    return completion.choices[0].message.content.strip().upper()

def run_80_20_planner(user_input):
    prompt = "You are the expert Decathlon Footwear Planner. Filter the user's issue and extract the high-priority 20% milestones that block production or validation. Keep it concise."
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": user_input}],
        temperature=0.3
    )
    return completion.choices[0].message.content


# ========================================================
# 💻 ৪. STREAMLIT VISUAL DYNAMIC TABS INTERFACE
# ========================================================

st.title("👟 Decathlon Footwear Production OS")
st.markdown("---")

# 🤖 এআই অ্যাসিস্ট্যান্ট সেকশন
st.write("### 🤖 Interact with Master AI Agent")
user_query = st.text_area("Ask the Master Router (e.g., 'Analyze running tasks', 'Audit BOM consumption')", height=70)
if st.button("Send to Master Router", type="primary"):
    with st.spinner("Routing..."):
        decision = route_request(user_query)
        st.write(f"**🎯 Master Router Decision:** `{decision}`")
        if "PLANNER" in decision:
            st.markdown("#### 📊 Specialist Agent: **[80/20 Footwear Planner Agent]**")
            st.info(run_80_20_planner(user_query))
        elif "WORKPLACE_EXECUTION" in decision:
            st.markdown("#### 🤖 Specialist Agent: **[Workplace Execution Agent]**")
            st.warning("👟 Technical calculations and BOM verification triggers here.")
        elif "KNOWLEDGE_BASE" in decision:
            st.markdown("#### 📚 Specialist Agent: **[Knowledge Base Agent]**")
            st.warning("📚 Decathlon Quality SOP and standard lookups triggers here.")

st.markdown("---")

# 🎯 ৫. ডাইনামিক সাইডবার কন্ট্রোল: নিউ শিট অ্যাড করার প্যানেল (ম্যাক্রো রিপ্লেসমেন্ট)
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

# 🗂️ ৬. ডাইনামিক ট্যাব জেনারেশন ইঞ্জিন (হুবহু এক্সেল ট্যাব বার ক্লোন)
# ডিফল্ট ২টি স্ট্যাটিক ট্যাব এবং এর সাথে সাথে মেমরিতে থাকা সমস্ত নিউ আর্টিকেল ডাইনামিক শিট ট্যাব হিসেবে যুক্ত হবে
base_tabs = ["📋 Master_Template", "📊 Dashboard"]
dynamic_article_tabs = list(st.session_state.article_sheets.keys())
all_tabs_list = base_tabs + dynamic_article_tabs

# সমস্ত ট্যাব একসাথে জেনারেট করা
ui_tabs = st.tabs(all_tabs_list)

# --- 📋 TAB 1: MASTER_TEMPLATE (যেখানে আপনার মাস্টার প্ল্যান স্টোর থাকে) ---
with ui_tabs[0]:
    st.subheader("📋 Core Master Template Configuration")
    st.markdown("এটি আপনার সেন্ট্রাল লিด টাইম কনফিগারেশন। এখান থেকে ফিক্সড ডেস্ লজিক নিয়ে নতুন শিট জেনারেট হয়।")
    st.dataframe(pd.DataFrame(st.session_state.master_template), use_container_width=True, hide_index=True)

# --- 📊 TAB 2: DASHBOARD (রানিং এবং ওভারডিউ টাস্ক উইন্ডো) ---
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

# --- 📁 DYNAMIC TABS: INDIVIDUAL ARTICLE SHEETS (নতুন মডেল ইনপুট শিটগুলো) ---
for i, article_name in enumerate(dynamic_article_tabs):
    # স্ট্যাটিক ২টি ট্যাবের ইণ্ডেক্সের পর থেকে এসাইন করা হচ্ছে
    with ui_tabs[i + 2]:
        st.subheader(f"📑 Production Sheet for Style: `{article_name}`")
        df_current = st.session_state.article_sheets[article_name]
        
        st.markdown("💡 *Status পরিবর্তন করতে কলামের ড্রপডাউনে ডাবল ক্লিক করুন:*")
        
        # এক্সেলের মতো গ্রিড ইন্টারফেস
        edited_df = st.data_editor(
            df_current,
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Not Started", "Running", "Done", "Delayed"],
                    required=True,
                ),
                "SL No": st.column_config.TextColumn(disabled=True),
                "Task Name": st.column_config.TextColumn(disabled=True),
                "Fixed Days": st.column_config.NumberColumn(disabled=True),
                "Target Date": st.column_config.TextColumn(disabled=True),
                "WK No": st.column_config.TextColumn(disabled=True),
            },
            hide_index=True,
            use_container_width=True,
            key=f"editor_{article_name}"
        )
        
        # শিটের স্ট্যাটাস মেমরিতে ডাইনামিকালি সেভ রাখা
        if st.button(f"💾 Save Updates to {article_name}", key=f"btn_{article_name}"):
            st.session_state.article_sheets[article_name] = edited_df
            st.success(f"✅ {article_name} শিটের ডেটা সফলভাবে আপডেট করা হয়েছে!")
