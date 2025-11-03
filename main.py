import sys
from flask import Flask, render_template, request, jsonify
from pathlib import Path
from src.scraper.disney_scraper import fetch_deals
from sqlalchemy import or_
from src.models.database import get_db
from src.models.product import Product, PriceHistory

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

@app.route('/api/search')
def search_products():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    db = next(get_db())
    try:
        app.logger.info(f"Searching for: {query}")
        products = db.query(Product).filter(
            Product.name.ilike(f'%{query}%')
        ).all()
        app.logger.info(f"Found {len(products)} matching products")
        
        # Get the current price for each product
        results = []
        for product in products:
            latest_price = db.query(PriceHistory)\
                .filter(PriceHistory.product_id == product.id)\
                .order_by(PriceHistory.date.desc())\
                .first()
            
            results.append({
                'id': product.id,
                'name': product.name,
                'image_url': product.image_url,
                'current_price': f"${latest_price.price:.2f}" if latest_price else 'Price not available'
            })
        
        return jsonify(results)
        
    except Exception as e:
        app.logger.error(f"Search error: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500
    finally:
        db.close()

@app.route('/api/price-history/<int:product_id>')
def get_price_history(product_id):
    db = next(get_db())
    try:
        # Get all price history for the product
        history = db.query(PriceHistory)\
            .filter(PriceHistory.product_id == product_id)\
            .order_by(PriceHistory.date.asc())\
            .all()
        
        if not history:
            return jsonify({'error': 'No price history found'}), 404
            
        return jsonify({
            'dates': [h.date.strftime('%Y-%m-%d') for h in history],
            'prices': [float(h.price) for h in history]
        })
        
    except Exception as e:
        app.logger.error(f"Price history error: {str(e)}")
        return jsonify({'error': 'Failed to fetch price history'}), 500
    finally:
        db.close()

if __name__ == '__main__':
    # Verify paths exist
    print(f"Template directory: {TEMPLATE_DIR} (exists: {TEMPLATE_DIR.exists()})")
    print(f"Static directory: {STATIC_DIR} (exists: {STATIC_DIR.exists()})")
    app.run(debug=True)