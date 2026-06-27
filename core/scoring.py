def black_swan_score(p):
    if not p: return 0,['尚未取得股價資料']
    score=0; r=[]
    if abs(p.get('daily_change',0))>=7: score+=25; r.append('單日漲跌超過 7%')
    if p.get('volume_ratio',0)>=2: score+=20; r.append('成交量超過 20 日均量 2 倍')
    if p.get('drop_from_high',0)<=-30: score+=15; r.append('距 52 週高點跌深超過 30%')
    if p.get('drop_from_high',0)<=-50: score+=15; r.append('距 52 週高點跌深超過 50%')
    return score, r or ['目前沒有明顯黑天鵝異動']
def grade(s):
    return 'S' if s>=85 else 'A' if s>=75 else 'B' if s>=60 else 'C' if s>=45 else 'D'
