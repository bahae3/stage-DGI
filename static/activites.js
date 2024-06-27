var rows = document.querySelectorAll(".activite-row");

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