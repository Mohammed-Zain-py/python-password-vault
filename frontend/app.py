import streamlit as st
import requests
import json

API_URL = "http://127.0.0.1:8000/api"

st.set_page_config(page_title="Secure Vault", page_icon="🔐", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #00FF41; font-family: 'Courier New', Courier, monospace; }
    h1, h2, h3, p, label { color: #00FF41 !important; font-family: 'Courier New', Courier, monospace !important; }
    .stTextInput input { background-color: #1e1e1e !important; color: #00FF41 !important; border: 1px solid #00FF41 !important; border-radius: 4px; }
    .stButton>button { background-color: #1e1e1e; color: #00FF41; border: 2px solid #00FF41; border-radius: 4px; transition: 0.3s; width: 100%; font-weight: bold; }
    .stButton>button:hover { background-color: #00FF41; color: #121212; border: 2px solid #00FF41; }
    .st-emotion-cache-1kqj04s { background-color: #1e1e1e; border-left-color: #00FF41; color: #00FF41;}
    .st-emotion-cache-16idsys { background-color: #1e1e1e; border-left-color: #ff3333; color: #ff3333;}
    </style>
""", unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

st.title("Secure Password Vault")
st.markdown("---")

if not st.session_state.authenticated:
    st.subheader("Login Required")
    master_pass = st.text_input("Master Password:", type="password")
    if st.button("Login"):
        if master_pass:
            try:
                response = requests.post(f"{API_URL}/login", json={"master_password": master_pass})
                if response.status_code == 200:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Incorrect password.")
            except:
                st.error("Cannot connect to API. Is Uvicorn running?")
        else:
            st.warning("Please enter your password.")

else:
    # --- DISASTER RECOVERY SIDEBAR ---
    with st.sidebar:
        st.header("🛡️ Vault Backup")
        st.write("Keep this file safe. It requires your `key.key` to decrypt.")
        
        if st.button("Prepare Export"):
            res = requests.get(f"{API_URL}/backup/export")
            if res.status_code == 200:
                json_data = json.dumps(res.json().get("data", []), indent=4)
                st.download_button(
                    label="💾 Download vault_backup.json", 
                    data=json_data, 
                    file_name="vault_backup.json", 
                    mime="application/json"
                )
            else:
                st.error("Export failed.")
        
        st.markdown("---")
        st.subheader("Restore Vault")
        uploaded_file = st.file_uploader("Upload vault_backup.json", type="json")
        if uploaded_file is not None:
            if st.button("Execute Import"):
                try:
                    records = json.load(uploaded_file)
                    res = requests.post(f"{API_URL}/backup/import", json={"records": records})
                    if res.status_code == 200:
                        st.success("Vault Restored Successfully!")
                    else:
                        st.error("Import failed.")
                except Exception as e:
                    st.error("Invalid JSON file.")
                    
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()
            
    tab1, tab2, tab3, tab4 = st.tabs(["VIEW", "ADD", "UPDATE", "DELETE"])

    # --- TAB 1: VIEW ---
    with tab1:
        st.subheader("View Passwords")
        search_query = st.text_input("🔍 Search by Account Name:")
        
        if st.button("Fetch Records"):
            response = requests.get(f"{API_URL}/passwords")
            if response.status_code == 200:
                data = response.json().get("data", [])
                
                if search_query:
                    data = [item for item in data if search_query.lower() in item['account_name'].lower()]
                
                if not data:
                    st.info("No passwords found.")
                else:
                    for item in data:
                        with st.container():
                            email_display = item.get('email') if item.get('email') else "N/A"
                            st.markdown(f"**Account:** `{item['account_name']}` | **Email:** `{email_display}`")
                            st.code(item['password'], language="plaintext") 
                            st.markdown("---")
            else:
                st.error("Failed to retrieve data.")

    # --- TAB 2: ADD ---
    with tab2:
        st.subheader("Add New Password")
        new_account = st.text_input("Account Name")
        new_email = st.text_input("Email (Optional)", key="add_email")
        
        gen_random = st.checkbox("Auto-generate Password", value=True, key="add_gen")
        
        new_password = ""
        pwd_length = 12
        use_nums = True
        use_spec = True
        
        if gen_random:
            st.markdown("---")
            st.write("🔧 AUTOGEN CRITERIA")
            pwd_length = st.number_input("Length", min_value=8, max_value=128, value=12, key="add_len")
            use_nums = st.checkbox("Include Numbers", value=True, key="add_num")
            use_spec = st.checkbox("Include Special Characters", value=True, key="add_spec")
            st.markdown("---")
        else:
            new_password = st.text_input("Custom Password", type="password", key="add_pass")
            
        if st.button("Save Entry"):
            if new_account:
                payload = {
                    "account_name": new_account,
                    "email": new_email,
                    "password": new_password,
                    "generate_random": gen_random,
                    "length": pwd_length,
                    "use_numbers": use_nums,
                    "use_special": use_spec
                }
                res = requests.post(f"{API_URL}/passwords", json=payload)
                if res.status_code == 200:
                    st.success(f"Saved: {new_account}")
                    if gen_random:
                        st.code(res.json().get('generated_password'), language="plaintext")
                else:
                    st.error(f"Failed: {res.text}")
            else:
                st.warning("Account Name is required.")

    # --- TAB 3: UPDATE ---
    with tab3:
        st.subheader("Update Password")
        upd_account = st.text_input("Account to Update")
        upd_email = st.text_input("New Email (Optional)", key="upd_email") 
        
        upd_random = st.checkbox("Auto-generate New Password", value=True, key="upd_gen")
        
        upd_password = ""
        upd_length = 12
        upd_use_nums = True
        upd_use_spec = True
        
        if upd_random:
            st.markdown("---")
            st.write("🔧 AUTOGEN CRITERIA")
            upd_length = st.number_input("Length", min_value=8, max_value=128, value=12, key="upd_len")
            upd_use_nums = st.checkbox("Include Numbers", value=True, key="upd_num")
            upd_use_spec = st.checkbox("Include Special Characters", value=True, key="upd_spec")
            st.markdown("---")
        else:
            upd_password = st.text_input("New Custom Password", type="password", key="upd_pass")

        if st.button("Update Entry"):
            if upd_account:
                payload = {
                    "email": upd_email,
                    "password": upd_password,
                    "generate_random": upd_random,
                    "length": upd_length,
                    "use_numbers": upd_use_nums,
                    "use_special": upd_use_spec
                }
                res = requests.put(f"{API_URL}/passwords/{upd_account}", json=payload)
                if res.status_code == 200:
                    st.success(f"Updated: {upd_account}")
                    if upd_random:
                        st.code(res.json().get('new_password'), language="plaintext")
                elif res.status_code == 404:
                    st.error("Account not found.")
                else:
                    st.error(f"Failed: {res.text}")
            else:
                st.warning("Account Name required.")

    # --- TAB 4: DELETE ---
    with tab4:
        st.subheader("Delete Password")
        del_account = st.text_input("Account to Delete")
        
        if st.button("Delete Entry"):
            if del_account:
                res = requests.delete(f"{API_URL}/passwords/{del_account}")
                if res.status_code == 200:
                    st.success(f"Deleted: {del_account}")
                elif res.status_code == 404:
                    st.error("Account not found.")
                else:
                    st.error(f"Failed: {res.text}")
            else:
                st.warning("Account Name required.")