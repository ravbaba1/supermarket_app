import os
import json
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from datetime import datetime

# Database files
INVENTORY_FILE = "inventory.json"
USER_FILE = "users.json"

# ================= DATABASE ENGINE CONSTRUCTS =================

def load_inventory():
    if os.path.exists(INVENTORY_FILE):
        try:
            with open(INVENTORY_FILE, "r") as f: return json.load(f)
        except: return []
    return [
        {"id": "1001", "name": "Loaf of Bread", "price": 2.50, "stock": 50},
        {"id": "1002", "name": "Fresh Milk (1L)", "price": 3.10, "stock": 30}
    ]

def save_inventory(data):
    with open(INVENTORY_FILE, "w") as f: json.dump(data, f, indent=4)

def load_users():
    """Loads all system users. Creates a master admin if missing."""
    if not os.path.exists(USER_FILE):
        default_admin = {
            "admin": {"password": "admin123", "role": "Admin", "name": "System Administrator"}
        }
        with open(USER_FILE, "w") as f:
            json.dump(default_admin, f, indent=4)
        return default_admin
    with open(USER_FILE, "r") as f:
        try: return json.load(f)
        except: return {}

def save_users(users_data):
    with open(USER_FILE, "w") as f: json.dump(users_data, f, indent=4)

# Load databases into application memory
inventory = load_inventory()
cart = []

# ================= ACCESS LOGS & ACCOUNT RUNTIME =================
CURRENT_USER = None
USER_ROLE = None
CASHIER_NAME = None

def run_secure_login():
    """Launches a full username and password challenge window before opening main app."""
    global CURRENT_USER, USER_ROLE, CASHIER_NAME
    
    login_win = tk.Tk()
    login_win.title("POS Terminal Security Login")
    login_win.geometry("340x220")
    login_win.resizable(False, False)
    
    tk.Label(login_win, text="Username:", font=("Arial", 10, "bold")).pack(pady=5)
    ent_username = tk.Entry(login_win, width=28)
    ent_username.pack()
    ent_username.focus()
    
    tk.Label(login_win, text="Password:", font=("Arial", 10, "bold")).pack(pady=5)
    ent_password = tk.Entry(login_win, width=28, show="*")
    ent_password.pack()
    
    def attempt_login():
        global CURRENT_USER, USER_ROLE, CASHIER_NAME
        u_name = ent_username.get().strip().lower()
        p_word = ent_password.get().strip()
        
        users_db = load_users()
        if u_name in users_db and users_db[u_name]["password"] == p_word:
            CURRENT_USER = u_name
            USER_ROLE = users_db[u_name]["role"]
            CASHIER_NAME = users_db[u_name]["name"]
            login_win.destroy()
        else:
            messagebox.showerror("Access Denied", "Invalid Username or Password configuration.")
            
    tk.Button(login_win, text="Authenticate System Securely", bg="#2c3e50", fg="white", font=("Arial", 10, "bold"), command=attempt_login, width=25).pack(pady=20)
    login_win.mainloop()

run_secure_login()

# Kill execution cleanly if they bypassed login window completely
if not CURRENT_USER:
    os._exit(0)

# ================= CORE RETRIES & APP INTERFACES =================

def refresh_grid():
    for item in tree.get_children(): tree.delete(item)
    for p in inventory:
        status = "OK" if p["stock"] > 5 else "LOW STOCK"
        tree.insert("", tk.END, values=(p["id"], p["name"], f"${p['price']:.2f}", p["stock"], status))

def refresh_cart_grid():
    for item in cart_tree.get_children(): cart_tree.delete(item)
    total = 0.0
    for c in cart:
        item_total = c["price"] * c["qty"]
        total += item_total
        cart_tree.insert("", tk.END, values=(c["id"], c["name"], f"${c['price']:.2f}", c["qty"], f"${item_total:.2f}"))
    lbl_total.config(text=f"Total: ${total:.2f}")

def refresh_users_grid():
    """Refreshes the dynamic employee profiles visual table."""
    if 'users_tree' in globals():
        for item in users_tree.get_children(): users_tree.delete(item)
        users_db = load_users()
        for u_username, u_info in users_db.items():
            users_tree.insert("", tk.END, values=(u_username, u_info["name"], u_info["role"]))

