import unittest
from src.scraper.disney_scraper import fetch_deals

class TestDisneyScraper(unittest.TestCase):

    def test_fetch_deals(self):
        deals = fetch_deals()
        self.assertIsInstance(deals, list)
        for deal in deals:
            self.assertIn('title', deal)
            self.assertIn('price', deal)
            self.assertIn('image_url', deal)

if __name__ == '__main__':
    unittest.main()