from datetime import datetime
import requests
import re
from ast import literal_eval

CURRENCY_URL = "https://api.exchangerate-api.com/v4/latest/usd"
try:
    EXCHANGES = literal_eval(requests.get(CURRENCY_URL).text)
except requests.RequestException as e:
    print(f"Failed to fetch exchange rates: {e}")
    EXCHANGES = {}


def formatResult(website, titles, prices, links, ratings, num_ratings, trending, df_flag, currency, img_link=None):
    title, price, link, rating, num_rating, converted_cur, trending_stmt = (
        "", "", "", "", "", "", ""
    )

    if website not in ['ebay', 'target']:
        if titles and isinstance(titles, list) and titles:
            title = titles[0].get_text().strip()
        elif isinstance(titles, str):
            title = titles.strip()
        else:
            title = "Title not available"  # Default message if title is missing

        if prices:
            price = prices[0].get_text().strip()
            price = re.sub(r'\s|,', '', price)
            price_match = re.search(r"[0-9\.]+", price)
            price = "$" + price_match.group() if price_match else "Price not available"

        link = links[0]["href"] if links else ""

        if ratings:
            try:
                if website == "bestbuy":
                    match = re.search(r"Rating (\d+\.\d+) out of 5 stars", ratings[0].get_text().strip())
                    rating = float(match.group(1)) if match else None
                elif isinstance(ratings, list):
                    rating = float(ratings[0].get_text().strip().split()[0])
                else:
                    rating = float(ratings)
            except (ValueError, AttributeError, IndexError):
                rating = None

        if num_ratings:
            if isinstance(num_ratings, int):
                num_rating = num_ratings
            elif isinstance(num_ratings, str):
                num_rating = re.sub(r"[^\d]", "", num_ratings)
            else:
                num_rating = re.sub(r"[^\d]", "", num_ratings[0].get_text()) if num_ratings else ""

        converted_cur = getCurrency(currency, price) if currency else None
        img_link = img_link[0].get('src') if img_link and not isinstance(img_link, str) else img_link

        product = {
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "title": title,
            "price": price,
            "img_link": img_link or "https://odoo-community.org/web/image/product.product/19823/image_1024/Default%20Product%20Images?unique=638e17b",
            "link": link if link.startswith('http') else f"https://www.{website}.com{link}",
            "website": website,
            "rating": rating,
            "no_of_ratings": num_rating,
            "trending": trending_stmt,
            "converted_price": converted_cur,
        }
    else:
        converted_cur = getCurrency(currency, prices) if currency else None
        product = {
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "title": titles,
            "price": prices,
            "link": links,
            "img_link": img_link or "https://avatars.githubusercontent.com/u/56881419",
            "website": website,
            "rating": ratings,
            "no_of_ratings": num_ratings,
            "trending": trending,
            "converted_price": converted_cur,
        }

    return product


def sortList(arr, sortBy, reverse):
    if sortBy == "pr":
        return arr.sort_values(
            key=lambda x: x.apply(lambda y: getNumbers(y)),
            by=["price"],
            ascending=reverse,
        )
    elif sortBy == "ra":
        arr["rating"] = arr["rating"].apply(lambda x: None if x == "" else float(x) if x is not None else None)
        return arr.sort_values(by=["rating"], ascending=reverse)
    return arr


def formatSearchQuery(query):
    return query.replace(" ", "+") if query else ""


def getNumbers(st):
    ans = ''.join(ch for ch in str(st) if ch.isdigit() or ch == ".")
    try:
        return float(ans)
    except ValueError:
        return 0


def getCurrency(currency, price):
    converted_cur = 0.0
    try:
        if price and "$" in price:
            numeric_price = int(re.sub(r"[^\d]", "", price.split("$")[1]))
            converted_cur = numeric_price * EXCHANGES["rates"].get(currency.upper(), 1)
            return f"{currency.upper()} {round(converted_cur, 2)}"
    except Exception as e:
        print(f"Error in currency conversion: {e}")
    return converted_cur