def handle_inventory_adjustment():
    p_id = ent_id.get().strip()
    name = ent_name.get().strip()
    price = ent_price.get().strip()
    stock_input = ent_stock.get().strip()
    
    if not (p_id and stock_input):
        messagebox.showerror("Error", "Barcode and Quantity required!")
        return
    qty_to_add = int(stock_input) if stock_input.isdigit() else 0
    
    existing_product = next((p for p in inventory if p["id"] == p_id), None)
    if existing_product:
        existing_product["stock"] += qty_to_add
        if price: existing_product["price"] = float(price)
        messagebox.showinfo("Restocked", f"Added inventory units. New count: {existing_product['stock']}")
    else:
        if not name or not price:
            messagebox.showerror("Error", "Fill out Name and Price for a brand new item profile configuration.")
            return
        inventory.append({"id": p_id, "name": name, "price": float(price), "stock": qty_to_add})
        messagebox.showinfo("Success", "New profile mapped successfully.")
        
    save_inventory(inventory)
    refresh_grid()
    ent_id.delete(0, tk.END); ent_name.delete(0, tk.END); ent_price.delete(0, tk.END); ent_stock.delete(0, tk.END)

def delete_product_profile():
    selected_item = tree.selection()
    if not selected_item: return
    values = tree.item(selected_item, "values")
    confirm = messagebox.askyesno("Confirm", f"Remove item ID {values[0]} entirely?")
    if confirm:
        global inventory
        inventory = [p for p in inventory if p["id"] != values[0]]
        save_inventory(inventory)
        refresh_grid()

def provision_new_employee():
    """Allows an Admin to onboard an employee and save to users.json."""
    emp_username = ent_new_user.get().strip().lower()
    emp_password = ent_new_pass.get().strip()
    emp_name = ent_new_name.get().strip()
    emp_role = combo_new_role.get()
    
    if not (emp_username and emp_password and emp_name):
        messagebox.showerror("Error", "All creation fields are mandatory!")
        return
        
    users_db = load_users()
    if emp_username in users_db:
        messagebox.showerror("Duplicate", "Username already exists in storage registers.")
        return
        
    users_db[emp_username] = {"password": emp_password, "role": emp_role, "name": emp_name}
    save_users(users_db)
    refresh_users_grid()
    ent_new_user.delete(0, tk.END); ent_new_pass.delete(0, tk.END); ent_new_name.delete(0, tk.END)
    messagebox.showinfo("Success", f"Provisioned profile credentials for {emp_name}!")

def add_to_cart():
    scan_id = ent_scan.get().strip()
    scan_qty_str = ent_qty.get().strip()
    if not scan_id: return
    qty = int(scan_qty_str) if scan_qty_str.isdigit() else 1
    
    product = next((p for p in inventory if p["id"] == scan_id), None)
    if not product or product["stock"] < qty:
        messagebox.showerror("Error", "Invalid checkout product lookup choice or unavailable stock quantities."); return
        
    product["stock"] -= qty
    cart_item = next((c for c in cart if c["id"] == scan_id), None)
    if cart_item: cart_item["qty"] += qty
    else: cart.append({"id": product["id"], "name": product["name"], "price": product["price"], "qty": qty})
    refresh_grid(); refresh_cart_grid()
    ent_scan.delete(0, tk.END); ent_qty.delete(0, tk.END); ent_qty.insert(0, "1")

def checkout_complete():
    global cart
    if not cart: return
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M:%S")
    transaction_id = now.strftime("%Y%m%d%H%M%S")
    total = sum(c["price"] * c["qty"] for c in cart)

    with open("receipt.txt", "w") as f:
        f.write(f"Txn: {transaction_id}\nOperator: {CASHIER_NAME} ({USER_ROLE})\nDate: {date_str}\nTotal: ${total:.2f}\n")
    with open("sales_history.txt", "a") as h:
        h.write(f"[{date_str}] TXN#{transaction_id} | Clerk: {CASHIER_NAME} ({USER_ROLE}) | Revenue: ${total:.2f}\n")
        
    save_inventory(inventory); cart = []; refresh_cart_grid()
    messagebox.showinfo("Approved", "Receipt generated.")

