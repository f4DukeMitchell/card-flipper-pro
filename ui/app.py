from flask import Flask, jsonify
from services.ebay_auth import get_ebay_access_token
from services.search_items import search_pokemon_items
from services.margin import calculate_margin
from services.confidence import compute_confidence_score
from services.bidding import calculate_max_bid
from services.resale_estimator import estimate_resale_from_comps
from datetime import datetime, timezone

app = Flask(__name__)

@app.route("/api/scan", methods=["GET"])
def scan_items():
    try:
        token = get_ebay_access_token()
    except Exception as e:
        return jsonify({"error": str(e)}), 401

    comps = search_pokemon_items(
        "pokemon (booster pack, psa, holo, etb, sealed, charizard) -lot -digital -online",
        limit=199,
        token=token,
        sort="price desc",
        filter_str="buyingOptions:{FIXED_PRICE},conditions:{NEW|USED},itemLocationCountry:US"
    )

    estimated_resale = estimate_resale_from_comps(
        comps.get("itemSummaries", []),
        target_keywords=["charizard", "booster", "etb", "sealed", "gx", "sv", "psa", "ex", "pack"]
    )

    auctions = search_pokemon_items(
        "pokemon (booster pack, psa, holo, etb, sealed, charizard) -lot -digital -online",
        limit=30,
        token=token,
        sort="endTime asc",
        filter_str="buyingOptions:{AUCTION},conditions:{NEW|USED},itemLocationCountry:US"
    )

    results = []
    for item in auctions.get("itemSummaries", []):
        try:
            title = item["title"]
            price = float(item["price"]["value"])
            shipping = float(item.get("shippingOptions", [{}])[0].get("shippingCost", {}).get("value", 0))
            condition = item.get("condition", "USED")
            feedback = float(item.get("seller", {}).get("feedbackPercentage", 0))
            end_time_str = item.get("itemEndDate")
            end_time = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
            time_left = int((end_time - datetime.now(timezone.utc)).total_seconds() / 60)

            margin, profit = calculate_margin(price, estimated_resale, shipping)
            confidence = compute_confidence_score(title, price, estimated_resale, condition=condition)
            max_bid = min(calculate_max_bid(estimated_resale, shipping), 40.0)

            results.append({
                "title": title,
                "price": price,
                "margin": margin,
                "profit": profit,
                "confidence": confidence,
                "maxBid": max_bid,
                "timeLeft": time_left,
                "feedback": feedback,
                "condition": condition,
                "url": item.get("itemWebUrl", "")
            })
        except:
            continue

    return jsonify({"items": results})

if __name__ == "__main__":
    app.run(debug=True)
