document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const resultsDiv = document.getElementById('results');
    const resultsBody = document.getElementById('resultsBody');
    const resultCount = document.getElementById('resultCount');

    analyzeBtn.addEventListener('click', async function() {
        // Get form values
        const dropThreshold = parseFloat(document.getElementById('dropThreshold').value) / 100;
        const increaseThreshold = parseFloat(document.getElementById('increaseThreshold').value) / 100;
        const maxStocks = document.getElementById('maxStocks').value || null;

        // Validate inputs
        if (isNaN(dropThreshold) || isNaN(increaseThreshold)) {
            showError('Please enter valid numbers for thresholds');
            return;
        }

        // Show loading, hide results and error
        loadingDiv.classList.remove('hidden');
        resultsDiv.classList.add('hidden');
        errorDiv.classList.add('hidden');
        analyzeBtn.disabled = true;

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    drop_threshold: dropThreshold,
                    increase_threshold: increaseThreshold,
                    max_stocks: maxStocks
                })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Analysis failed');
            }

            // Display results
            displayResults(data.results, data.count);

        } catch (error) {
            showError('Error: ' + error.message);
        } finally {
            loadingDiv.classList.add('hidden');
            analyzeBtn.disabled = false;
        }
    });

    function displayResults(results, count) {
        // Clear previous results
        resultsBody.innerHTML = '';

        if (count === 0) {
            resultCount.textContent = 'No stocks found matching the criteria.';
            resultsDiv.classList.remove('hidden');
            return;
        }

        resultCount.textContent = `Found ${count} stock${count !== 1 ? 's' : ''} matching the criteria:`;

        // Populate table
        results.forEach(stock => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td><strong>${stock.ticker}</strong></td>
                <td>$${stock.yesterday_price.toFixed(2)}</td>
                <td>$${stock.today_price.toFixed(2)}</td>
                <td>$${stock.ytd_high.toFixed(2)}</td>
                <td class="negative">-${stock.drop_from_high.toFixed(2)}%</td>
                <td class="positive">+${stock.increase_today.toFixed(2)}%</td>
                <td>${stock.yesterday_date}</td>
                <td>${stock.today_date}</td>
            `;
            
            resultsBody.appendChild(row);
        });

        resultsDiv.classList.remove('hidden');
    }

    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
    }
});

