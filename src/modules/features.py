"""
Copyright (C) 2023 SE23-Team44

Licensed under the MIT License.
See the LICENSE file in the project root for the full license information.
"""

import os
import pandas as pd
import re
import ssl
import smtplib
from pathlib import Path
from email.message import EmailMessage
import csv
from .config import Config
from . import scraper

# Define the path for user profiles and their wishlists
users_main_dir = Path(__file__).parent.parent / "users"
users_main_dir.mkdir(parents=True, exist_ok=True)

# Helper function to get user directory path
def usr_dir(email):
    return users_main_dir / email


# User Management Functions

def create_user(email, password=None, name=None):
    """
    Creates a new user directory and initializes user credentials.
    """
    user_dir = usr_dir(email)
    cred_file = user_dir / "cred.csv"
    default_file = user_dir / "default.csv"

    # Create user directory if it doesn’t exist
    os.makedirs(user_dir, exist_ok=True)

    # Initialize cred.csv with user info if it doesn’t exist
    if not cred_file.exists():
        with open(cred_file, mode="w", newline="") as csvfile:
            fieldnames = ["email", "name"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({"email": email, "name": name})

    # Create an empty default.csv for wishlist if it doesn’t exist
    if not default_file.exists():
        with open(default_file, mode="w", newline="") as csvfile:
            csvfile.write("")


def check_user(email, password=None):
    """
    Checks if the user exists by verifying the presence of cred.csv.
    """
    cred_file = usr_dir(email) / "cred.csv"
    return cred_file.exists()


# Wishlist Functions

def create_wishlist(email, wishlist_name):
    """
    Creates a new wishlist file for the user.
    """
    wishlist_path = usr_dir(email) / f"{wishlist_name}.csv"
    open(wishlist_path, "a").close()


def list_wishlists(email):
    """
    Lists all wishlists for a user.
    """
    user_dir = usr_dir(email)
    wishlists = [
        wishlist.replace(".csv", "") for wishlist in os.listdir(user_dir)
        if wishlist.endswith(".csv")
    ]
    return wishlists


def delete_wishlist(email, wishlist_name):
    """
    Deletes a specified wishlist file for the user.
    """
    wishlist_path = usr_dir(email) / f"{wishlist_name}.csv"
    wishlist_path.unlink(missing_ok=True)


def wishlist_add_item(email, wishlist_name, item_data):
    """
    Adds an item to a user's wishlist.
    """
    wishlist_path = usr_dir(email) / f"{wishlist_name}.csv"
    if isinstance(item_data, dict):
        item_data = pd.DataFrame([item_data])

    if wishlist_path.exists() and wishlist_path.stat().st_size > 0:
        old_data = pd.read_csv(wishlist_path)
    else:
        old_data = pd.DataFrame()

    final_data = pd.concat([old_data, item_data])
    final_data.to_csv(wishlist_path, index=False, header=item_data.columns)


def read_wishlist(email, wishlist_name):
    """
    Reads items from a user's wishlist and updates their prices.
    """
    wishlist_path = usr_dir(email) / f"{wishlist_name}.csv"
    if wishlist_path.exists():
        try:
            csv_data = pd.read_csv(wishlist_path)
            for index, row in csv_data.iterrows():
                new_price = update_price(row['link'], row['website'], row['price'])
                csv_data.at[index, 'price'] = new_price
            return csv_data
        except Exception:
            return pd.DataFrame()
    return None


def wishlist_remove_list(email, wishlist_name, index):
    """
    Removes an item from a user's wishlist by index.
    """
    wishlist_path = usr_dir(email) / f"{wishlist_name}.csv"
    old_data = read_wishlist(email, wishlist_name)
    if old_data is not None:
        old_data = old_data.drop(index=index)
        old_data.to_csv(wishlist_path, index=False, header=old_data.columns)


# Email and Price Update Functions

def share_wishlist(email_sender, wishlist_name, email_receiver):
    """
    Sends a user's wishlist via email to a specified recipient.
    """
    wishlist_path = usr_dir(email_sender) / f"{wishlist_name}.csv"
    if wishlist_path.exists():
        try:
            email_password = Config.EMAIL_PASS
            subject = f'Slash wishlist of {email_sender}'
            df = pd.read_csv(wishlist_path)
            links_list = df['link'].astype(str).str.cat(sep=' ')
            body = "\n".join([
                f"{i}. {link}" for i, link in enumerate(links_list.split(), start=1)
            ])

            em = EmailMessage()
            em['From'] = email_sender
            em['To'] = email_receiver
            em['Subject'] = subject
            em.set_content(body)

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, email_receiver, em.as_string())

        except Exception:
            return 'Failed to send email'
    return None


def find_currency(price):
    """
    Helper function to detect currency from a price string.
    """
    currency = re.match(r'^[a-zA-Z]{3,5}', price)
    return currency.group() if currency else None


def update_price(link, website, price):
    """
    Updates the price of an item by scraping the respective website.
    """
    currency = find_currency(price)
    updated_price = price

    # Update price using scraper based on website
    scraped_price = None
    if website == "amazon":
        scraped_price = scraper.amazon_scraper(link).strip()
    elif website == "google":
        scraped_price = scraper.google_scraper(link).strip()
    elif website == "walmart":
        scraped_price = scraper.walmart_scraper(link).strip()
    elif website == "ebay":
        scraped_price = scraper.ebay_scraper(link).strip()
    elif website == "bestbuy":
        scraped_price = scraper.bestbuy_scraper(link).strip()
    elif website == "target":
        scraped_price = scraper.target_scraper(link).strip()

    if scraped_price:
        updated_price = (
            scraper.getCurrency(currency, scraped_price) if currency else scraped_price
        )

    return updated_price
