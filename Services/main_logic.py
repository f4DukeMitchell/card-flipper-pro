from services.ebay_auth import get_ebay_access_token
from services.search_items import search_pokemon_items
from services.margin import calculate_margin
from services.confidence import compute_confidence_score
from services.bidding import calculate_max_bid
from services.resale_estimator import estimate_resale_from_sales
from datetime import datetime, timezone
from statistics import median
import csv
import re

HARD_BID_CAP = 40.00
TOTAL_AVAILABLE_FUNDS = 150.00
BID_LOG_PATH = "bid_log.csv"


def log_to_csv(path, items):
    if not items:
        return
    fieldnames = list(items[0].keys())
    with open(path, mode="w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            writer.writerow(item)


def process_item_for_resale(item, sold_comps):
    title = item.get("title", "")
    condition = item.get("condition", "").lower()
    keywords = [kw.strip().lower() for kw in re.split(r'[-:|,/]', title) if kw.strip()]
    target_keywords = [kw for kw in keywords if kw not in ["lot", "digital", "code", "bundle"]]

    filtered_comps = [c for c in sold_comps if condition in c.get("title", "").lower() and any(kw in c.get("title", "").lower() for kw in target_keywords)]

    sample_titles = [c['title'] for c in filtered_comps[:5]]
    print(f"🔍 [{title}] ({condition}) | Matching comps: {len(filtered_comps)}")
    for t in sample_titles:
        print(f"   - {t}")

    resale_value = estimate_resale_from_sales(filtered_comps, target_keywords)
    print(f"📈 Estimated resale: ${resale_value:.2f}\n")
    return resale_value


def scan_items():
    try:
        token = get_ebay_access_token()
    except Exception as e:
        print("❌ Token fetch failed. Exiting:", e)
        return []

    sold_comps = search_pokemon_items(
        "pokemon (booster pack, psa, holo, etb, sealed, charizard) -lot -digital -online",
        limit=199,
        token=token,
        sort="price desc",
        filter_str="buyingOptions:{FIXED_PRICE},conditions:{NEW|USED},itemLocationCountry:US"
    ).get("itemSummaries", [])

    results = search_pokemon_items(
        "pokemon (booster pack, psa, holo, etb, sealed, charizard) -lot -digital -online",
        limit=199,
        token=token,
        sort="endTime asc",
        filter_str="buyingOptions:{AUCTION},conditions:{NEW|USED},itemLocationCountry:US"
    )

    qualified_items = []
    funds_remaining = TOTAL_AVAILABLE_FUNDS

    for item in results.get("itemSummaries", []):
        try:
            title = item["title"]
            price = float(item["price"]["value"])
            currency = item["price"]["currency"]
            condition = item.get("condition", "USED")
            feedback = float(item.get("seller", {}).get("feedbackPercentage", 0))
            shipping_cost = float(item.get("shippingOptions", [{}])[0].get("shippingCost", {}).get("value", 0))
            buying_options = item.get("buyingOptions", [])
            type_str = "Auction" if "AUCTION" in buying_options else "BIN" if "FIXED_PRICE" in buying_options else "Unknown"

            end_time_str = item.get("itemEndDate")
            time_left_minutes = None
            if end_time_str:
                end_time = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
                time_left_minutes = int((end_time - datetime.now(timezone.utc)).total_seconds() / 60)

            estimated_resale = process_item_for_resale(item, sold_comps)
            margin, profit = calculate_margin(price, estimated_resale, shipping_cost)
            confidence = compute_confidence_score(title, price, estimated_resale, condition=condition)
            max_bid = min(calculate_max_bid(estimated_resale, shipping_cost), HARD_BID_CAP)

            can_afford = price <= max_bid and price <= funds_remaining
            bid_status = "✅ Bid placed" if can_afford else "❌ Skipped (limit/funds)"

            if time_left_minutes is None or time_left_minutes <= 60:
                item_url = item.get("itemWebUrl", "").strip()
                if title and currency and confidence is not None and price > 0:
                    qualified_items.append({
                        "Timestamp": datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
                        "Title": title,
                        "Price": price,
                        "Currency": currency,
                        "Margin (%)": margin,
                        "Profit ($)": profit,
                        "Max Bid": max_bid,
                        "Confidence": confidence,
                        "Time Left (min)": time_left_minutes,
                        "Seller Feedback (%)": feedback,
                        "Condition": condition,
                        "Type": type_str,
                        "Bid Status": bid_status,
                        "eBay Link": item_url,
                        "Sold Price": "",
                        "Sold Date": "",
                        "Fees": "",
                        "Net Profit": "",
                        "ROI": ""
                    })
                    if can_afford:
                        funds_remaining -= price
                else:
                    print(f"⚠️ Skipped malformed item: title={title}, price={price}")
        except KeyError as e:
            print(f"❌ Skipping item due to missing key: {e}")

    qualified_items.sort(key=lambda x: x["Max Bid"], reverse=True)
    return qualified_items


if __name__ == "__main__":
    items = scan_items()
    for item in items:
        print(f"{item['Title']} - {item['Price']} {item['Currency']} | Margin: {item['Margin (%)']}% | Profit: ${item['Profit ($)']} | Max Bid: ${item['Max Bid']} | "
              f"Confidence: {item['Confidence']}/100 | Ends in: {item['Time Left (min)']} min | Seller: {item['Seller Feedback (%)']}% | "
              f"Condition: {item['Condition']} | Type: {item['Type']} | {item['Bid Status']} | 🔗 {item['eBay Link']}")

    if items:
        log_to_csv(BID_LOG_PATH, items)
        print(f"\n📥 Saved {len(items)} items to {BID_LOG_PATH}.")
    else:
        print("ℹ️ No qualified items to log.")
