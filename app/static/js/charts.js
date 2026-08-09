document.addEventListener("DOMContentLoaded", () => {
    const reportRows = document.querySelectorAll("#reviewReportTable .report-row");
    const buttons = document.querySelectorAll("button[data-filter]");

    buttons.forEach((button) => {
        button.addEventListener("click", () => {
            const level = button.getAttribute("data-filter");
            reportRows.forEach((row) => {
                const severity = row.dataset.severity;
                if (level === "all") {
                    row.style.display = "";
                } else if (level === "issues") {
                    row.style.display = severity === "safe" ? "none" : "";
                } else {
                    row.style.display = severity === level ? "" : "none";
                }
            });
        });
    });

    const chartCanvas = document.getElementById("pieChart");
    if (chartCanvas && window.Chart) {
        new Chart(chartCanvas.getContext("2d"), {
            type: "pie",
            data: {
                labels: ["Score", "Remaining"],
                datasets: [{
                    data: [
                        Number(chartCanvas.dataset.score || 0),
                        100 - Number(chartCanvas.dataset.score || 0),
                    ],
                    backgroundColor: ["#198754", "#e0e0e0"],
                }],
            },
            options: {
                plugins: { legend: { position: "bottom" } },
            },
        });
    }
});
