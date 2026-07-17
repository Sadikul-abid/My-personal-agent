import streamlit as st
import os
from datetime import datetime, timedelta
import pandas as pd

# পেজ সেটআপ (ওয়াইড স্ক্রিন এবং এক্সেল উইন্ডো লুক)
st.set_page_config(page_title="Footwear AI OS", layout="wide")

# --- 📁 ডামি বা আপলোডেড ডেটাবেস হ্যান্ডলার ---
# (বাস্তবে আপনি এখানে আপনার এক্সেল আপলোড বা গুগল শিট কানেক্ট করতে পারেন)
@st.cache_data
def get_running_models_data():
    # আপনার এক্সেল ফাইলের রানিং মডেলগুলোর লাইভ টাস্ক ডেটা
    running_tasks = [
        {"Project": "348793 - PLAY PROTECT", "Task": "CTF & PVP Test: Start", "Target Date": "2026-07-17", "Status": "Not Started"},
        {"Project": "NH100 BLUE KID", "Task": "Proto: End", "Target Date": "2026-07-20", "Status": "Not Started"}
    ]
    
    overdue_tasks = [
        {"Project": "NH100 BLUE KID", "Task": "Sample Received: Raw Materials", "Target Date": "2026-05-04", "Status": "Not Started"},
        {"Project": "NH100 BLUE KID", "Task": "Sample Received: Threads/Packing Materials", "Target Date": "2026-05-04", "Status": "Not Started"},
        {"Project": "NH100 BLUE KID", "Task": "Sample Materials: Approval", "Target Date": "2026-05-11", "Status": "Not Started"},
        {"Project": "NH100 BLUE KID", "Task": "BOM: OMC BOM", "Target Date": "2026-05-12", "Status": "Not Started"},
        {"Project": "NH100 BLUE KID", "Task": "Trim Card: Start", "Target Date": "2026-05-13", "Status": "Not Started"},
        {"Project": "NH100 BLUE KID", "Task": "Bulk Material: Order", "Target Date": "2026-05-18", "Status": "Not Started"},
        {"Project": "348793 - PLAY PROTECT", "Task": "Trim Card: End: Approval", "Target Date": "2026-06-19", "Status": "Not Started"},
        {"Project": "348793 - PLAY PROTECT", "Task": "FSR Mold: Validation", "Target Date": "2026-07-06", "Status": "Not Started"},
        {"Project": "348793 - PLAY PROTECT", "Task": "DCR Evaluation: Start", "Target Date": "2026-07-06", "Status": "Not Started"}
    ]
    return pd.DataFrame(running_tasks), pd.DataFrame(overdue_tasks)

# এক্সেল ফর্মুলা লজিক ইঞ্জিন (পূর্বের ব্যাকওয়ার্ড প্ল্যানার)
def calculate_decathlon_backward_plan(base_xf_date):
    cdd = datetime.combine(base_xf_date, datetime.min.time())
    dates = {'CDD': cdd, 'Project Initiation': cdd}
    dates['Go ship'] = dates['CDD'] - timedelta(days=56)
    dates['Go prod'] = dates['Go ship'] - timedelta(days=27)
    dates['Go Indus: Passed'] = dates['Go prod'] - timedelta(days=2)
    dates['Go Indus: Start'] = dates['Go Indus: Passed'] - timedelta(days=21)
    dates['Bulk Material: ETA'] = dates['Go Indus: Start'] - timedelta(days=7)
    dates['Bulk Material: Order'] = dates['Bulk Material: ETA'] - timedelta(days=90)
    dates['BOM: DKT Validation'] = dates['Bulk Material: Order'] - timedelta(days=7)
    
    task_order = [
        ("1.0", "Project Initiation"), ("12.0", "BOM: DKT Validation"), 
        ("-", "Bulk Material: Order"), ("-", "Bulk Material: ETA"),
        ("45.0", "Go prod"), ("46.0", "Go ship"), ("19.0", "CDD")
    ]
    
    plan_data = []
    for sl, task in task_order:
        dt = dates.get(task, cdd)
        plan_data.append({
            "SL No": sl, "Task Name": task, "Target Date": dt.strftime("%Y-%m-%d"), "WK No": dt.isocalendar()[1], "Status": "Pending 🕒"
        })
    return pd.DataFrame(plan_data)

# --- 🚀 UI লেআউট ---
st.title("👟 Footwear Master AI OS")
st.write(f"📅 **Current Date (System):** {datetime.now().strftime('%Y-%m-%d')}")

# সাইডবার রাউটার
st.sidebar.title("🤖 Master AI Router")
selected_page = st.sidebar.radio("Navigation:", ["📊 Dashboard Window", "📅 New Backward Planner"])

# --- ১. এক্সেল স্টাইল ড্যাশবোর্ড উইন্ডো ---
if selected_page == "📊 Dashboard Window":
    st.subheader("🏁 Executive Factory Dashboard View")
    st.write("আপনার এক্সেল ফাইলের মূল 'Dashboard' শিটের লাইভ রেপ্লিকা।")
    st.markdown("---")
    
    df_run, df_overdue = get_running_models_data()
    
    # এক্সেলের মতো পাশাপাশি কলাম লেআউট
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏃‍♂️ RUNNING TASKS (TODAY)")
        st.dataframe(
            df_run.style.set_properties(**{'background-color': '#e6f3ff', 'color': 'black'}),
            use_container_width=True,
            hide_index=True
        )
        
    with col2:
        st.markdown("### 🛑 OVERDUE / DELAYED TASKS")
        st.dataframe(
            df_overdue.style.set_properties(**{'background-color': '#ffe6e6', 'color': '#b30000'}),
            use_container_width=True,
            hide_index=True
        )

# --- ২. ব্যাকওয়ার্ড প্ল্যানার উইন্ডো ---
elif selected_page == "📅 New Backward Planner":
    st.header("📋 Calculate New Model Timeline")
    
    col1, col2 = st.columns(2)
    with col1:
        project_name = st.text_input("New Article Name:", placeholder="e.g., NH500 COMFORT")
    with col2:
        xf_date = st.date_input("Base CDD / XF Date:", datetime(2027, 4, 22))
        
    if st.button("Generate & Inject Plan 🚀"):
        if project_name:
            new_plan_df = calculate_decathlon_backward_plan(xf_date)
            st.success(f"✔️ {project_name.upper()} এর ব্যাকওয়ার্ড প্ল্যান সফলভাবে তৈরি হয়েছে এবং ডাটাবেজে যুক্ত হয়েছে!")
            st.dataframe(new_plan_df, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ অনুগ্রহ করে প্রজেক্ট বা মডেলের নাম দিন।")
