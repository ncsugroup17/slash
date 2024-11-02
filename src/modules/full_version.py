"""
Copyright (C) 2021 SE Slash - All Rights Reserved
You may use, distribute and modify this code under the terms of the MIT license.
You should have received a copy of the MIT license with this file. If not, please write to: secheaper@gmail.com
"""

import json
import os
import pandas as pd
import webbrowser
from src.modules.scraper import driver
from src.modules.features import (
    users_main_dir,
    create_user,
    list_users,
    create_wishlist,
    delete_wishlist,
    list_wishlists,
    read_wishlist,
    wishlist_add_item,
    wishlist_remove_list
)
from shutil import get_terminal_size


class FullVersion:
    def __init__(self):
        self.name = "default"
        self.password = "pass"
        self.default_user_file = users_main_dir / "default_user.json"
        self.df = pd.DataFrame()
        self.currency = ""
        pd.set_option("display.max_rows", None)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", get_terminal_size()[0])
        pd.set_option("display.max_colwidth", 40)

    def login(self):
        """Used for User Login. Returns the username and email."""
        if not os.path.exists(self.default_user_file):
            print("Welcome to Slash!")
            print("Please enter the following information: ")
            name = input("Name: ")
            user_data = {"name": name}
            with open(self.default_user_file, "w") as outfile:
                json.dump(user_data, outfile)
            self.name = name
            create_user(self.name, self.password)
        else:
            with open(self.default_user_file) as json_file:
                data = json.load(json_file)
                self.name = data["name"]
        return self.name

    def search_fn(self):
        """Searches for a product, returns the scraped list, and allows user to save or open an item."""
        prod = input("Enter name of product to Search: ")
        self.scrape(prod)
        ch = input(
            "\nEnter 1 to save product to wishlist \nEnter 2 to open link in browser\nElse enter any other key to continue\n"
        )
        try:
            ch = int(ch)
        except ValueError:
            return

        if ch == 1:
            wish_lists = self.wishlist_maker()
            wishlist_index = int(input("\nEnter your wishlist index: "))
            selected_wishlist = wish_lists[wishlist_index]
            indx = int(input("\nEnter row number of product to save: "))
            if indx < len(self.df):
                new_data = self.df.iloc[[indx]]
                wishlist_add_item(self.name, selected_wishlist, new_data)
                print("Item added successfully")

        elif ch == 2:
            indx = int(input("\nEnter row number of product to open: "))
            webbrowser.open_new(self.df.link[indx])

    def extract_list(self):
        """Helps user manage saved products, create new lists, or open products in browser."""
        wish_lists = self.wishlist_maker()
        wishlist_options = int(
            input(
                "\nSelect from the following: \n1. Open Wishlist \n2. Create new Wishlist \n3. Delete Wishlist \n4. Return to Main\n"
            )
        )

        if wishlist_options == 1:
            wishlist_index = int(input("\nEnter the wishlist index: "))
            selected_wishlist = wish_lists[wishlist_index]
            items_data = read_wishlist(self.name, selected_wishlist)
            if items_data is not None:
                if len(items_data):
                    print(items_data)
                else:
                    print("Empty Wishlist")
                choice = int(
                    input(
                        "\nSelect from the following:\n1. Delete item from list\n2. Open link in Chrome\n3. Return to Main\n"
                    )
                )
                if choice == 1:
                    indx = int(input("\nEnter row number to be removed: "))
                    wishlist_remove_list(self.name, selected_wishlist, indx)
                elif choice == 2:
                    indx = int(input("\nEnter row number to open in chrome: "))
                    url = items_data.link[indx]
                    webbrowser.open_new(url)
            else:
                print("Wishlist does not exist")

        elif wishlist_options == 2:
            wishlist_name = str(input("\nName your wishlist: "))
            create_wishlist(self.name, wishlist_name)

        elif wishlist_options == 3:
            wishlist_index = int(input("Enter the wishlist index to delete: "))
            selected_wishlist = wish_lists[wishlist_index]
            delete_wishlist(self.name, selected_wishlist)

    def wishlist_maker(self):
        """Displays existing wishlists and returns them as a list."""
        wish_lists = []
        print("----------Wishlists---------")
        for index, wishlist in enumerate(list_wishlists(self.name)):
            wish_lists.append(wishlist)
            print(index, "\t", wishlist)
        return wish_lists

    def view_users(self):
        """Displays all users."""
        users_list = []
        print("----------Users---------")
        for user in list_users():
            users_list.append(user)
            print("\t", user)
        return users_list

    def change_user(self):
        """Allows changing the current user."""
        self.view_users()
        username = input("Enter username (username will be created if not exist):")
        create_user(username, self.password)
        self.name = username
        user_data = {"name": username}
        with open(self.default_user_file, "w") as outfile:
            json.dump(user_data, outfile)
        print("Welcome ", self.name)

    def scrape(self, prod):
        """Calls the scraper function from scraper.py."""
        results = driver(prod, df_flag=1, currency=self.currency)
        self.df = pd.DataFrame.from_dict(results, orient="columns")
        print(self.df)

    def driver(self):
        """Main driver function to control user interactions."""
        self.login()
        print("Welcome ", self.name)
        while True:
            print("Select from following:")
            print(
                "1. Search new product\n2. Manage Wishlists\n3. See Currency Conversion\n4. Change user\n0. Exit"
            )
            choice = int(input())
            if choice == 1:
                self.search_fn()
            elif choice == 2:
                self.extract_list()
            elif choice == 3:
                self.currency = str.lower(input("Enter INR/EUR\n"))
            elif choice == 4:
                self.change_user()
            elif choice == 0:
                print("Thank You for Using Slash")
                break
            else:
                print("Incorrect Option")
