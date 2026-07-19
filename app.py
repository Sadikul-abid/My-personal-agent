import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from groq import Groq

# 📄 ১. পেজ এবং থিম কনফিগারেশন
st.set_page_config(
    page_title="Footwear Production OS",
    page_icon="👟",
    layout="wide"
)

# 🔐 Groq API কী চেকিং
GROQ_API_KEY = os.environ.get('GROQ_API_KEY') or st.sidebar.text_input("Enter Groq API Key:", type="password")

# 💾 ২. স্ট্রীমলিট স্টেট ম্যানেজমেন্ট (আপনার এক্সেলের ব্যাকএন্ড ডাটাবেস)
if 'projects' not in st.session_state:
    st.session_state.projects = {}  # এখানে প্রতিটি New Article এর জন্য একটি করে 'Sheet' বা ডিকশনারি তৈরি হবে

# ফিক্সড মাস্টার লিড টাইম লজিক (যা আপনার এক্সেল শিটে ফর্মুলা আকারে ছিল)
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

# ব্যাকওয়ার্ড ক্যালকুলেশন ইঞ্জিন (যা এক্সেলে অটো-ডেট জেনারেট করত)
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

# --- 🖥️ ৩. নেভিগেশন ট্যাব বা এক্সেল শিট ট্যাব মেকানিজম ---
# আপনার এক্সেলের নিচের ট্যাবগুলোর মতো এখানে আমরা মূল ৩টি সেকশন তৈরি করলাম
tab_dashboard, tab_new_article, tab_all_sheets = st.tabs([
    "📊 Central Dashboard", 
    "➕ Add New Article (New Sheet)", 
    "📁 View Article Sheets"
])

# ==========================================
# 📊 সেকশন ১: CENTRAL DASHBOARD (এক্সেল ড্যাশবোর্ড)
# ==========================================
with tab_dashboard:
    st.title("📊 Footwear Production Master Dashboard")
    st.markdown("আপনার সমস্ত রানিং আর্টিকেলের ওভারভিউ এবং কারেন্ট স্ট্যাটাস একনজরে দেখুন।")
    
    if not st.session_state.projects:
        st.info("💡 বর্তমানে কোনো অ্যাক্টিভ প্রজেক্ট বা শিট নেই। 'Add New Article' ট্যাব থেকে প্রথম প্রজেক্ট যুক্ত করুন।")
    else:
        # ড্যাশবোর্ড কেপিআই কার্ডস (KPI Cards)
        total_articles = len(st.session_state.projects)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Running Articles", total_articles)
        
        # ড্যাশবোর্ডের জন্য একটি মাস্টার সামারি টেবিল তৈরি করা
        dashboard_summary = []
        for name, df in st.session_state.projects.items():
            xf_date = df[df["Task Name"] == "Go ship"]["Target Date"].values[0]
            prod_date = df[df["Task Name"] == "Go prod"]["Target Date"].values[0]
            
            # প্রজেক্টের টোটাল কত পার্সেন্ট কাজ 'Done' হয়েছে তা বের করা
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

# ==========================================
# ➕ সেকশন ২: ADD NEW ARTICLE (এক্সেলের New Sheet ক্রিয়েশন)
# ==========================================
with tab_new_article:
    st.title("➕ Launch New Footwear Style")
    st.markdown("এখানে নতুন আর্টিকেল ইনপুট দিলে ব্যাকএন্ডে একটি ডেডিকেটেড **'Individual Sheet'** তৈরি হয়ে যাবে।")
    
    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        new_style_name = st.text_input("Enter Style / Article Name (Unique ID):", placeholder="e.g., 380148 - PLAY 100")
    with col_input2:
        new_xf_date = st.date_input("Select Proposed XF Date (Shipment Date):", datetime.now() + timedelta(days=365))
        
    if st.button("🚀 Create Article Sheet & Generate Timeline"):
        if not new_style_name.strip():
            st.error("⚠️ অনুগ্রহ করে একটি সঠিক আর্টিকেলের নাম দিন।")
        elif new_style_name in st.session_state.projects:
            st.warning(f"⚠️ '{new_style_name}' নামে অলরেডি একটি শিট রয়েছে! দয়া করে ইউনিক নাম ব্যবহার করুন।")
        else:
            with st.spinner("ক্যালকুলেটিং ব্যাকওয়ার্ড টাইমলাইন..."):
                # নতুন আর্টিকেলের জন্য অটোমেটিক ডাটাফ্রেম শিট তৈরি
                base_datetime = datetime.combine(new_xf_date, datetime.min.time())
                generated_df = generate_timeline_df(base_datetime)
                
                # এক্সেলের মতো নতুন শিট মেমরিতে পুশ করা
                st.session_state.projects[new_style_name] = generated_df
                
                st.success(f"🎉 সাফল্যজনক! '{new_style_name}' শিটটি সফলভাবে যুক্ত হয়েছে।")
                st.balloons()

# ==========================================
# 📁 সেকশন ৩: VIEW ARTICLE SHEETS (আলাদা আলাদা শিট দেখা ও এডিট করা)
# ==========================================
with tab_all_sheets:
    st.title("📁 Individual Article Worksheets")
    st.markdown("আপনার তৈরি করা যেকোনো সুনির্দিষ্ট আর্টিকেলের শিট সিলেক্ট করে তার ভেতরের ২৪টি টাস্কের ডেট ও স্ট্যাটাস আপডেট করুন।")
    
    if not st.session_state.projects:
        st.info("কোনো ডাটা শিট পাওয়া যায়নি।")
    else:
        # ড্রপডাউন মেনু (যেমনটি এক্সেলে শিট ট্যাব চেঞ্জ করার মতো)
        selected_style = st.selectbox("🎯 Select Active Sheet to View/Edit:", list(st.session_state.projects.keys()))
        
        if selected_style:
            st.write(f"### 📑 Worksheet for Style: `{selected_style}`")
            
            current_df = st.session_state.projects[selected_style]
            
            # 📝 ইন্টারঅ্যাক্টিভ এডিটিং (এক্সেলের মতো করে গ্রিডেই স্ট্যাটাস চেঞ্জ করার সুবিধা)
            st.markdown("💡 *আপনি সরাসরি নিচের টেবিলের 'Status' কলামে ডাবল ক্লিক করে স্ট্যাটাস (Pending/Done) পরিবর্তন করতে পারেন:*")
            
            edited_df = st.data_editor(
                current_df,
                column_config={
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        help="Task Current Status",
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
            
            # সেভ বা আপডেট স্টেট চেঞ্জ
            if st.button(f"💾 Save Changes to {selected_style} Sheet"):
                st.session_state.projects[selected_style] = edited_df
                st.success(f"✅ {selected_style} শিটের স্ট্যাটাস আপডেট সেভ করা হয়েছে!")
