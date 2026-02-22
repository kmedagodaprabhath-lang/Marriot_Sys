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

# Convenience alias used across the UI
THEME = CORE_UI["THEME"]

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
        self.root.title("Marriott v238 - Premium UI Restored")
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
        # TTK Button style (for ttk.Button widgets)
        try:
            style.configure('TButton', background=CORE_UI["THEME"]["CARD"], foreground="white", font=("Segoe UI", 10, "bold"), relief='flat')
            style.map('TButton', background=[('active', CORE_UI["THEME"]["HOVER"])], foreground=[('active', 'white')])
        except Exception:
            pass

        # Global defaults for classic tk.Button widgets to give a unified, professional look
        try:
            self.root.option_add('*Button.background', CORE_UI["THEME"]["CARD"])
            self.root.option_add('*Button.foreground', 'white')
            self.root.option_add('*Button.activeBackground', CORE_UI["THEME"]["HOVER"])
            self.root.option_add('*Button.activeForeground', 'white')
            self.root.option_add('*Button.font', ("Segoe UI", 10, "bold"))
            self.root.option_add('*Button.relief', 'flat')
            self.root.option_add('*Button.borderWidth', 0)
            self.root.option_add('*Button.padx', 8)
            self.root.option_add('*Button.pady', 6)
        except Exception:
            pass

    def safe_float(self, val):
        try: return float(str(val).replace(',', '').strip())
        except: return 0.0

    def clear_ui(self):
        for w in self.root.winfo_children(): w.destroy()

    def load_data(self):
        try:
            with open(DB_FILE, 'r', encoding='utf-8-sig') as f: self.inventory = list(csv.DictReader(f))
        except: self.inventory = []

    def save_to_db(self):
        with open(DB_FILE, 'w', newline='', encoding='utf-8') as f:
            dw = csv.DictWriter(f, fieldnames=self.all_cols); dw.writeheader(); dw.writerows(self.inventory)

    def show_login_screen(self):
        self.clear_ui()
        c = tk.Frame(self.root, bg=CORE_UI["THEME"]["BG"]); c.pack(expand=True)
        tk.Label(c, text="COURTYARD BY MARRIOTT", font=("Times New Roman", 45, "bold"), bg=CORE_UI["THEME"]["BG"], fg="white").pack(pady=40)
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
        pwd = self.pwd_ent.get()
        if PASSWORDS.get(rcode) == pwd:
            self.ov.destroy()
            if rcode == "COST": self.build_cost_controller_ui()
            elif rcode == "CHEF": self.build_chef_dashboard()
            elif rcode == "STORE": self.build_store_dashboard()
            else: self.setup_order_meta(rcode)
        else:
            messagebox.showerror("Error", "Invalid Password!")

    # ========================================================
    # [ADMIN PANEL]
    # ========================================================
    def build_cost_controller_ui(self):
        self.clear_ui(); self.load_data()
        header = tk.Frame(self.root, bg=CORE_UI["THEME"]["HEADER"]); header.pack(fill="x", ipady=5)
        tk.Label(header, text="COST CONTROLLER MASTER PANEL", bg=CORE_UI["THEME"]["HEADER"], fg="white", font=("Arial", 14, "bold")).pack(side="left", padx=20)
        tk.Button(header, text="LOGOUT", bg="#D32F2F", fg="white", command=self.show_login_screen).pack(side="right", padx=20)
        
        top_f = tk.Frame(self.root, bg=CORE_UI["THEME"]["BG"], pady=10); top_f.pack(fill="x", padx=20)
        self.admin_search_var = tk.StringVar(); self.admin_search_var.trace_add("write", self.filter_admin_inventory)
        tk.Label(top_f, text="🔍 Search:", bg=CORE_UI["THEME"]["BG"], fg="white").pack(side="left")
        tk.Entry(top_f, textvariable=self.admin_search_var, font=("Arial", 11), bg="#222", fg="white", width=40).pack(side="left", padx=10)
        
        ctrl_f = tk.Frame(self.root, bg=CORE_UI["THEME"]["BG"], pady=5); ctrl_f.pack(fill="x", padx=20)
        tk.Button(ctrl_f, text="+ NEW ITEM", bg="#2196F3", fg="white", font=("Arial", 9, "bold"), width=15, command=self.add_new_item_popup).pack(side="left", padx=5)
        tk.Button(ctrl_f, text="🗑️ DELETE", bg="#f44336", fg="white", font=("Arial", 9, "bold"), width=15, command=self.delete_inventory_item).pack(side="left", padx=5)
        tk.Button(ctrl_f, text="📥 UPDATE CSV", bg=CORE_UI["THEME"]["ON"], fg="white", font=("Arial", 9, "bold"), width=20, command=self.import_csv).pack(side="left", padx=5)
        tk.Button(ctrl_f, text="📤 EXPORT ALL", bg="#607D8B", fg="white", font=("Arial", 9, "bold"), width=15, command=lambda: self.export_to_csv(False)).pack(side="left", padx=5)
        tk.Button(ctrl_f, text="💜 BELOW PAR", bg=CORE_UI["THEME"]["LOW"], fg="white", font=("Arial", 9, "bold"), width=20, command=lambda: self.export_to_csv(True)).pack(side="left", padx=5)
        
        self.admin_tree = ttk.Treeview(self.root, columns=self.all_cols, show='headings')
        for c in self.all_cols: 
            self.admin_tree.heading(c, text=c.upper())
            align = "w" if c in ['Product code', 'Catogory', 'Product Description'] else "center"
            self.admin_tree.column(c, width=150 if 'Description' in c else 100, anchor=align)
        
        self.admin_tree.tag_configure('low_stock', background=CORE_UI["THEME"]["LOW"], foreground="white")
        self.admin_tree.pack(fill="both", expand=True, padx=20, pady=5)
        
        self.trans_tree = ttk.Treeview(self.root, columns=('ID', 'Date', 'Outlet', 'Status'), show='headings', height=6)
        for c in ('ID', 'Date', 'Outlet', 'Status'): self.trans_tree.heading(c, text=c); self.trans_tree.column(c, anchor="center")
        self.trans_tree.pack(fill="x", padx=20, pady=5)
        tk.Button(self.root, text="🖨️ PRINT SELECTED (A4)", bg="#FF9800", fg="black", font=("Arial", 10, "bold"), height=2, command=self.print_selected_trans).pack(pady=5)
        
        self.refresh_admin_table(); self.load_transactions("CHEF APPROVED", self.trans_tree)

    # --- RE-DESIGNED ADD NEW ITEM POPUP ---
    def add_new_item_popup(self):
        win = tk.Toplevel(self.root)
        win.title("ADD NEW INVENTORY ITEM")
        win.geometry("500x600")
        win.configure(bg=CORE_UI["THEME"]["BG"])
        win.grab_set() # Focus on this window
        
        tk.Label(win, text="ITEM MASTER ENTRY", font=("Arial", 14, "bold"), bg=CORE_UI["THEME"]["BG"], fg=CORE_UI["THEME"]["HOVER"]).pack(pady=20)
        
        fields = [
            ("Product Code:", "code"), ("Category:", "cat"), 
            ("Description:", "desc"), ("Unit Cost (LKR):", "cost"), 
            ("Min Par Level:", "min"), ("Max Par Level:", "max")
        ]
        
        ents = {}
        for label, key in fields:
            f = tk.Frame(win, bg=CORE_UI["THEME"]["BG"])
            f.pack(fill="x", padx=40, pady=5)
            tk.Label(f, text=label, bg=CORE_UI["THEME"]["BG"], fg="white", font=("Arial", 10)).pack(side="left")
            e = tk.Entry(f, font=("Arial", 11), bg="#222", fg="white", insertbackground="white", bd=1)
            e.pack(side="right", expand=True, fill="x", padx=(10, 0))
            ents[key] = e

        def save_item():
            if not ents['code'].get() or not ents['desc'].get():
                messagebox.showwarning("Warning", "Code and Description are mandatory!")
                return
            
            new_r = {c: "0" for c in self.all_cols}
            new_r.update({
                'Product code': ents['code'].get().strip(),
                'Catogory': ents['cat'].get().strip(),
                'Product Description': ents['desc'].get().strip(),
                'Unit cost': ents['cost'].get().strip() or "0",
                'Min Par': ents['min'].get().strip() or "0",
                'Max Par': ents['max'].get().strip() or "0",
                'Stock On Hand': "0",
                'Total Value': "0.00"
            })
            self.inventory.append(new_r)
            self.save_to_db()
            self.refresh_admin_table()
            win.destroy()
            messagebox.showinfo("Success", "New Item Added to Inventory!")

        btn_f = tk.Frame(win, bg=CORE_UI["THEME"]["BG"])
        btn_f.pack(pady=30)
        tk.Button(btn_f, text="SAVE ITEM", bg=CORE_UI["THEME"]["ON"], fg="white", font=("Arial", 10, "bold"), width=15, height=2, command=save_item).pack(side="left", padx=10)
        tk.Button(btn_f, text="CANCEL", bg="#444", fg="white", font=("Arial", 10, "bold"), width=10, height=2, command=win.destroy).pack(side="left")

    def show_transaction_print(self, req_data, on_close=None):
        try:
            items = ast.literal_eval(req_data.get('Items', '[]'))
        except Exception:
            items = []

        pv = tk.Toplevel(self.root)
        pv.title("Print Report Preview")
        pv.state('zoomed')
        pv.configure(bg="#333")
        # Ensure preview window appears above other windows and receives focus
        try:
            pv.transient(self.root)
            pv.attributes('-topmost', True)
            pv.lift()
            pv.grab_set()
            pv.focus_force()
        except Exception:
            pass

        # control bar with orientation and print actions
        ctrl_bar = tk.Frame(pv, bg="#222", pady=10); ctrl_bar.pack(fill="x")
        def scroll_top():
            try: canvas.yview_moveto(0)
            except: pass
        def scroll_bottom():
            try: canvas.yview_moveto(1)
            except: pass

        def do_print_action():
            rid = req_data.get('ReqID')
            if rid:
                try:
                    rows = [] ; fn = None
                    with open(TRANS_FILE, 'r', encoding='utf-8') as tf:
                        rdr = csv.DictReader(tf); fn = rdr.fieldnames
                        for r in rdr:
                            if r.get('ReqID') == rid:
                                r['Status'] = 'CHEF APPROVED'
                                r['Items'] = req_data.get('Items')
                                r['TotalValue'] = str(req_data.get('TotalValue', r.get('TotalValue', '0')))
                            rows.append(r)
                    with open(TRANS_FILE, 'w', newline='', encoding='utf-8') as tf:
                        dw = csv.DictWriter(tf, fieldnames=fn); dw.writeheader(); dw.writerows(rows)
                except Exception:
                    pass
            messagebox.showinfo("Print", "Sent to Printer (simulated)")
            try:
                pv.destroy()
            except:
                pass
            # call optional on_close callback (e.g., to return to Chef dashboard)
            try:
                if callable(on_close):
                    on_close()
            except Exception:
                pass

        orient_var = tk.StringVar(value='Portrait')
        tk.Label(ctrl_bar, text="Orientation:", bg="#222", fg="white").pack(side='left', padx=(8,4))
        tk.Radiobutton(ctrl_bar, text="Portrait", variable=orient_var, value='Portrait', bg="#222", fg="white", selectcolor="#222").pack(side='left')
        tk.Radiobutton(ctrl_bar, text="Landscape", variable=orient_var, value='Landscape', bg="#222", fg="white", selectcolor="#222").pack(side='left')
        tk.Button(ctrl_bar, text="⬆︎ TOP", bg="#555", fg="white", width=8, command=scroll_top).pack(side='left', padx=6)
        tk.Button(ctrl_bar, text="⬇︎ BOTTOM", bg="#555", fg="white", width=10, command=scroll_bottom).pack(side='left')
        tk.Button(ctrl_bar, text="🖨️ PRINT (A4)", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), width=20, command=do_print_action).pack(side='right', padx=8)

        container = tk.Frame(pv, bg="#333"); container.pack(fill="both", expand=True, padx=50, pady=20)
        canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scrollable_frame, anchor='nw', width=595)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def render_report(orientation='Portrait'):
            for w in scrollable_frame.winfo_children(): w.destroy()
            if orientation == 'Portrait':
                page_w, page_h = 595, 1200
            else:
                page_w, page_h = 842, 900

            cx = page_w // 2
            right = page_w - 30
            report_canvas = tk.Canvas(scrollable_frame, bg="white", width=page_w, height=page_h, highlightthickness=0)
            report_canvas.pack(pady=20)
            report_canvas.create_text(cx, 40, text="COURTYARD BY MARRIOTT COLOMBO", font=("Times New Roman", 18, "bold"))
            report_canvas.create_text(cx, 70, text="Inventory Requisition Report", font=("Arial", 11, "italic"))
            report_canvas.create_line(30, 90, right, 90, width=2)
            report_canvas.create_text(40, 120, text=f"REQ ID: {req_data.get('ReqID','')}", anchor="w", font=("Arial", 9, "bold"))
            report_canvas.create_text(40, 140, text=f"DATE  : {req_data.get('Date','')}", anchor="w", font=("Arial", 9))
            report_canvas.create_text(40, 160, text=f"OUTLET: {req_data.get('Outlet','')}", anchor="w", font=("Arial", 9))
            y = 190
            report_canvas.create_rectangle(30, y, right, y+28, fill="#EEEEEE", outline="black")
            headers = [("Code", 40), ("Product Description", 160), ("Cost", page_w-175), ("Qty", page_w-115), ("Total (LKR)", page_w-35)]
            for text, x in headers:
                anchor = 'e' if x > (page_w-200) else 'w'
                report_canvas.create_text(x, y+14, text=text, anchor=anchor, font=("Arial", 9, "bold"))
            y += 40
            for i in items:
                report_canvas.create_text(40, y, text=str(i.get('Code', 'N/A')), anchor="w", font=("Arial", 9))
                report_canvas.create_text(160, y, text=str(i.get('Desc', ''))[:60], anchor="w", font=("Arial", 9))
                try: report_canvas.create_text(page_w-175, y, text=f"{float(i.get('Cost',0)):,.2f}", anchor="e", font=("Arial", 9))
                except: report_canvas.create_text(page_w-175, y, text="0.00", anchor="e", font=("Arial", 9))
                try: report_canvas.create_text(page_w-115, y, text=f"{float(i.get('Qty',0)):.2f}", anchor="e", font=("Arial", 9))
                except: report_canvas.create_text(page_w-115, y, text="0", anchor="e", font=("Arial", 9))
                try: report_canvas.create_text(page_w-35, y, text=f"{float(i.get('Total',0)):,.2f}", anchor="e", font=("Arial", 9))
                except: report_canvas.create_text(page_w-35, y, text="0.00", anchor="e", font=("Arial", 9))
                y += 22
                if y > page_h - 100:
                    report_canvas.config(height=y+200)
            try:
                report_canvas.create_text(page_w-35, y+30, text=f"GRAND TOTAL: LKR {float(req_data.get('TotalValue',0)):,.2f}", anchor="e", font=("Arial", 11, "bold"))
            except:
                report_canvas.create_text(page_w-35, y+30, text=f"GRAND TOTAL: LKR 0.00", anchor="e", font=("Arial", 11, "bold"))
            sig_y = y + 120
            report_canvas.config(height=sig_y+80)
            report_canvas.create_line(40, sig_y, 220, sig_y); report_canvas.create_text(130, sig_y+12, text="Requested By (Outlet Chef)")
            status = str(req_data.get('Status','')).upper() if req_data.get('Status') is not None else ''
            if not status and req_data.get('ReqID'):
                try:
                    with open(TRANS_FILE, 'r', encoding='utf-8') as tf:
                        for r in csv.DictReader(tf):
                            if r.get('ReqID') == req_data.get('ReqID'):
                                status = str(r.get('Status','')).upper(); break
                except Exception:
                    status = ''
            approver_label = "Approved By (Cost Controller)"
            if status == 'CHEF APPROVED': approver_label = "Approved By (Executive Chef)"
            report_canvas.create_line(page_w-260, sig_y, page_w-40, sig_y); report_canvas.create_text(page_w-170, sig_y+12, text=approver_label)

        # initial render (catch errors and ensure window stays on top briefly)
        try:
            render_report(orient_var.get())
            orient_var.trace_add('write', lambda *a: render_report(orient_var.get()))
        except Exception as e:
            try:
                messagebox.showerror('Render Error', f'Failed to render print preview: {e}')
            except:
                pass
        try:
            pv.attributes('-topmost', False)
        except Exception:
            pass

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
                messagebox.showinfo("Success", "Import Complete!")
            except Exception as e: messagebox.showerror("Error", str(e))

    def export_to_csv(self, below_par_only):
        data = self.inventory
        if below_par_only: data = [r for r in self.inventory if self.safe_float(r.get('Stock On Hand', 0)) < self.safe_float(r.get('Min Par', 0))]
        if not data: messagebox.showinfo("Info", "No data."); return
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if path:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                dw = csv.DictWriter(f, fieldnames=self.all_cols); dw.writeheader(); dw.writerows(data)

    def filter_admin_inventory(self, *args):
        q = self.admin_search_var.get().lower(); self.refresh_admin_table(q)

    def refresh_admin_table(self, query=""):
        for i in self.admin_tree.get_children(): self.admin_tree.delete(i)
        for r in self.inventory:
            if query in r.get('Product code','').lower() or query in r.get('Product Description','').lower():
                stock, min_p = self.safe_float(r.get('Stock On Hand', 0)), self.safe_float(r.get('Min Par', 0))
                tag = 'low_stock' if stock < min_p else ''
                self.admin_tree.insert('', 'end', values=[r.get(c, "0") for c in self.all_cols], tags=(tag,))

    def build_outlet_selection_ui(self):
        self.clear_ui()
        tk.Label(self.root, text="CHOOSE YOUR KITCHEN", font=("Arial", 28, "bold"), bg=CORE_UI["THEME"]["BG"], fg="white").pack(pady=40)
        grid = tk.Frame(self.root, bg=CORE_UI["THEME"]["BG"]); grid.pack(expand=True)
        for i, name in enumerate(OUTLET_NAMES):
            row, col = i // 2, i % 2
            def make_btn(n=name, r=row, c=col):
                btn = tk.Button(grid, text=n.upper(), font=("Arial", 11, "bold"), bg=CORE_UI["THEME"]["CARD"], fg="white", width=35, height=3, bd=0, relief="flat", activebackground=CORE_UI["THEME"]["HOVER"], command=lambda n=n: self.auth_overlay(n))
                btn.grid(row=r, column=c, padx=15, pady=15)
                def on_enter(e, b=btn):
                    try:
                        b.config(bg=CORE_UI["THEME"]["HOVER"], fg="white", bd=2, relief="raised")
                    except: pass
                def on_leave(e, b=btn):
                    try:
                        b.config(bg=CORE_UI["THEME"]["CARD"], fg="white", bd=0, relief="flat")
                    except: pass
                btn.bind("<Enter>", on_enter)
                btn.bind("<Leave>", on_leave)
            make_btn()

    def setup_order_meta(self, name):
        self.selected_outlet = name
        self.req_id = f"M-REQ-{datetime.datetime.now().strftime('%y%m%d-%H%M%S')}"
        self.clear_ui()
        c = tk.Frame(self.root, bg=CORE_UI["THEME"]["CARD"], padx=60, pady=40); c.pack(expand=True)
        tk.Label(c, text=f"OUTLET: {self.selected_outlet}", font=("Arial", 14, "bold"), bg=CORE_UI["THEME"]["CARD"], fg="white").pack(pady=(0,8))
        tk.Label(c, text=f"REQUEST ID: {self.req_id}", font=("Arial", 12), bg=CORE_UI["THEME"]["CARD"], fg=CORE_UI["THEME"]["ON"]).pack(pady=(0,12))
        self.date_sel = DateEntry(c, width=45, background='black', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd', mindate=datetime.date.today(), state='readonly')
        self.date_sel.pack(pady=10)
        fsub = tk.Frame(c, bg=CORE_UI["THEME"]["CARD"]); fsub.pack(pady=10)
        tk.Label(fsub, text="Subject:", bg=CORE_UI["THEME"]["CARD"], fg="white").pack(side='left')
        self.sub_ent = tk.Entry(fsub, font=("Arial", 12), width=48, bg="#000", fg="white")
        self.sub_ent.insert(0, "Daily Order")
        self.sub_ent.pack(side='left', padx=(10,0))
        tk.Button(c, text="OPEN INVENTORY", bg=CORE_UI["THEME"]["ON"], fg="white", font=("Arial", 11, "bold"), width=35, height=2, command=self.validate_order_meta).pack(pady=30)

    def validate_order_meta(self):
        subj = self.sub_ent.get().strip() if hasattr(self, 'sub_ent') else ''
        try:
            sel_date = self.date_sel.get_date()
        except Exception:
            try:
                sel_date = datetime.datetime.strptime(self.date_sel.get(), "%Y-%m-%d").date()
            except Exception:
                sel_date = None
        if not subj:
            messagebox.showwarning("Warning", "Please enter a subject before continuing.")
            return
        if sel_date is None:
            messagebox.showwarning("Warning", "Please select a valid date.")
            return
        if sel_date < datetime.date.today():
            messagebox.showwarning("Warning", "Back-dating is not allowed. Please choose today or a future date.")
            return
        self.req_date = sel_date.strftime('%Y-%m-%d')
        self.order_subject = subj
        self.build_outlet_grid()

    def build_outlet_grid(self):
        self.req_date, self.order_subject = self.date_sel.get(), self.sub_ent.get()
        self.clear_ui(); self.load_data(); self.cart = []
        header = tk.Frame(self.root, bg=CORE_UI["THEME"]["HEADER"], pady=10); header.pack(fill="x")
        tk.Label(header, text=f"REQ: {self.req_id} | OUTLET: {self.selected_outlet}", fg="white", bg=CORE_UI["THEME"]["HEADER"]).pack()
        sf = tk.Frame(self.root, bg=CORE_UI["THEME"]["BG"], pady=15); sf.pack(fill="x", padx=20)
        self.search_var = tk.StringVar(); self.search_var.trace_add("write", self.filter_inventory)
        tk.Entry(sf, textvariable=self.search_var, font=("Arial", 12), width=50).pack(side="left", padx=10)
        self.tree = ttk.Treeview(self.root, columns=('Code', 'Cat', 'Desc', 'Stock', 'Cost'), show='headings')
        for c in ('Code', 'Cat', 'Desc', 'Stock', 'Cost'): self.tree.heading(c, text=c); self.tree.column(c, width=150)
        self.tree.pack(fill="both", expand=True, padx=20); self.tree.bind("<Return>", self.on_item_add_popup)
        self.cart_tree = ttk.Treeview(self.root, columns=('Code', 'Desc', 'Qty', 'Cost', 'Total'), show='headings', height=6)
        for c in ('Code', 'Desc', 'Qty', 'Cost', 'Total'): self.cart_tree.heading(c, text=c); self.cart_tree.column(c, width=150)
        self.cart_tree.pack(fill="x", padx=20, pady=5); self.cart_tree.bind("<Return>", self.cart_edit_qty)
        btm = tk.Frame(self.root, bg=CORE_UI["THEME"]["HEADER"], pady=10); btm.pack(fill="x", side="bottom")
        self.cart_lbl = tk.Label(btm, text="TOTAL: 0.00", bg=CORE_UI["THEME"]["HEADER"], fg=CORE_UI["THEME"]["ON"], font=("Arial", 18, "bold")); self.cart_lbl.pack(side="left", padx=20)
        tk.Button(btm, text="🚀 SUBMIT", bg=CORE_UI["THEME"]["ON"], fg="white", font=("Arial", 11, "bold"), width=15, height=2, command=self.submit_to_chef).pack(side="right", padx=10)
        tk.Button(btm, text="🔍 PREVIEW", bg="#2196F3", fg="white", font=("Arial", 11, "bold"), width=15, height=2, command=self.show_outlet_order_preview).pack(side="right", padx=10)
        self.update_tree_view(self.inventory)

    def on_item_add_popup(self, event):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0], 'values'); q = simpledialog.askfloat("Quantity", f"Qty for {vals[2]}:")
        if q: c = self.safe_float(vals[4]); self.cart.append({'Code': vals[0], 'Desc': vals[2], 'Qty': q, 'Cost': c, 'Total': q*c}); self.refresh_cart_display()

    def cart_edit_qty(self, event):
        sel = self.cart_tree.selection()
        if not sel: return
        idx = self.cart_tree.index(sel[0]); old = self.cart[idx]
        new_q = simpledialog.askfloat("Edit", f"New Qty for {old['Desc']}:", initialvalue=old['Qty'])
        if new_q is not None:
            if new_q <= 0: del self.cart[idx]
            else: self.cart[idx]['Qty'] = new_q; self.cart[idx]['Total'] = new_q * old['Cost']
            self.refresh_cart_display()

    def refresh_cart_display(self):
        for i in self.cart_tree.get_children(): self.cart_tree.delete(i)
        for i in self.cart: self.cart_tree.insert('', 'end', values=(i['Code'], i['Desc'], f"{i['Qty']:.2f}", f"{i['Cost']:,.2f}", f"{i['Total']:,.2f}"))
        self.cart_lbl.config(text=f"TOTAL: {sum(i['Total'] for i in self.cart):,.2f}")

    def show_outlet_order_preview(self):
        if not self.cart: return
        d = {'ReqID': self.req_id, 'Date': self.req_date, 'Outlet': self.selected_outlet, 'TotalValue': sum(i['Total'] for i in self.cart), 'Items': str(self.cart)}
        self.show_transaction_print(d)

    def delete_inventory_item(self):
        sel = self.admin_tree.selection()
        if sel: idx = self.admin_tree.index(sel[0]); del self.inventory[idx]; self.save_to_db(); self.refresh_admin_table()

    def filter_inventory(self, *args):
        q = self.search_var.get().lower(); f = [i for i in self.inventory if q in i.get('Product code','').lower() or q in i.get('Product Description','').lower()]; self.update_tree_view(f)

    def update_tree_view(self, data):
        for i in self.tree.get_children(): self.tree.delete(i)
        for r in data: self.tree.insert('', 'end', values=(r.get('Product code'), r.get('Catogory'), r.get('Product Description'), r.get('Stock On Hand'), r.get('Unit cost')))

    def submit_to_chef(self):
        if not self.cart: return
        with open(TRANS_FILE, 'a', newline='', encoding='utf-8') as f:
            dw = csv.DictWriter(f, fieldnames=['ReqID', 'Date', 'Outlet', 'Subject', 'TotalValue', 'Status', 'Items'])
            dw.writerow({'ReqID': self.req_id, 'Date': self.req_date, 'Outlet': self.selected_outlet, 'Subject': self.order_subject, 'TotalValue': sum(i['Total'] for i in self.cart), 'Status': 'PENDING', 'Items': str(self.cart)})

        # Styled confirmation modal
        win = tk.Toplevel(self.root)
        win.title("Request Sent")
        win.transient(self.root)
        win.grab_set()
        win.configure(bg=CORE_UI["THEME"]["BG"], padx=20, pady=20)
        win.geometry("480x220")
        tk.Label(win, text="✅ Request Sent to Chef", font=("Arial", 16, "bold"), bg=CORE_UI["THEME"]["BG"], fg="white").pack(pady=(10,6))
        tk.Label(win, text=f"ReqID: {self.req_id}", font=("Arial", 11), bg=CORE_UI["THEME"]["BG"], fg=CORE_UI["THEME"]["ON"]).pack(pady=4)
        tk.Label(win, text=f"Outlet: {self.selected_outlet}", font=("Arial", 11), bg=CORE_UI["THEME"]["BG"], fg="white").pack(pady=2)
        tk.Label(win, text=f"Total: LKR {sum(i['Total'] for i in self.cart):,.2f}", font=("Arial", 11, "bold"), bg=CORE_UI["THEME"]["BG"], fg="white").pack(pady=6)

        def ok_and_close():
            win.destroy(); self.show_login_screen()

        tk.Button(win, text="OK", bg=CORE_UI["THEME"]["ON"], fg="white", font=("Arial", 11, "bold"), width=12, command=ok_and_close).pack(pady=12)

    def load_transactions(self, status, tree):
        for i in tree.get_children(): tree.delete(i)
        try:
            with open(TRANS_FILE, 'r', encoding='utf-8') as f:
                for r in csv.DictReader(f):
                    if r.get('Status') == status:
                        cols = tree['columns']
                        vals = []
                        for c in cols:
                            if c == 'ID': vals.append(r.get('ReqID'))
                            elif c == 'Total': vals.append(r.get('TotalValue'))
                            else: vals.append(r.get(c) if c in r else r.get(c) if c in r else r.get(c))
                        tree.insert('', 'end', values=tuple(vals))
        except Exception:
            pass

    def print_selected_trans(self):
        sel = self.trans_tree.selection(); rid = self.trans_tree.item(sel[0], 'values')[0] if sel else None
        if rid:
            with open(TRANS_FILE, 'r') as f:
                for r in csv.DictReader(f):
                    if r['ReqID'] == rid: self.show_transaction_print(r); break

    def build_chef_dashboard(self):
        self.clear_ui()
        header = tk.Frame(self.root, bg="#222")
        header.pack(fill="x")
        tk.Label(header, text="CHEF APPROVAL", bg="#222", fg="white", font=("Arial", 18)).pack(side='left', padx=10, pady=8)
        btn_f = tk.Frame(header, bg="#222"); btn_f.pack(side='right', padx=10)

        cols = ('ReqID', 'Date', 'Outlet', 'Subject', 'Total')
        t = ttk.Treeview(self.root, columns=cols, show='headings')
        for c in cols:
            t.heading(c, text=c); t.column(c, anchor='center')
        t.pack(fill='both', expand=True, padx=12, pady=12)
        self.load_transactions('PENDING', t)

        tk.Button(btn_f, text="VIEW & EDIT", bg="#1976D2", fg="white", font=("Arial", 11, "bold"), width=14, command=lambda: self.chef_review(t)).pack(side='left', padx=6)
        tk.Button(btn_f, text="APPROVE SELECTED", bg=CORE_UI["THEME"]["ON"], fg="white", font=("Arial", 11, "bold"), width=16, command=lambda: self.chef_approve_logic(t)).pack(side='left', padx=6)
        tk.Button(btn_f, text="LOGOUT", bg="#D32F2F", fg="white", font=("Arial", 11, "bold"), width=10, command=self.show_login_screen).pack(side='left', padx=6)
        t.bind('<Double-1>', lambda e: self.chef_review(t))

    def chef_approve_logic(self, t):
        sel = t.selection(); rid = t.item(sel[0], 'values')[0] if sel else None
        if rid:
            rows = []
            with open(TRANS_FILE, 'r') as f:
                rdr = csv.DictReader(f); fn = rdr.fieldnames
                for r in rdr:
                    if r['ReqID'] == rid: r['Status'] = 'CHEF APPROVED'
                    rows.append(r)
            with open(TRANS_FILE, 'w', newline='') as f:
                dw = csv.DictWriter(f, fieldnames=fn); dw.writeheader(); dw.writerows(rows)
            self.build_chef_dashboard()

    def chef_review(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a request to open.")
            return
        rid = tree.item(sel[0], 'values')[0]
        with open(TRANS_FILE, 'r', encoding='utf-8') as f:
            all_t = list(csv.DictReader(f))
        req = next((r for r in all_t if r['ReqID'] == rid), None)
        if not req:
            messagebox.showerror("Error", "Request not found")
            return

        try:
            items = ast.literal_eval(req.get('Items', '[]'))
        except Exception:
            items = []

        rev = tk.Toplevel(self.root); rev.state('zoomed'); rev.configure(bg="#DDD")
        paper = tk.Frame(rev, bg="white", padx=30, pady=30); paper.pack(pady=20, fill="both", expand=True)
        tk.Label(paper, text="STOCK REQUISITION", font=("Arial", 20, "bold"), bg="white").pack()
        tk.Label(paper, text=f"REQ: {rid} | {req.get('Outlet','')} | {req.get('Date','')}\nSubject: {req.get('Subject','')}", bg="white", justify="left").pack(pady=10)

        t = ttk.Treeview(paper, columns=('Code', 'Desc', 'Qty', 'Cost', 'Total'), show='headings', selectmode='browse')
        for col, width in (('Code',100), ('Desc',450), ('Qty',100), ('Cost',120), ('Total',120)):
            anchor = 'w' if col in ('Code', 'Desc') else 'e' if col in ('Cost','Total') else 'center'
            t.heading(col, text=col); t.column(col, width=width, anchor=anchor)
        t.pack(fill="both", expand=True, padx=10, pady=10)

        total_lbl = tk.Label(paper, text="TOTAL: LKR 0.00", font=("Arial", 14, "bold"), bg='white')
        total_lbl.pack(pady=6)

        def refresh_items():
            for i in t.get_children(): t.delete(i)
            for it in items:
                t.insert('', 'end', values=(it.get('Code',''), it.get('Desc',''), f"{float(it.get('Qty',0)):.2f}", f"{float(it.get('Cost',0)):,.2f}", f"{float(it.get('Total',0)):,.2f}"))
            total = sum(float(it.get('Total',0) or 0) for it in items)
            try:
                total_lbl.config(text=f"TOTAL: LKR {total:,.2f}")
            except Exception:
                pass

        refresh_items()

        def open_cell_editor(item_id, col_name):
            # Only allow Qty edits from chef review. Other columns are read-only.
            if not item_id: return
            if col_name != 'Qty':
                return
            idx = t.index(item_id)
            old = items[idx]
            try:
                curv = float(old.get('Qty', 0) or 0)
            except:
                curv = 0.0
            new_q = simpledialog.askfloat("Edit Qty", f"New Qty for {old.get('Desc','')}:", initialvalue=curv, parent=rev)
            if new_q is None:
                return
            if new_q <= 0:
                del items[idx]
            else:
                old['Qty'] = new_q
                try: cost = float(old.get('Cost', 0) or 0)
                except: cost = 0
                old['Total'] = new_q * cost
            refresh_items(); autosave_items()
            # move to next row automatically if exists
            children = t.get_children()
            next_idx = idx + 1
            if next_idx < len(children):
                next_item = children[next_idx]
                rev.after(50, lambda: open_cell_editor(next_item, 'Qty'))
            return

        # Only allow keyboard-triggered editing (Return / F2). Disable mouse double-click edits.
        try: t.unbind('<Double-1>')
        except: pass
        def edit_cell_inline(event=None):
            # Keyboard-only: edit Qty for the selected row
            try:
                sel = t.selection()
                if not sel:
                    return
                item_id = sel[0]
                open_cell_editor(item_id, 'Qty')
            except Exception:
                return

        t.bind('<Return>', edit_cell_inline)
        t.bind('<F2>', edit_cell_inline)

        def autosave_items():
            for r in all_t:
                if r.get('ReqID') == rid:
                    r['Items'] = str(items)
                    try: r['TotalValue'] = str(sum(float(it.get('Total',0) or 0) for it in items))
                    except: r['TotalValue'] = '0'
                    break
            try:
                with open(TRANS_FILE, 'w', newline='', encoding='utf-8') as f:
                    dw = csv.DictWriter(f, fieldnames=all_t[0].keys()); dw.writeheader(); dw.writerows(all_t)
            except Exception:
                pass

        def approve_and_print():
            for r in all_t:
                if r.get('ReqID') == rid:
                    r['Status'] = 'CHEF APPROVED'
                    r['Items'] = str(items)
                    try: r['TotalValue'] = str(sum(float(it.get('Total',0) or 0) for it in items))
                    except: r['TotalValue'] = '0'
                    break
            with open(TRANS_FILE, 'w', newline='', encoding='utf-8') as f:
                dw = csv.DictWriter(f, fieldnames=all_t[0].keys()); dw.writeheader(); dw.writerows(all_t)
            def _close_review_and_refresh():
                try:
                    rev.destroy()
                except:
                    pass
                try:
                    self.build_chef_dashboard()
                except:
                    pass

            try:
                self.show_transaction_print({'ReqID': rid, 'Date': r.get('Date',''), 'Outlet': r.get('Outlet',''), 'TotalValue': r.get('TotalValue','0'), 'Items': str(items), 'Status': 'CHEF APPROVED'}, on_close=_close_review_and_refresh)
            except Exception as e:
                messagebox.showerror('Print Error', f'Unable to open print preview: {e}')

        btn_frame = tk.Frame(paper, bg='white')
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text='Save Changes', bg='#1976D2', fg='white', command=lambda: (autosave_items(), messagebox.showinfo('Saved','Changes saved'))).pack(side='left', padx=6)
        tk.Button(btn_frame, text='Approve & Print', bg=CORE_UI['THEME']['ON'], fg='white', command=approve_and_print).pack(side='left', padx=6)

    def build_store_dashboard(self):
        self.clear_ui()
        header = tk.Frame(self.root, bg="#222"); header.pack(fill="x")
        tk.Label(header, text="STORE ISSUING", bg="#222", fg="white", font=("Arial", 18)).pack(side='left', padx=10, ipady=10)
        btn_f = tk.Frame(header, bg="#222"); btn_f.pack(side='right', padx=10, pady=8)
        t = ttk.Treeview(self.root, columns=('ID', 'Outlet', 'Total'), show='headings'); t.pack(fill="both", expand=True, padx=20, pady=10)
        for c in ('ID', 'Outlet', 'Total'): t.heading(c, text=c); t.column(c, anchor="center")
        try:
            with open(TRANS_FILE, 'r', encoding='utf-8') as f:
                for r in csv.DictReader(f):
                    if r.get('Status') == 'CHEF APPROVED': t.insert('', 'end', values=(r['ReqID'], r['Outlet'], r['TotalValue']))
        except Exception:
            pass

        def view_items(event=None):
            sel = t.selection()
            if not sel:
                messagebox.showwarning("Select", "Please select a request to view.")
                return
            rid = t.item(sel[0], 'values')[0]
            try:
                req = None
                with open(TRANS_FILE, 'r', encoding='utf-8') as f:
                    for r in csv.DictReader(f):
                        if r.get('ReqID') == rid:
                            req = r
                            break
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return
            if not req:
                messagebox.showerror("Error", "Request not found.")
                return
            try:
                items = ast.literal_eval(req.get('Items', '[]'))
            except Exception:
                items = []

            win = tk.Toplevel(self.root)
            win.title(f"Item Breakdown — {rid}")
            win.geometry("750x500")
            win.configure(bg=CORE_UI["THEME"]["BG"])
            win.transient(self.root); win.grab_set()

            tk.Label(win, text=f"ITEM BREAKDOWN", font=("Arial", 14, "bold"),
                     bg=CORE_UI["THEME"]["BG"], fg=CORE_UI["THEME"]["HOVER"]).pack(pady=(16, 4))
            tk.Label(win, text=f"Req ID: {rid}  |  Outlet: {req.get('Outlet','')}  |  Date: {req.get('Date','')}",
                     font=("Arial", 10), bg=CORE_UI["THEME"]["BG"], fg="white").pack(pady=(0, 10))

            cols = ('Code', 'Description', 'Qty', 'Unit Cost', 'Total')
            tree = ttk.Treeview(win, columns=cols, show='headings')
            for col, w, anc in (('Code', 100, 'w'), ('Description', 280, 'w'),
                                 ('Qty', 80, 'center'), ('Unit Cost', 110, 'e'), ('Total', 110, 'e')):
                tree.heading(col, text=col); tree.column(col, width=w, anchor=anc)
            tree.pack(fill='both', expand=True, padx=16, pady=6)

            grand = 0.0
            for item in items:
                try: cost = float(item.get('Cost', 0) or 0)
                except (ValueError, TypeError): cost = 0.0
                try: qty = float(item.get('Qty', 0) or 0)
                except (ValueError, TypeError): qty = 0.0
                try: total = float(item.get('Total', 0) or 0)
                except (ValueError, TypeError): total = cost * qty
                grand += total
                tree.insert('', 'end', values=(
                    item.get('Code', ''), item.get('Desc', ''),
                    f"{qty:.2f}", f"{cost:,.2f}", f"{total:,.2f}"))

            tk.Label(win, text=f"GRAND TOTAL:  LKR {grand:,.2f}", font=("Arial", 12, "bold"),
                     bg=CORE_UI["THEME"]["BG"], fg=CORE_UI["THEME"]["ON"]).pack(pady=8)
            tk.Button(win, text="CLOSE", bg="#444", fg="white", font=("Arial", 10, "bold"),
                      width=12, command=win.destroy).pack(pady=(0, 12))

        t.bind('<Double-1>', view_items)

        def issue_selected():
            sel = t.selection()
            if not sel:
                messagebox.showwarning("Select", "Please select a request to issue.")
                return
            rid = t.item(sel[0], 'values')[0]
            if not messagebox.askyesno("Confirm Issue", f"Issue stock for request {rid} and update inventory?"):
                return
            try:
                all_t = []
                req = None
                with open(TRANS_FILE, 'r', encoding='utf-8') as f:
                    rdr = csv.DictReader(f); fn = rdr.fieldnames; all_t = list(rdr)
                for r in all_t:
                    if r.get('ReqID') == rid:
                        r['Status'] = 'ISSUED'; req = r; break
                if req:
                    self.load_data()
                    try:
                        items = ast.literal_eval(req.get('Items', '[]'))
                    except Exception:
                        items = []
                    for item in items:
                        for inv_row in self.inventory:
                            if inv_row.get('Product code') == item.get('Code'):
                                issued_stock = max(self.safe_float(inv_row.get('Stock On Hand', 0)) - self.safe_float(item.get('Qty', 0)), 0)
                                inv_row['Stock On Hand'] = f"{issued_stock:.4f}"
                                inv_row['Total Value'] = f"{issued_stock * self.safe_float(inv_row.get('Unit cost', 0)):.2f}"
                                break
                    self.save_to_db()
                with open(TRANS_FILE, 'w', newline='', encoding='utf-8') as f:
                    dw = csv.DictWriter(f, fieldnames=fn); dw.writeheader(); dw.writerows(all_t)
                messagebox.showinfo("Issued", f"Request {rid} marked as ISSUED and stock updated.")
                self.build_store_dashboard()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(btn_f, text="🔍 VIEW ITEMS", bg="#1976D2", fg="white", font=("Arial", 11, "bold"), width=14, command=view_items).pack(side='left', padx=6)
        tk.Button(btn_f, text="✅ ISSUE SELECTED", bg=CORE_UI["THEME"]["ON"], fg="white", font=("Arial", 11, "bold"), width=18, command=issue_selected).pack(side='left', padx=6)
        tk.Button(btn_f, text="LOGOUT", bg="#D32F2F", fg="white", font=("Arial", 11, "bold"), width=10, command=self.show_login_screen).pack(side='left', padx=6)

if __name__ == "__main__":
    root = tk.Tk(); app = MarriottUltimateSystem(root); root.mainloop()