def view_history_log():
    """Calculates dynamic financial performance summaries and opens raw audit log text files."""
    if not os.path.exists("sales_history.txt"):
        messagebox.showinfo("Log Empty", "No transactional history records logged yet.")
        return
        
    # Get current date stamp prefix to check records matching today
    today_prefix = datetime.now().strftime("%Y-%m-%d")
    
    total_revenue_today = 0.0
    total_transactions_today = 0
    
    try:
        with open("sales_history.txt", "r") as h:
            for line in h:
                # Check if the text row contains today's date stamp and a cash index total indicator
                if today_prefix in line and "Revenue:" in line:
                    total_transactions_today += 1
                    # Extract numeric total value directly out of the matched string segment split
                    parts = line.split("Revenue: $")
                    if len(parts) > 1:
                        revenue_val = float(parts[1].split()[0].strip())
                        total_revenue_today += revenue_val
                        
        # Display the financial summary insights box
        summary_msg = (
            f"=== 📊 TODAY'S SALES SUMMARY ===\n"
            f"Date Focus: {today_prefix}\n\n"
            f"Transactions Handled: {total_transactions_today}\n"
            f"Total Gross Revenue:   ${total_revenue_today:.2f}\n"
            f"================================\n\n"
            f"Click OK to review raw history log records file."
        )
        messagebox.showinfo("Accounting Dashboard Insights", summary_msg)
        
    except Exception as e:
        print(f"Log calculation error: {e}")

    # Launch local file editor window automatically for record audit review
    os.system("notepad.exe sales_history.txt" if os.name == "nt" else "open sales_history.txt")

# ================= ROOT MAIN APP USER LAYOUT WINDOW =================


root = tk.Tk()
root.title(f"Supermarket Framework POS Engine - Node Authority: {USER_ROLE}")
root.geometry("1200x650")

# --- LEFT COLUMN COMPONENT LAYER ---
left_pane = tk.Frame(root, padx=10, pady=10)
left_pane.pack(side="left", fill="both", expand=True)

frame_form = tk.LabelFrame(left_pane, text=" Inventory Management Panel ")
frame_form.pack(fill="x", pady=5, ipady=5)

tk.Label(frame_form, text="Barcode:").grid(row=0, column=0, padx=5, pady=2)
ent_id = tk.Entry(frame_form, width=8)
ent_id.grid(row=0, column=1, padx=5, pady=2)

tk.Label(frame_form, text="Name:").grid(row=0, column=2, padx=5, pady=2)
ent_name = tk.Entry(frame_form, width=12)
ent_name.grid(row=0, column=3, padx=5, pady=2)

tk.Label(frame_form, text="Price:").grid(row=1, column=0, padx=5, pady=2)
ent_price = tk.Entry(frame_form, width=8)
ent_price.grid(row=1, column=1, padx=5, pady=2)

tk.Label(frame_form, text="Qty:").grid(row=1, column=2, padx=5, pady=2)
ent_stock = tk.Entry(frame_form, width=12)
ent_stock.grid(row=1, column=3, padx=5, pady=2)

btn_save = tk.Button(frame_form, text="Apply Stock", bg="#2980b9", fg="white", command=handle_inventory_adjustment)
btn_save.grid(row=0, column=4, rowspan=2, padx=5, pady=2)

btn_del_prof = tk.Button(frame_form, text="Delete Item", bg="#c0392b", fg="white", command=delete_product_profile)
btn_del_prof.grid(row=0, column=5, rowspan=2, padx=5, pady=2)

cols = ("id", "name", "price", "stock", "status")
tree = ttk.Treeview(left_pane, columns=cols, show="headings", height=10)
tree.heading("id", text="Barcode")
tree.heading("name", text="Product")
tree.heading("price", text="Price")
tree.heading("stock", text="Stock")
tree.heading("status", text="Status")

tree.column("id", width=60, anchor="center")
tree.column("name", width=120)
tree.column("price", width=60, anchor="center")
tree.column("stock", width=50, anchor="center")
tree.column("status", width=70, anchor="center")
tree.pack(fill="both", expand=True, pady=5)

