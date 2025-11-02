document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('product-search');
    const searchResults = document.getElementById('search-results');
    let chart = null;

    async function loadPriceHistory() {
        const response = await fetch('/static/data/price_history.json');
        const data = await response.json();
        return data;
    }

    // Replace API calls with static data
    searchInput.addEventListener('input', debounce(async function() {
        const query = this.value.toLowerCase();
        if (query.length < 3) {
            searchResults.innerHTML = '';
            return;
        }

        const data = await loadPriceHistory();
        const matches = data.products.filter(p => 
            p.name.toLowerCase().includes(query)
        );
        
        searchResults.innerHTML = matches.map(product => `
            <div class="search-result" data-id="${product.id}">
                <img src="${product.image_url}" alt="${product.name}">
                <span>${product.name}</span>
            </div>
        `).join('');
    }, 300));

    searchResults.addEventListener('click', async function(e) {
        const result = e.target.closest('.search-result');
        if (!result) return;

        const productId = result.dataset.id;
        const response = await fetch(`/api/price-history/${productId}`);
        const history = await response.json();

        renderChart(history);
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
                        beginAtZero: false
                    }
                }
            }
        });
    }

    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
});