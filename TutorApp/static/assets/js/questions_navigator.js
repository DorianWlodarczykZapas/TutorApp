document.addEventListener("DOMContentLoaded", function() {
        let currentPage = 0
        const navButtons = document.querySelectorAll("[data-page]");

        function showPage(page) {
            navButtons.forEach(function (button) {
                const buttonPage = parseInt(button.getAttribute("data-page"), 10);

                if (buttonPage === page) {
                    button.style.display = "inline-block";
                    }
                else {
                    button.style.display = "none";
                    }
            });
        }
        document.getElementById("nav-prev-page").addEventListener("click", function () {
            if (currentPage > 0) {
                currentPage = currentPage -1;
                showPage(currentPage);
                }
        });

        document.getElementById("nav-next-page").addEventListener("click", function () {
           if (currentPage < maxPage) {
            currentPage = currentPage + 1;
            showPage(currentPage);
            }
        });

        showPage(currentPage);
        });