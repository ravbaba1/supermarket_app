import streamlit as st
import pandas as pd
import market_logic as ml
from datetime import datetime
import os

st.set_page_config(page_title="Supermarket Cloud POS (RBAC)", page_icon="🛒", layout="wide")

# Initialize persistent session state memory buffers
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None
if 'web_cart' not in st.session_state:
    st.session_state.web_cart = []
if 'last_receipt' not in st.session_state:
    st.session_state.last_receipt = None
if 'selected_reprint_id' not in st.session_state:
    st.session_state.selected_reprint_id = None

# ---- 1. LOGIN LAYER PANEL ----
if st.session_state.logged_in_user is None:
    st.title("🔐 Supermarket Secure Terminal Login")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.form("login_form"):
            username = st.text_input("Username:").strip().lower()
            password = st.text_input("Password:", type="password")
            btn = st.form_submit_button("Authenticate System Securely", use_container_width=True)
            
            if btn:
                profile = ml.check_login(username, password)
                if profile:
                    st.session_state.logged_in_user = {"username": username, "role": profile["role"], "name": profile["name"]}
                    st.success(f"Welcome back, {profile['name']}!")
                    st.rerun()
                else:
                    st.error("Invalid Username or Password configuration.")
    with col2:
        st.info("💡 **Developer Portfolio Notes**:\n* Sign in as **`admin`** with password **`admin123`** to access administrative staff creation suites and stock shelf logs.\n* Create a custom cashier account to test role restrictions.")

