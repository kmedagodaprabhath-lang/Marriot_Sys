import csv, os

BASE_DIR = os.path.expanduser('~')
DB_FILE = os.path.join(BASE_DIR, 'marriott_inventory.csv')

class InventoryDB:
    def __init__(self, path=DB_FILE):
        self.path = path
        self.cols = ['Product code','Catogory','Product Description','Stock On Hand','Unit cost','Total Value','Min Par','Max Par']
        if not os.path.exists(self.path):
            with open(self.path, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(self.cols)

    def all(self):
        try:
            with open(self.path, 'r', encoding='utf-8-sig') as f:
                return list(csv.DictReader(f))
        except Exception:
            return []

    def save(self, rows):
        with open(self.path, 'w', newline='', encoding='utf-8') as f:
            dw = csv.DictWriter(f, fieldnames=self.cols); dw.writeheader(); dw.writerows(rows)

    def add(self, record):
        rows = self.all(); rows.append(record); self.save(rows)

    def find_by_code(self, code):
        for r in self.all():
            if r.get('Product code') == code:
                return r
        return None
