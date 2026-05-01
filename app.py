import streamlit as st
import hashlib
import pandas as pd
import os
import json
import time
from datetime import datetime
from cryptography.fernet import Fernet

# ====================== 1. SECURITY & BLOCKCHAIN ENGINE ======================
if 'encryption_key' not in st.session_state:
    st.session_state.encryption_key = Fernet.generate_key()
    st.session_state.cipher = Fernet(st.session_state.encryption_key)

# Multi-Admin Database for Decentralized Governance
ADMIN_DB = {
    "Admin_BOUESTI": "bouesti2026",
    "Admin_MOH": "nigeria_health",
    "Admin_General": "hospital_sec"
}

class Block:
    def __init__(self, index, patient_id, data_type, content, staff_info, previous_hash):
        self.index = index
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.patient_id = patient_id
        self.data_type = data_type 
        self.content = content     
        self.staff_info = staff_info
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_dict = {
            "index": self.index, "timestamp": self.timestamp, "patient_id": self.patient_id,
            "data_type": self.data_type, "content": str(self.content),
            "staff_info": self.staff_info, "previous_hash": self.previous_hash
        }
        return hashlib.sha256(json.dumps(block_dict, sort_keys=True).encode()).hexdigest()

class HealthcareBlockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, "GENESIS", "SYSTEM", "Network Root Initialized", {"id": "Consensus", "role": "System"}, "0")

    def add_new_block(self, new_block):
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            if self.chain[i].hash != self.chain[i].calculate_hash(): return False
            if self.chain[i].previous_hash != self.chain[i-1].hash: return False
        return True

# ====================== 2. SYSTEM INITIALIZATION ======================
st.set_page_config(page_title="MedSec Blockchain", layout="wide")

if 'my_blockchain' not in st.session_state: 
    st.session_state.my_blockchain = HealthcareBlockchain()
if 'consent_registry' not in st.session_state: 
    st.session_state.consent_registry = {}
if 'admin_signatures' not in st.session_state:
    st.session_state.admin_signatures = []
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_id = None

# ====================== 3. SECURE MULTI-DOOR LOGIN ======================
if not st.session_state.logged_in:
    st.title("🛡️ MedSec: Blockchain Based Healthcare Data Security")
    st.info("Identity verification required for all roles.")
    
    tab_doc, tab_nur, tab_pat, tab_adm = st.tabs(["🩺 Doctor", "📋 Nurse", "👤 Patient", "🏛️ Admin"])
    
    with tab_doc:
        d_id = st.text_input("Doctor ID", placeholder="DOC-001", key="d_id")
        d_pw = st.text_input("Password", type="password", key="d_pw")
        if st.button("Doctor Login") and d_pw == "doctor123":
            st.session_state.update({'logged_in': True, 'user_role': 'Doctor', 'user_id': d_id})
            st.rerun()

    with tab_nur:
        n_id = st.text_input("Nurse ID", placeholder="NUR-001", key="n_id")
        n_pw = st.text_input("Password", type="password", key="n_pw")
        if st.button("Nurse Login") and n_pw == "nurse123":
            st.session_state.update({'logged_in': True, 'user_role': 'Nurse', 'user_id': n_id})
            st.rerun()

    with tab_pat:
        p_id = st.text_input("Patient ID (NIN)", placeholder="PAT-101", key="p_id")
        p_pin = st.text_input("Secure PIN", type="password", key="p_pin")
        if st.button("Patient Login") and p_pin == "0000":
            st.session_state.update({'logged_in': True, 'user_role': 'Patient', 'user_id': p_id})
            st.rerun()

    with tab_adm:
        a_id = st.selectbox("Admin Identity", list(ADMIN_DB.keys()))
        a_pw = st.text_input("Admin Password", type="password", key="a_pw")
        if st.button("Admin Login"):
            if ADMIN_DB[a_id] == a_pw:
                st.session_state.update({'logged_in': True, 'user_role': 'Admin', 'user_id': a_id})
                st.rerun()
            else: st.error("Access Denied")
    st.stop()

# ====================== 4. ROLE-BASED DASHBOARD ======================
role = st.session_state.user_role
user_id = st.session_state.user_id

st.sidebar.title("🔐 Active Session")
st.sidebar.success(f"User: {user_id}\nRole: {role}")
if st.sidebar.button("🔒 Logout"):
    st.session_state.logged_in = False
    st.rerun()

st.title(f"🛡️ MedSec Dashboard — {role} Portal")
tab_work, tab_ledger = st.tabs(["📊 Workspace", "⛓️ Audit Ledger"])