# ---- 2. MAIN APPLICATION INTERFACE LAYER ----
else:
    user = st.session_state.logged_in_user
    
    # Left Sidebar Control Dashboard Panels
    st.sidebar.title("🛒 POS Control Node")
    st.sidebar.write(f"Active Operator: **{user['name']}**")
    st.sidebar.info(f"🛡️ Authority Level: **{user['role']}**")
    
    if st.sidebar.button("Log Out of Terminal", use_container_width=True):
        st.session_state.logged_in_user = None
        st.session_state.web_cart = []
        st.session_state.last_receipt = None
        st.session_state.selected_reprint_id = None
        st.rerun()
        
    st.sidebar.markdown("---")
    
    # Configure navigation access arrays dynamically based on security level clearings
    nav_choices = ["Sales Counter Terminal", "Sales History & Reprints"]
    if user["role"] == "Admin":
        nav_choices.append("Stock Management shelves")
        nav_choices.append("Staff Profile Accounts")
        
    menu = st.sidebar.radio("Navigate Sections:", nav_choices)

    # VIEW 1: SALES COUNTER TERMINAL
    if menu == "Sales Counter Terminal":
        st.title("💰 Live Checkout Sales Counter Terminal")
        st.markdown("---")
        
        # Display the last printed customer receipt prominently if it exists
        if st.session_state.last_receipt:
            st.success("✅ TRANSACTION APPROVED & PAID SUCCESSFULLY!")
            with st.expander("🧾 View Active Customer Receipt Paper Ribbon", expanded=True):
                st.code(st.session_state.last_receipt, language="text")
                if st.button("Clear Receipt View Layout"):
                    st.session_state.last_receipt = None
                    st.rerun()
        
        c_left, c_right = st.columns()
        
        with c_left:
            st.subheader("📦 Available Stock Shelves")
            inv_data = ml.load_inventory()
            df_inv = pd.DataFrame(inv_data)
            st.dataframe(df_inv[["id", "name", "price", "stock"]], use_container_width=True, hide_index=True)
            
            # Simple item ringing framework widget tools
            st.subheader("⚡ Scan Barcode Item")
            scan_id = st.text_input("Enter Barcode / Product ID:").strip()
            scan_qty = st.number_input("Purchase Quantity:", min_value=1, value=1, step=1)
            
            if st.button("Ring Up Item into Cart", type="secondary", use_container_width=True):
                prod = next((p for p in inv_data if p["id"] == scan_id), None)
                if not prod:
                    st.error("Barcode item configuration unrecognized on store shelves.")
                elif prod["stock"] < scan_qty:
                    st.error(f"Insufficient stock levels! Only {prod['stock']} remaining.")
                else:
                    # Deduct quantity count instantly from application tracking array
                    prod["stock"] -= scan_qty
                    ml.save_inventory(inv_data)
                    
                    # Update local item session trays
                    cart_item = next((item for item in st.session_state.web_cart if item["id"] == scan_id), None)
                    if cart_item:
                        cart_item["qty"] += scan_qty
                    else:
                        st.session_state.web_cart.append({"id": prod["id"], "name": prod["name"], "price": prod["price"], "qty": scan_qty})
                    st.success(f"Added {prod['name']} to transaction bundle tray.")
                    st.rerun()

        with c_right:
            st.subheader("🛒 Current Shopping Cart Session")
            if not st.session_state.web_cart:
                st.info("Shopping cart is empty. Scan products to compile order balance tallies.")
            else:
                cart_rows = []
                total_checkout = 0.0
                for c in st.session_state.web_cart:
                    subt = c["price"] * c["qty"]
                    total_checkout += subt
                    cart_rows.append({"ID": c["id"], "Description": c["name"], "Unit Price": f"${c['price']:.2f}", "Qty": c["qty"], "Subtotal": f"${subt:.2f}"})
                
                st.dataframe(pd.DataFrame(cart_rows), use_container_width=True, hide_index=True)
                st.metric(label="Total Balance Due", value=f"${total_checkout:.2f}")
                
                if st.button("Complete Transaction & Authorize Payment", type="primary", use_container_width=True):
                    # Record tracking files transaction timestamps logs
                    now = datetime.now()
                    date_str = now.strftime("%Y-%m-%d %H:%M:%S")
                    txn_id = now.strftime("%Y%m%d%H%M%S")
                    
                    # 1. BUILD FORMATTED PAPER TEXT RECEIPT BLOCK
                    receipt_text = "========================================\n"
                    receipt_text += "          SUPERMARKET RETAIL POS        \n"
                    receipt_text += "========================================\n"
                    receipt_text += f"Txn ID:  {txn_id}\n"
                    receipt_text += f"Date:    {date_str}\n"
                    receipt_text += f"Cashier: {user['name']} ({user['role']})\n"
                    receipt_text += "========================================\n"
                    receipt_text += "Item Name          Price   Qty   Subtotal\n"
                    receipt_text += "----------------------------------------\n"
                    for c in st.session_state.web_cart:
                        item_sub = c["price"] * c["qty"]
                        receipt_text += f"{c['name']:<18} ${c['price']:>4.2f}   {c['qty']:>2}    ${item_sub:>5.2f}\n"
                    receipt_text += "----------------------------------------\n"
                    receipt_text += f"TOTAL AMOUNT PAID:             ${total_checkout:>5.2f}\n"
                    receipt_text += "========================================\n"
                    receipt_text += "       THANK YOU FOR YOUR PATRONAGE!     \n"
                    receipt_text += "========================================\n"
                    
                    # Save receipt string to state session buffer memory layout
                    st.session_state.last_receipt = receipt_text
                    
                    # 2. SAVE STRUCTURAL LOG DATA TO JSON LOG EXTENSION FILE FOR LOCAL PERSISTENCE REPRINTS
                    history_file = "sales_history.json"
                    history_data = []
                    if os.path.exists(history_file):
                        try:
                            with open(history_file, "r") as hf: history_data = json.load(hf)
                        except: history_data = []
                        
                    history_data.append({
                        "txn_id": txn_id,
                        "date": date_str,
                        "cashier": user['name'],
                        "total": total_checkout,
                        "receipt": receipt_text
                    })
                    
                    with open(history_file, "w") as hf:
                        json.dump(history_data, hf, indent=4)
                    
                    # Clear cart session memory
                    st.session_state.web_cart = []
                    st.balloons()
                    st.rerun()

        # VIEW 2: SALES HISTORY & REPRINTS (OPEN TO ALL ROLES)
    elif menu == "Sales History & Reprints":
        st.title("📋 Terminal Ledger Logs & Receipt Reprints")
        st.markdown("---")
        
        history_file = "sales_history.json"
        if not os.path.exists(history_file):
            st.info("No transaction logging records found in system storage databases yet.")
        else:
            with open(history_file, "r") as hf:
                history_data = json.load(hf)
                
            # Build analytical dashboard performance rows
            df_history = pd.DataFrame(history_data)
            
            # Show high-level accounting totals boxes
            col_a, col_b = st.columns(2)
            col_a.metric("Total Transactions Handled", len(df_history))
            col_b.metric("Gross Network Revenue", f"${df_history['total'].sum():.2f}")
            
            st.subheader("Master Transactions History Register Grid")
            st.dataframe(df_history[["txn_id", "date", "cashier", "total"]].rename(columns={"txn_id":"Transaction ID", "date":"Timestamp", "cashier":"Cashier Operating", "total":"Total Paid ($)"}), use_container_width=True, hide_index=True)
            
            # REPRINT SELECTOR CORE FEATURE BLOCK
            st.subheader("🧾 Select Transaction Reference to Reprint Receipt")
            txn_list = [t["txn_id"] for t in history_data]
            selected_txn = st.selectbox("Choose Transaction ID:", txn_list)
            
            if st.button("Fetch and Reprint Target Receipt Layout", type="secondary"):
                target_rec = next((t["receipt"] for t in history_data if t["txn_id"] == selected_txn), "")
                st.session_state.selected_reprint_id = target_rec
                
            if st.session_state.selected_reprint_id:
                st.info(f"✨ REPRINT RE-ISSUED FOR TRANSACTION ID: {selected_txn}")
                st.code(st.session_state.selected_reprint_id, language="text")
                if st.button("Close Reprint Ribbon Component View"):
                    st.session_state.selected_reprint_id = None
                    st.rerun()

    # VIEW 3: STOCK MANAGEMENT SHELVES (ADMIN PROMPT PRIVILEGES)
    elif menu == "Stock Management shelves":
        st.title("⚙️ Shelf Stock Configuration Management Panel")
        st.markdown("---")
        inv_data = ml.load_inventory()
        
        with st.form("inventory_add_form"):
            st.subheader("Adjust / Add Shelf Stock profiles")
            p_id = st.text_input("Product Barcode / ID:").strip()
            p_name = st.text_input("Product Name (New items only):").strip()
            p_price = st.number_input("Retail Price ($):", min_value=0.0, step=0.01)
            p_stock = st.number_input("Quantity count to add:", min_value=1, step=1)
            
            sub_btn = st.form_submit_button("Apply Stock Updates")
            if sub_btn:
                if not p_id:
                    st.error("Barcode index required.")
                else:
                    existing = next((p for p in inv_data if p["id"] == p_id), None)
                    if existing:
                        existing["stock"] += p_stock
                        if p_price > 0: existing["price"] = p_price
                        st.success(f"Restocked {existing['name']}. New count: {existing['stock']}")
                    else:
                        if not p_name or p_price <= 0:
                            st.error("Fill out name and price values to configure a new product profile configuration.")
                        else:
                            inv_data.append({"id": p_id, "name": p_name, "price": p_price, "stock": p_stock})
                            st.success(f"Successfully generated profile configuration for '{p_name}'")
                    ml.save_inventory(inv_data)
                    st.rerun()
                    
        st.subheader("Active Shelves System Monitor Matrix")
        st.dataframe(pd.DataFrame(inv_data), use_container_width=True, hide_index=True)

    # VIEW 4: STAFF PROFILE ACCOUNTS (ADMIN SECURED ROUTE)
    elif menu == "Staff Profile Accounts":
        st.title("👤 Employee Account Provisioning Dashboard")
        st.markdown("---")
        
        with st.form("create_user_form"):
            new_name = st.text_input("Full Employee Name:")
            new_user = st.text_input("Assign Username:").lower().strip()
            new_pass = st.text_input("Assign Temporary Password:", type="password")
            new_role = st.selectbox("Assign Security Privilege Role:", ["Cashier", "Admin"])
            
            create_btn = st.form_submit_button("Provision Employee Account Credentials", use_container_width=True)
            if create_btn:
                if new_name and new_user and new_pass:
                    success, message = ml.create_employee(user["username"], new_user, new_pass, new_name, new_role)
                    if success: st.success(message)
                    else: st.error(message)
                else: st.warning("Please fill out all credential inputs fields.")
                
        st.subheader("Active Terminal User Registry Logs")
        users_db = ml.load_users()
        user_list = [{"Username": u, "Full Name": data["name"], "Privilege Level": data["role"]} for u, data in users_db.items()]
        st.dataframe(pd.DataFrame(user_list), use_container_width=True, hide_index=True)
