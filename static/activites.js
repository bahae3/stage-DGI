//// This is for activites.html, ecart_table.html, comparaison.html

var rows = document.querySelectorAll(".activite-row");

if (rows.length < 10) {
    document.querySelector(".left-arrow").style.display = "none";
    document.querySelector(".right-arrow").style.display = "none";
}

var begin = 0;
var end = 10;

const totalPages = Math.ceil(rows.length / end);

function showPage(page) {
    for (let i = 0; i < rows.length; i++) {
        rows[i].style.display = "none";
    }
    for (let i = page * end; i < (page + 1) * end && i < rows.length; i++) {
        rows[i].style.display = "";
    }
}

document.querySelector(".left-arrow").addEventListener("click", () => {
    if (begin > 0) {
        begin--;
        showPage(begin);
    }
});

document.querySelector(".right-arrow").addEventListener("click", () => {
    if (begin < totalPages - 1) {
        begin++;
        showPage(begin);
    }
});

// Initial call to display the first page
showPage(begin);