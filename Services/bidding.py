def calculate_max_bid(resale_price, shipping_cost=0.0, fee_rate=0.13, min_profit=10.0):
    try:
        net_resale = resale_price * (1 - fee_rate)
        max_total_cost = net_resale - min_profit
        max_bid = max_total_cost - shipping_cost
        return round(max_bid, 2) if max_bid > 0 else 0
    except Exception:
        return 0
