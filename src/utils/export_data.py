import json
from datetime import datetime, timedelta
from pathlib import Path
from src.models.database import SessionLocal
from src.models.product import Product, PriceHistory

def export_price_history():
    """Export price history to static JSON files"""
    db = SessionLocal()
    output_dir = Path(__file__).parent.parent.parent / "src" / "web" / "static" / "data"
    output_dir.mkdir(exist_ok=True)
    
    products = db.query(Product).all()
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    export_data = {
        "last_updated": datetime.utcnow().isoformat(),
        "products": []
    }
    
    for product in products:
        history = db.query(PriceHistory).filter(
            PriceHistory.product_id == product.id,
            PriceHistory.date >= thirty_days_ago
        ).order_by(PriceHistory.date).all()
        
        product_data = {
            "id": product.id,
            "name": product.name,
            "image_url": product.image_url,
            "url": product.url,
            "price_history": [
                {
                    "date": h.date.strftime("%Y-%m-%d"),
                    "price": float(h.price)
                } for h in history
            ]
        }
        export_data["products"].append(product_data)
    
    with open(output_dir / "price_history.json", "w") as f:
        json.dump(export_data, f, indent=2)

if __name__ == "__main__":
    export_price_history()