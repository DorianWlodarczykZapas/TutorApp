document.addEventListener('DOMContentLoaded', function () {
    const paymentData = document.getElementById('payment-data');
    const paymentUrl = paymentData.dataset.paymentUrl;
    const successUrl = paymentData.dataset.successUrl;
    const planPrice = paymentData.dataset.planPrice;
    const planCurrency = paymentData.dataset.planCurrency;

    document.getElementById('payment-form').addEventListener('submit', async function (e) {
        e.preventDefault();

        const submitBtn = document.getElementById('submit-btn');
        const blikCode = document.getElementById('blik-code').value;

        if (blikCode.length !== 6 || !/^\d{6}$/.test(blikCode)) {
            showAlert('BLIK code must be exactly 6 digits.', 'error');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';

        try {
            const response = await fetch(paymentUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    blik_code: blikCode,
                }),
            });

            const data = await response.json();

            if (data.error) {
                showAlert(data.error, 'error');
                resetButton(submitBtn, planPrice, planCurrency);
                return;
            }

            showAlert('Payment successful! Check your banking app to confirm.', 'success');
            setTimeout(() => window.location.href = successUrl, 3000);

        } catch (error) {
            showAlert('An error occurred. Please try again.', 'error');
            resetButton(submitBtn, planPrice, planCurrency);
        }
    });

    function resetButton(btn, price, currency) {
        btn.disabled = false;
        btn.textContent = `Pay ${price} ${currency}`;
    }

    function showAlert(message, type) {
        const alerts = document.getElementById('payment-alerts');
        alerts.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
    }
});