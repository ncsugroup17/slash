"""
Copyright (C) 2021 SE Slash - All Rights Reserved
You may use, distribute and modify this code under the
terms of the MIT license.
You should have received a copy of the MIT license with
this file. If not, please write to: secheaper@gmail.com
"""

"""
The scraper module holds functions that actually scrape the e-commerce websites
"""

import requests
from .formatter import formatSearchQuery,formatResult,getCurrency,sortList
from bs4 import BeautifulSoup
import re
import csv
import pandas as pd
import os
from datetime import datetime
from ebaysdk.finding import Connection

def httpsGet(URL):
    """
    The httpsGet function makes HTTP called to the requested URL with custom headers
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',  # noqa: E501
        'Accept-Encoding': 'gzip, deflate',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'no-cache'
    }
    s = requests.Session()
    page = s.get(URL, headers=headers, allow_redirects=False)
    soup1 = BeautifulSoup(page.content, "html.parser")
    return BeautifulSoup(soup1.prettify(), "html.parser")


def searchAmazon(query, df_flag, currency):
    """
    The searchAmazon function scrapes amazon.com
    Parameters: query- search query for the product, df_flag- flag variable, currency- currency type entered by the user
    Returns a list of items available on Amazon.com that match the product entered by the user.
    """
    query = formatSearchQuery(query)
    URL = f"https://www.amazon.com/s?k={query}"
    page = httpsGet(URL)
    results = page.findAll("div", {"data-component-type": "s-search-result"})
    products = []
    for res in results:
        titles, prices, links = (
            res.select("h2 a span"),
            res.select("span.a-price span"),
            res.select("h2 a.a-link-normal"),
        )
        ratings = res.select("span.a-icon-alt")
        num_ratings = res.select("span.a-size-base")
        trending = res.select("span.a-badge-text")
        img_links = res.select("img.s-image")

        if len(trending) > 0:
            trending = trending[0]
        else:
            trending = None
        product = formatResult(
            "amazon",
            titles,
            prices,
            links,
            ratings,
            num_ratings,
            trending,
            df_flag,
            currency,
            img_links
        )
        products.append(product)
    return products



def searchWalmart(query, df_flag, currency):
    """
    The searchWalmart function scrapes walmart.com
    Parameters: query- search query for the product, df_flag- flag variable, currency- currency type entered by the user
    Returns a list of items available on walmart.com that match the product entered by the user
    """
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
            res.select("a"),
        )
        ratings = res.findAll("span", {"class": "w_iUH7"}, text=pattern)
        num_ratings = res.findAll("span", {"class": "sans-serif gray f7"})
        trending = res.select("span.w_Cs")
        img_links = res.select("div.relative.overflow-hidden img")
        if len(trending) > 0:
            trending = trending[0]
        else:
            trending = None
        product = formatResult(
            "walmart",
            titles,
            prices,
            links,
            ratings,
            num_ratings,
            trending,
            df_flag,
            currency,
            img_links
        )
        products.append(product)
    return products

def amazon_scraper(link):
    try:
        page = httpsGet(link)

        whole_price = page.select('span.a-price-whole')[0].text.strip()
        numeric_value = re.search(r'\b\d+\b',whole_price)
        if numeric_value:
            numeric_value = numeric_value.group()
            res = page.select('span.a-price-symbol')[0].text.strip() + numeric_value + '.' + page.select('span.a-price-fraction')[0].text.strip()
            return res
        else:
            return None
    
    except Exception as e:
        print(f'There was an error in scraping {link}, Error is {e}')
        return None
    
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
        if match:
            return match.group(1)
        else:
            return None
    except Exception as e:
        print(f'There was an error in scraping {link}, Error is {e}')
        return None

def ebay_scraper(link):
    try:
        page = httpsGet(link)

        res = page.select('div.x-price-primary span')[0].text
        pattern = r'\$\d+(\.\d{1,2})?'
        match = re.search(pattern, res)
        if match:
            return match.group(1)
        else:
            return None
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
    """
    The searchEtsy function scrapes Etsy.com
    Parameters: query- search query for the product, df_flag- flag variable, currency- currency type entered by the user
    Returns a list of items available on Etsy.com that match the product entered by the user
    """
    query = formatSearchQuery(query)
    url = f"https://www.etsy.com/search?q={query}"
    products = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "lxml")
    for item in soup.findAll(".wt-grid__item-xs-6"):
        str = item.select("a")
        if str == []:
            continue
        else:
            links = str

        ratings=None
        num_ratings=None
       
        titles, prices = (item.select("h3")), (item.select(".currency-value"))
        ratings_text = item.find("div",class_='wt-align-items-center wt-max-height-full wt-display-flex-xs flex-direction-row-xs wt-text-title-small wt-no-wrap')
        
        if ratings_text:
            ratings = ratings_text.get_text().split()[0]
            num_ratings = ratings_text.get_text().split()[1]
        
        trending = item.select("span.wt-badge")
        if len(trending) > 0:
            trending = trending[0]
        else:
            trending = None
        product = formatResult(
            "Etsy",
            titles,
            prices,
            links,
            ratings,
            num_ratings,
            trending,
            df_flag,
            currency,
        )
        products.append(product)
    
    return products


def searchGoogleShopping(query, df_flag, currency):
    """
    The searchGoogleShopping function scrapes https://shopping.google.com/
    Parameters: query- search query for the product, df_flag- flag variable, currency- currency type entered by the user
    Returns a list of items available on shopping.google.com that match the product entered by the user
    """
    query = formatSearchQuery(query)
    URL = f"https://www.google.com/search?tbm=shop&q={query}"
    page = httpsGet(URL)
    results = page.findAll("div", {"class": "sh-dgr__grid-result"})
    results1 = page.find_all()
    products = []
    pattern = re.compile(r"[0-9]+ product reviews")
    for i,res in enumerate(results):
        titles, prices, links = (
            res.select("h3"),
            res.select("span.a8Pemb"),
            res.select("a"),
        )
        ratings = res.findAll("span", {"class": "Rsc7Yb"})
        num_ratings=None
        ratings_number = res.find("span", {"class": "QIrs8"}).get_text()
        if ratings_number:
            match = re.search(r'(\d+,\d+)', ratings_number)
            if match:
                num_ratings = match.group(1)
        trending = res.select("span.Ib8pOd")
        img_links = results1[i].select("div.SirUVb.sh-img__image img")
        if len(trending) > 0:
            trending = trending[0]
        else:
            trending = None
        product = formatResult(
            "google",
            titles,
            prices,
            links,
            ratings,
            num_ratings,
            trending,
            df_flag,
            currency,
            img_links
        )
        products.append(product)
    return products


def searchBJs(query, df_flag, currency):
    """
    The searchBJs function scrapes https://www.bjs.com/
    Parameters: query- search query for the product, df_flag- flag variable, currency- currency type entered by the user
    Returns a list of items available on bjs.com that match the product entered by the user
    """
    query = formatSearchQuery(query)
    URL = f"https://www.bjs.com/search/{query}"
    page = httpsGet(URL)
    # print("page", URL)
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
        if len(trending) > 0:
            trending = trending[0]
        else:
            trending = None
        product = formatResult(
            "bjs", titles, prices, links, "", num_ratings, trending, df_flag, currency
        )
        if len(ratings) != 0:
            product["rating"] = len(ratings)
        products.append(product)
    return products

def searchEbay(query, df_flag, currency):
    """
    The searchEbay function scrapes https://www.ebay.com/
    Parameters: query- search query for the product, df_flag- flag variable, currency- currency type entered by the user
    Returns a list of items available on ebay.com that match the product entered by the user
    """
    EBAY_APP = 'BradleyE-slash-PRD-2ddd2999f-2ae39cfa'

    try:
        api = Connection(appid=EBAY_APP, config_file=None, siteid='EBAY-US')
        response = api.execute('findItemsByKeywords', {'keywords': query})
    except ConnectionError as e:
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
        
        product = formatResult(
            "ebay",
            titles,
            prices,
            links,
            ratings,
            num_ratings,
            trending,
            df_flag,
            currency,
            img_link
        )
        products.append(product)

    return products

import requests

def searchTarget(query, df_flag, currency):
    """
    The searchTarget function scrapes https://www.target.com/
    Parameters: query- search query for the product, df_flag- flag variable, currency- currency type entered by the user
    Returns a list of items available on target.com that match the product entered by the user
    """

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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',  # noqa: E501
        'Accept-Encoding': 'gzip, deflate',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'no-cache'
    }

    # Make the request
    response = requests.get(api_url, headers=headers, params=params)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code} from {api_url}")
        print(f"Response content: {response.text}")  # Log the response content for debugging
        return []

    # Try to parse the response as JSON
    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"Error: Unable to parse JSON response from {api_url}")
        print(f"Response content: {response.text}")  # Log the response content for debugging
        return []

    # Process the data and build the product list
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
    
        product = formatResult(
            "target",
            titles,
            prices,
            links,
            ratings,
            num_ratings,
            trending,
            df_flag,
            currency,
            img_link
        )
        products.append(product)

    return products


def searchBestbuy(query, df_flag, currency):
    """
    The searchBestbuy function scrapes bestbuy.com
    Parameters: query- search query for the product, df_flag- flag variable, currency- currency type entered by the user
    Returns a list of items available on bestbuy.com that match the product entered by the user
    """
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
        product = formatResult(
            "bestbuy",
            titles,
            prices,
            links,
            ratings,
            num_ratings,
            trending,
            df_flag,
            currency,
            img_link
        )
        products.append(product)

    return products


def condense_helper(result_condensed, list, num):
    """This is a helper function to limit number of entries in the result"""
    for p in list:
        if num != None and len(result_condensed) >= int(num):
            break
        else:
            if p["title"] != None and p["title"] != "":
                result_condensed.append(p)

def filter(data, price_min = None, price_max = None, rating_min = None):
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

def driver(
    product, currency, num=None, df_flag=0, csv=False, cd=None, ui=False, sort=None
):
    """Returns csv is the user enters the --csv arg,
    else will display the result table in the terminal based on the args entered by the user"""

    products_1 = searchAmazon(product, df_flag, currency)
    products_2 = searchWalmart(product, df_flag, currency)
    products_3 = searchEtsy(product, df_flag, currency)
    products_4 = searchGoogleShopping(product, df_flag, currency)
    products_5 = searchBJs(product, df_flag, currency)
    products_6 = searchEbay(product,df_flag,currency)
    products_7 = searchBestbuy(product,df_flag,currency)
    products_8 = searchTarget(product,df_flag,currency)

    result_condensed = ""
    if not ui:
        results = products_1 + products_2 + products_3 + products_4 + products_5 + products_6 + products_7 + products_8
        result_condensed = (
            products_1[:num]
            + products_2[:num]
            + products_3[:num]
            + products_4[:num]
            + products_5[:num]
            + products_6[:num]
            + products_7[:num]
            + products_8[:num]
        )
        result_condensed = pd.DataFrame.from_dict(result_condensed, orient="columns")
        results = pd.DataFrame.from_dict(results, orient="columns")
        if currency == "" or currency == None:
            results = results.drop(columns="converted_price")
            result_condensed = result_condensed.drop(columns="converted_price")
        if csv == True:
            file_name = os.path.join(
                cd, (product + datetime.now().strftime("%y%m%d_%H%M") + ".csv")
            )
            print("CSV Saved at: ", cd)
            print("File Name:", file_name)
            results.to_csv(file_name, index=False, header=results.columns)
    else:
        result_condensed = []
        condense_helper(result_condensed, products_1, num)
        condense_helper(result_condensed, products_2, num)
        condense_helper(result_condensed, products_3, num)
        condense_helper(result_condensed, products_4, num)
        condense_helper(result_condensed, products_5, num)
        condense_helper(result_condensed, products_6, num)
        condense_helper(result_condensed, products_7, num)
        condense_helper(result_condensed, products_8, num)

        if currency != None:
            for p in result_condensed:
                p["price"] = getCurrency(currency, p["price"])

        # Fix URLs so that they contain http before www
        for p in result_condensed:
            link = p["link"]
            if p["website"] == "Etsy":
                link = link[12:]
                p["link"] = link
            elif "http" not in link:
                link = "http://" + link
                p["link"] = link

        if sort != None:
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
            file_name = os.path.join(
                cd, (product + datetime.now().strftime("%y%m%d_%H%M") + ".csv")
            )
            result_condensed = pd.DataFrame(result_condensed)
            
            result_condensed = result_condensed.to_csv(
                file_name, index=False, header=result_condensed.columns
            )
            print(result_condensed)
    return result_condensed
