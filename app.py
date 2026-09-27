import streamlit as st
import pandas as pd
import market_logic as ml  # 🔗 Link to the cloud-safe logic file instead!

st.set_page_config(page_title="Supermarket Management (RBAC)", page_icon="🛒", layout="wide")

if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None

# ---- LOGIN LAYER ----
if st.session_state.logged_in_user is None:
    st.title("🔐 Supermarket Login Portal")
    with st.form("login_form"):
        username = st.text_input("Username").strip().lower()
        password = st.text_input("Password", type="password")
        btn = st.form_submit_button("Sign In")
        if btn:
            user_profile = ml.check_login(username, password)
            if user_profile:
                st.session_state.logged_in_user = {"username": username, "role": user_profile["role"], "name": user_profile["name"]}
                st.success("Log in successful!")
                st.rerun()
            else:
                st.error("Invalid Username or Password.")

# ---- MAIN APPLICATION LAYER ----
else:
    user = st.session_state.logged_in_user
    st.sidebar.title("🛒 Dashboard Controls")
    st.sidebar.write(f"Logged in as: **{user['name']}**")
    st.sidebar.info(f"Role: **{user['role']}**")
    
    if st.sidebar.button("Logout Interface"):
        st.session_state.logged_in_user = None
        st.rerun()
        
    menu = st.sidebar.selectbox("Navigation Options", ["Sales Checkout", "Create User Management"])
    
    if menu == "Create User Management":
        st.title("👤 Employee Account Provisioning")
        if user["role"] != "Admin":
            st.error("❌ Access Denied: Cashiers cannot create users.")
        else:
            with st.form("create_user_form"):
                new_name = st.text_input("Full Employee Name")
                new_user = st.text_input("Assign Username").lower().strip()
                new_pass = st.text_input("Assign Temp Password", type="password")
                new_role = st.selectbox("Assign Security Role", ["Cashier", "Admin"])
                create_btn = st.form_submit_button("Provision Employee Account")
                if create_btn:
                    if new_name and new_user and new_pass:
                        success, message = ml.create_employee(user["username"], new_user, new_pass, new_name, new_role)
                        if success: st.success(message)
                        else: st.error(message)
                    else: st.warning("Please fill out all fields.")
                    
            # Visual Employee Profiles Grid Table
            st.subheader("👥 Active System Profiles")
            users_db = ml.load_users()
            user_list = [{"Username": u, "Full Name": data["name"], "Privilege Level": data["role"]} for u, data in users_db.items()]
            st.dataframe(pd.DataFrame(user_list), use_container_width=True)
            
    elif menu == "Sales Checkout":
        st.title("💰 Live Sales Checkout Interface")
        st.write("Point of sale transaction controls are operational.")
        
        # Display current shelf items table
        st.subheader("📦 Current Shelf Inventory")
        inv_data = ml.load_inventory()
        st.dataframe(pd.DataFrame(inv_data), use_container_width=True)
