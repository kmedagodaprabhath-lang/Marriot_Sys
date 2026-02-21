import tkcalendar 
from tkcalendar import DateEntry
import tkinter as tk
from tkinter import messagebox, filedialog, ttk, simpledialog
import csv, os, datetime, uuid, ast

# ========================================================
# [CORE UI & THEME SETTINGS]
# ========================================================
CORE_UI = {
    "THEME": {
        "BG": "#0F0F0F", "CARD": "#1A1A1A", "HOVER": "#D32F2F", 
        "ACCENT": "#FFFFFF", "HEADER": "#252525", "SELECT": "#D32F2F", 
        "ON": "#43A047", "LOW": "#9370DB", "GRID_BG": "#111111" 
    }
}

PASSWORDS = {
    "COST": "101", "CHEF": "202", "STORE": "303", 
    "01. Beira Kitchen": "1", "02. Pastry Kitchen": "2", "03. Butchery": "3",
    "04. Cold Kitchen": "4", "05. Titos": "5", "06. Banquet Kitchen": "6",
    "07. The Lounge": "7", "08. Banquet Service": "8", "09. Us Embassy": "9", "10. Ird Service": "10"
}

OUTLET_NAMES = ["01. Beira Kitchen", "02. Pastry Kitchen", "03. Butchery", "04. Cold Kitchen", "05. Titos",
                "06. Banquet Kitchen", "07. The Lounge", "08. Banquet Service", "09. Us Embassy", "10. Ird Service"]

BASE_DIR = os.path.expanduser("~")
DB_FILE = os.path.join(BASE_DIR, 'marriott_inventory.csv')
TRANS_FILE = os.path.join(BASE_DIR, 'marriott_transactions.csv')

class MarriottUltimateSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Marriott v230 - Cost Controller Master")
        self.root.state('zoomed') 
        self.root.configure(bg=CORE_UI["THEME"]["BG"])
        self.role, self.selected_outlet, self.inventory, self.cart = None, None, [], []
        self.all_cols = ['Product code', 'Catogory', 'Product Description', 'Stock On Hand', 'Unit cost', 'Total Value', 'Min Par', 'Max Par']
        
        self.setup_styles()
        self.init_files()
        self.show_login_screen()

    def init_files(self):
        for f in [DB_FILE, TRANS_FILE]:
            if not os.path.exists(f):
                with open(f, 'w', newline='', encoding='utf-8') as file:
                    csv.writer(file).writerow(self.all_cols if f == DB_FILE else ['ReqID', 'Date', 'Outlet', 'Subject', 'TotalValue', 'Status', 'Items'])

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=CORE_UI["THEME"]["GRID_BG"], foreground="white", 
                        fieldbackground=CORE_UI["THEME"]["GRID_BG"], rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=CORE_UI["THEME"]["HEADER"], foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[('selected', CORE_UI["THEME"]["SELECT"])])

    def safe_float(self, val):
        try: return float(str(val).replace(',', '').strip())
        except: return 0.0

    def clear_ui(self):
        for w in self.root.winfo_children(): w.destroy()

    def load_data(self):
        try:
            with open(DB_FILE, 'r', encoding='utf-8-sig') as f: self.inventory = list(csv.DictReader(f))
        except: self.inventory = []

    def show_login_screen(self):
        self.clear_ui()
        c = tk.Frame(self.root, bg=CORE_UI["THEME"]["BG"]); c.pack(expand=True)
        tk.Label(c, text="COURTYARD BY MARRIOTT", font=("Times New Roman", 50, "bold"), bg=CORE_UI["THEME"]["BG"], fg="white").pack(pady=40)
        roles = [("COST CONTROLLER", "COST"), ("EXECUTIVE CHEF", "CHEF"), ("STOREKEEPER", "STORE"), ("OUTLET TEAM", "OUTLET_SEL")]
        for txt, rcode in roles:
            tk.Button(c, text=txt, font=("Arial", 12, "bold"), bg=CORE_UI["THEME"]["CARD"], fg="white", width=50, height=2, bd=0, 
                      command=lambda r=rcode: self.auth_overlay(r) if r != "OUTLET_SEL" else self.build_outlet_selection_ui()).pack(pady=10)

    def auth_overlay(self, rcode):
        self.ov = tk.Frame(self.root, bg=CORE_UI["THEME"]["BG"]); self.ov.place(x=0, y=0, relwidth=1, relheight=1)
        center = tk.Frame(self.ov, bg=CORE_UI["THEME"]["CARD"], padx=40, pady=40); center.pack(expand=True)
        tk.Label(center, text=f"PASSWORD FOR {rcode}", fg="white", bg=CORE_UI["THEME"]["CARD"], font=("Arial", 12, "bold")).pack(pady=10)
        self.pwd_ent = tk.Entry(center, font=("Arial", 24), show="*", bg="#000", fg=CORE_UI["THEME"]["ON"], justify="center", width=12)
        self.pwd_ent.pack(pady=15); self.pwd_ent.focus_set()
        self.pwd_ent.bind("<Return>", lambda e: self.verify_login(rcode))
        tk.Button(center, text="LOGIN", bg=CORE_UI["THEME"]["ON"], fg="white", width=20, height=2, command=lambda: self.verify_login(rcode)).pack(pady=10)
        tk.Button(center, text="CANCEL", bg="#444", fg="white", width=10, command=self.ov.destroy).pack()

    def verify_login(self, rcode):
        if self.pwd_ent.get() == PASSWORDS.get(rcode) or (rcode in OUTLET_NAMES and self.pwd_ent.get() == PASSWORDS.get(rcode)):
            self.role = rcode; self.ov.destroy()
            if rcode == "COST": self.build_cost_controller_ui()
            elif rcode == "CHEF": self.build_chef_dashboard()
            elif rcode == "STORE": self.build_store_dashboard()
            else: self.setup_order_meta(rcode)
        else: messagebox.showerror("Error", "Invalid Password!")

    def build_cost_controller_ui(self):
        self.clear_ui(); self.load_data()
        header = tk.Frame(self.root, bg=CORE_UI["THEME"]["HEADER"]); header.pack(fill="x", ipady=5)
        tk.Label(header, text="COST CONTROLLER MASTER PANEL", bg=CORE_UI["THEME"]["HEADER"], fg="white", font=("Arial", 14, "bold")).pack(side="left", padx=20)
        tk.Button(header, text="LOGOUT", bg="#D32F2F", fg="white", command=self.show_login_screen).pack(side="right", padx=20)

        ctrl_f = tk.Frame(self.root, bg=CORE_UI["THEME"]["BG"], pady=10); ctrl_f.pack(fill="x", padx=20)
        tk.Button(ctrl_f, text="+ NEW ITEM", bg="#2196F3", fg="white", font=("Arial", 9, "bold"), width=15, command=self.add_new_item_popup).pack(side="left", padx=5)
        tk.Button(ctrl_f, text="🗑️ DELETE ITEM", bg="#f44336", fg="white", font=("Arial", 9, "bold"), width=15, command=self.delete_inventory_item).pack(side="left", padx=5)
        tk.Button(ctrl_f, text="📥 UPDATE VIA CSV", bg=CORE_UI["THEME"]["ON"], fg="white", font=("Arial", 9, "bold"), width=18, command=self.import_csv).pack(side="left", padx=5)
        tk.Button(ctrl_f, text="📤 EXPORT MASTER", bg="#607D8B", fg="white", font=("Arial", 9, "bold"), width=18, command=lambda: self.export_to_csv(False)).pack(side="left", padx=5)
        tk.Button(ctrl_f, text="💜 EXPORT BELOW PAR", bg=CORE_UI["THEME"]["LOW"], fg="white", font=("Arial", 9, "bold"), width=22, command=lambda: self.export_to_csv(True)).pack(side="left", padx=5)

        self.admin_tree = ttk.Treeview(self.root, columns=self.all_cols, show='headings')
        for c in self.all_cols: self.admin_tree.heading(c, text=c.upper()); self.admin_tree.column(c, width=120, anchor="center")
        self.admin_tree.tag_configure('low_stock', background=CORE_UI["THEME"]["LOW"], foreground="white")
        self.admin_tree.pack(fill="both", expand=True, padx=20, pady=5)
        
        tk.Label(self.root, text="APPROVED REQUESTS (FOR PRINTING)", bg=CORE_UI["THEME"]["HEADER"], fg="white", font=("Arial", 10, "bold")).pack(fill="x")
        self.trans_tree = ttk.Treeview(self.root, columns=('ID', 'Date', 'Outlet', 'Status'), show='headings', height=6)
        for c in ('ID', 'Date', 'Outlet', 'Status'): self.trans_tree.heading(c, text=c); self.trans_tree.column(c, anchor="center")
        self.trans_tree.pack(fill="x", padx=20, pady=5)
        tk.Button(self.root, text="🖨️ PRINT SELECTED REQUEST (A4)", bg="#FF9800", fg="black", font=("Arial", 10, "bold"), height=2, command=self.print_selected_trans).pack(pady=5)
        
        self.refresh_admin_table(); self.load_transactions("CHEF APPROVED", self.trans_tree)

    # --- [UPDATED NEW ITEM POPUP - v230] ---
    def add_new_item_popup(self):
        win = tk.Toplevel(self.root); win.title("Add New Article"); win.geometry("450x550"); win.configure(bg=CORE_UI["THEME"]["CARD"])
        win.grab_set() # Make it modal
        
        tk.Label(win, text="ADD NEW INVENTORY ITEM", font=("Arial", 14, "bold"), bg=CORE_UI["THEME"]["CARD"], fg=CORE_UI["THEME"]["ON"]).pack(pady=20)
        
        fields = [("Product Code:", "code"), ("Category:", "cat"), ("Description:", "desc"), 
                  ("Unit Cost:", "cost"), ("Min Par Qty:", "min_par")]
        entries = {}

        for lbl_txt, key in fields:
            tk.Label(win, text=lbl_txt, bg=CORE_UI["THEME"]["CARD"], fg="white", font=("Arial", 10)).pack(pady=(10, 0), padx=40, anchor="w")
            ent = tk.Entry(win, font=("Arial", 12), bg="#000", fg="white", insertbackground="white")
            ent.pack(pady=5, padx=40, fill="x")
            entries[key] = ent

        def submit():
            data = {k: v.get().strip() for k, v in entries.items()}
            if not data['code'] or not data['desc']:
                messagebox.showerror("Error", "Product Code and Description are required!", parent=win)
                return
            
            new_row = {c: "0" for c in self.all_cols}
            new_row.update({
                'Product code': data['code'], 'Catogory': data['cat'], 'Product Description': data['desc'],
                'Unit cost': str(self.safe_float(data['cost'])), 'Min Par': str(self.safe_float(data['min_par']))
            })
            self.inventory.append(new_row); self.save_to_db(); self.refresh_admin_table(); win.destroy()
            messagebox.showinfo("Success", "New Item Added Successfully!")

        tk.Button(win, text="ADD TO SYSTEM", bg=CORE_UI["THEME"]["ON"], fg="white", font=("Arial", 11, "bold"), 
                  height=2, command=submit).pack(pady=30, padx=40, fill="x")

    def refresh_admin_table(self):
        for i in self.admin_tree.get_children(): self.admin_tree.delete(i)
        for r in self.inventory:
            stock, min_par = self.safe_float(r.get('Stock On Hand', 0)), self.safe_float(r.get('Min Par', 0))
            tag = 'low_stock' if stock < min_par else ''
            self.admin_tree.insert('', 'end', values=[r.get(c, "0") for c in self.all_cols], tags=(tag,))

    def delete_inventory_item(self):
        sel = self.admin_tree.selection()
        if not sel: return
        if messagebox.askyesno("Confirm", "Delete this item permanently?"):
            idx = self.admin_tree.index(sel[0]); del self.inventory[idx]; self.save_to_db(); self.refresh_admin_table()

    def export_to_csv(self, below_par_only):
        data = self.inventory
        if below_par_only: data = [r for r in self.inventory if self.safe_float(r.get('Stock On Hand')) < self.safe_float(r.get('Min Par'))]
        if not data: messagebox.showinfo("Info", "No data to export!"); return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                dw = csv.DictWriter(f, fieldnames=self.all_cols); dw.writeheader(); dw.writerows(data)
            messagebox.showinfo("Success", "Exported Successfully!")

    def save_to_db(self):
        with open(DB_FILE, 'w', newline='', encoding='utf-8') as f:
            dw = csv.DictWriter(f, fieldnames=self.all_cols); dw.writeheader(); dw.writerows(self.inventory)

    def import_csv(self):
        p = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if p:
            try:
                with open(p, 'r', encoding='utf-8-sig') as f:
                    raw = list(csv.DictReader(f)); cleaned = []
                    for row in raw:
                        r = {k.strip(): v.strip() for k, v in row.items()}
                        s, uc = self.safe_float(r.get('Stock On Hand',0)), self.safe_float(r.get('Unit cost',0))
                        r['Total Value'] = f"{s * uc:.2f}"
                        cleaned.append({col: r.get(col, "0") for col in self.all_cols})
                    self.inventory = cleaned; self.save_to_db(); self.refresh_admin_table()
                messagebox.showinfo("Success", "Inventory Synced!")
            except Exception as e: messagebox.showerror("Error", str(e))

    def load_transactions(self, status, tree):
        for i in tree.get_children(): tree.delete(i)
        try:
            with open(TRANS_FILE, 'r') as f:
                for r in csv.DictReader(f):
                    if r['Status'] == status: tree.insert('', 'end', values=(r['ReqID'], r['Date'], r['Outlet'], r['Status']))
        except: pass

    def print_selected_trans(self):
        sel = self.trans_tree.selection()
        if not sel: return
        rid = self.trans_tree.item(sel[0], 'values')[0]
        with open(TRANS_FILE, 'r') as f:
            for r in csv.DictReader(f):
                if r['ReqID'] == rid: self.show_transaction_print(r); break

    def show_transaction_print(self, req_data):
        items = ast.literal_eval(req_data['Items'])
        pv = tk.Toplevel(self.root); pv.title("PRINT VIEW"); pv.state('zoomed')
        can = tk.Canvas(pv, bg="white", width=800, height=1100); can.pack(pady=20, expand=True)
        can.create_text(400, 50, text="COURTYARD BY MARRIOTT COLOMBO", font=("Arial", 16, "bold"))
        can.create_text(400, 80, text="STOCK REQUISITION (A4)", font=("Arial", 12, "bold", "underline"))
        can.create_text(60, 150, text=f"REQ ID: {req_data['ReqID']} | DATE: {req_data['Date']} | OUTLET: {req_data['Outlet']}", anchor="w")
        y = 200; can.create_text(60, y, text="ITEM DESCRIPTION", anchor="w", font=("Arial", 10, "bold"))
        can.create_text(500, y, text="QTY", anchor="e", font=("Arial", 10, "bold")); can.create_text(700, y, text="VALUE", anchor="e", font=("Arial", 10, "bold"))
        y += 30
        for i in items:
            can.create_text(60, y, text=str(i['Desc'])[:50], anchor="w")
            can.create_text(500, y, text=f"{i['Qty']:.2f}", anchor="e")
            can.create_text(700, y, text=f"{i['Total']:,.2f}", anchor="e"); y += 25
        can.create_text(700, y+40, text=f"GRAND TOTAL: LKR {float(req_data['TotalValue']):,.2f}", anchor="e", font=("Arial", 12, "bold"))

    # (Chef, Store, Outlet sections stay the same as v229)
    def build_chef_dashboard(self):
        self.clear_ui(); tk.Label(self.root, text="EXECUTIVE CHEF - APPROVAL PANEL", bg=CORE_UI["THEME"]["HEADER"], fg="white", font=("Arial", 12, "bold")).pack(fill="x", ipady=15)
        main_f = tk.Frame(self.root, bg=CORE_UI["THEME"]["BG"]); main_f.pack(fill="both", expand=True, padx=20, pady=10)
        list_f = tk.Frame(main_f, bg=CORE_UI["THEME"]["BG"]); list_f.pack(side="left", fill="both", expand=True)
        self.chef_tree = ttk.Treeview(list_f, columns=('ID', 'Outlet', 'Subject', 'Status'), show='headings')
        for c in ('ID', 'Outlet', 'Subject', 'Status'): self.chef_tree.heading(c, text=c); self.chef_tree.column(c, anchor="center")
        self.chef_tree.pack(fill="both", expand=True); self.chef_tree.bind("<<TreeviewSelect>>", self.load_chef_req_details)
        self.detail_f = tk.Frame(main_f, bg=CORE_UI["THEME"]["CARD"], width=500, padx=20); self.detail_f.pack(side="right", fill="both")
        self.chef_items_tree = ttk.Treeview(self.detail_f, columns=('Desc', 'Qty', 'Value'), show='headings', height=15)
        for c in ('Desc', 'Qty', 'Value'): self.chef_items_tree.heading(c, text=c); self.chef_items_tree.column(c, width=150)
        self.chef_items_tree.pack(fill="both", expand=True); self.chef_items_tree.bind("<Return>", self.chef_edit_qty)
        self.chef_total_lbl = tk.Label(self.detail_f, text="TOTAL: 0.00", bg=CORE_UI["THEME"]["CARD"], fg="white", font=("Arial", 12, "bold")); self.chef_total_lbl.pack(pady=10)
        tk.Button(self.detail_f, text="✅ APPROVE REQUISITION", bg=CORE_UI["THEME"]["ON"], fg="white", font=("Arial", 11, "bold"), height=2, command=self.chef_approve_action).pack(fill="x", pady=5)
        tk.Button(self.root, text="LOGOUT", bg="#444", fg="white", command=self.show_login_screen).pack(pady=10)
        self.load_transactions("PENDING", self.chef_tree)

    def load_chef_req_details(self, event):
        sel = self.chef_tree.selection()
        if not sel: return
        rid = self.chef_tree.item(sel[0], 'values')[0]
        for i in self.chef_items_tree.get_children(): self.chef_items_tree.delete(i)
        with open(TRANS_FILE, 'r') as f:
            for r in csv.DictReader(f):
                if r['ReqID'] == rid:
                    self.current_chef_items = ast.literal_eval(r['Items'])
                    for it in self.current_chef_items: self.chef_items_tree.insert('', 'end', values=(it['Desc'], it['Qty'], f"{it['Total']:,.2f}"))
                    self.chef_total_lbl.config(text=f"TOTAL: {self.safe_float(r['TotalValue']):,.2f}"); break

    def chef_edit_qty(self, event):
        sel = self.chef_items_tree.selection()
        if not sel: return
        idx = self.chef_items_tree.index(sel[0]); old = self.current_chef_items[idx]
        new_q = simpledialog.askfloat("Chef Edit", f"Adjust Qty for {old['Desc']}:", initialvalue=old['Qty'])
        if new_q is not None:
            self.current_chef_items[idx]['Qty'] = new_q; self.current_chef_items[idx]['Total'] = new_q * old['Cost']; self.refresh_chef_items_view()

    def refresh_chef_items_view(self):
        for i in self.chef_items_tree.get_children(): self.chef_items_tree.delete(i)
        new_tot = sum(it['Total'] for it in self.current_chef_items)
        for it in self.current_chef_items: self.chef_items_tree.insert('', 'end', values=(it['Desc'], it['Qty'], f"{it['Total']:,.2f}"))
        self.chef_total_lbl.config(text=f"TOTAL: {new_tot:,.2f}")

    def chef_approve_action(self):
        sel = self.chef_tree.selection()
        if not sel: return
        rid = self.chef_tree.item(sel[0], 'values')[0]; rows = []
        with open(TRANS_FILE, 'r') as f:
            reader = csv.DictReader(f); fn = reader.fieldnames
            for r in reader:
                if r['ReqID'] == rid: r['Status'] = 'CHEF APPROVED'; r['Items'] = str(self.current_chef_items); r['TotalValue'] = sum(i['Total'] for i in self.current_chef_items)
                rows.append(r)
        with open(TRANS_FILE, 'w', newline='') as f:
            dw = csv.DictWriter(f, fieldnames=fn); dw.writeheader(); dw.writerows(rows)
        messagebox.showinfo("Success", "Request Approved!"); self.build_chef_dashboard()

    def build_store_dashboard(self):
        self.clear_ui(); tk.Label(self.root, text="STOREKEEPER - ISSUING", bg=CORE_UI["THEME"]["HEADER"], fg="white", font=("Arial", 12, "bold")).pack(fill="x", ipady=15)
        t = ttk.Treeview(self.root, columns=('ID', 'Date', 'Outlet', 'Subject', 'Total'), show='headings')
        for c in ('ID', 'Date', 'Outlet', 'Subject', 'Total'): t.heading(c, text=c); t.column(c, anchor="center")
        t.pack(fill="both", expand=True, padx=20, pady=10); self.load_transactions_for_store(t)
        tk.Button(self.root, text="📦 ISSUE STOCK", bg=CORE_UI["THEME"]["ON"], fg="white", height=2, command=lambda: self.process_store_issue(t.item(t.selection()[0], 'values')[0]) if t.selection() else None).pack(pady=10)
        tk.Button(self.root, text="LOGOUT", bg="#444", fg="white", command=self.show_login_screen).pack(pady=5)

    def load_transactions_for_store(self, tree):
        for i in tree.get_children(): tree.delete(i)
        with open(TRANS_FILE, 'r') as f:
            for r in csv.DictReader(f):
                if r['Status'] == 'CHEF APPROVED': tree.insert('', 'end', values=(r['ReqID'], r['Date'], r['Outlet'], r['Subject'], r['TotalValue']))

    def process_store_issue(self, rid):
        req_items, rows = [], []
        with open(TRANS_FILE, 'r') as f:
            reader = csv.DictReader(f); fn = reader.fieldnames
            for r in reader:
                if r['ReqID'] == rid: r['Status'] = 'ISSUED'; req_items = ast.literal_eval(r['Items'])
                rows.append(r)
        with open(TRANS_FILE, 'w', newline='') as f:
            dw = csv.DictWriter(f, fieldnames=fn); dw.writeheader(); dw.writerows(rows)
        self.load_data()
        for item in req_items:
            for p in self.inventory:
                if p['Product code'] == item['Code']:
                    p['Stock On Hand'] = f"{self.safe_float(p['Stock On Hand']) - self.safe_float(item['Qty']):.2f}"
                    p['Total Value'] = f"{self.safe_float(p['Stock On Hand']) * self.safe_float(p['Unit cost']):.2f}"
        self.save_to_db(); messagebox.showinfo("Success", "Stock Issued!"); self.build_store_dashboard()

    def build_outlet_selection_ui(self):
        self.clear_ui(); tk.Label(self.root, text="CHOOSE KITCHEN", font=("Arial", 25, "bold"), bg=CORE_UI["THEME"]["BG"], fg="white").pack(pady=30)
        grid = tk.Frame(self.root, bg=CORE_UI["THEME"]["BG"]); grid.pack(expand=True)
        for i, name in enumerate(OUTLET_NAMES):
            tk.Button(grid, text=name.upper(), font=("Arial", 10, "bold"), bg=CORE_UI["THEME"]["CARD"], fg="white", width=35, height=3, command=lambda n=name: self.auth_overlay(n)).grid(row=i//2, column=i%2, padx=15, pady=15)

    def setup_order_meta(self, name):
        self.selected_outlet = name; self.req_id = f"M-REQ-{datetime.datetime.now().strftime('%y%m%d-%H%M')}"; self.clear_ui()
        c = tk.Frame(self.root, bg=CORE_UI["THEME"]["CARD"], padx=50, pady=50); c.pack(expand=True)
        tk.Label(c, text=f"📍 {self.selected_outlet}", font=("Arial", 18, "bold"), fg=CORE_UI["THEME"]["ON"], bg=CORE_UI["THEME"]["CARD"]).pack(pady=5)
        self.date_sel = DateEntry(c, width=45, background='black', date_pattern='yyyy-mm-dd'); self.date_sel.pack(pady=5)
        self.sub_ent = tk.Entry(c, font=("Arial", 12), width=48); self.sub_ent.insert(0, "Inventory Order"); self.sub_ent.pack(pady=5)
        tk.Button(c, text="OPEN INVENTORY", bg=CORE_UI["THEME"]["ON"], fg="white", width=35, height=2, command=self.build_outlet_grid).pack(pady=20)

    def build_outlet_grid(self):
        self.req_date, self.order_subject = self.date_sel.get(), self.sub_ent.get(); self.clear_ui(); self.load_data(); self.cart = []
        header = tk.Frame(self.root, bg=CORE_UI["THEME"]["HEADER"], pady=10); header.pack(fill="x")
        tk.Label(header, text=f"ORDER: {self.req_id} | {self.selected_outlet}", fg="white", bg=CORE_UI["THEME"]["HEADER"]).pack()
        sf = tk.Frame(self.root, bg=CORE_UI["THEME"]["BG"], pady=15); sf.pack(fill="x", padx=20)
        self.search_var = tk.StringVar(); self.search_var.trace_add("write", self.filter_inventory)
        tk.Entry(sf, textvariable=self.search_var, font=("Arial", 12), width=50).pack(side="left", padx=10)
        self.tree = ttk.Treeview(self.root, columns=('Code', 'Cat', 'Desc', 'Stock', 'Cost'), show='headings')
        for c in ('Code', 'Cat', 'Desc', 'Stock', 'Cost'): self.tree.heading(c, text=c); self.tree.column(c, width=150)
        self.tree.pack(fill="both", expand=True, padx=20); self.tree.bind("<Return>", self.on_item_add_popup)
        self.cart_tree = ttk.Treeview(self.root, columns=('Code', 'Desc', 'Qty', 'Cost', 'Total'), show='headings', height=5)
        for c in ('Code', 'Desc', 'Qty', 'Cost', 'Total'): self.cart_tree.heading(c, text=c); self.cart_tree.column(c, width=150)
        self.cart_tree.pack(fill="x", padx=20, pady=10)
        btm = tk.Frame(self.root, bg=CORE_UI["THEME"]["HEADER"]); btm.pack(fill="x", side="bottom")
        self.cart_lbl = tk.Label(btm, text="TOTAL: 0.00", bg=CORE_UI["THEME"]["HEADER"], fg=CORE_UI["THEME"]["ON"], font=("Arial", 18, "bold")); self.cart_lbl.pack(side="left", padx=20)
        tk.Button(btm, text="🚀 SUBMIT", bg=CORE_UI["THEME"]["ON"], fg="white", command=self.submit_to_chef).pack(side="right", padx=20, pady=10)
        self.update_tree_view(self.inventory)

    def on_item_add_popup(self, event):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0], 'values'); q = simpledialog.askfloat("Quantity", f"Qty for {vals[2]}:")
        if q: c = self.safe_float(vals[4]); self.cart.append({'Code': vals[0], 'Desc': vals[2], 'Qty': q, 'Cost': c, 'Total': q*c}); self.refresh_cart_display()

    def refresh_cart_display(self):
        for i in self.cart_tree.get_children(): self.cart_tree.delete(i)
        for i in self.cart: self.cart_tree.insert('', 'end', values=(i['Code'], i['Desc'], i['Qty'], i['Cost'], i['Total']))
        self.cart_lbl.config(text=f"TOTAL: {sum(i['Total'] for i in self.cart):,.2f}")

    def filter_inventory(self, *args):
        q = self.search_var.get().lower(); f = [i for i in self.inventory if q in i.get('Product code','').lower() or q in i.get('Product Description','').lower()]; self.update_tree_view(f)

    def update_tree_view(self, data):
        for i in self.tree.get_children(): self.tree.delete(i)
        for r in data: self.tree.insert('', 'end', values=(r.get('Product code'), r.get('Catogory'), r.get('Product Description'), r.get('Stock On Hand'), r.get('Unit cost')))

    def submit_to_chef(self):
        if not self.cart: return
        with open(TRANS_FILE, 'a', newline='') as f:
            dw = csv.DictWriter(f, fieldnames=['ReqID', 'Date', 'Outlet', 'Subject', 'TotalValue', 'Status', 'Items'])
            dw.writerow({'ReqID': self.req_id, 'Date': self.req_date, 'Outlet': self.selected_outlet, 'Subject': self.order_subject, 'TotalValue': sum(i['Total'] for i in self.cart), 'Status': 'PENDING', 'Items': str(self.cart)})
        messagebox.showinfo("Success", "Sent to Chef."); self.show_login_screen()

if __name__ == "__main__":
    root = tk.Tk(); app = MarriottUltimateSystem(root); root.mainloop()