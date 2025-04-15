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

1. Clone the repository and navigate to it:
```bash
git clone https://github.com/DillonMichels/slash
cd slash
```

2. Install the backend dependencies:
```bash
pip install -r requirements.txt
```

3. Start the backend server:
```bash
python run.py --frontend-url http://localhost:3000
```

4. Set up the frontend (optional - for modern UI):
```bash
cd new-frontend
npm install --legacy-peer-deps
npm run dev
```

5. Access the application:
   - Traditional UI: Open `http://127.0.0.1:5000/` in your browser
   - Modern UI (Next.js): Open `http://localhost:3000/` in your browser

# :computer: Available UIs

## Traditional UI

The original Flask-based UI is available at `http://127.0.0.1:5000/` when running the Flask backend. This UI provides access to all core features including product search, filtering, and wishlist management.

## Modern UI (Next.js)

A new, modern frontend built with Next.js is available in the `new-frontend` directory. This UI features:

- Responsive design for all devices
- Improved user experience with real-time feedback
- Modern UI components with ShadCN
- Streamlined search and wishlist management
- Seamless integration with the Flask backend

To use the modern UI, follow the setup instructions for the frontend in the Quick Guide.

# :dizzy: What's New?

- Modern Next.js frontend with improved UX
- Enhanced and integrated backend with database
- Wishlist functionality for saving favorite deals
- AI-powered product recommendations
- Faster and more accirate web scraper
- Improved authentication with Google OAuth

![alt text](/src/modules/static/images/wishlist.png)

# :sparkles: Contributors
<table>
  <tr>
    <td align="center"><a href="https://github.com/Mohsen-Esfandyari"><img src="https://avatars.githubusercontent.com/u/166367760?v=4" width="75px;" alt=""/><br /><sub><b>Mohsen-Esfandyari</b></sub></a></td>
    <td align="center"><a href="https://github.com/ali-f-alfa"><img src="https://avatars.githubusercontent.com/u/45769531?v=4" width="75px;" alt=""/><br /><sub><b>Ali Farahat</b></sub></a></td>
    <td align="center"><a href="https://github.com/DillonMichels"><img src="https://avatars.githubusercontent.com/u/88557889?v=4" width="75px;" alt=""/><br /><sub><b>Dillon Michels</b></sub></a></td>
  </tr>
    <tr>
    <td align="center"><a href="https://github.com/rymikula"><img src="https://avatars.githubusercontent.com/u/194296512?v=4" width="75px;" alt=""/><br /><sub><b>Ryan Mikula</b></sub></a></td>
    <td align="center"><a href="https://github.com/MesekerWK"><img src="https://avatars.githubusercontent.com/u/63201911?v=4" width="75px;" alt=""/><br /><sub><b>Meseker Worku</b></sub></a></td>
    <td align="center"><a href="https://github.com/ONeal2467"><img src="https://avatars.githubusercontent.com/u/89427296?v=4" width="75px;" alt=""/><br /><sub><b>O'Neal M'Beri</b></sub></a></td>
    <td align="center"><a href="https://github.com/SyntaxErrorThapa"><img src="https://avatars.githubusercontent.com/u/125596457?v=4" width="75px;" alt=""/><br /><sub><b>Pratik Thapa</b></sub></a></td>
  </tr>
</table>

# :gear: Advanced Configuration

## Backend (Flask)

The Flask backend can be configured with various options:

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

The application dynamically determines URLs based on:
1. Environment variables if provided
2. Request information (headers, referrers)
3. Smart fallbacks with sensible defaults

This approach avoids hardcoded URLs and makes the application work seamlessly with both the original and new frontends.

## Advanced Frontend Commands (Next.js)

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Run tests
npm run test
```

The Next.js application will be available at http://localhost:3000 by default.
