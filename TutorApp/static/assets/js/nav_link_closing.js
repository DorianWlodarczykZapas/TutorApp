document.addEventListener('click', function(event) {


    const clickedInsideMenu = event.target.closest('.nav-menu');


    if (clickedInsideMenu === null) {


        const allToggles = document.querySelectorAll('input[name="navigation-link"]');

        allToggles.forEach((element) => element.checked = false)
    }
});