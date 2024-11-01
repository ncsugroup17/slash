// grid.js

document.addEventListener("DOMContentLoaded", function () {
    console.log("grid.js loaded");

    // Fetch data from the page to ensure it's ready
    const productsContainer = document.getElementById("products-container");
    const paginationContainer = document.getElementById("pagination");

    if (!productsContainer || !paginationContainer) {
        console.error("Missing containers in HTML for products or pagination");
        return;
    }

    // Example function to render products
    function renderProducts(products) {
        // Clear previous products
        productsContainer.innerHTML = "";

        // Check if there are products to display
        if (!products || products.length === 0) {
            productsContainer.innerHTML = "<p>No products found.</p>";
            return;
        }

        // Iterate over products and create HTML for each product card
        products.forEach((product) => {
            const productCard = document.createElement("div");
            productCard.className = "product-card";

            productCard.innerHTML = `
                <img src="${product.img_link}" alt="${product.title}" class="product-image">
                <h3>${product.title}</h3>
                <p>Price: ${product.price}</p>
                <p>Rating: ${product.rating || "N/A"}</p>
                <a href="${product.link}" target="_blank">View Product</a>
            `;
            productsContainer.appendChild(productCard);
        });
    }

    // Example function to render pagination buttons
    function renderPagination(totalPages, currentPage) {
        paginationContainer.innerHTML = "";

        // Create pagination buttons
        for (let i = 1; i <= totalPages; i++) {
            const pageButton = document.createElement("button");
            pageButton.innerText = i;
            pageButton.className = "pagination-button";
            if (i === currentPage) {
                pageButton.classList.add("active");
            }
            pageButton.addEventListener("click", function () {
                loadPage(i);
            });
            paginationContainer.appendChild(pageButton);
        }
    }

    // Function to simulate loading a specific page
    function loadPage(pageNumber) {
        // Simulating an AJAX request here. Replace with actual fetch if needed.
        console.log(`Loading page ${pageNumber}`);

        // Example data format (replace with actual data fetch)
        const sampleData = [
            {
                title: "Sample Product 1",
                price: "$19.99",
                rating: 4.5,
                img_link: "https://via.placeholder.com/150",
                link: "#",
            },
            {
                title: "Sample Product 2",
                price: "$29.99",
                rating: 4.0,
                img_link: "https://via.placeholder.com/150",
                link: "#",
            },
            // Add more sample products as needed
        ];

        // Render fetched data
        renderProducts(sampleData);
        renderPagination(8, pageNumber); // Assuming 8 total pages
    }

    // Initial load for page 1
    loadPage(1);
});
