def compute_confidence_score(title, price, resale_estimate, condition="used"):
    score = 50  # Base score

    # 🔎 Title signal
    title_lower = title.lower()
    if "charizard" in title_lower:
        score += 10
    if any(word in title_lower for word in ["gx", "vmax", "sv49", "shiny"]):
        score += 5

    # 💰 Margin signal
    try:
        margin = (float(resale_estimate) - float(price)) / float(price) * 100
        if margin >= 50:
            score += 10
        elif margin >= 30:
            score += 5
        elif margin < 15:
            score -= 10
    except ZeroDivisionError:
        margin = 0

    # 🧾 Condition
    if condition.lower() == "new":
        score += 5
    elif condition.lower() == "used":
        score -= 5

    return max(0, min(100, score))  # Clamp to 0–100
