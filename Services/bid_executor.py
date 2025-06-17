def simulate_bid(current_price, max_bid, time_left_minutes, is_auction=True):
    if not is_auction:
        return "❌ Skipped (not auction)"

    if time_left_minutes is None or time_left_minutes > 2:
        return "⏳ Too early to bid"

    if current_price >= max_bid:
        return f"❌ Skipped (price ${current_price} exceeds max bid ${max_bid})"

    # Simulate successful snipe
    return f"✅ Bid placed at ${current_price}"
