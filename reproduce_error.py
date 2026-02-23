from ntscraper import Nitter

print("Testing Nitter initialization...")
try:
    scraper = Nitter(log_level=1, skip_instance_check=False)
    print("Scraper initialized.")
    tweets = scraper.get_tweets("test", mode='term', number=1)
    print(f"Result: {tweets}")
except Exception as e:
    print(f"Error caught: {e}")
