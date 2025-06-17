from datetime import datetime
import requests

def post_to_google_sheets(webhook_url, items):
    rows = []

    for item in items:
        (
            timestamp, title, price, currency, margin, profit, max_bid, confidence,
            time_left, feedback, condition, type_str, bid_status,
            item_url, sold_price, sold_date, fees, net_profit, roi
        ) = item

        # 🚫 Skip if critical fields are missing
        if not all([title, price, currency, margin, confidence, item_url]):
            print(f"⚠️ Skipping empty or incomplete row: {title}")
            continue

        rows.append({
            "Timestamp": timestamp,
            "Title": title,
            "Price": price,
            "Currency": currency,
            "Margin (%)": margin,
            "Profit ($)": profit,
            "Max Bid": max_bid,
            "Confidence": confidence,
            "Time Left (min)": time_left,
            "Seller Feedback (%)": feedback,
            "Condition": condition,
            "Type": type_str,
            "Bid Status": bid_status,
            "eBay Link": item_url,
            "Sold Price": sold_price,
            "Sold Date": sold_date,
            "Fees": fees,
            "Net Profit": net_profit,
            "ROI": roi
        })

    if not rows:
        print("ℹ️ No valid rows to post to Google Sheets.")
        return

    payload = {"items": rows}
    r = requests.post(webhook_url, json=payload)
    print("📤 Posted to Google Sheets:", r.status_code, r.text)
