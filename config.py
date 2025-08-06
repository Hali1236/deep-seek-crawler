# List of all community “Available Homes” URLs you want to scrape
BASE_URLS = [
    "https://www.drhorton.com/texas/austin/austin/trails-at-wildhorse#relatedmovein",
    "https://www.drhorton.com/texas/austin/manor/monarch-ranch%20#relatedmovein",
    "https://www.drhorton.com/texas/austin/manor/palomino%20#relatedmovein",
    "https://www.drhorton.com/texas/austin/manor/carillon%20#relatedmovein",
    "https://www.drhorton.com/texas/austin/mustang-ridge/durango#relatedmovein",
    
    
    # add as many as you like here…
]

CSS_SELECTOR = ".card-content"

REQUIRED_KEYS = [
    "Price",
    "Address",
    "Beds",
    "Baths",
    "Garage",
    "Stories",
    "Sqft",
    "Lot",
    "Community",
]
