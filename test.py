import requests
from bs4 import BeautifulSoup
import pandas as pd

# Step 1: Send request
URL = "http://books.toscrape.com/"
response = requests.get(URL)

# Step 2: Parse content
soup = BeautifulSoup(response.text, "lxml")

# Step 3: Extract data
books = soup.find_all("article", class_="product_pod")

book_data = []
for book in books:
    title = book.h3.a["title"]
    price = book.find("p", class_="price_color").text
    book_data.append({"Title": title, "Price": price})

# Step 4: Save data
df = pd.DataFrame(book_data)
df.to_csv("books.csv", index=False)

print("Scraping completed. Data saved to books.csv")
