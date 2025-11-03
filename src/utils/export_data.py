import json
from datetime import datetime
from pathlib import Path
from ..models.database import SessionLocal
from ..models.product import Product, PriceHistory

def export_price_history():
    """Export price history from SQLite database to JSON file"""
    db = SessionLocal()
    try:
        # Create data directory if it doesn't exist
        data_dir = Path(__file__).parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        
        # Query all products and their latest prices
        products = db.query(Product).all()
        export_data = {
            "last_updated": datetime.utcnow().isoformat(),
            "products": []
        }
        
        for product in products:
            # Get latest price
            latest_price = db.query(PriceHistory)\
                .filter(PriceHistory.product_id == product.id)\
                .order_by(PriceHistory.date.desc())\
                .first()
                
            if latest_price:
                product_data = {
                    "id": product.id,
                    "name": product.name,
                    "url": product.url,
                    "image_url": product.image_url,
                    "price": str(latest_price.price),
                    "price_history": []
                }
                
                # Get all price history
                history = db.query(PriceHistory)\
                    .filter(PriceHistory.product_id == product.id)\
                    .order_by(PriceHistory.date.asc())\
                    .all()
                    
                product_data["price_history"] = [
                    {
                        "date": h.date.strftime("%Y-%m-%d"),
                        "price": str(h.price)
                    } for h in history
                ]
                
                export_data["products"].append(product_data)
        
        # Write to JSON file
        json_path = data_dir / "price_history.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
            
        print(f"Exported price history to {json_path}")
        
    except Exception as e:
        print(f"Error exporting data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    export_price_history()