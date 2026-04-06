document.addEventListener('DOMContentLoaded', function () {
    const paymentData = document.getElementById('payment-data');
    const publishableKey = paymentData.dataset.publishableKey;
    const paymentUrl = paymentData.dataset.paymentUrl;
    const successUrl = paymentData.dataset.successUrl;
    const isUltimate = paymentData.dataset.isUltimate === 'true';
    const planPrice = paymentData.dataset.planPrice;
    const planCurrency = paymentData.dataset.planCurrency;

    const stripe = Stripe(publishableKey);
    const elements = stripe.elements();

    const card = elements.create('card', {
        hidePostalCode: true,
        style: {
            base: {
                fontSize: '18px',
                fontFamily: "'Inter', sans-serif",
                color: '#333',
                '::placeholder': { color: '#999' }
            },
            invalid: { color: '#dc3545' }
        }
    });
    card.mount('#card-element');

    card.on('change', function (event) {
        const displayError = document.getElementById('card-errors');
        displayError.textContent = event.error ? event.error.message : '';
    });

    document.getElementById('payment-form').addEventListener('submit', async function (e) {
        e.preventDefault();

        const submitBtn = document.getElementById('submit-btn');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';

        try {
            const { paymentMethod, error: pmError } = await stripe.createPaymentMethod({
                type: 'card',
                card: card,
            });

            if (pmError) {
                showAlert(pmError.message, 'error');
                resetButton(submitBtn, planPrice, planCurrency);
                return;
            }

            const response = await fetch(paymentUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    payment_method_id: paymentMethod.id,
                }),
            });

            const data = await response.json();

            if (data.error) {
                showAlert(data.error, 'error');
                resetButton(submitBtn, planPrice, planCurrency);
                return;
            }

            if (isUltimate) {
                const { error: confirmError } = await stripe.confirmCardPayment(data.client_secret, {
                    payment_method: paymentMethod.id
                });

                if (confirmError) {
                    showAlert(confirmError.message, 'error');
                    resetButton(submitBtn, planPrice, planCurrency);
                    return;
                }
            }

            showAlert('Payment successful!', 'success');
            setTimeout(() => window.location.href = successUrl, 2000);

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