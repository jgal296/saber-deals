document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('product-search');
    const searchResults = document.getElementById('search-results');
    let chart = null;

    // Handle form submission (both button click and enter key)
    searchForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const query = searchInput.value.trim();
        
        if (query.length < 2) {
            searchResults.innerHTML = '<p class="search-message">Please enter at least 2 characters</p>';
            return;
        }

        try {
            searchResults.innerHTML = '<p class="search-message">Searching...</p>';
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Search request failed');
            }
            
            if (data.length === 0) {
                searchResults.innerHTML = '<p class="search-message">No products found</p>';
                return;
            }

            searchResults.innerHTML = data.map(product => `
                <div class="search-result" data-id="${product.id}">
                    <img src="${product.image_url}" alt="${product.name}">
                    <div class="search-result-info">
                        <span class="product-name">${product.name}</span>
                        <span class="current-price">${product.current_price || 'Price not available'}</span>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Search error:', error);
            searchResults.innerHTML = '<p class="search-message error">Error performing search</p>';
        }
    });

    // Handle product selection
    searchResults.addEventListener('click', async function(e) {
        const result = e.target.closest('.search-result');
        if (!result) return;

        try {
            const productId = result.dataset.id;
            const response = await fetch(`/api/price-history/${productId}`);
            
            if (!response.ok) {
                throw new Error('Failed to fetch price history');
            }

            const history = await response.json();
            renderChart(history);
            
            // Highlight selected product
            document.querySelectorAll('.search-result').forEach(el => 
                el.classList.remove('selected'));
            result.classList.add('selected');
            
        } catch (error) {
            console.error('Error fetching price history:', error);
        }
    });

    function renderChart(history) {
        const ctx = document.getElementById('priceChart').getContext('2d');
        
        if (chart) {
            chart.destroy();
        }

        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: history.dates,
                datasets: [{
                    label: 'Price History',
                    data: history.prices,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: value => `$${value}`
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: context => `$${context.parsed.y}`
                        }
                    }
                }
            }
        });
    }
});