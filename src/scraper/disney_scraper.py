import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_on_sale(item: BeautifulSoup) -> tuple[bool, dict]:
    """
    Determines if a product is on sale by checking multiple indicators.
    Returns (is_sale, price_info)
    """
    price_info = {
        'current_price': None,
        'original_price': None,
        'savings_percent': None,
        'is_sale': False,
        'reason': None
    }

    try:
        # Method 1: Check for explicit sale markers
        sale_badge = item.find(['span', 'div'], class_=['sale', 'discount', 'promotion'])
        if sale_badge:
            price_info['reason'] = f"Sale badge found: {sale_badge.get_text().strip()}"
            price_info['is_sale'] = True

        # Method 2: Compare prices
        price_container = item.find(['div', 'span'], class_=['price', 'product-price'])
        if price_container:
            current = price_container.find(['span', 'div'], class_=['current-price', 'sale-price'])
            original = price_container.find(['span', 'div'], class_=['original-price', 'list-price'])

            if current and original:
                current_text = current.get_text().strip()
                original_text = original.get_text().strip()
                
                # Clean and convert prices
                current_price = float(current_text.replace('$', '').replace(',', ''))
                original_price = float(original_text.replace('$', '').replace(',', ''))

                price_info['current_price'] = current_price
                price_info['original_price'] = original_price

                if current_price < original_price:
                    savings = ((original_price - current_price) / original_price) * 100
                    price_info['savings_percent'] = round(savings, 2)
                    price_info['reason'] = f"Price reduced by {price_info['savings_percent']}%"
                    price_info['is_sale'] = True

        # Method 3: Look for special offer text
        special_text = item.find(string=lambda s: s and any(word in s.lower() 
            for word in ['sale', 'special offer', 'discount', 'save', 'reduced']))
        if special_text:
            price_info['reason'] = f"Special offer text found: {special_text.strip()}"
            price_info['is_sale'] = True

        return price_info['is_sale'], price_info

    except (AttributeError, ValueError) as e:
        logger.debug(f"Error checking sale status: {e}")
        return False, price_info


def fetch_deals() -> List[Dict]:
    """
    Scrapes Disney Store website for lightsaber deals.
    Returns a list of dictionaries containing deal information.
    """
    url = "https://www.disneystore.com/collectibles/lightsabers-and-relics/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    # Initialize deals list
    deals = []
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Content Length: {len(response.text)}")
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Save HTML for debugging
        with open('disney_response.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        
        # First, let's analyze what we got
        logger.debug("HTML structure sample:")
        for tag in list(soup.children)[:5]:
            logger.debug(f"Found tag: {tag.name if hasattr(tag, 'name') else 'NavigableString'}")
        
        # Try different possible selectors
        items = []
        selectors = [
            'div.product',  # This one worked previously
            'article.product',
            'div[data-component="product"]',
            '.product-grid-item'
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                logger.info(f"Found items using selector: {selector}")
                break
        
        logger.info(f"Found {len(items)} items")
        
        # Debug first item structure
        if items:
            logger.debug(f"First item HTML structure: {items[0].prettify()}")
        
        for item in items:
            is_sale, price_info = is_on_sale(item)
            if is_sale:
                try:
                    name_elem = item.find(['h2', 'h3', 'div'], class_=['product-title', 'title'])
                    image = item.find('img')
                    link = item.find('a')
                    
                    if all([name_elem, image, link]):
                        deal = {
                            'name': name_elem.get_text().strip(),
                            'price': f"${price_info['current_price']:.2f}",
                            'original_price': f"${price_info['original_price']:.2f}" if price_info['original_price'] else None,
                            'savings_percent': price_info['savings_percent'],
                            'sale_reason': price_info['reason'],
                            'image_url': image.get('src', image.get('data-src', '')),
                            'url': link.get('href', ''),
                        }
                        deals.append(deal)
                        logger.info(f"Found deal: {deal['name']}")
                        logger.info(f"Reason: {deal['sale_reason']}")
                
                except (AttributeError, KeyError) as e:
                    logger.error(f"Error parsing item: {e}")
                    continue
            
            return deals
        
    except requests.RequestException as e:
        logger.error(f"Error fetching deals: {e}")
        return []

def calculate_savings(current: str, original: str) -> str:
    """Calculate percentage savings"""
    try:
        current_price = float(current.replace('$', '').replace(',', ''))
        original_price = float(original.replace('$', '').replace(',', ''))
        savings = ((original_price - current_price) / original_price) * 100
        return f"{savings:.0f}% OFF"
    except (ValueError, ZeroDivisionError):
        return ""

if __name__ == "__main__":
    deals = fetch_deals()
    print(f"Found {len(deals)} deals")