import csv

def analyze_resale_log(csv_path="resale_log.csv"):
    total_profit = 0
    total_roi = 0
    count = 0
    best = {"title": "", "profit": float("-inf")}
    worst = {"title": "", "profit": float("inf")}

    try:
        with open(csv_path, newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get("Sold Price") or not row.get("Net Profit"):
                    continue

                profit = float(row["Net Profit"])
                roi = float(row["ROI (%)"])
                title = row["Title"]

                total_profit += profit
                total_roi += roi
                count += 1

                if profit > best["profit"]:
                    best.update({"title": title, "profit": profit})

                if profit < worst["profit"]:
                    worst.update({"title": title, "profit": profit})

        if count == 0:
            print("⚠️ No completed resale data found.")
            return

        print(f"\n📊 ROI Summary ({count} items)")
        print(f"→ Avg Net Profit: ${round(total_profit / count, 2)}")
        print(f"→ Avg ROI: {round(total_roi / count, 2)}%")
        print(f"💰 Best Flip: {best['title']} → ${best['profit']}")
        print(f"🔻 Worst Flip: {worst['title']} → ${worst['profit']}")

    except FileNotFoundError:
        print(f"❌ resale_log.csv not found in path: {csv_path}")
