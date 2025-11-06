from flask import Flask, render_template, request, redirect, url_for, jsonify
start_date=start_date.isoformat() if start_date else '',
end_date=end_date.isoformat() if end_date else '',
budget=stats['budget']


from datetime import timedelta


@app.route('/add', methods=['POST'])
def add_record():
amount = request.form.get('amount')
rtype = request.form.get('type')
category = request.form.get('category')
date_str = request.form.get('date')
note = request.form.get('note')


try:
amt = float(amount)
except (ValueError, TypeError):
return redirect(url_for('index'))


rdate = parse_date(date_str, date.today())
if rtype not in ('income', 'expense'):
rtype = 'expense'


rec = Record(amount=amt, type=rtype, category=category or '未分類', date=rdate, note=note)
db.session.add(rec)
db.session.commit()


return redirect(url_for('index'))


# API endpoint: 返回統計 JSON（可供前端 fetch 重新繪圖）
@app.route('/api/stats', methods=['GET'])
def api_stats():
start_str = request.args.get('start_date', '')
end_str = request.args.get('end_date', '')
budget_str = request.args.get('budget', '')


start_date = parse_date(start_str, None)
end_date = parse_date(end_str, None)
budget = 30000
try:
if budget_str:
budget = float(budget_str)
except ValueError:
budget = 30000


stats = compute_stats(start_date, end_date, budget)
return jsonify(stats)


# API: 取得所有分類清單（可用於表單的下拉）
@app.route('/api/categories', methods=['GET'])
def api_categories():
cats = db.session.query(Record.category).distinct().all()
cats = [c[0] for c in cats]
# 加上一些常用分類
defaults = ['餐飲', '交通', '娛樂', '薪水', '其他收入', '購物']
merged = sorted(list(dict.fromkeys(defaults + cats)))
return jsonify(merged)


# API: 取出紀錄（用於顯示或匯出）
@app.route('/api/records', methods=['GET'])
def api_records():
start_str = request.args.get('start_date', '')
end_str = request.args.get('end_date', '')
start_date = parse_date(start_str, None)
end_date = parse_date(end_str, None)


q = Record.query
if start_date:
q = q.filter(Record.date >= start_date)
if end_date:
q = q.filter(Record.date <= end_date)
rows = [r.to_dict() for r in q.order_by(Record.date.desc()).limit(500).all()]
return jsonify(rows)


if __name__ == '__main__':
init_db()
app.run(debug=True)
