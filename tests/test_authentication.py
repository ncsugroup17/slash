import unittest
import sys
import os

# Adjust the path to include the project's root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from slash.src.modules.app import app  # Import the app object from your main application module

class TestApplicationFunctionality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    def test_home_page_loads(self):
        """Test that the home page loads successfully and contains expected title text."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Slash", response.data)

    def test_login_page_loads(self):
        """Test that the login page loads successfully and contains the expected content."""
        response = self.client.get('/login')  # Adjust this route if necessary
        self.assertEqual(response.status_code, 200)
        # Checking for an identifiable element from the HTML response
        self.assertIn(b"navbar", response.data)  # Check for navbar class to confirm the page loaded

    def test_google_login_redirect(self):
        """Test that the Google login route redirects as expected."""
        response = self.client.get('/login/google', follow_redirects=False)
        # Check for a redirect status code
        self.assertEqual(response.status_code, 302)
        # Check if redirect location contains 'accounts.google.com' indicating Google OAuth
        self.assertIn(b'accounts.google.com', response.headers['Location'].encode())

    def test_register_page_loads_content(self):
        """Test that the registration page loads and contains some expected content."""
        response = self.client.get('/register')
        
        # Ensure the page loads with a 200 status code
        self.assertEqual(response.status_code, 200)
        
        # Check if the response contains any non-empty body content
        self.assertGreater(len(response.data.strip()), 0, "Registration page appears to be empty.")

    def test_register_page_status_code(self):
        """Test that the registration page returns a 200 status code."""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200, "Registration page did not return a 200 status code.")

    def test_register_page_content_type(self):
        """Test that the registration page returns HTML content."""
        response = self.client.get('/register')
        self.assertIn(b"text/html", response.content_type.encode(), "Registration page did not return HTML content type.")

    def test_register_page_contains_form_tag(self):
        """Test that the registration page includes at least one form element."""
        response = self.client.get('/register')
        self.assertIn(b"<form", response.data, "Registration page does not contain a <form> tag.")

    def test_register_page_contains_title(self):
        """Test that the registration page includes a title element."""
        response = self.client.get('/register')
        self.assertIn(b"<title>", response.data, "Registration page does not contain a <title> tag.")

    def test_register_page_has_submit_button(self):
        """Test that the registration page contains a submit button."""
        response = self.client.get('/register')
        self.assertIn(b'<button', response.data, "Registration page does not contain a submit button.")

    def test_register_page_contains_registration_script(self):
        """Test that the registration page includes at least one <script> tag, indicating JavaScript functionality."""
        response = self.client.get('/register')
        self.assertIn(b"<script", response.data, "Registration page does not contain any <script> tag.")

    def test_register_page_title_exists(self):
        """Test that the registration page has a title tag."""
        response = self.client.get('/register')
        self.assertIn(b'<title>', response.data, "Registration page does not contain a <title> tag.")

    def test_register_page_contains_css_link(self):
        """Test that the registration page includes a CSS stylesheet link."""
        response = self.client.get('/register')
        self.assertIn(b'<link rel="stylesheet"', response.data, "Registration page does not contain a CSS stylesheet link.")

    def test_register_page_contains_submit_button(self):
        """Test that the registration page has a submit button."""
        response = self.client.get('/register')
        self.assertIn(b'type="submit"', response.data, "Registration page does not contain a submit button.")

    def test_register_page_has_remember_me_checkbox(self):
        """Test that the registration page has a 'Remember Me' checkbox."""
        response = self.client.get('/register')
        self.assertIn(b'type="checkbox"', response.data, "Registration page does not contain a 'Remember Me' checkbox.")

    def test_registration_page_has_submit_button(self):
        """Test that the registration page contains a submit button."""
        response = self.client.get('/register')
        self.assertIn(b'type="submit"', response.data, "Submit button not found on registration page.")

    def test_registration_page_has_submit_button(self):
        """Test that the registration page contains a submit button."""
        response = self.client.get('/register')
        self.assertIn(b'type="submit"', response.data, "Submit button not found on registration page.")

    def test_registration_page_contains_form_tag(self):
        """Test that the registration page contains a <form> tag."""
        response = self.client.get('/register')
        self.assertIn(b'<form', response.data, "Form tag not found on registration page.")

    def test_registration_page_contains_submit_button(self):
        """Test that the registration page contains a 'Submit' button."""
        response = self.client.get('/register')
        self.assertIn(b'type="submit"', response.data, "'Submit' button not found on registration page.")

    def test_registration_page_has_form_tag(self):
        """Test that the registration page contains a <form> tag."""
        response = self.client.get('/register')
        self.assertIn(b'<form', response.data, "No <form> tag found on the registration page.")

    def test_registration_page_has_input_field(self):
        """Test that the registration page contains at least one <input> field."""
        response = self.client.get('/register')
        self.assertIn(b'<input', response.data, "No <input> field found on the registration page.")

    def test_registration_page_has_submit_button(self):
        """Test that the registration page contains a submit button."""
        response = self.client.get('/register')
        self.assertIn(b'type="submit"', response.data.lower(), "Submit button not found on the registration page.")

# from slash.src.modules.scraper import searchAmazon
# class TestAmazonScraper(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         # Set parameters for the test
#         cls.query = "Bag"
#         cls.df_flag = False  # Adjust based on your data requirements
#         cls.currency = "USD"  # Set desired currency

#     def test_amazon_scraper_retrieves_data(self):
#         """Test that the Amazon scraper retrieves non-empty data with expected keys."""
#         # Call the function directly with the required arguments
#         product_data = searchAmazon(self.query, self.df_flag, self.currency)

#         # Check that the returned data is not empty
#         self.assertTrue(product_data, "Amazon scraper returned empty data.")

#         # Validate the expected keys in each entry
#         expected_keys = {"title", "price", "rating"}
#         for entry in product_data:
#             self.assertTrue(expected_keys.issubset(entry.keys()), "Scraped data missing expected keys.")

#         # Validate the format of "price" and "rating" fields
#         for entry in product_data:
#             # Check if price is a valid currency string or None
#             price = entry.get("price")
#             if price is not None:
#                 try:
#                     # Remove currency symbols and commas, then convert to float
#                     numeric_price = float(price.replace("$", "").replace(",", ""))
#                     self.assertIsInstance(numeric_price, (float, int), "Price should be convertible to float or int.")
#                 except ValueError:
#                     self.fail("Price format is incorrect; cannot convert to float.")
            
#             # Check if rating is a float, None, or empty string
#             rating = entry.get("rating")
#             self.assertTrue(
#                 isinstance(rating, (float, type(None))) or rating == "",
#                 "Rating is not a float, None, or empty string."
#             )

if __name__ == '__main__':
    unittest.main()