document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.querySelector(".sidebar");
    const brand = document.querySelector(".brand");

    if (sidebar && brand) {
        const menuButton = document.createElement("button");
        menuButton.className = "menu-toggle";
        menuButton.type = "button";
        menuButton.setAttribute("aria-label", "Open navigation menu");
        menuButton.setAttribute("aria-controls", "main-navigation");
        menuButton.setAttribute("aria-expanded", "false");
        menuButton.textContent = "☰";
        sidebar.id = "main-navigation";
        brand.prepend(menuButton);

        const setSidebarOpen = (isOpen) => {
            sidebar.classList.toggle("is-open", isOpen);
            document.body.classList.toggle("sidebar-open", isOpen);
            menuButton.setAttribute("aria-expanded", String(isOpen));
            menuButton.setAttribute("aria-label", isOpen ? "Close navigation menu" : "Open navigation menu");
            menuButton.textContent = isOpen ? "×" : "☰";
        };

        menuButton.addEventListener("click", () => {
            setSidebarOpen(!sidebar.classList.contains("is-open"));
        });

        document.addEventListener("click", (event) => {
            if (window.innerWidth <= 840 && sidebar.classList.contains("is-open")
                && !sidebar.contains(event.target) && !brand.contains(event.target)) {
                setSidebarOpen(false);
            }
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && sidebar.classList.contains("is-open")) {
                setSidebarOpen(false);
                menuButton.focus();
            }
        });

        window.addEventListener("resize", () => {
            if (window.innerWidth > 840 && sidebar.classList.contains("is-open")) {
                setSidebarOpen(false);
            }
        });

        sidebar.querySelectorAll(".nav-link").forEach((link) => {
            link.addEventListener("click", () => {
                if (window.innerWidth <= 840) setSidebarOpen(false);
            });
        });

        const currentPath = window.location.pathname.replace(/\/+$/, "") || "/";
        sidebar.querySelectorAll(".nav-link").forEach((link) => {
            const linkPath = new URL(link.href, window.location.origin).pathname.replace(/\/+$/, "") || "/";
            const isCurrent = currentPath === linkPath || (linkPath !== "/" && currentPath.startsWith(`${linkPath}/`));
            if (isCurrent) {
                link.classList.add("is-active");
                link.setAttribute("aria-current", "page");
            }
        });
    }

    const transactionSearch = document.querySelector(".transaction-search");
    const transactionTable = document.querySelector(".transactions-table");
    if (transactionSearch && transactionTable) {
        const rows = [...transactionTable.querySelectorAll("tbody tr")]
            .filter((row) => !row.querySelector("[colspan]"));
        const noResults = document.createElement("p");
        noResults.className = "transaction-search-empty";
        noResults.setAttribute("aria-live", "polite");
        noResults.textContent = "No transactions match your search.";
        noResults.hidden = true;
        transactionTable.after(noResults);

        transactionSearch.addEventListener("input", () => {
            const query = transactionSearch.value.trim().toLocaleLowerCase();
            let matchCount = 0;
            rows.forEach((row) => {
                const matches = row.textContent.toLocaleLowerCase().includes(query);
                row.hidden = !matches;
                if (matches) matchCount += 1;
            });
            noResults.hidden = !query || matchCount > 0 || rows.length === 0;
        });
    }

    const transactionForm = document.querySelector(".form form");
    const amountInput = transactionForm?.querySelector('input[name="amount"]');
    const currencySelect = transactionForm?.querySelector('select[name="currency"]');
    if (amountInput && currencySelect) {
        const preview = document.createElement("p");
        preview.className = "amount-preview";
        preview.setAttribute("aria-live", "polite");
        amountInput.insertAdjacentElement("afterend", preview);

        const updatePreview = () => {
            const amount = Number(amountInput.value);
            const currency = currencySelect.value;
            preview.textContent = amount > 0
                ? `You’re recording ${currency} ${amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}.`
                : "Enter an amount to preview this transaction.";
        };
        amountInput.addEventListener("input", updatePreview);
        currencySelect.addEventListener("change", updatePreview);
        updatePreview();
    }

    document.querySelectorAll(".valid form").forEach((form) => {
        form.addEventListener("submit", () => {
            const submitButton = form.querySelector('button[type="submit"]');
            if (!submitButton) return;
            submitButton.disabled = true;
            submitButton.textContent = "Processing...";
        });
    });

    const chartDataElement = document.getElementById("report-chart-data");
    if (chartDataElement) {
        const reportData = JSON.parse(chartDataElement.textContent);
        const currencySelect = document.getElementById("report-currency-select");
        const barCanvas = document.getElementById("cashflow-chart");
        const categoryCanvas = document.getElementById("category-chart");
        const categoryLegend = document.getElementById("category-legend");
        const donutTotal = document.getElementById("donut-total");
        const categoryTotal = document.getElementById("category-total");
        const chartColors = ["#087f65", "#f3a849", "#6488d8", "#a774c8", "#e47972", "#5b9fba"];
        const currencySymbols = { NGN: "₦", USD: "$", GBP: "£", EUR: "€" };
        const compactNumber = new Intl.NumberFormat(undefined, {
            notation: "compact",
            maximumFractionDigits: 1,
        });

        const prepareCanvas = (canvas, height) => {
            const ratio = window.devicePixelRatio || 1;
            const width = Math.max(canvas.clientWidth, 240);
            canvas.width = Math.round(width * ratio);
            canvas.height = Math.round(height * ratio);
            const context = canvas.getContext("2d");
            context.scale(ratio, ratio);
            return { context, width, height };
        };

        const drawCashflow = (currency) => {
            const data = reportData[currency];
            const { context: ctx, width, height } = prepareCanvas(barCanvas, 250);
            const values = [...data.income, ...data.expenses].map(Number);
            const maxValue = Math.max(...values, 0);
            const chart = { left: 42, right: 12, top: 16, bottom: 35 };
            const plotWidth = width - chart.left - chart.right;
            const plotHeight = height - chart.top - chart.bottom;
            const scaleMax = maxValue > 0 ? maxValue * 1.15 : 1;

            ctx.clearRect(0, 0, width, height);
            ctx.font = '11px "DM Sans", sans-serif';
            ctx.textBaseline = "middle";
            ctx.textAlign = "right";

            for (let tick = 0; tick <= 4; tick += 1) {
                const y = chart.top + plotHeight * tick / 4;
                const value = scaleMax * (4 - tick) / 4;
                ctx.strokeStyle = "#edf1ef";
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(chart.left, y);
                ctx.lineTo(width - chart.right, y);
                ctx.stroke();
                ctx.fillStyle = "#8a9793";
                ctx.fillText(compactNumber.format(value), chart.left - 8, y);
            }

            if (maxValue === 0) {
                ctx.fillStyle = "#71807e";
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText("No cash flow in the last six months", chart.left + plotWidth / 2, chart.top + plotHeight / 2);
            }

            const groupWidth = plotWidth / data.months.length;
            const barWidth = Math.min(22, groupWidth * .27);
            data.months.forEach((month, index) => {
                const center = chart.left + groupWidth * (index + .5);
                [data.income[index], data.expenses[index]].forEach((rawValue, series) => {
                    const value = Number(rawValue);
                    const barHeight = plotHeight * value / scaleMax;
                    ctx.fillStyle = series === 0 ? "#087f65" : "#f3a849";
                    ctx.beginPath();
                    ctx.roundRect(
                        center + (series === 0 ? -barWidth - 2 : 2),
                        chart.top + plotHeight - barHeight,
                        barWidth,
                        Math.max(barHeight, value > 0 ? 3 : 0),
                        [4, 4, 0, 0]
                    );
                    ctx.fill();
                });
                ctx.fillStyle = "#71807e";
                ctx.textAlign = "center";
                ctx.textBaseline = "top";
                ctx.fillText(month, center, height - chart.bottom + 12);
            });
        };

        const drawCategories = (currency) => {
            const data = reportData[currency].categories;
            const { context: ctx, width, height } = prepareCanvas(categoryCanvas, 210);
            const total = data.reduce((sum, item) => sum + Number(item.value), 0);
            const centerX = width / 2;
            const centerY = height / 2;
            const radius = Math.min(width, height) * .43;
            const lineWidth = 22;

            ctx.clearRect(0, 0, width, height);
            ctx.beginPath();
            ctx.strokeStyle = "#edf2ef";
            ctx.lineWidth = lineWidth;
            ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
            ctx.stroke();

            if (total > 0) {
                let startAngle = -Math.PI / 2;
                data.forEach((item, index) => {
                    const endAngle = startAngle + Number(item.value) / total * Math.PI * 2;
                    ctx.beginPath();
                    ctx.strokeStyle = chartColors[index % chartColors.length];
                    ctx.lineWidth = lineWidth;
                    ctx.lineCap = "butt";
                    ctx.arc(centerX, centerY, radius, startAngle, endAngle);
                    ctx.stroke();
                    startAngle = endAngle;
                });
            }

            donutTotal.textContent = total > 0
                ? `${currencySymbols[currency]}${compactNumber.format(total)}`
                : `${currencySymbols[currency]}0`;
            categoryTotal.textContent = total > 0
                ? `${currencySymbols[currency]}${total.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                : "No expenses yet";
            categoryLegend.replaceChildren();

            if (data.length === 0) {
                const emptyState = document.createElement("p");
                emptyState.className = "chart-empty";
                emptyState.textContent = "No expense data for this currency yet.";
                categoryLegend.append(emptyState);
                return;
            }

            data.forEach((item, index) => {
                const value = Number(item.value);
                const row = document.createElement("div");
                row.className = "category-legend-row";
                const label = document.createElement("span");
                label.className = "category-name";
                const dot = document.createElement("i");
                dot.className = "legend-dot";
                dot.style.backgroundColor = chartColors[index % chartColors.length];
                const name = document.createElement("span");
                name.textContent = item.name;
                label.append(dot, name);

                const amount = document.createElement("strong");
                amount.textContent = `${Math.round(value / total * 100)}%`;
                amount.title = `${currencySymbols[currency]}${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
                row.append(label, amount);
                categoryLegend.append(row);
            });
        };

        const updateCharts = () => {
            const currency = currencySelect.value;
            barCanvas.setAttribute("aria-label", `Monthly ${currency} income and expense bar chart for the last six months`);
            categoryCanvas.setAttribute("aria-label", `${currency} expense breakdown by category`);
            drawCashflow(currency);
            drawCategories(currency);
        };

        currencySelect.addEventListener("change", updateCharts);
        window.addEventListener("resize", updateCharts);
        updateCharts();
    }
});
