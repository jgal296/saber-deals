from ..models.database import engine, Base
from ..scraper.disney_scraper import fetch_deals
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    logger.info("Fetching initial price data...")
    fetch_deals()
    
    logger.info("Database initialization complete")

if __name__ == "__main__":
    init_database()