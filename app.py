import streamlit as st
import hashlib
import time
import pandas as pd
import os
from datetime import datetime

# --- 1. BLOCKCHAIN CORE ---
class Block:
    def __init__(self, index, patient_id, diagnosis, vitals, staff_info, previous_hash):
        self.index = index
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.patient_id = patient_id
        self.diagnosis = diagnosis
        self.vitals = vitals  
        self.staff_info = staff_info
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        sha = hashlib.sha256()
        block_content = str(self.index) + str(self.timestamp) + str(self.patient_id) + \
                        str(self.diagnosis) + str(self.vitals) + str(self.previous_hash)
        sha.update(block_content.encode('utf-8'))
        return sha.hexdigest()

class HealthcareBlockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, "GENESIS", "System Start", {}, {"id": "Admin", "role": "System"}, "0")

    def add_new_block(self, new_block):
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

# --- 2. STREAMLIT CONFIG ---
st.set_page_config(page_title="Blockchain MedSec", layout="wide")
st.title("🛡️ Blockchain Based Data Health Care Security")
st.markdown("---")

if 'my_blockchain' not in st.session_state:
    st.session_state.my_blockchain = HealthcareBlockchain()

# --- 3. SIDEBAR: AUTH & EHR SYNC ---
st.sidebar.header("🔐 Staff Authentication")
staff_id = st.sidebar.text_input("Staff ID", value="DR-ADEYEMI-01")
role = st.sidebar.selectbox("Access Level", ["Doctor", "Nurse", "Lab Technician", "Administrator"])

st.sidebar.divider()
st.sidebar.subheader("📡 EHR Database Sync")
if os.path.exists('EHR.csv'):
    if st.sidebar.button("🔗 Sync & Secure EHR Records"):
        df_ehr = pd.read_csv('EHR.csv')
        for index, row in df_ehr.head(15).iterrows():
            p_id = str(row['uniquepid'])
            diag = str(row['apacheadmissiondx']) if pd.notna(row['apacheadmissiondx']) else "General Admission"
            normalized_year = int(row['hospitaldischargeyear']) + 10 
            
            vitals_dict = {
                "age": str(row['age']), "gender": str(row['gender']),
                "weight": f"{row['admissionweight']} kg", "outcome": str(row['hospitaldischargestatus']),
                "year": str(normalized_year)
            }
            prev_h = st.session_state.my_blockchain.chain[-1].hash
            new_block = Block(len(st.session_state.my_blockchain.chain), p_id, diag, vitals_dict, {"id": staff_id, "role": role}, prev_h)
            st.session_state.my_blockchain.add_new_block(new_block)
        st.sidebar.success("Bulk Sync Complete (2021-2026)!")

st.sidebar.divider()
st.sidebar.subheader("🛡️ Security Tools")
if st.sidebar.button("🔍 Run Integrity Scan"):
    if st.session_state.my_blockchain.is_chain_valid():
        st.sidebar.success("✅ System Integrity Verified")
        st.balloons()
    else:
        st.sidebar.error("🚨 ALERT: Data Tampering Detected!")

# --- 4. MAIN INTERFACE ---
col_main, col_stats = st.columns([2, 1])

with col_main:
    # --- FIXED: MANUAL ENTRY FORM ---
    with st.expander("➕ Create New Manual EHR Record", expanded=False):
        st.write("Enter clinical data to witness the hashing process:")
        
        # We give these inputs unique variable names
        manual_pid = st.text_input("Patient ID", value="PAT-888", key="input_pid")
        manual_diag = st.text_input("Diagnosis", value="Routine Checkup", key="input_diag")
        
        c_m1, c_m2, c_m3 = st.columns(3)
        with c_m1: manual_age = st.number_input("Age", 1, 120, 25, key="input_age")
        with c_m2: manual_gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="input_gender")
        with c_m3: manual_year = st.number_input("Record Year", 2021, 2026, 2026, key="input_year")
        
        if st.button("🚀 Secure to Blockchain", key="manual_submit_btn"):
            # We bundle the data from the INPUTS above
            manual_vitals = {
                "age": str(manual_age), 
                "gender": manual_gender, 
                "weight": "N/A", 
                "outcome": "Active", 
                "year": str(manual_year)
            }
            
            # Grab the current staff info from the sidebar
            manual_staff = {"id": staff_id, "role": role}
            
            # Get the link to the previous block
            m_prev_hash = st.session_state.my_blockchain.chain[-1].hash
            
            # CREATE THE BLOCK using the specific manual variables
            m_block = Block(
                len(st.session_state.my_blockchain.chain), 
                manual_pid, 
                manual_diag, 
                manual_vitals, 
                manual_staff, 
                m_prev_hash
            )
            
            st.session_state.my_blockchain.add_new_block(m_block)
            st.success(f"Block #{m_block.index} successfully hashed and added!")
            st.rerun() # This refreshes the page so the new block shows up immediately

    st.subheader("📑 Secure Audit Ledger")
    display_chain = [b for b in st.session_state.my_blockchain.chain if b.index != 0]
    
    for block in reversed(display_chain):
        with st.expander(f"📁 EHR Block #{block.index} | Patient: {block.patient_id}"):
            c1, c2 = st.columns(2)
            with c1:
                st.write("**🩺 Clinical Data**")
                st.write(f"**Diagnosis:** {block.diagnosis}")
                st.write(f"**Patient Info:** {block.vitals.get('age')}yr | {block.vitals.get('gender')}")
            with c2:
                st.write("**🔐 Security Meta**")
                st.write(f"**Authorized By:** {block.staff_info.get('id')}")
                st.write(f"**Year:** {block.vitals.get('year')}")
            st.divider()
            st.caption(f"**Current Hash:** {block.hash}")
            st.caption(f"**Previous Hash:** {block.previous_hash}")

with col_stats:
    st.subheader("📊 System Health")
    total = len(st.session_state.my_blockchain.chain) - 1
    st.metric("Secured Records", total)
    
    if total > 0:
        # CLEAN CHART LOGIC
        years_list = [b.vitals.get('year') for b in st.session_state.my_blockchain.chain if b.index != 0]
        chart_df = pd.DataFrame(years_list, columns=['Year']).value_counts().reset_index(name='Count')
        st.write("**Record Distribution by Year**")
        st.bar_chart(chart_df, x="Year", y="Count")
        
        st.write("**Access Control Log**")
        roles = [b.staff_info.get('role') for b in st.session_state.my_blockchain.chain if b.index != 0]
        role_df = pd.DataFrame(roles, columns=['Role']).value_counts().reset_index(name='Total')
        st.table(role_df)