with tab_work:
    # --- ADMIN CONSENSUS TOOLS ---
    if role == "Admin":
        st.subheader("🏛️ Multi-Sig Governance")
        st.write("**Active Proposal:** Authorize Global System Maintenance")
        if user_id not in st.session_state.admin_signatures:
            if st.button(f"✍️ Sign as {user_id}"):
                st.session_state.admin_signatures.append(user_id)
                st.rerun()
        
        signatures = len(st.session_state.admin_signatures)
        st.progress(signatures / 2 if signatures < 2 else 1.0)
        st.write(f"Signatures Collected: {signatures}/2 required.")
        
        if signatures >= 2:
            st.warning("Consensus Reached. Administrative actions unlocked.")
            if st.button("⚡ Reset Consent Registry (Emergency Clean)"):
                st.session_state.consent_registry = {}
                st.session_state.admin_signatures = []
                st.success("Action Executed!")

    # --- DOCTOR CLINICAL TOOLS ---
    if role == "Doctor":
        st.subheader("Clinical Management")
        c1, c2 = st.columns(2)
        with c1:
            with st.expander("📡 Bulk EHR Sync"):
                if os.path.exists('EHR.csv') and st.button("🔗 Sync & Encrypt"):
                    df = pd.read_csv('EHR.csv')
                    for _, row in df.head(15).iterrows():
                        pid = str(row['patientunitstayid'])
                        rec = {"Diagnosis": str(row.get('apacheadmissiondx', 'N/A')), "Vitals": {"Age": str(row.get('age'))}}
                        enc = st.session_state.cipher.encrypt(json.dumps(rec).encode()).decode()
                        st.session_state.consent_registry[pid] = True
                        st.session_state.my_blockchain.add_new_block(Block(len(st.session_state.my_blockchain.chain), pid, "MEDICAL_RECORD", enc, {"id": user_id}, st.session_state.my_blockchain.chain[-1].hash))
                    st.success("Sync Complete")
        with c2:
            with st.expander("➕ Manual Clinical Entry"):
                m_pid = st.text_input("Patient ID (Manual)")
                m_diag = st.text_input("Diagnosis")
                
                # Added Age and Gender fields
                col_a, col_g = st.columns(2)
                with col_a:
                    m_age = st.number_input("Age", 0, 120, 25)
                with col_g:
                    m_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                
                m_h = st.number_input("Height", 50, 250, 170)
                m_w = st.number_input("Weight", 1, 300, 70)
                m_t = st.number_input("Temp", 30.0, 45.0, 36.5)
                m_bp = st.text_input("Blood Pressure", "120/80")
                m_p = st.number_input("Pulse", 40, 200, 72)
                
                if st.button("Mine Encrypted Block"):
                    # Structured dictionary including new demographic fields
                    data = {
                        "Diagnosis": m_diag, 
                        "Demographics": {"Age": m_age, "Gender": m_gender},
                        "Vitals": {"H": m_h, "W": m_w, "T": m_t, "BP": m_bp, "P": m_p}
                    }
                    enc_m = st.session_state.cipher.encrypt(json.dumps(data).encode()).decode()
                    st.session_state.consent_registry[m_pid] = True
                    st.session_state.my_blockchain.add_new_block(Block(len(st.session_state.my_blockchain.chain), m_pid, "MANUAL_ENTRY", enc_m, {"id": user_id}, st.session_state.my_blockchain.chain[-1].hash))
                    st.rerun()

    # --- SEARCH & BREAK-GLASS (DOCTOR/NURSE) ---
    if role in ["Doctor", "Nurse"]:
        st.divider()
        st.subheader("🔎 Search Patient Records")
        search_pid = st.text_input("Enter Patient ID to pull history")
        if search_pid:
            has_consent = st.session_state.consent_registry.get(search_pid, False)
            if not has_consent:
                st.error("🚨 Access Restricted: Consent Required.")
                if role == "Doctor":
                    with st.expander("🆘 EMERGENCY OVERRIDE (Break-Glass)"):
                        reason = st.text_area("Justification")
                        if st.button("Force Emergency Access"):
                            log = Block(len(st.session_state.my_blockchain.chain), search_pid, "BREAK_GLASS", {"reason": reason}, {"id": user_id}, st.session_state.my_blockchain.chain[-1].hash)
                            st.session_state.my_blockchain.add_new_block(log)
                            st.session_state.consent_registry[search_pid] = True
                            st.rerun()
            else:
                recs = [b for b in st.session_state.my_blockchain.chain if b.patient_id == search_pid and "LOG" not in b.data_type]
                for r in recs:
                    with st.expander(f"File #{r.index}"):
                        try: st.json(json.loads(st.session_state.cipher.decrypt(r.content.encode()).decode()))
                        except: st.write("Encrypted Data")

    # --- PATIENT ACCESS ---
    if role == "Patient":
        st.subheader("My Digital Health Records")
        st.session_state.consent_registry[user_id] = st.toggle("Grant Doctors Global Access", value=st.session_state.consent_registry.get(user_id, False))
        my_files = [b for b in st.session_state.my_blockchain.chain if b.patient_id == user_id and "LOG" not in b.data_type]
        for f in my_files:
            with st.expander(f"Medical File #{f.index}"):
                try: st.json(json.loads(st.session_state.cipher.decrypt(f.content.encode()).decode()))
                except: st.write("Encrypted Content")

with tab_ledger:
    st.subheader("⛓️ Immutable Audit Ledger")
    if st.button("🔍 Check Chain Integrity"):
        if st.session_state.my_blockchain.is_chain_valid(): st.success("Blockchain Integrity Verified: No Tampering Detected")
        else: st.error("CRITICAL: Blockchain Tampering Detected!")
    for b in reversed(st.session_state.my_blockchain.chain):
        with st.expander(f"Block #{b.index} | {b.data_type}"):
            st.write(f"Owner: {b.patient_id} | Staff: {b.staff_info.get('id')}")
            st.caption(f"Block Hash: {b.hash}")

st.caption("Built in BOUESTI • Ikere City, Ekiti State • May 2026")
