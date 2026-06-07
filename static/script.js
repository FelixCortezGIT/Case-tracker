const sortableHeaders = document.querySelectorAll(".user-summary-table-wrap th[data-sort]");
const tableBody = document.querySelector(".user-summary-table-wrap tbody");

let activeColumnIndex = null;
let currentDirection = "desc";

sortableHeaders.forEach(function (header) {
    header.addEventListener("click", function () {
        const columnIndex = header.cellIndex;

        if (activeColumnIndex === columnIndex) {
            currentDirection = currentDirection === "asc" ? "desc" : "asc";
        } else {
            activeColumnIndex = columnIndex;
            currentDirection = "desc";
        }

        sortUserSummaryTable(columnIndex, currentDirection);
        updateSortArrows(header, currentDirection);
        highlightActiveColumn(columnIndex);
    });
});

function sortUserSummaryTable(columnIndex, direction) {
    const rows = Array.from(tableBody.querySelectorAll("tr"));

    rows.sort(function (rowA, rowB) {
        const valueA = Number(rowA.children[columnIndex].textContent.trim());
        const valueB = Number(rowB.children[columnIndex].textContent.trim());

        if (direction === "asc") {
            return valueA - valueB;
        }

        return valueB - valueA;
    });

    rows.forEach(function (row) {
        tableBody.appendChild(row);
    });
}

function updateSortArrows(activeHeader, direction) {
    sortableHeaders.forEach(function (header) {
        const arrow = header.querySelector(".sort-arrows");
        arrow.textContent = "↕";
    });

    const activeArrow = activeHeader.querySelector(".sort-arrows");
    activeArrow.textContent = direction === "asc" ? "↑" : "↓";
}

function highlightActiveColumn(columnIndex) {
    const tableRows = document.querySelectorAll(".user-summary-table-wrap tr");

    tableRows.forEach(function (row) {
        Array.from(row.children).forEach(function (cell) {
            cell.classList.remove("active-sort-column");
        });

        if (row.children[columnIndex]) {
            row.children[columnIndex].classList.add("active-sort-column");
        }
    });
}

const activityFilter = document.getElementById("activity-filter");
const customRangeWrap = document.getElementById("custom-range-wrap");
const dateRangeInput = document.getElementById("activity-date-range");

if (activityFilter && customRangeWrap) {

    function toggleDateRange() {
        if (activityFilter.value === "custom") {
            customRangeWrap.style.display = "block";
        } else {
            customRangeWrap.style.display = "none";
        }
    }

    flatpickr(dateRangeInput, {
        mode: "range",
        dateFormat: "Y-m-d"
    });

    toggleDateRange();

    activityFilter.addEventListener("change", toggleDateRange);
}
