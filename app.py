import streamlit as st
import os
from datetime import datetime, timedelta
import pandas as pd

# পেজ সেটআপ রেসপনসিভ করার জন্য
st.set_page_config(page_title="Footwear AI OS", layout="wide")

# Groq সেটআপ
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
client = None
if GROQ_API_KEY:
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)

# --- 🧠 ১. রিয়েল ডিপেন্ডেন্সি ক্যালকুলেশন ইঞ্জিন (এক্সেল লজিক অনুযায়ী) ---
def calculate_decathlon_backward_plan(base_xf_date):
    # base_xf_date হচ্ছ আপনার CDD বা Base XF Date
    cdd = datetime.combine(base_xf_date, datetime.min.time())
    
    # এক্সেলের ফর্মুলা অনুযায়ী রিলেশন সেটআপ
    dates = {}
    dates['CDD'] = cdd
    dates['Project Initiation'] = cdd # Row 2: =G2 - C2 (where C2=0)
    
    # Go ship & production sequence
    dates['Go ship'] = dates['CDD'] - timedelta(days=56)
    dates['Go prod'] = dates['Go ship'] - timedelta(days=27)
    dates['Go Indus: Passed'] = dates['Go prod'] - timedelta(days=2)
    dates['Go Indus: Start'] = dates['Go Indus: Passed'] - timedelta(days=21)
    
    # Tooling and Tests tied to Go Indus: Start
    dates['Tooling Ready: End'] = dates['Go Indus: Start'] - timedelta(days=7)
    dates['Tooling Ready: Start'] = dates['Tooling Ready: End'] - timedelta(days=7)
    dates['CTF & PVP Test: Report'] = dates['Go Indus: Start'] - timedelta(days=7)
    dates['CTF & PVP Test: Start'] = dates['CTF & PVP Test: Report'] - timedelta(days=30)
    dates['RTI:CDCT file: Start'] = dates['Go Indus: Start'] - timedelta(days=5)
    
    # Sample Size Proto Trial ties to Go prod
    dates['Sample size proto trial'] = dates['Go prod'] - timedelta(days=0)
    dates['Sample Mold: Validation'] = dates['Sample size proto trial'] - timedelta(days=0)
    
    # CFM & FSR Sample Validation ties to Go Indus: Start
    dates['CFM Sample: Validation'] = dates['Go Indus: Start'] - timedelta(days=0)
    dates['CFM Sample: ETD'] = dates['CFM Sample: Validation'] - timedelta(days=14)
    dates['CFM Sample: Start'] = dates['CFM Sample: ETD'] - timedelta(days=6)
    
    dates['FSR Sample:Validation'] = dates['CFM Sample: Start'] - timedelta(days=0)
    dates['FSR Sample: End'] = dates['FSR Sample:Validation'] - timedelta(days=21)
    dates['FSR Sample: Start'] = dates['FSR Sample: End'] - timedelta(days=7)
    
    # FSR Mold Sequence
    dates['FSR Mold: Validation'] = dates['FSR Sample: Start'] - timedelta(days=0)
    dates['FSR Mold: ETA'] = dates['FSR Mold: Validation'] - timedelta(days=7)
    dates['FSR Mold: Order'] = dates['FSR Mold: ETA'] - timedelta(days=70)
    
    # Sample Mold Sequence
    dates['Samlpe Mold: ETA'] = dates['FSR Mold: Order'] - timedelta(days=7)
    dates['Sample Mold: Order'] = dates['Samlpe Mold: ETA'] - timedelta(days=42)
    
    # Proto Sequence
    dates['Proto: Validation'] = dates['FSR Sample: Start'] - timedelta(days=0)
    dates['DCR Evaluation: Start'] = dates['Proto: Validation']
    dates['Proto: End'] = dates['Proto: Validation'] - timedelta(days=7)
    dates['Proto: Start'] = dates['Proto: End'] - timedelta(days=7)
    
    # Trim Card Sequence
    dates['Trim Card: End: Approval'] = dates['Proto: Start'] - timedelta(days=3)
    
    # Bulk Material Sequence tied to Go Indus: Start
    dates['Bulk Material: ETA'] = dates['Go Indus: Start'] - timedelta(days=7)
    dates['Bulk Material: Order'] = dates['Bulk Material: ETA'] - timedelta(days=90)
    dates['BOM: DKT Validation'] = dates['Bulk Material: Order'] - timedelta(days=7)
    
    # BOM & Raw Material Sequence
    dates['BOM: Preparation for validation'] = dates['BOM: DKT Validation'] - timedelta(days=7)
    dates['Sample Materials: Approval'] = dates['BOM: DKT Validation'] - timedelta(days=0)
    dates['BOM: OMC BOM '] = dates['BOM: DKT Validation'] + timedelta(days=1)
    dates['Trim Card: Start'] = dates['BOM: OMC BOM '] + timedelta(days=1)
    
    dates['Sample Received: Raw Materials'] = dates['Sample Materials: Approval'] - timedelta(days=7)
    dates['Sample Order: Raw Materials'] = dates['Sample Received: Raw Materials'] - timedelta(days=30)
    dates['Consumption, CBD (sharing)\n'] = dates['Sample Order: Raw Materials'] - timedelta(days=0)
    
    dates['Sample Received: Threads/Packing Materials'] = dates['Sample Materials: Approval'] - timedelta(days=7)
    dates['Sample Order: Threads/Packing Materials'] = dates['Sample Received: Threads/Packing Materials'] - timedelta(days=15)
    
    dates['Duplibox: Evaluation'] = dates['BOM: Preparation for validation'] - timedelta(days=7)
    dates['Duplibox: Received'] = dates['Duplibox: Evaluation'] - timedelta(days=7)
    dates['Duplibox: Ask'] = dates['Duplibox: Received'] - timedelta(days=28)

    # সাজানো সিকোয়েন্স ডেটাফ্রেম তৈরি
    task_order = [
        ("1.0", "Project Initiation"), ("2.0", "Consumption, CBD (sharing)\n"), 
        ("3.0", "Sample Order: Raw Materials"), ("4.0", "Sample Received: Raw Materials"),
        ("5.0", "Sample Order: Threads/Packing Materials"), ("6.0", "Sample Received: Threads/Packing Materials"),
        ("12.0", "BOM: DKT Validation"), ("-", "Bulk Material: Order"), ("-", "Bulk Material: ETA"),
        ("21.0", "Sample Mold: Order"), ("23.0", "Samlpe Mold: ETA"), ("24.0", "Sample Mold: Validation"),
        ("16.0", "Proto: Start"), ("17.0", "Proto: End"), ("18.0", "Proto: Validation"),
        ("26.0", "FSR Mold: Order"), ("28.0", "FSR Mold: ETA"), ("29.0", "FSR Mold: Validation"),
        ("30.0", "FSR Sample: Start"), ("31.0", "FSR Sample: End"), ("32.0", "FSR Sample:Validation"),
        ("37.0", "CFM Sample: Start"), ("39.0", "CFM Sample: ETD"), ("40.0", "CFM Sample: Validation"),
        ("42.0", "Go Indus: Start"), ("44.0", "Go Indus: Passed"), ("45.0", "Go prod"),
        ("46.0", "Go ship"), ("19.0", "CDD"), ("7.0", "Sample Materials: Approval"),
        ("8.0", "Duplibox: Ask"), ("9.0", "Duplibox: Received"), ("10.0", "Duplibox: Evaluation"),
        ("11.0", "BOM: Preparation for validation"), ("13.0", "BOM: OMC BOM "), ("14.0", "Trim Card: Start"),
        ("15.0", "Trim Card: End: Approval"), ("19.0", "DCR Evaluation: Start"), ("25.0", "Sample size proto trial"),
        ("33.0", "CTF & PVP Test: Start"), ("34.0", "CTF & PVP Test: Report"), ("35.0", "Tooling Ready: Start"),
        ("36.0", "Tooling Ready: End"), ("41.0", "RTI:CDCT file: Start")
    ]
    
    plan_data = []
    for sl, task in task_order:
        dt = dates.get(task, cdd)
        plan_data.append({
            "SL No": sl,
            "Task Name": task.strip(),
            "Target Date": dt.strftime("%m/%d/%Y"),
            "WK No": dt.isocalendar()[1],
            "Status": "Pending 🕒"
        })
    return plan_data

