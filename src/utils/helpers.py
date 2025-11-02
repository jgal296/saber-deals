def format_deal(deal):
    """Format the deal information for display."""
    return {
        'title': deal.get('title', 'No Title'),
        'price': deal.get('price', 'No Price'),
        'description': deal.get('description', 'No Description'),
        'image_url': deal.get('image_url', ''),
    }

def extract_deals(html_content):
    """Extract deals from the HTML content of the Disney Store page."""
    # Placeholder for extraction logic
    deals = []
    # Logic to parse HTML and populate deals list goes here
    return deals

def save_deals_to_file(deals, filename='deals.json'):
    """Save the extracted deals to a JSON file."""
    import json
    with open(filename, 'w') as f:
        json.dump(deals, f, indent=4)