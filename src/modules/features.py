# """
# Copyright (C) 2023 SE23-Team44
 
# Licensed under the MIT License.
# See the LICENSE file in the project root for the full license information.
# """

import json
import os
import pandas as pd
import numpy as np
import re
import ssl
import smtplib
from pathlib import Path
from .config import Config
import sqlite3
from . import scraper
from email.message import EmailMessage
import csv


# path for user profiles and their wish lists
users_main_dir = Path(__file__).parent.parent / "users"
users_main_dir.mkdir(parents=True, exist_ok=True)

def usr_dir(username):
    return users_main_dir / username

def create_user(email, password=None, name=None):
    user_dir = f"slash/src/users/{email}"
    cred_file = os.path.join(user_dir, "cred.csv")
    default_file = os.path.join(user_dir, "default.csv")

    # Create user directory if it doesn’t exist
    os.makedirs(user_dir, exist_ok=True)

    # Create and populate cred.csv if it doesn’t exist
    if not os.path.exists(cred_file):
        with open(cred_file, mode="w", newline="") as csvfile:
            fieldnames = ["email", "name"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({"email": email, "name": name})

    # Create an empty default.csv if it doesn’t exist
    if not os.path.exists(default_file):
        with open(default_file, mode="w", newline="") as csvfile:
            csvfile.write("")  # Empty file
    
def check_user(username, password):
    user_dir = usr_dir(username)
    if os.path.exists(user_dir): # user already exist
        if password == get_credentials(username):
            return True
        else:
            return False
    else: # create new user
        return False

# # features.py

def check_user(email, password=None):
    # Define the path to the user's directory and credential file
    user_dir = f"slash/src/users/{email}"
    cred_file = os.path.join(user_dir, "cred.csv")
    
    # Check if the user's credential file exists
    return os.path.exists(cred_file)

def list_users():
    ls = os.listdir(users_main_dir)
    list_of_users = list(filter(lambda u: os.path.isdir(os.path.join(users_main_dir, u)), ls))
    return list_of_users

def create_wishlist(username, wishlist_name):
    wishlist_path = usr_dir(username) / (wishlist_name + ".csv")
    open(wishlist_path, "a").close()
def create_wishlist(username, wishlist_name):
    wishlist_path = usr_dir(username) / (wishlist_name + ".csv")
    open(wishlist_path, "a").close()

def create_credentials(username, password):
    cred_path = usr_dir(username) / ("cred.csv")
    open(cred_path, "a").close()
    item_data = {
        "username": username,
        "password": password,
    }
    item_data = pd.DataFrame([item_data])
    item_data.to_csv(cred_path, index=False, header=item_data.columns)
def create_credentials(username, password):
    cred_path = usr_dir(username) / ("cred.csv")
    open(cred_path, "a").close()
    item_data = {
        "username": username,
        "password": password,
    }
    item_data = pd.DataFrame([item_data])
    item_data.to_csv(cred_path, index=False, header=item_data.columns)

def get_credentials(username):
    cred_path = usr_dir(username) / ("cred.csv")
    if os.path.exists(cred_path):
        try:
            csv = pd.read_csv(cred_path)
            row = csv.iloc[0]
            return str(row['password'])
        except Exception:
            return ''
    else:
        return '' 
def get_credentials(username):
    cred_path = usr_dir(username) / ("cred.csv")
    if os.path.exists(cred_path):
        try:
            csv = pd.read_csv(cred_path)
            row = csv.iloc[0]
            return str(row['password'])
        except Exception:
            return ''
    else:
        return '' 

def list_wishlists(username):
    user_dir = usr_dir(username)
    wishlists = list(map(lambda w: w.replace(".csv", ""), os.listdir(user_dir)))
    return wishlists
def list_wishlists(username):
    user_dir = usr_dir(username)
    wishlists = list(map(lambda w: w.replace(".csv", ""), os.listdir(user_dir)))
    return wishlists

def delete_wishlist(username, wishlist_name):
    wishlist_path = usr_dir(username) / (wishlist_name + ".csv")
    wishlist_path.unlink(missing_ok=True)
def delete_wishlist(username, wishlist_name):
    wishlist_path = usr_dir(username) / (wishlist_name + ".csv")
    wishlist_path.unlink(missing_ok=True)

def wishlist_add_item(username, wishlist_name, item_data):
    if isinstance(item_data, dict):
        item_data = pd.DataFrame([item_data])
    wishlist_path = usr_dir(username) / (wishlist_name + ".csv")
    if os.path.exists(wishlist_path) and (os.path.getsize(wishlist_path) > 0 ):
        old_data = pd.read_csv(wishlist_path)
    else:
        old_data = pd.DataFrame()
    #if self.df.title[indx] not in old_data:
    final_data = pd.concat([old_data, item_data])
    final_data.to_csv(wishlist_path, index=False, header=item_data.columns)
def wishlist_add_item(username, wishlist_name, item_data):
    if isinstance(item_data, dict):
        item_data = pd.DataFrame([item_data])
    wishlist_path = usr_dir(username) / (wishlist_name + ".csv")
    if os.path.exists(wishlist_path) and (os.path.getsize(wishlist_path) > 0 ):
        old_data = pd.read_csv(wishlist_path)
    else:
        old_data = pd.DataFrame()
    #if self.df.title[indx] not in old_data:
    final_data = pd.concat([old_data, item_data])
    final_data.to_csv(wishlist_path, index=False, header=item_data.columns)

def read_wishlist(username, wishlist_name):
    wishlist_path = usr_dir(username) / (wishlist_name + ".csv")
    if os.path.exists(wishlist_path):
        try:
            csv = pd.read_csv(wishlist_path)
            for index,obj in csv.iterrows():
                new_price = update_price(obj['link'],obj['website'],obj['price'])
                csv.at[index, 'price'] = new_price
            return csv
        except Exception:
            return pd.DataFrame()
    else:
        return None # wishlist not found

def share_wishlist(username, wishlist_name, email_receiver):
    wishlist_path = usr_dir(username) / (wishlist_name + ".csv")
    if os.path.exists(wishlist_path):
        try:
            email_sender = 'slash.se23@gmail.com'
            email_password = Config.EMAIL_PASS

            subject = ' slash wishlist of ' + username
            subject = ' slash wishlist of ' + username

            df = pd.read_csv(wishlist_path)
            links_list = df['link'].astype(str).str.cat(sep=' ')
            body = "\n".join([f"{i}. {link}" for i, link in enumerate(links_list.split(), start=1)])
            df = pd.read_csv(wishlist_path)
            links_list = df['link'].astype(str).str.cat(sep=' ')
            body = "\n".join([f"{i}. {link}" for i, link in enumerate(links_list.split(), start=1)])

            em = EmailMessage()
            em['from'] = email_sender
            em['to'] = email_receiver
            em['subject'] = subject
            em.set_content(body)
            em = EmailMessage()
            em['from'] = email_sender
            em['to'] = email_receiver
            em['subject'] = subject
            em.set_content(body)
            

            context = ssl.create_default_context()
            context = ssl.create_default_context()

            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, email_receiver, em.as_string())
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, email_receiver, em.as_string())

        except Exception:
            return 'failed to send email'
    else:
        return None # wishlist not found
       

