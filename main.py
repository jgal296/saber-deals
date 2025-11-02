import sys
from flask import Flask, render_template
from pathlib import Path
from src.scraper.disney_scraper import fetch_deals

# Get absolute paths
ROOT_DIR = Path(__file__).parent
SRC_DIR = ROOT_DIR / "src"
TEMPLATE_DIR = SRC_DIR / "web" / "templates"
STATIC_DIR = SRC_DIR / "web" / "static"

app = Flask(__name__, 
    template_folder='src/web/templates',
    static_folder='src/web/static'
)

@app.route('/')
def index():
    deals = fetch_deals()
    return render_template('index.html', deals=deals)

@app.route('/price-history')
def price_history():
    return render_template('price_history.html')

if __name__ == '__main__':
    # Verify paths exist
    print(f"Template directory: {TEMPLATE_DIR} (exists: {TEMPLATE_DIR.exists()})")
    print(f"Static directory: {STATIC_DIR} (exists: {STATIC_DIR.exists()})")
    app.run(debug=True)