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

# 🎨 🛠️ ULTIMATE STREAMLIT DATA EDITOR SCROLLBAR FIX
# এই CSS কোডটি সরাসরি Streamlit-এর ইন্টারনাল Glide Data Grid (টেবিল ইঞ্জিন) এর উইডথ লক ভেঙে স্ক্রলবার আনতে বাধ্য করবে
st.markdown("""
    <style>
        /* Target the actual canvas container inside Streamlit's data grid */
        [data-testid="stDataEditor"] > div:first-child {
            max-width: 100% !important;
            overflow-x: auto !important;
        }
        
        /* Force the inner scroll container to be active */
        .glideDataEditor-container, [data-testid="data-grid-canvas"] {
            overflow-x: auto !important;
            display: block !important;
        }

        /* 🎛️ Scrollbar Styling to make it highly visible */
        [data-testid="stDataEditor"] ::-webkit-scrollbar {
            height: 12px !important;
            width: 12px !important;
            display: block !important;
        }
        [data-testid="stDataEditor"] ::-webkit-scrollbar-track {
            background: #f8f9fa !important;
            border-radius: 6px !important;
        }
        [data-testid="stDataEditor"] ::-webkit-scrollbar-thumb {
            background: #bdc3c7 !important;
            border-radius: 6px !important;
            border: 2px solid #f8f9fa !important;
        }
        [data-testid="stDataEditor"] ::-webkit-scrollbar-thumb:hover {
            background: #7f8c8d !important;
        }
    </style>
""", unsafe_allow_html=True)

# 🔐 Groq API কী চেকিং
GROQ_API_KEY = os.environ.get('GROQ_API_KEY') or st.sidebar.text_input("Enter Groq API Key:", type="password")

if not GROQ_API_KEY:
    st.warning("⚠️ Please provide a Groq API Key to activate the Master Router Agent.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# 💾 ২. স্ট্রীমলিট স্টেট ম্যানেজমেন্ট
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

# --- 🧠 ৩. সেন্ট্রাল মাস্টার এজেন্ট ---
MASTER_ROUTER_PROMPT = """
You are the "Master AI Agent". Output exactly ONE word in uppercase: PLANNER_SPECIALIST, WORKPLACE_EXECUTION, or KNOWLEDGE_BASE.
"""

def route_request_to_agent(user_input):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "system", "content": MASTER_ROUTER_PROMPT}, {"role": "user", "content": user_input}],
        temperature=0.0, max_tokens=15
    )
    return completion.choices[0].message.content.strip().upper()

def run_planner_specialist_agent(user_input):
    prompt = "You are the 'Planner Specialist Agent'. Provide analysis on scheduling."
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

st.write("### 🤖 Master AI Agent Portal")
user_query = st.text_area("Communicate with Master Agent", height=70)

if st.button("Query Master Agent", type="primary"):
    with st.spinner("Processing..."):
        assigned_specialist = route_request_to_agent(user_query)
        st.write(f"**⚡ Master Agent Routing Decision:** `Delegated to {assigned_specialist}`")
        if "PLANNER_SPECIALIST" in assigned_specialist:
            st.info(run_planner_specialist_agent(user_query))

st.markdown("---")

# 🎯 ৫. সাইডবার কন্ট্রোল
st.sidebar.header("➕ Create New Article Sheet")
new_article_name = st.sidebar.text_input("New Model / Article Name:", placeholder="e.g., PLAY PROTECT 8882684")
initiation_date = st.sidebar.date_input("Select Project Initiation Date:", datetime.now())

if st.sidebar.button("🚀 Add Tab / Sheet"):
    if new_article_name.strip() and new_article_name not in st.session_state.article_sheets:
        base_dt = datetime.combine(initiation_date, datetime.min.time())
        st.session_state.article_sheets[new_article_name] = calculate_forward_timeline(base_dt)
        st.rerun()

# 🗂️ ৬. ডাইনামিক ট্যাব ইঞ্জিন
base_tabs = ["📋 Master_Template", "📊 Dashboard"]
dynamic_article_tabs = list(st.session_state.article_sheets.keys())
all_tabs_list = base_tabs + dynamic_article_tabs

ui_tabs = st.tabs(all_tabs_list)

# --- 📋 TAB 1: MASTER_TEMPLATE ---
with ui_tabs[0]:
    st.subheader("📋 Core Master Template Configuration")
    st.data_editor(
        pd.DataFrame(st.session_state.master_template),
        column_config={
            "SL No": st.column_config.TextColumn("SL No", width=100),
            "Task Name": st.column_config.TextColumn("Task Name", width=420),
            "Fixed Days": st.column_config.NumberColumn("Fixed Days", width=120),
        },
        hide_index=True,
        use_container_width=True, # মাস্টার ভিউ ৩টি কলামের জন্য ফুল উইডথ রাখাই বেস্ট
        key="master_template_editor"
    )

# --- 📊 TAB 2: DASHBOARD ---
with ui_tabs[1]:
    st.subheader("📊 Central Operations Dashboard Radar")
    if not st.session_state.article_sheets:
        st.info("💡 সাইডবার থেকে প্রজেক্ট ইনপুট দিয়ে নতুন মডেল শিট এড করুন।")

# --- 📁 DYNAMIC TABS: INDIVIDUAL ARTICLE SHEETS ---
for i, article_name in enumerate(dynamic_article_tabs):
    with ui_tabs[i + 2]:
        st.subheader(f"📑 Production Sheet for Style: `{article_name}`")
        df_current = st.session_state.article_sheets[article_name]
        
        # এখানে কলামের ফিক্সড পিক্সেল উইডথ বাড়িয়ে `use_container_width=False` করা হয়েছে যেন কন্টেন্ট ওভারফ্লো হয়ে স্ক্রলবার চলে আসে
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
                    width=180,
                    required=True,
                ),
            },
            hide_index=True,
            use_container_width=False, 
            key=f"editor_{article_name}"
        )
        
        if st.button(f"💾 Save Updates to {article_name}", key=f"btn_{article_name}"):
            st.session_state.article_sheets[article_name] = edited_df
            st.success(f"✅ {article_name} শিটের ডেটা সফলভাবে আপডেট করা হয়েছে!")
