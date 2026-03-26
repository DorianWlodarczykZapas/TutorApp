document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('complete-task-form');
    const btn = document.getElementById('btn-complete');

    if (!form || !btn) return;


    if (btn.classList.contains('btn-submit--completed')) {
        btn.style.backgroundColor = "#2ed573";
        btn.style.cursor = "default";
    }

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const url = this.getAttribute('data-url');
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        btn.disabled = true;
        btn.innerText = "...";

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                btn.innerText = "✓ " + "{% trans 'Completed' %}";
                btn.style.backgroundColor = "#2ed573";
                btn.classList.add('btn-submit--completed');
            }
        })
        .catch(error => {
            btn.disabled = false;
            btn.innerText = "Error";
            console.error('AJAX Error:', error);
        });
    });
});