def wishlist_remove_list(username, wishlist_name, indx):
    wishlist_path = usr_dir(username) / (wishlist_name + ".csv")
    old_data = read_wishlist(username, wishlist_name)
    old_data = old_data.drop(index=indx)
    old_data.to_csv(wishlist_path, index=False, header=old_data.columns)
def wishlist_remove_list(username, wishlist_name, indx):
    wishlist_path = usr_dir(username) / (wishlist_name + ".csv")
    old_data = read_wishlist(username, wishlist_name)
    old_data = old_data.drop(index=indx)
    old_data.to_csv(wishlist_path, index=False, header=old_data.columns)

def find_currency(price):
    currency = re.match(r'^[a-zA-Z]{3,5}', price)
    return currency.group() if currency else currency

def update_price(link,website,price):
    currency = find_currency(price)
    updated_price = price
    if website == "amazon":
        scraped_price = scraper.amazon_scraper(link).strip()
        if scraped_price:
            updated_price = scraper.getCurrency(currency,scraped_price) if currency is not None else scraped_price
    if website == "google":
        scraped_price = scraper.google_scraper(link).strip()
        if scraped_price:
            updated_price = scraper.getCurrency(currency,scraped_price) if currency is not None else scraped_price
    if website == "BJS":
        pass
    if website == "Etsy":
        pass
    if website == "walmart":
        scraped_price = scraper.walmart_scraper(link).strip()
        if scraped_price:
            updated_price = scraper.getCurrency(currency,scraped_price) if currency is not None else scraped_price
    if website == "ebay":
        scraped_price = scraper.ebay_scraper(link).strip()
        if scraped_price:
            updated_price = scraper.getCurrency(currency,scraped_price) if currency is not None else scraped_price
    if website == "bestbuy":
        scraped_price = scraper.bestbuy_scraper(link).strip()
        if scraped_price:
            updated_price = scraper.getCurrency(currency,scraped_price) if currency is not None else scraped_price       
    if website == "target":
        scraped_price = scraper.target_scraper(link).strip()
        if scraped_price:
            updated_price = scraper.getCurrency(currency,scraped_price) if currency is not None else scraped_price      
    return updated_price

