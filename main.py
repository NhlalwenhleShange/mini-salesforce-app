from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import random
from datetime import datetime
import uvicorn

app = FastAPI(title="Mini-Salesforce API")

# This is our Salesforce database - in memory for demo
# In real Salesforce this would be their DB
deals_db = []

companies = ["Nedbank", "Shoprite", "MTN", "Sasol", "Discovery", "Capitec", "Woolworths"]
products = ["Software License", "Consulting", "Cloud Hosting", "Support Plan", "Training"]
stages = ["Prospecting", "Qualification", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
reps = ["Thabo", "Naledi", "Sipho", "Ayanda", "Lerato", "Kabelo"]

def make_deal(company=None, product=None, rep=None, stage=None, value=None):
    return {
        "opportunity_id": f"OPP-{random.randint(10000, 99999)}",
        "company": company or random.choice(companies),
        "product": product or random.choice(products),
        "sales_rep": rep or random.choice(reps),
        "stage": stage or random.choice(stages),
        "close_value": value or random.randint(5000, 250000),
        "close_date": datetime.now().strftime("%Y-%m-%d"),
        "created_at": datetime.now().isoformat()
    }

# --- FRONTEND - The website salespeople use ---
@app.get("/", response_class=HTMLResponse)
def home():
    rows = "".join([f"<tr><td>{d['opportunity_id']}</td><td>{d['company']}</td><td>{d['product']}</td><td>{d['sales_rep']}</td><td>{d['stage']}</td><td>R{d['close_value']}</td></tr>" for d in deals_db[-20:]])
    return f"""
    <html><head><title>Mini-Salesforce</title>
    <style>body{{font-family:Arial;padding:20px}} table{{border-collapse:collapse;width:100%}} td,th{{border:1px solid #ddd;padding:8px}} button{{background:#0176d3;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer}}</style>
    </head><body>
    <h1>💼 Mini-Salesforce</h1>
    <p>Total deals: <b>{len(deals_db)}</b> | API for ADF: <a href="/api/deals">/api/deals</a></p>
    <form action="/add-deal" method="post">
        Company: <select name="company">{''.join([f'<option>{c}</option>' for c in companies])}</select>
        Product: <select name="product">{''.join([f'<option>{p}</option>' for p in products])}</select>
        Rep: <select name="rep">{''.join([f'<option>{r}</option>' for r in reps])}</select>
        Value: <input type="number" name="value" value="50000">
        <button type="submit">Save Deal</button>
    </form>
    <br><a href="/generate?count=50"><button>Generate 50 Random Deals</button></a>
    <br><br><table><tr><th>ID</th><th>Company</th><th>Product</th><th>Rep</th><th>Stage</th><th>Value</th></tr>{rows}</table>
    </body></html>
    """

@app.post("/add-deal")
def add_deal(company: str = Form(...), product: str = Form(...), rep: str = Form(...), value: int = Form(...)):
    deals_db.append(make_deal(company, product, rep, "Prospecting", value))
    from fastapi.responses import RedirectResponse
    return RedirectResponse("/", status_code=303)

@app.get("/generate")
def generate(count: int = 50):
    for _ in range(count):
        deals_db.append(make_deal())
    from fastapi.responses import RedirectResponse
    return RedirectResponse("/", status_code=303)

# --- API - THIS IS WHAT ADF CALLS ---
@app.get("/api/deals")
def get_deals():
    # ADF will call this URL every hour
    return {"count": len(deals_db), "deals": deals_db}

@app.get("/api/health")
def health():
    return {"status": "ok"}