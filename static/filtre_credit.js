function afficherTous() {
    var rows = document.querySelectorAll('.fl-table tbody tr');
    rows.forEach(function (row) {
        row.style.display = '';
    });
}

function filtrerPositif() {
    var rows = document.querySelectorAll('.fl-table tbody tr');
    rows.forEach(function (row) {
        var ecartCell = row.querySelector('td:nth-child(5)');
        var ecartValue = parseFloat(ecartCell.textContent.trim());

        if (ecartValue >= 0) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function filtrerNegatif() {
    var rows = document.querySelectorAll('.fl-table tbody tr');
    rows.forEach(function (row) {
        var ecartCell = row.querySelector('td:nth-child(5)');
        var ecartValue = parseFloat(ecartCell.textContent.trim());

        if (ecartValue < 0) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}