# SLASH
Slash Your Spending, Not Your Style - Unleash the Best Deals!!

<p align="center"><img width="500" src="./assets/Shop.gif"></p>

[![GitHub license](https://img.shields.io/github/license/DillonMichels/slash)](https://github.com/DillonMichels/slash/blob/main/LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14932526.svg)](https://doi.org/10.5281/zenodo.14932526)
![Github](https://img.shields.io/badge/language-python-red.svg)
[![Pylint](https://github.com/DillonMichels/slash/actions/workflows/pylint.yml/badge.svg)](https://github.com/DillonMichels/slash/actions/workflows/pylint.yml)
[![Python Application](https://github.com/DillonMichels/slash/actions/workflows/python-package.yml/badge.svg)](https://github.com/DillonMichels/slash/actions/workflows/python-package.yml)
[![Running Code Coverage](https://github.com/DillonMichels/slash/actions/workflows/code_cov.yml/badge.svg)](https://github.com/DillonMichels/slash/actions/workflows/code_cov.yml)
[![OAuth and scrappers](https://github.com/DillonMichels/slash/actions/workflows/python-package.yml/badge.svg)](https://github.com/DillonMichels/slash/actions/workflows/python-package.yml)
[![Python Style Checker](https://github.com/DillonMichels/slash/actions/workflows/style_checker.yml/badge.svg)](https://github.com/DillonMichels/slash/actions/workflows/style_checker.yml)
[![Format Check](https://github.com/DillonMichels/slash/actions/workflows/code_formatter.yml/badge.svg)](https://github.com/DillonMichels/slash/actions/workflows/code_formatter.yml)

[![GitHub issues](https://img.shields.io/github/issues/DillonMichels/slash)](https://github.com/DillonMichels/slash/issues)
[![Github closes issues](https://img.shields.io/github/issues-closed-raw/DillonMichels/slash)](https://github.com/DillonMichels/slash/issues?q=is%3Aissue+is%3Aclosed)
[![Github closed pull requests](https://img.shields.io/github/issues-pr-closed/DillonMichels/slash)](https://github.com/DillonMichels/slash/pulls?q=is%3Apr+is%3Aclosed)
<a href="https://github.com/DillonMichels/slash/network"><img alt="GitHub forks" src="https://img.shields.io/github/forks/DillonMichels/slash"></a>
<a href="https://github.com/DillonMichels/slash/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/DillonMichels/slash"></a>
![Discord](https://img.shields.io/discord/1162231656980168876)

Slash is a powerful tool designed to scrape leading e-commerce websites to find the best deals on products you're searching for. It currently supports popular platforms including [Walmart](https://www.walmart.com/), [Target](https://www.target.com/), [BestBuy](https://www.bestbuy.com/),  [Amazon](https://www.amazon.com/), [Google Shopping](https://shopping.google.com/),  [BJs](https://www.bjs.com/),  [Etsy](https://www.etsy.com/), and [EBay](https://www.ebay.com/).
- **Fast**: With slash, you can save over 50% of your time by comparing deals across websites within seconds
- **Easy**: Slash uses very easy commands to filter, sort and search your items
- **Powerful**: Quickly alter the commands to get desired results

# :rocket: Quick Guide

1. Access the Github repository from your computer. 
 - First, pre-install [git](https://git-scm.com/) on  your machine. 
 - Then, clone the repo using the following command:
 ```
 git clone https://github.com/DillonMichels/slash
 ```
 * Finally, ```cd``` into the local repository.
```
cd slash
```
2. Install the ```requirements.txt```. 
- This project uses Python 3, so make sure that [Python](https://www.python.org/downloads/) and [Pip](https://pip.pypa.io/en/stable/installation/) are preinstalled.
- Install the ```requirements.txt``` file using pip.
```
pip3 install -r requirements.txt
```
3. Running the program

- Set the environmental variable using either of the following commands:
 ```
MAC
export FLASK_APP=./src/modules/app
flask run

Windows Command Prompt
set FLASK_APP=.\src\modules\app 
flask run

Windows Powershell
$Env:FLASK_APP='.\src\modules\app'
flask run
```

4. Once flask is running, open your internet browser and type ```http://127.0.0.1:5000/``` into the search bar.

<p>
 
# :dizzy: What's New? (Project 2 Updates)

Updated to use a Database, testing of the Database, Wishlist, and faster Web Scraper times.


![alt text](/src/modules/static/images/wishlist.png)

:sparkles: Contributors
---
<table>
  <tr>
    <td align="center"><a href="https://github.com/Mohsen-Esfandyari"><img src="https://avatars.githubusercontent.com/u/166367760?v=4" width="75px;" alt=""/><br /><sub><b>Mohsen-Esfandyari</b></sub></a></td>
    <td align="center"><a href="https://github.com/ali-f-alfa"><img src="https://avatars.githubusercontent.com/u/45769531?v=4" width="75px;" alt=""/><br /><sub><b>Ali Farahat</b></sub></a></td>
    <td align="center"><a href="https://github.com/DillonMichels"><img src="https://avatars.githubusercontent.com/u/88557889?v=4" width="75px;" alt=""/><br /><sub><b>Dillon Michels</b></sub></a></td>
  </tr>
</table>

## Running the Application

### Backend (Flask)

You can run the Flask backend with proper URL configuration using the `run.py` script:

```bash
# Basic run at port 5000
python run.py

# Specify frontend URL (e.g., for Next.js frontend)
python run.py --frontend-url http://localhost:3000

# Specify custom Google redirect URI
python run.py --redirect-uri http://localhost:5000/callback 

# Full configuration example
python run.py --host localhost --port 5000 --frontend-url http://localhost:3000 --debug
```

The application now dynamically determines URLs based on:
1. Environment variables if provided
2. Request information (headers, referrers)
3. Smart fallbacks with sensible defaults

This approach avoids hardcoded URLs and makes the application work seamlessly with both the original and new frontends.

### Frontend (Next.js)

Run the Next.js frontend:

```bash
cd new-frontend
npm run dev
```

The Next.js application will be available at http://localhost:3000.
