"""
Copyright (C) 2021 SE Slash - All Rights Reserved
You may use, distribute and modify this code under the terms of the MIT license.
You should have received a copy of the MIT license with this file. If not, please write to: secheaper@gmail.com
"""

"""
The scraper module contains functions that scrape various e-commerce websites.
"""

import requests
import os
import re
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from ebaysdk.finding import Connection
from .formatter import formatSearchQuery, formatResult, getCurrency, sortList
from concurrent.futures import ThreadPoolExecutor

# Create a global session to enable connection pooling.
SESSION = requests.Session()

def httpsGet(URL):
    """
    Makes an HTTP GET request to the specified URL with custom headers.
    Reuses the global SESSION for connection pooling.
    Uses the "lxml" parser without an extra prettify call.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'no-cache'
    }
    response = SESSION.get(URL, headers=headers, allow_redirects=False)
    # Parse once using the fast "lxml" parser.
    return BeautifulSoup(response.content, "lxml")


def searchAmazon(query, df_flag, currency):
    query = formatSearchQuery(query)
    URL = f"https://www.amazon.com/s?k={query}"
    page = httpsGet(URL)
    results = page.findAll("div", {"data-component-type": "s-search-result"})
    products = []
    for res in results:
        titles, prices, links = (
            res.select("h2 a span"),
            res.select("span.a-price span"),
            res.select("h2 a.a-link-normal")
        )
        ratings = res.select("span.a-icon-alt")
        num_ratings = res.select("span.a-size-base")
        trending = res.select("span.a-badge-text")
        img_links = res.select("img.s-image")
        trending = trending[0] if trending else None
        product = formatResult("amazon", titles, prices, links, ratings,
                                num_ratings, trending, df_flag, currency, img_links)
        products.append(product)
    return products


def searchWalmart(query, df_flag, currency):
    query = formatSearchQuery(query)
    URL = f"https://www.walmart.com/search?q={query}"
    page = httpsGet(URL)
    results = page.findAll("div", {"data-item-id": True})
    products = []
    pattern = re.compile(r"out of 5 Stars")
    for res in results:
        titles, prices, links = (
            res.select("span.lh-title"),
            res.select("div.lh-copy"),
            res.select("a")
        )
        ratings = res.findAll("span", {"class": "w_iUH7"}, text=pattern)
        num_ratings = res.findAll("span", {"class": "sans-serif gray f7"})
        trending = res.select("span.w_Cs")
        img_links = res.select("div.relative.overflow-hidden img")
        trending = trending[0] if trending else None
        product = formatResult("walmart", titles, prices, links, ratings,
                                num_ratings, trending, df_flag, currency, img_links)
        products.append(product)
    return products


def google_scraper(link):
    try:
        page = httpsGet(link)
        res = page.select('span.g9WBQb')[0].text
        return res
    except Exception as e:
        print(f'There was an error in scraping {link}, Error is {e}')
        return None


def walmart_scraper(link):
    try:
        page = httpsGet(link)
        res = page.select('span.inline-flex.flex-column span')[0].text
        pattern = r'(\$\s?\d+\.\d{2})'
        match = re.search(pattern, res)
        return match.group(1) if match else None
    except Exception as e:
        print(f'There was an error in scraping {link}, Error is {e}')
        return None


def ebay_scraper(link):
    try:
        page = httpsGet(link)
        res = page.select('div.x-price-primary span')[0].text
        pattern = r'\$\d+(\.\d{1,2})?'
        match = re.search(pattern, res)
        return match.group(1) if match else None
    except Exception as e:
        print(f'There was an error in scraping {link}, Error is {e}')
        return None


def bestbuy_scraper(link):
    try:
        page = httpsGet(link)
        res = page.select('div.priceView-hero-price.priceView-customer-price span')[0].text
        return res
    except Exception as e:
        print(f'There was an error in scraping {link}, Error is {e}')
        return None


def target_scraper(link):
    try:
        page = httpsGet(link)
        res = page.select('span.styles__CurrentPriceFontSize-sc-1mh0sjm-1.bksmYC')[0].text
        return res
    except Exception as e:
        print(f'There was an error in scraping {link}, Error is {e}')
        return None


def searchEtsy(query, df_flag, currency):
    query = formatSearchQuery(query)
    url = f"https://www.etsy.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9"
    }
    response = SESSION.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "lxml")
    products = []
    for item in soup.findAll(".wt-grid__item-xs-6"):
        links = item.select("a")
        if not links:
            continue
        titles = item.select("h3")
        prices = item.select(".currency-value")
        ratings_text = item.find("div", class_='wt-align-items-center wt-no-wrap')
        ratings, num_ratings = None, None
        if ratings_text:
            ratings, num_ratings = ratings_text.get_text().split()[:2]
        trending = item.select("span.wt-badge")[0] if item.select("span.wt-badge") else None
        product = formatResult("Etsy", titles, prices, links, ratings,
                                num_ratings, trending, df_flag, currency)
        products.append(product)
    return products


def searchGoogleShopping(query, df_flag, currency):
    query = formatSearchQuery(query)
    URL = f"https://www.google.com/search?tbm=shop&q={query}"
    page = httpsGet(URL)
    results = page.findAll("div", {"class": "sh-dgr__grid-result"})
    results1 = page.find_all()
    products = []
    pattern = re.compile(r"[0-9]+ product reviews")
    for i, res in enumerate(results):
        titles, prices, links = (
            res.select("h3"),
            res.select("span.a8Pemb"),
            res.select("a"),
        )
        ratings = res.findAll("span", {"class": "Rsc7Yb"})
        num_ratings = None
        ratings_number = res.find("span", {"class": "QIrs8"}).get_text()
        if ratings_number:
            match = re.search(r'(\d+,\d+)', ratings_number)
            if match:
                num_ratings = match.group(1)
        trending = res.select("span.Ib8pOd")
        img_links = results1[i].select("div.SirUVb.sh-img__image img")
        trending = trending[0] if trending else None
        product = formatResult("google", titles, prices, links, ratings,
                                num_ratings, trending, df_flag, currency, img_links)
        products.append(product)
    return products


def searchBJs(query, df_flag, currency):
    query = formatSearchQuery(query)
    URL = f"https://www.bjs.com/search/{query}"
    page = httpsGet(URL)
    results = page.findAll("div", {"class": "product"})
    products = []
    for res in results:
        titles, prices, links = (
            res.find("p", {"class": "no-select d-none auto-height"}),
            res.select("span.price"),
            res.select("a"),
        )
        ratings = res.findAll("span", {"class": "on"})
        num_ratings = res.select("span.prod-comments-count")
        trending = res.select("p.instantSavings")
        trending = trending[0] if trending else None
        product = formatResult("bjs", titles, prices, links, "", num_ratings,
                                trending, df_flag, currency)
        if ratings:
            product["rating"] = len(ratings)
        products.append(product)
    return products


def searchEbay(query, df_flag, currency):
    EBAY_APP = 'BradleyE-slash-PRD-2ddd2999f-2ae39cfa'
    try:
        api = Connection(appid=EBAY_APP, config_file=None, siteid='EBAY-US')
        response = api.execute('findItemsByKeywords', {'keywords': query})
    except Exception as e:
        print(e)
        return []
    data = response.dict()
    products = []
    for p in data['searchResult']['item']:
        titles = p['title']
        prices = '$' + p['sellingStatus']['currentPrice']['value']
        links = p['viewItemURL']
        img_link = p['galleryURL']
        ratings = None
        num_ratings = None
        trending = None
        product = formatResult("ebay", titles, prices, links, ratings,
                                num_ratings, trending, df_flag, currency, img_link)
        products.append(product)
    return products


def searchTarget(query, df_flag, currency):
    # Try the Target API first, but have fallbacks ready
    try:
        # First attempt with the API
        api_url = 'https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v1'
        page = '/s/' + query
        params = {
            'key': 'ff457966e64d5e877fdbad070f276d18ecec4a01',
            'channel': 'WEB',
            'count': '24',
            'default_purchasability_filter': 'false',
            'include_sponsored': 'true',
            'keyword': query,
            'offset': '0',
            'page': page,
            'platform': 'desktop',
            'pricing_store_id': '3991',
            'useragent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0',
            'visitor_id': 'AAA',
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache'
        }
        response = SESSION.get(api_url, headers=headers, params=params)
        
        # Check if we got rate limited (410 Gone or 429 Too Many Requests)
        if response.status_code in [410, 429]:
            print(f"Rate limited by Target API (status {response.status_code}). Using fallback scraping method.")
            raise Exception("Rate limited")
            
        # Check for other response errors
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code} from {api_url}")
            print(f"Response content: {response.text}")
            raise Exception(f"API error: {response.status_code}")
            
        # Parse the JSON response    
        data = response.json()
        
        # Extract product data
        products = []
        for p in data.get('data', {}).get('search', {}).get('products', []):
            titles = p['item']['product_description']['title']
            prices = '$' + str(p['price']['reg_retail'])
            links = p['item']['enrichment']['buy_url']
            img_link = p['item']['enrichment']['images']['primary_image_url']
            try:
                ratings = p['ratings_and_reviews']['statistics']['rating']['average']
            except KeyError:
                ratings = None
            try:
                num_ratings = p['ratings_and_reviews']['statistics']['rating']['count']
            except KeyError:
                num_ratings = None
            trending = None
            product = formatResult("target", titles, prices, links, ratings,
                                   num_ratings, trending, df_flag, currency, img_link)
            products.append(product)
        return products
        
    except Exception as e:
        # If the API call failed, try web scraping as fallback
        print(f"Target API error: {str(e)}. Attempting fallback using web scraping.")
        try:
            # Fallback to scraping the Target website directly
            query = formatSearchQuery(query)
            URL = f"https://www.target.com/s?searchTerm={query}"
            page = httpsGet(URL)
            
            # Extract products using HTML parsing
            products = []
            results = page.select("li[data-test='product-list-item']")
            
            for res in results:
                try:
                    title_elem = res.select_one("a[data-test='product-title']")
                    price_elem = res.select_one("span[data-test='current-price']")
                    
                    if not title_elem or not price_elem:
                        continue
                        
                    title = title_elem.text.strip()
                    price = price_elem.text.strip()
                    link = "https://www.target.com" + title_elem.get("href", "")
                    
                    # Try to get image
                    img_elem = res.select_one("img")
                    img_link = img_elem.get("src", "") if img_elem else ""
                    
                    product = {
                        "title": title,
                        "price": price,
                        "link": link,
                        "rating": None,  # Ratings are harder to get from HTML
                        "num_ratings": None,
                        "website": "target",
                        "image_url": img_link
                    }
                    
                    if df_flag:
                        if product["price"] and product["price"].startswith("$"):
                            try:
                                product["price_float"] = float(product["price"][1:].replace(",", ""))
                            except:
                                product["price_float"] = 0
                    
                    products.append(product)
                except Exception as item_error:
                    print(f"Error parsing Target product: {str(item_error)}")
                    continue
                    
            return products
            
        except Exception as scrape_error:
            print(f"Target fallback scraping also failed: {str(scrape_error)}")
            # Return empty list on total failure
            return []


def searchBestbuy(query, df_flag, currency):
    query = formatSearchQuery(query)
    URL = f"https://www.bestbuy.com/site/searchpage.jsp?st={query}"
    page = httpsGet(URL)
    results = page.findAll("li", {'class': 'sku-item'})
    products = []
    pattern = re.compile(r"out of 5 stars with")
    for res in results:
        titles, prices, links = (
            res.select("h4.sku-title a"),
            res.select("div.priceView-customer-price span"),
            res.select("a"),
        )
        ratings = res.find("div", class_="c-ratings-reviews").findAll("p", text=pattern)
        num_ratings = res.select("span.c-reviews")
        trending = None
        img_link = res.select("img.product-image")
        product = formatResult("bestbuy", titles, prices, links, ratings,
                                num_ratings, trending, df_flag, currency, img_link)
        products.append(product)
    return products


def condense_helper(result_condensed, lst, num):
    """Helper function to limit number of entries in the result."""
    for p in lst:
        if num is not None and len(result_condensed) >= int(num):
            break
        else:
            if p["title"] is not None and p["title"] != "":
                result_condensed.append(p)


def filter(data, price_min=None, price_max=None, rating_min=None):
    filtered_result = []
    for row in data:
        try:
            price = float(row['price'][1:])
        except:
            price = None
        try:
            rating = float(row['rating'])
        except:
            rating = None
        if price_min is not None and (price is None or price < price_min):
            continue
        elif price_max is not None and (price is None or price > price_max):
            continue
        elif rating_min is not None and (rating is None or rating < rating_min):
            continue
        else:
            filtered_result.append(row)
    return filtered_result


def driver(product, currency, num=None, df_flag=0, csv=False, cd=None, ui=False, sort=None):
    """
    Returns CSV if the user enters the --csv arg,
    else displays the result table in the terminal based on the args entered by the user.
    This version uses ThreadPoolExecutor with a global requests.Session for faster concurrent scraping.
    """
    # Initialize results container for each source
    results = [[] for _ in range(8)]
    
    # Define a wrapper function to handle exceptions in each scraper
    def safe_search(search_func, product, df_flag, currency, index):
        try:
            results[index] = search_func(product, df_flag, currency)
        except Exception as e:
            print(f"Error in {search_func.__name__}: {str(e)}")
            results[index] = []  # Empty list on failure
    
    # Launch all scrapers in parallel
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = []
        futures.append(executor.submit(safe_search, searchAmazon, product, df_flag, currency, 0))
        futures.append(executor.submit(safe_search, searchWalmart, product, df_flag, currency, 1))
        futures.append(executor.submit(safe_search, searchEtsy, product, df_flag, currency, 2))
        futures.append(executor.submit(safe_search, searchGoogleShopping, product, df_flag, currency, 3))
        futures.append(executor.submit(safe_search, searchBJs, product, df_flag, currency, 4))
        futures.append(executor.submit(safe_search, searchEbay, product, df_flag, currency, 5))
        futures.append(executor.submit(safe_search, searchBestbuy, product, df_flag, currency, 6))
        futures.append(executor.submit(safe_search, searchTarget, product, df_flag, currency, 7))
        
        # Wait for all futures to complete
        for future in futures:
            try:
                future.result()  # This will re-raise any exceptions from the thread
            except Exception as e:
                print(f"Error in scraper thread: {str(e)}")

    # Check if we have any results at all
    total_results = sum(len(r) for r in results)
    if total_results == 0:
        print("Warning: No results found from any source. Check your search query or network connectivity.")
    else:
        print(f"Found a total of {total_results} results across all sources")

    if not ui:
        all_results = []
        result_condensed = []
        for product_list in results:
            all_results.extend(product_list)
            if num is not None:
                result_condensed.extend(product_list[:num])
            else:
                result_condensed.extend(product_list)
        
        # Make sure we have results before creating DataFrames
        if not result_condensed:
            print("No results to display")
            return pd.DataFrame()  # Return empty DataFrame
            
        result_condensed = pd.DataFrame.from_dict(result_condensed, orient="columns")
        all_results = pd.DataFrame.from_dict(all_results, orient="columns")
        if not currency:
            result_condensed = result_condensed.drop(columns="converted_price", errors='ignore')
            all_results = all_results.drop(columns="converted_price", errors='ignore')
        if csv:
            file_name = os.path.join(cd, product + datetime.now().strftime("%y%m%d_%H%M") + ".csv")
            print("CSV Saved at: ", cd)
            print("File Name:", file_name)
            all_results.to_csv(file_name, index=False, header=all_results.columns)
        return result_condensed
    else:
        result_condensed = []
        for i in range(8):
            condense_helper(result_condensed, results[i], num)
            
        # Make sure we have results
        if not result_condensed:
            print("No results to display")
            return []
            
        if currency is not None:
            for p in result_condensed:
                p["price"] = getCurrency(currency, p["price"])
        for p in result_condensed:
            link = p["link"]
            if p["website"] == "Etsy":
                link = link[12:]
                p["link"] = link
            elif "http" not in link:
                p["link"] = "http://" + link
        if sort is not None:
            result_condensed = pd.DataFrame(result_condensed)
            if sort == "rades":
                result_condensed = sortList(result_condensed, "ra", False)
            elif sort == "raasc":
                result_condensed = sortList(result_condensed, "ra", True)
            elif sort == "pasc":
                result_condensed = sortList(result_condensed, "pr", False)
            else:
                result_condensed = sortList(result_condensed, "pr", True)
            result_condensed = result_condensed.to_dict(orient="records")
        if csv:
            file_name = os.path.join(cd, product + datetime.now().strftime("%y%m%d_%H%M") + ".csv")
            result_condensed = pd.DataFrame(result_condensed)
            result_condensed.to_csv(file_name, index=False, header=result_condensed.columns)
            print(result_condensed)
        return result_condensed
#