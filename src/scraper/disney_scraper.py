import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.database import SessionLocal
from ..models.product import Product, PriceHistory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_to_db(items: list) -> None:
    """Save scraped items to database"""
    db = SessionLocal()
    try:
        for item in items:
            # Check if product exists
            product = db.query(Product).filter(Product.url == item['url']).first()
            
            if not product:
                product = Product(
                    name=item['name'],
                    url=item['url'],
                    image_url=item['image_url']
                )
                db.add(product)
                db.flush()  # Get product ID
            
            # Add price history
            price_history = PriceHistory(
                product_id=product.id,
                price=float(item['price'].replace('$', '').replace(',', '')),
                date=datetime.utcnow()
            )
            db.add(price_history)
        
        db.commit()
        logger.info(f"Saved {len(items)} items to database")
    
    except Exception as e:
        logger.error(f"Error saving to database: {e}")
        db.rollback()
    finally:
        db.close()

def fetch_deals():
    """Fetch all lightsaber products from Disney Store"""
    url = "https://www.disneystore.com/collectibles/lightsabers-and-relics/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Save HTML for debugging
        with open('disney_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
            logger.info(f"Saved HTML response to disney_response.html")
        
        soup = BeautifulSoup(response.text, 'lxml')
        items = []

        # Find all product divs directly
        products = soup.find_all('div', class_='product')
        if not products:
            logger.error("No products found with class 'product'")
            # Try alternative selectors
            products = soup.select('div[class*="product-"], div[data-product]')
            
        logger.info(f"Found {len(products)} products")
        
        for product in products:
            try:
                # Try multiple selectors for each element
                name_elem = (
                    product.find(['h2', 'h3', 'div'], class_=lambda x: x and 'title' in x.lower()) or
                    product.find(['h2', 'h3', 'div'], class_=lambda x: x and 'name' in x.lower())
                )
                
                link_elem = product.find('a')
                
                # Updated image element handling
                img_elem = product.find('img')
                img_url = None
                if img_elem:
                    # Try different image source attributes
                    img_url = (
                        img_elem.get('src') or 
                        img_elem.get('data-src') or 
                        img_elem.get('data-lazy-src') or
                        img_elem.get('srcset', '').split(',')[0].strip().split(' ')[0]
                    )
                
                price_elem = (
                    product.find(['span', 'div'], class_=lambda x: x and 'price' in x.lower()) or
                    product.find(['span', 'div'], string=lambda x: x and '$' in x)
                )

                # Debug element finding
                if name_elem:
                    logger.debug(f"Found name: {name_elem.text.strip()}")
                if link_elem:
                    logger.debug(f"Found link: {link_elem.get('href', '')}")
                if img_url:
                    logger.debug(f"Found image: {img_url}")
                if price_elem:
                    logger.debug(f"Found price: {price_elem.text.strip()}")

                if all([name_elem, link_elem, img_url, price_elem]):
                    base_url = 'https://www.disneystore.com'
                    item = {
                        'name': name_elem.text.strip(),
                        'url': base_url + link_elem['href'] if not link_elem['href'].startswith('http') else link_elem['href'],
                        'image_url': img_url if img_url.startswith('http') else base_url + img_url,
                        'price': price_elem.text.strip()
                    }
                    items.append(item)
                    logger.info(f"Found product: {item['name']} - {item['price']}")
                else:
                    missing = []
                    if not name_elem: missing.append('name')
                    if not link_elem: missing.append('link')
                    if not img_url: missing.append('image')
                    if not price_elem: missing.append('price')
                    logger.warning(f"Skipping product - missing elements: {', '.join(missing)}")
            
            except Exception as e:
                logger.error(f"Error parsing product: {str(e)}")
                logger.debug(f"Product HTML causing error:\n{product.prettify()}")
                continue

        logger.info(f"Successfully parsed {len(items)} products")
        
        if items:
            save_to_db(items)
        else:
            logger.warning("No valid products found to save")
            
        return items
        
    except requests.RequestException as e:
        logger.error(f"Error fetching deals: {e}")
        return []

if __name__ == "__main__":
    deals = fetch_deals()
    print(f"Found {len(deals)} items")