import os
from time import time
from urllib.parse import urljoin
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from tinydb import TinyDB
 
 
def insert_to_db(db, ecommerce_name, product_image_url, product_url, product_title, product_quantity, product_price, product_discounted_price):
    db.insert({
        "ecommerce_name": ecommerce_name,
        "product_image_url": product_image_url,
        "product_url": product_url,
        "product_title": product_title,
        "product_quantity": product_quantity,
        "product_price": product_price,
        "product_discounted_price": product_discounted_price,
        "created_at": time()
    })
 
def scrape_chaldal_offers(headers):
    url = "https://chaldal.com/offers"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
 
    offer_data = []
 
    for offer in soup.find_all("li", class_="offer-item"):
        product = offer.find("div", class_="product")
 
        try:
            product_image_url = product.find("img").get("src")
            product_url = product.find("a", class_="btnShowDetails").get("href")
            product_full_url = urljoin(response.url, product_url)
            product_title = product.find("div", class_="name").text
            product_quantity = product.find("div", class_="subText").text
            product_price = product.find("div", class_="price").findChildren("span")[-1].text
            try:
                product_discounted_price = product.find("div", class_="discountedPrice").findChildren("span")[-1].text
            except Exception:
                product_discounted_price = ""
                pass
            offer_data.append({
                "product_image_url": product_image_url,
                "product_url": product_full_url,
                "product_title": product_title,
                "product_quantity": product_quantity,
                "product_price": product_price,
                "product_discounted_price": product_discounted_price
            })
        except Exception as e:
            print(e)
 
    return offer_data
 
 
def main():
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db = TinyDB(os.path.join(project_path, "db.json"))
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random
    }
 
    print("Scraping ChalDal")
    chaldal_offer_data = scrape_chaldal_offers(headers)
 
    for chaldal_offer_item in chaldal_offer_data:
        insert_to_db(db, "chaldal", chaldal_offer_item["product_image_url"], chaldal_offer_item["product_url"], chaldal_offer_item["product_title"], chaldal_offer_item["product_quantity"], chaldal_offer_item["product_price"], chaldal_offer_item["product_discounted_price"])
 
    print("Finished scraping")
 
if __name__ == "__main__":
    main()