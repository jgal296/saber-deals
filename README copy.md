# saber-deals

This project is a web scraping service that retrieves daily deals on lightsabers from the Disney Store website. It provides a simple web page displaying current deals, descriptions, and images of the items. Future integrations may include email alerts or push notifications.

## Project Structure

```
saber-deals
├── src
│   ├── scraper
│   │   ├── __init__.py
│   │   └── disney_scraper.py
│   ├── web
│   │   ├── __init__.py
│   │   ├── templates
│   │   │   ├── base.html
│   │   │   └── index.html
│   │   └── static
│   │       ├── css
│   │       │   └── styles.css
│   │       └── js
│   │           └── main.js
│   └── utils
│       ├── __init__.py
│       └── helpers.py
├── tests
│   ├── __init__.py
│   └── test_scraper.py
├── requirements.txt
├── config.py
├── main.py
├── .env
├── .gitignore
└── README.md
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/saber-deals.git
   cd saber-deals
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

## Usage

- Access the web application at `http://localhost:5000` to view current deals on lightsabers.
- The application will scrape the Disney Store website daily for updates on deals.

## Future Enhancements

- Implement email alerts for new deals.
- Add push notifications for real-time updates.