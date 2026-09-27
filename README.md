# Role-Based Enterprise Inventory & Point-of-Sale (POS) System

A hybrid full-stack retail management ecosystem designed to bridge localized native operations with remote administrative cloud management. Built completely in Python, this system utilizes **Role-Based Access Control (RBAC)** to enforce privilege constraints across dual-interface portals, all communicating with an integrated local storage engine.

---

## 🌐 Live Cloud Deployment
* **Interactive Web Application URL:** https://supermarketapp-6kcutapp3cbl8umfgotx9hq.streamlit.app/
* **Testing Credentials:**
  * **Administrator Access:** Username: `admin` | Password: `admin123` *(Full inventory provisioning rights)*
  * **Standard Cashier Access:** Create custom profiles via the Admin panel to test dynamic privilege lockouts instantly.

---

## 🚀 Key Architectural Features

* **Dual-Interface Synchronization:** Features a native graphical desktop interface (`tkinter`) designed for fast cashier scanning counters alongside a responsive network browser portal (`streamlit`) tailored for remote management.
* **Persistent Data Engine Layer:** Centralized architecture driving atomic data transactions to encrypted local JSON arrays (`inventory.json` & `users.json`), eliminating volatile state runtime data loss.
* **Granular Role-Based Access Control (RBAC):** Strict security layers checking operational context clearings. Cashiers are dynamically locked out from inventory adjustment trays and user creation tables, providing a completely isolated POS billing checkout environment.
* **Real-time Inventory Tracking & Restock Logic:** Unified validation algorithms that catch over-selling errors, handle shelf quantities, flag low stock lines, and restock existing barcodes rather than creating duplicates.
* **Persistent Transaction Ledger Audits:** Automated checkout pipeline logging custom receipts (`receipt.txt`) alongside a master history log tracker (`sales_history.json`) that computes total gross margins, item volume counts, and transactional operator time stamps.
* **Instant Digital Reprint Engine:** Browser-integrated billing layout allowing terminal users to dynamically select past reference IDs and reprint verified register receipts on demand.

---

## 📁 System Repository Components

* `market_logic.py` — The core logic package handling database reading, validation operations, and data persistence.
* `desktop_market.py` — The visual desktop window cashier counter workspace powered by Tkinter.
* `app.py` — The full-stack multi-role web wrapper terminal running live on the cloud browser.
* `inventory.json` — The master database containing product barcodes, prices, shelf names, and units.
* `users.json` — The encrypted system user register storing employee profiles and security authorization clearances.
* `requirements.txt` — Lists dependencies (`pandas`) to facilitate cloud server runtime environments.

---

## 💻 Running the Interfaces Locally

Make sure you are inside the project root folder directory in your shell command line console before running.

### 1. Launching the Local Cashier Counter Desktop App:
```bash
python desktop_market.py
```
*A native application window will spawn. Authenticate using your username and password.*

### 2. Launching the Browser Manager Web View Locally:
```bash
python -m streamlit run app.py
```
*Your computer will automatically host a local server connection node and deploy the interface inside your web browser.*

---

## 🎯 Portfolio Presentation Summary

> "Engineered an enterprise-grade retail inventory optimization and point-of-sale transactional data management suite using Python. Leveraged a shared JSON storage protocol to link a native event-driven Tkinter desktop cash register interface with a decoupled web dashboard architecture deployed to Streamlit Cloud. Designed and enforced strict Role-Based Access Control matrices to isolate operator privileges, integrated a real-time data analysis layer to compute daily revenue velocity arrays, and structured an autonomous digital auditing system capable of generating detailed text-based receipts and executing dynamic log file reprints."