# --- ২. Streamlit UI হাব ---
st.title("👟 Footwear AI OS - Decathlon Edition")

st.sidebar.title("🤖 Master AI Router")
selected_agent = st.sidebar.radio("Active Agent:", ["📊 80/20 Planner Agent", "⚙️ Workplace Execution", "📚 Knowledge Base"])

if selected_agent == "📊 80/20 Planner Agent":
    st.header("📋 Automated Backward Planning Engine")
    
    col1, col2 = st.columns(2)
    with col1:
        project_name = st.text_input("New Project / Article Name:", placeholder="e.g., NH100 BLUE KID")
    with col2:
        xf_date = st.date_input("Base XF Date (Shipment / CDD):", datetime(2027, 4, 22))
        
    if st.button("Calculate Master Timeline 🚀"):
        if project_name:
            plan = calculate_decathlon_backward_plan(xf_date)
            
            st.subheader(f"📊 Live Production Roadmap for: {project_name.upper()}")
            st.dataframe(pd.DataFrame(plan), use_container_width=True)
            
            # AI এক্সপার্ট কমেন্ট্রি
            if client:
                st.subheader("🧠 Planner Agent 80/20 Insights")
                with st.spinner("অ্যানালাইসিস করা হচ্ছে..."):
                    try:
                        summary = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[
                                {"role": "system", "content": "You are Decathlon Footwear Production Expert. Point out the 3 most critical order deadlines from data."},
                                {"role": "user", "content": str(plan)}
                            ],
                            temperature=0.3
                        )
                        st.info(summary.choices[0].message.content)
                    except Exception as e:
                        st.warning("AI রেসপন্স দিতে পারছে না, তবে আপনার টেবিল ওপরে জেনারেট হয়েছে।")
        else:
            st.warning("⚠️ প্রজেক্টের নাম ইনপুট দিন।")
