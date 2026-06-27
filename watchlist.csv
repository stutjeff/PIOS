def black_swan_score(price_data):
    if not price_data:
        return 0, ['尚未取得股價資料']
    score = 0
    reasons = []
    if abs(price_data.get('daily_change', 0)) >= 7:
        score += 25; reasons.append('單日漲跌超過 7%')
    if price_data.get('volume_ratio', 0) >= 2:
        score += 20; reasons.append('成交量超過 20 日均量 2 倍')
    if price_data.get('drop_from_high', 0) <= -30:
        score += 15; reasons.append('距 52 週高點跌深超過 30%')
    if price_data.get('drop_from_high', 0) <= -50:
        score += 15; reasons.append('距 52 週高點跌深超過 50%')
    if not reasons:
        reasons.append('目前沒有明顯黑天鵝異動')
    return score, reasons

def grade(score):
    if score >= 85: return 'S'
    if score >= 75: return 'A'
    if score >= 60: return 'B'
    if score >= 45: return 'C'
    return 'D'