"""
Copyright (C) 2023 SE23-Team44

Licensed under the MIT License.
See the LICENSE file in the project root for the full license information.
"""

import os
import pandas as pd
from pathlib import Path
import csv
from .config import Config
import smtplib
from email.message import EmailMessage
import ssl
import re
from . import scraper

# Define the path for user profiles and their wishlists
users_main_dir = Path(__file__).parent.parent / "users"
users_main_dir.mkdir(parents=True, exist_ok=True)

# Function to get user directory path
def usr_dir(email):
    return users_main_dir / email

# Create a user directory and initialize files if needed
def create_user(email, password=None, name=None):
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
            csvfile.write("")  # Empty file to represent an empty wishlist

# Check if the user exists by verifying the presence of cred.csv
def check_user(email, password=None):
    cred_file = usr_dir(email) / "cred.csv"
    return cred_file.exists()

def wishlist_add_item(email, wishlist_name, item_data):
    wishlist_path = usr_dir(email) / f"{wishlist_name}.csv"
    print(f"Adding item to wishlist at: {wishlist_path}")  # Debug statement
    
    if isinstance(item_data, dict):
        item_data = pd.DataFrame([item_data])
    
    # Load existing data if wishlist file exists, else create new
    if wishlist_path.exists() and wishlist_path.stat().st_size > 0:
        old_data = pd.read_csv(wishlist_path)
        print("Existing wishlist data found")  # Debug statement
    else:
        old_data = pd.DataFrame()
        print("No existing data, creating new wishlist file")  # Debug statement

    # Append new item data and save
    final_data = pd.concat([old_data, item_data])
    final_data.to_csv(wishlist_path, index=False, header=item_data.columns)
    print("Item added to wishlist and saved.")  # Debug statement


# Read items from a user's wishlist
def read_wishlist(email, wishlist_name):
    wishlist_path = usr_dir(email) / f"{wishlist_name}.csv"
    if wishlist_path.exists():
        try:
            csv_data = pd.read_csv(wishlist_path)
            # Update prices for each item
            for index, row in csv_data.iterrows():
                new_price = update_price(row['link'], row['website'], row['price'])
                csv_data.at[index, 'price'] = new_price
            return csv_data
        except Exception:
            return pd.DataFrame()  # Return empty DataFrame on error
    else:
        return None  # Wishlist not found

# Send wishlist via email to a specified recipient
def share_wishlist(email_sender, wishlist_name, email_receiver):
    wishlist_path = usr_dir(email_sender) / f"{wishlist_name}.csv"
    if wishlist_path.exists():
        try:
            email_password = Config.EMAIL_PASS
            subject = f'Slash wishlist of {email_sender}'
            df = pd.read_csv(wishlist_path)
            links_list = df['link'].astype(str).str.cat(sep=' ')
            body = "\n".join([f"{i}. {link}" for i, link in enumerate(links_list.split(), start=1)])

            # Set up the email
            em = EmailMessage()
            em['From'] = email_sender
            em['To'] = email_receiver
            em['Subject'] = subject
            em.set_content(body)

            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, email_receiver, em.as_string())

        except Exception:
            return 'Failed to send email'
    else:
        return None  # Wishlist not found

# Remove an item from the wishlist by index
def wishlist_remove_list(email, wishlist_name, index):
    wishlist_path = usr_dir(email) / f"{wishlist_name}.csv"
    old_data = read_wishlist(email, wishlist_name)
    if old_data is not None:
        old_data = old_data.drop(index=index)
        old_data.to_csv(wishlist_path, index=False, header=old_data.columns)

# Helper function to detect currency from price string
def find_currency(price):
    currency = re.match(r'^[a-zA-Z]{3,5}', price)
    return currency.group() if currency else None

# Update the price of an item by scraping the respective website
def update_price(link, website, price):
    currency = find_currency(price)
    updated_price = price
    # Update price using scraper based on website
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
    else:
        scraped_price = None  # Website not handled

    # Convert and update price if scraped price exists
    if scraped_price:
        updated_price = scraper.getCurrency(currency, scraped_price) if currency else scraped_price
    return updated_price

