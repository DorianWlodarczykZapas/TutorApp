class TimestampFormsetHandler {
    constructor(containerSelector, templateSelector, addButtonSelector, prefix) {
        this.container = document.querySelector(containerSelector);
        this.template = document.querySelector(templateSelector);
        this.addButton = document.querySelector(addButtonSelector);
        this.prefix = prefix;
        this.totalFormsInput = document.querySelector(
            `#id_${this.prefix}-TOTAL_FORMS`
        );
    }


    init() {
        if (!this.container || !this.template || !this.addButton) {
            console.error('FormsetHandler: No required  DOM elements');
            return;
        }


        this.addButton.addEventListener('click', () => this.addForm());


        this.container.addEventListener('click', (event) => {
            if (event.target.closest('.remove-timestamp')) {
                this.removeForm(event);
            }
        });
    }


    addForm() {
        const formIndex = parseInt(this.totalFormsInput.value, 10);


        let newFormHtml = this.template.innerHTML.replace(
            /__prefix__/g,
            formIndex
        );


        this.container.insertAdjacentHTML('beforeend', newFormHtml);


        this.totalFormsInput.value = formIndex + 1;


        const newForm = this.container.lastElementChild;
        newForm.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }


    removeForm(event) {
        const forms = this.container.querySelectorAll('.timestamp-form-wrapper');


        if (forms.length <= 1) {
            const errorMsg = this.container.dataset.minFormsError ||
                           'At least one timestamp is required!';
            alert(errorMsg);
            return;
        }

        const formElement = event.target.closest('.timestamp-form-wrapper');
        if (!formElement) return;


        formElement.style.opacity = '0';
        formElement.style.transition = 'opacity 0.3s';

        setTimeout(() => {
            formElement.remove();
            this.updateFormIndexes();
        }, 300);
    }


    updateFormIndexes() {
        const forms = this.container.querySelectorAll('.timestamp-form-wrapper');

        forms.forEach((form, index) => {

            const elements = form.querySelectorAll('input, select, textarea, label');

            elements.forEach(el => {

                if (el.name) {
                    el.name = el.name.replace(
                        new RegExp(`${this.prefix}-(\\d+)-`),
                        `${this.prefix}-${index}-`
                    );
                }


                if (el.id) {
                    el.id = el.id.replace(
                        new RegExp(`${this.prefix}-(\\d+)-`),
                        `${this.prefix}-${index}-`
                    );
                }


                if (el.htmlFor) {
                    el.htmlFor = el.htmlFor.replace(
                        new RegExp(`${this.prefix}-(\\d+)-`),
                        `${this.prefix}-${index}-`
                    );
                }
            });
        });


        this.totalFormsInput.value = forms.length;
    }
}


document.addEventListener('DOMContentLoaded', () => {
    const formsetHandler = new TimestampFormsetHandler(
        '#timestamp-formset-container',
        '#empty-timestamp-form',
        '#add-timestamp-btn',
        'timestamps'
    );
    formsetHandler.init();
});