# --- ADMIN SECURED EMPLOYEE SYSTEM CONTROL TRAYS ---
if USER_ROLE == "Admin":
    frame_admin = tk.LabelFrame(left_pane, text=" 🛡️ Admin Suite: Onboard Staff Accounts ", fg="blue", padx=10, pady=5)
    frame_admin.pack(fill="both", expand=True, pady=10)
    
    tk.Label(frame_admin, text="Username:").grid(row=0, column=0, padx=5, pady=2)
    ent_new_user = tk.Entry(frame_admin, width=12)
    ent_new_user.grid(row=0, column=1, padx=5, pady=2)
    
    tk.Label(frame_admin, text="Password:").grid(row=0, column=2, padx=5, pady=2)
    ent_new_pass = tk.Entry(frame_admin, width=12, show="*")
    ent_new_pass.grid(row=0, column=3, padx=5, pady=2)
    
    tk.Label(frame_admin, text="Full Name:").grid(row=1, column=0, padx=5, pady=2)
    ent_new_name = tk.Entry(frame_admin, width=12)
    ent_new_name.grid(row=1, column=1, padx=5, pady=2)
    
    tk.Label(frame_admin, text="Role:").grid(row=1, column=2, padx=5, pady=2)
    combo_new_role = ttk.Combobox(frame_admin, values=["Cashier", "Admin"], width=10, state="readonly")
    combo_new_role.set("Cashier")
    combo_new_role.grid(row=1, column=3, padx=5, pady=2)
    
    btn_provision = tk.Button(frame_admin, text="Provision Account", bg="#8e44ad", fg="white", font=("Arial", 9, "bold"), command=provision_new_employee)
    btn_provision.grid(row=0, column=4, rowspan=2, padx=15, pady=2)
    
    # Visual User Table View
    users_cols = ("username", "name", "role")
    users_tree = ttk.Treeview(frame_admin, columns=users_cols, show="headings", height=4)
    users_tree.heading("username", text="Username")
    users_tree.heading("name", text="Full Name")
    users_tree.heading("role", text="Privilege Level")
    
    users_tree.column("username", width=80, anchor="center")
    users_tree.column("name", width=140)
    users_tree.column("role", width=80, anchor="center")
    users_tree.grid(row=2, column=0, columnspan=5, pady=8, padx=5, sticky="nsew")
    
    refresh_users_grid()
else:
    # Strong Security Enforcement Lockouts for standard Cashiers
    ent_id.config(state="disabled")
    ent_name.config(state="disabled")
    ent_price.config(state="disabled")
    ent_stock.config(state="disabled")
    btn_save.config(state="disabled")
    btn_del_prof.config(state="disabled")
    frame_form.config(text=" Stock Management (LOCKED - MANAGERS/ADMIN ONLY) ")

# --- RIGHT COLUMN COMPONENT LAYER ---
right_pane = tk.LabelFrame(root, text=f" 🛒 Terminal Operator Station: {CASHIER_NAME} ", padx=10, pady=10)
right_pane.pack(side="right", fill="both", expand=True, padx=10, pady=10)

scan_frame = tk.Frame(right_pane)
scan_frame.pack(fill="x", pady=5)

tk.Label(scan_frame, text="Barcode:", font=("Arial", 10, "bold")).pack(side="left")
ent_scan = tk.Entry(scan_frame, width=12, font=("Arial", 11))
ent_scan.pack(side="left", padx=5)

tk.Label(scan_frame, text="Qty:").pack(side="left")
ent_qty = tk.Entry(scan_frame, width=4)
ent_qty.pack(side="left", padx=2)
ent_qty.insert(0, "1")

btn_ring = tk.Button(scan_frame, text="Ring Up", bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), command=add_to_cart)
btn_ring.pack(side="left", padx=10)

cart_cols = ("id", "name", "price", "qty", "total")
cart_tree = ttk.Treeview(right_pane, columns=cart_cols, show="headings", height=12)
cart_tree.heading("id", text="ID")
cart_tree.heading("name", text="Description")
cart_tree.heading("price", text="Unit")
cart_tree.heading("qty", text="Qty")
cart_tree.heading("total", text="Subtotal")

cart_tree.column("id", width=40, anchor="center")
cart_tree.column("name", width=140)
cart_tree.column("price", width=60, anchor="center")
cart_tree.column("qty", width=40, anchor="center")
cart_tree.column("total", width=60, anchor="center")
cart_tree.pack(fill="both", expand=True, pady=5)

checkout_frame = tk.Frame(right_pane)
checkout_frame.pack(fill="x", pady=5)

lbl_total = tk.Label(checkout_frame, text="Total: $0.00", font=("Arial", 16, "bold"), fg="#c0392b")
lbl_total.pack(side="left", padx=5)

btn_pay = tk.Button(checkout_frame, text="Pay & Print", bg="#e67e22", fg="white", font=("Arial", 11, "bold"), command=checkout_complete)
btn_pay.pack(side="right", padx=5)

btn_hist = tk.Button(checkout_frame, text="📋 History Log", bg="#7f8c8d", fg="white", font=("Arial", 11, "bold"), command=view_history_log)
btn_hist.pack(side="right", padx=5)

refresh_grid()
root.mainloop()
