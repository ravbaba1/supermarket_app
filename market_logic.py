import os
import json
from datetime import datetime

INVENTORY_FILE = "inventory.json"
USER_FILE = "users.json"

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
    if not os.path.exists(USER_FILE):
        default_admin = {"admin": {"password": "admin123", "role": "Admin", "name": "System Administrator"}}
        with open(USER_FILE, "w") as f: json.dump(default_admin, f, indent=4)
        return default_admin
    with open(USER_FILE, "r") as f:
        try: return json.load(f)
        except: return {}

def save_users(users_data):
    with open(USER_FILE, "w") as f: json.dump(users_data, f, indent=4)

def check_login(username, password):
    users = load_users()
    if username in users and users[username]["password"] == password:
        return users[username]
    return None

def create_employee(admin_username, new_username, new_password, employee_name, role="Cashier"):
    users = load_users()
    if users.get(admin_username, {}).get("role") != "Admin":
        return False, "Unauthorized: Only Admins can create users."
    if new_username in users:
        return False, f"Username '{new_username}' already exists."
    users[new_username] = {"password": new_password, "role": role, "name": employee_name}
    save_users(users)
    return True, f"Success: Created account for {employee_name}."
