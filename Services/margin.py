def calculate_margin(purchase_price, estimated_resale_price, shipping_cost=0, fee_rate=0.13):
    try:
        total_cost = float(purchase_price) + float(shipping_cost)
        net_resale = float(estimated_resale_price) * (1 - fee_rate)
        profit = net_resale - total_cost
        margin = (profit / total_cost) * 100 if total_cost > 0 else 0
        return round(margin, 2), round(profit, 2)
    except (ValueError, ZeroDivisionError):
        return 0, 0
