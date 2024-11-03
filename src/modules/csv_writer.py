import csv
import os


class CSVWriter:
    def __init__(self, filename='comments.csv'):
        self.filename = filename
        # Ensure the CSV file has headers if it doesn’t exist
        if not os.path.exists(self.filename):
            with open(self.filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(
                    ['product_id', 'username', 'comment']
                )  # Column headers

    def add_comment(self, product_id, username, comment):
        """
        Adds a new comment to the CSV file.

        Args:
            product_id (str): The unique ID of the product.
            username (str): The username of the commenter.
            comment (str): The comment text.
        """
        with open(self.filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([product_id, username, comment])

    def get_comments(self, product_id):
        """
        Retrieves all comments for a specific product.

        Args:
            product_id (str): The unique ID of the product.

        Returns:
            list: A list of dictionaries containing comments for the product.
        """
        comments = []
        with open(self.filename, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['product_id'] == product_id:
                    comments.append({
                        'username': row['username'],
                        'comment': row['comment']
                    })
        return comments
