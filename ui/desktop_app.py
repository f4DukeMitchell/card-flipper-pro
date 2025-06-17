import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import ttk, messagebox
from services.main_logic import scan_items

def run_ui():
    root = tk.Tk()
    root.title("CardFlipper Pro – Sniper Dashboard")
    root.geometry("1400x600")

    # Table
    columns = [
        "Timestamp", "Title", "Price", "Currency", "Margin (%)", "Profit ($)",
        "Max Bid", "Confidence", "Time Left (min)", "Seller Feedback (%)",
        "Condition", "Type", "Bid Status", "eBay Link"
    ]

    tree = ttk.Treeview(root, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=100)

    tree.pack(fill="both", expand=True)

    def refresh_data():
        tree.delete(*tree.get_children())
        try:
            items = scan_items()
            for row in items:
                tree.insert("", "end", values=row[:14])  # Display first 14 fields
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Button
    refresh_btn = tk.Button(root, text="🔄 Refresh Listings", command=refresh_data)
    refresh_btn.pack(pady=5)

    # First load
    refresh_data()
    root.mainloop()

if __name__ == "__main__":
    run_ui()
