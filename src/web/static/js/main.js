async function loadDeals() {
    try {
        const response = await fetch('data/price_history.json');
        const data = await response.json();
        const dealsContainer = document.getElementById('deals-container');
        
        const currentDeals = data.products.filter(p => p.is_sale);
        
        if (currentDeals.length === 0) {
            dealsContainer.innerHTML = '<p>No current deals available.</p>';
            return;
        }
        
        dealsContainer.innerHTML = currentDeals.map(deal => `
            <div class="deal-card">
                <img src="${deal.image_url}" alt="${deal.name}">
                <h2>${deal.name}</h2>
                <p class="price">$${deal.price}</p>
                <p class="original-price">Was: $${deal.original_price}</p>
                <a href="${deal.url}" class="btn" target="_blank">View Deal</a>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading deals:', error);
    }
}

document.addEventListener('DOMContentLoaded', loadDeals);