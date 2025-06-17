from services.ebay_auth import get_ebay_access_token
from services.search_items import search_pokemon_items
from services.margin import calculate_margin
from services.confidence import compute_confidence_score
from services.bidding import calculate_max_bid
from services.bid_executor import simulate_bid
from services.resale_estimator import estimate_resale_from_comps
from datetime import datetime, timezone
import csv

HARD_BID_CAP = 40.00
TOTAL_AVAILABLE_FUNDS = 150.00
funds_remaining = TOTAL_AVAILABLE_FUNDS

BID_LOG_PATH = "bid_log.csv"

def log_to_csv(path, items):
    fieldnames = [
        "Timestamp", "Title", "Price", "Currency", "Margin (%)", "Profit ($)", "Max Bid", "Confidence",
        "Time Left (min)", "Seller Feedback (%)", "Condition", "Type", "Bid Status",
        "eBay Link", "Sold Price", "Sold Date", "Fees", "Net Profit", "ROI"
    ]
    with open(path, mode="w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            writer.writerow(dict(zip(fieldnames, item)))

if __name__ == "__main__":
    try:
        token = get_ebay_access_token()
        print("✅ Token fetched. Using live data...")
    except Exception as e:
        print("❌ Token fetch failed. Exiting:", e)
        exit(1)

    comps = search_pokemon_items(
        "pokemon (booster pack, psa, holo, etb, sealed, charizard) -lot -digital -online",
        limit=199,
        token=token,
        sort="price desc",
        filter_str="buyingOptions:{FIXED_PRICE},conditions:{NEW|USED},itemLocationCountry:US"
    )

    ESTIMATED_RESALE = estimate_resale_from_comps(
        comps.get("itemSummaries", []),
        target_keywords=["charizard", "booster", "etb", "sealed", "gx", "sv", "psa", "ex", "pack"]
    )

    results = search_pokemon_items(
        "pokemon (booster pack, psa, holo, etb, sealed, charizard) -lot -digital -online",
        limit=199,
        token=token,
        sort="endTime asc",
        filter_str="buyingOptions:{AUCTION},conditions:{NEW|USED},itemLocationCountry:US"
    )

    qualified_items = []

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

            margin, profit = calculate_margin(price, ESTIMATED_RESALE, shipping_cost)
            confidence = compute_confidence_score(title, price, ESTIMATED_RESALE, condition=condition)
            max_bid = min(calculate_max_bid(ESTIMATED_RESALE, shipping_cost), HARD_BID_CAP)

            can_afford = price <= max_bid and price <= funds_remaining
            bid_status = "✅ Bid placed" if can_afford else "❌ Skipped (limit/funds)"

            if time_left_minutes is None or time_left_minutes <= 60:
                item_url = item.get("itemWebUrl", "").strip()
                if title and currency and confidence is not None and price > 0:
                    qualified_items.append((
                        datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
                        title, price, currency, margin, profit, max_bid, confidence,
                        time_left_minutes, feedback, condition, type_str, bid_status,
                        item_url, "", "", "", "", ""
                    ))
                    if can_afford:
                        funds_remaining -= price
                else:
                    print(f"⚠️ Skipped malformed item: title={title}, price={price}")
        except KeyError as e:
            print(f"❌ Skipping item due to missing key: {e}")

    qualified_items.sort(key=lambda x: x[6], reverse=True)

    for item in qualified_items:
        print(f"{item[1]} - {item[2]} {item[3]} | Margin: {item[4]}% | Profit: ${item[5]} | Max Bid: ${item[6]} | "
              f"Confidence: {item[7]}/100 | Ends in: {item[8]} min | Seller: {item[9]}% | "
              f"Condition: {item[10]} | Type: {item[11]} | {item[12]} | 🔗 {item[13]}")

    if qualified_items:
        log_to_csv(BID_LOG_PATH, qualified_items)
        print(f"\n📥 Saved {len(qualified_items)} items to {BID_LOG_PATH}.")
    else:
        print("ℹ️ No qualified items to log.")
