document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".add-to-wishlist").forEach(button => {
        button.addEventListener("click", function () {
            const productId = this.dataset.productId; // Ensure your button has data-product-id

            fetch('/add-wishlist-item', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ id: productId }) // Sends the product ID
            })
            .then(response => response.json())  // Parse the JSON response
            .then(data => {
                console.log(data);  // Log the response for debugging
                if (data.error) {
                    alert(`Error: ${data.error}`);  // If there's an error, alert the user
                } else {
                    alert(data.message);  // Show success message
                    window.location.href = '/wishlist.html'; // Redirect to wishlist page after success
                }
            })
            .catch(error => console.error("Error:", error));  // Handle fetch errors
        });
    });
});
