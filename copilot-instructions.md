# Copilot Instructions for Marriott _Sys

## Overview
This is a Tkinter-based GUI application for Marriott hotel inventory and order management. It features role-based access (Cost Controller, Chef, Storekeeper, Outlets) with CSV-based data persistence. No external databases or APIs; all data flows through local CSV files like `transactions.csv`.

## Architecture
- **Core Class**: `MarriottUltimateSystem` in `Main.py`/`Storekeeper.py` handles all UI logic, authentication, and dashboards.
- **Data Flow**: User inputs → CSV updates → UI refreshes. No real-time sync; changes require manual reload.
- **Components**: Login overlay (`auth_overlay`), role-specific dashboards (`build_*_dashboard`), treeviews for data display, and CSV readers/writers.
- **Why**: Simple file-based system for offline hotel operations; Tkinter chosen for easy GUI without web dependencies.

## Key Patterns
- **Authentication**: Use `PASSWORDS` dict (e.g., `"STORE": "303"`). Call `auth_overlay(rcode)` for login prompts, set `self.role` on success.
- **UI Building**: Start with `clear_ui()` to reset screen, then pack frames/buttons. Example: `build_store_dashboard()` uses frames for header, filters, treeview.
- **Data Handling**: Read/write CSVs with `csv.DictReader/Writer`. Filter data in memory (e.g., `refresh_tree(filter_date)`).
- **Event Binding**: Double-click treeview rows to open details (e.g., `tree.bind('<Double-1>', on_double)`).
- **Styling**: Use `THEME` dict for consistent colors (BG: "#121212", ON: "#4CAF50").

## Workflows
- **Run App**: `python Main.py` or `python Storekeeper.py` (standalone storekeeper view).
- **Debug**: Add `print()` in methods like `verify_login` or `refresh_tree`. No linters/tests; check console for CSV errors.
- **Add Features**: Modify `build_*_dashboard` methods; test by selecting role and navigating UI.
- **Data Updates**: Edit `transactions.csv` manually for testing; app overwrites on status changes.

## Conventions
- **File Structure**: `Main.py` for full app, `Storekeeper.py` for storekeeper-focused version. `import tkcalendar.py` patches tkcalendar import.
- **Naming**: Methods like `build_store_dashboard`, variables like `tree` for treeviews, `rid` for request IDs.
- **Error Handling**: Use `try/except` for file ops; show `messagebox` for user feedback.
- **Dependencies**: `tkinter`, `tkcalendar`, `csv`, `os`, `datetime`, `json`. Install via pip if needed.

Reference: `README.md` for setup, `Storekeeper.py` for dashboard examples.