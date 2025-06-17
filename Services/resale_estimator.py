from statistics import median
import re

def estimate_resale_from_sales(sold_items, target_keywords):
    resale_values = []

    for item in sold_items:
        try:
            title = item.get("title", "").lower()
            price = float(item["price"]["value"])
            shipping = float(item.get("shippingOptions", [{}])[0].get("shippingCost", {}).get("value", 0))
            full_cost = price + shipping

            # Must contain one of the target keywords
            if not any(kw.lower() in title for kw in target_keywords):
                continue

            # Reject lot, digital, bulk, etc.
            if re.search(r'\blot\b|\bdigital\b|\bbundle\b|\bcode\b', title):
                continue

            # Optional: stricter graded/ungraded matching can go here
            # e.g., require "psa 10" or "ungraded" explicitly based on mode

            # Fee calculations
            ebay_fee = 0.1325 * full_cost
            paypal_fee = 0.0299 * full_cost + 0.49
            handling_fee = 0.75
            estimated_shipping = 0.99

            net = full_cost - (ebay_fee + paypal_fee + handling_fee + estimated_shipping)
            resale_values.append(net)
        except Exception as e:
            print(f"⚠️ Skipping bad sale entry: {e}")

    if not resale_values:
        return 0.0

    return round(median(resale_values), 2)
