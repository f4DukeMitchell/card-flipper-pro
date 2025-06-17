import csv
from datetime import datetime

def update_resale_log(csv_path="bid_log.csv", updated_path="resale_log.csv"):
    rows = []

    with open(csv_path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row["Title"]
            price = float(row["Price"])
            shipping = 0  # (optional: parse or prompt)
            total_cost = price + shipping

            print(f"\n🃏 {title}")
            sold_price = float(input("Enter sold price: $"))
            fees = float(input("Enter total fees (eBay/PayPal/etc): $"))
            sold_date = input("Enter sold date (YYYY-MM-DD): ")

            net_profit = sold_price - total_cost - fees
            roi = (net_profit / total_cost) * 100 if total_cost > 0 else 0

            # Store resale data in standardized columns
            row["Sold Price"] = sold_price
            row["Fees"] = fees
            row["Net Profit"] = round(net_profit, 2)
            row["ROI (%)"] = round(roi, 2)
            row["Sold Date"] = sold_date

            rows.append(row)

    # Save enriched log
    with open(updated_path, mode="w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✅ Resale log saved to {updated_path}")
