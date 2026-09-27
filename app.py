import streamlit as st
import pandas as pd
import desktop_market  # 🔗 Connects directly to your logic file

st.set_page_config(page_title="Supermarket Management (RBAC)", page_icon="🛒", layout="wide")

# Persistent Session State Tracking
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None

# ---- LOGIN LAYER COMPONENT ----
if st.session_state.logged_in_user is None:
    st.title("🔐 Supermarket Login Portal")
    st.markdown("Use default portfolio testing credentials: **admin / admin123**")
    
    with st.form("login_form"):
        username = st.text_input("Username").strip()
        password = st.text_input("Password", type="password")
        btn = st.form_submit_button("Sign In")
        
        if btn:
            user_profile = desktop_market.check_login(username, password)
            if user_profile:
                st.session_state.logged_in_user = {
                    "username": username,
                    "role": user_profile["role"],
                    "name": user_profile["name"]
                }
                st.success(f"Log in successful. Welcome {user_profile['name']}!")
                st.rerun()
            else:
                st.error("Invalid Username or Password.")

# ---- MAIN APPLICATION LAYER ----
else:
    user = st.session_state.logged_in_user
    
    # Sidebar Header
    st.sidebar.title("🛒 Dashboard Controls")
    st.sidebar.write(f"**Logged in as:** {user['name']}")
    st.sidebar.info(f"🛡️ Role Privilege Level: **{user['role']}**")
    
    if st.sidebar.button("Logout Interface"):
        st.session_state.logged_in_user = None
        st.rerun()
        
    # Navigation View Selection
    menu = st.sidebar.selectbox("Navigation Options", ["Sales Checkout", "Create User Management"])
    
    # VIEW: CREATE USER MANAGEMENT (ADMIN SECURED ROUTE)
    if menu == "Create User Management":
        st.title("👤 Employee Account Provisioning")
        
        if user["role"] != "Admin":
            st.error("❌ Access Denied: Your current role privilege (Cashier) does not allow account creation.")
        else:
            st.markdown("As an **Admin**, you can onboard new cashiers and issue terminal credentials.")
            
            with st.form("create_user_form"):
                new_name = st.text_input("Full Employee Name")
                new_user = st.text_input("Assign Username").lower().strip()
                new_pass = st.text_input("Assign Temp Password", type="password")
                new_role = st.selectbox("Assign Security Role", ["Cashier", "Admin"])
                
                create_btn = st.form_submit_button("Provision Employee Account")
                
                if create_btn:
                    if new_name and new_user and new_pass:
                        # 🔗 Core logic connection run!
                        success, message = desktop_market.create_employee(
                            user["username"], new_user, new_pass, new_name, new_role
                        )
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                    else:
                        st.warning("Please fill out all credential input fields.")
                        
    # VIEW: SALES CHECKOUT (OPEN TO BOTH)
    elif menu == "Sales Checkout":
        st.title("💰 Live Sales Checkout Interface")
        st.write("Point of sale transaction controls are operational.")
