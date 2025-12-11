// ======================================================
// UI Utilities
// ======================================================
const $ = sel => document.querySelector(sel);
const $$ = sel => Array.from(document.querySelectorAll(sel));

// ======================================================
// Navigation
// ======================================================
const navBtns = $$(".nav-btn");
const sections = $$(".main-section");

navBtns.forEach(btn => {
    btn.addEventListener("click", () => {
        sections.forEach(s => s.style.display = "none");
        document.getElementById(btn.dataset.section).style.display = "block";
    });
});

sections.forEach(s => s.style.display = "none");
$("#dashboard-section").style.display = "block";

// ======================================================
// Logout (front-end only)
// ======================================================
$("#logout-btn")?.addEventListener("click", () => {
    alert("Logged out (frontend only — no backend).");
});

// ======================================================
// Year Switcher
// ======================================================
const yearContents = $$(".year-content");
yearContents.forEach(y => y.style.display = "none");
$("#year1").style.display = "block";

$$(".year-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        yearContents.forEach(y => y.style.display = "none");
        $("#" + btn.dataset.year).style.display = "block";
    });
});

// ======================================================
// Overlays
// ======================================================
const overlayForm = $("#overlay-form");
const maleForm = $("#male-form");
const femaleForm = $("#female-form");
const addStockForm = $("#add-stock-form");

$("#add-entry-btn").addEventListener("click", () => overlayForm.classList.remove("hidden"));
$("#male-btn").addEventListener("click", () => { overlayForm.classList.add("hidden"); maleForm.classList.remove("hidden"); });
$("#female-btn").addEventListener("click", () => { overlayForm.classList.add("hidden"); femaleForm.classList.remove("hidden"); });
$("#add-stock-btn").addEventListener("click", () => addStockForm.classList.remove("hidden"));

document.querySelectorAll(".close-btn").forEach(btn => btn.addEventListener("click", e => {
    let el = e.target;
    while (el && !el.classList.contains("overlay")) el = el.parentElement;
    if (el) el.classList.add("hidden");
}));

// ======================================================
// FRONT-END ONLY DATA (NO DATABASE)
// ======================================================
let students = [];   // simulated student data
let stock = {        // simulated uniform stock
    "boys-polo": { small: 20, medium: 15, large: 10 },
    "shirt": { small: 30, medium: 25, large: 20 },
    "jp": { small: 12, medium: 14, large: 8 }
};

// ======================================================
// Date Navigation
// ======================================================
let currentDate = new Date();
function formatDate(date) {
    return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,"0")}-${String(date.getDate()).padStart(2,"0")}`;
}

// ======================================================
// Dashboard Rendering (front-end only)
// ======================================================
function renderDashboard() {
    const boysBody = $("#dashboard-table-boys tbody");
    const girlsBody = $("#dashboard-table-girls tbody");

    boysBody.innerHTML = "";
    girlsBody.innerHTML = "";

    const today = formatDate(currentDate);

    students
        .filter(s => s.scheduled_date === today)
        .forEach(entry => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${entry.student_id}</td>
                <td>${entry.year}</td>
                <td>${entry.student_name}</td>
                <td>${entry.gender}</td>
            `;

            if (entry.gender === "male") boysBody.appendChild(row);
            else girlsBody.appendChild(row);
        });

    $("#dashboard-date").textContent = today;
}

$("#prev-day-btn").addEventListener("click", () => {
    currentDate.setDate(currentDate.getDate()-1);
    renderDashboard();
});
$("#next-day-btn").addEventListener("click", () => {
    currentDate.setDate(currentDate.getDate()+1);
    renderDashboard();
});

// ======================================================
// Add Student (frontend simulation)
// ======================================================
function addStudent(payload, formEl) {
    students.push(payload);
    formEl.querySelectorAll("input").forEach(i => i.value = "");
    formEl.classList.add("hidden");
    renderDashboard();
}

// Male: form submits to server (no frontend interception)

// Female


// ======================================================
// Stock (frontend only)
// ======================================================
function renderStock() {
    for (const [garment, sizes] of Object.entries(stock)) {
        for (const [size, qty] of Object.entries(sizes)) {
            const td = document.getElementById(`${garment}-${size}`);
            if (td) td.textContent = qty;
        }
    }
}

$("#submit-stock-btn").addEventListener("click", () => {
    const garment = $("#stock-garment").value;
    const size = $("#stock-size").value.trim();
    const quantity = parseInt($("#stock-quantity").value);

    if (!size || isNaN(quantity) || quantity < 1) {
        alert("Enter valid size + quantity");
        return;
    }

    if (!stock[garment]) stock[garment] = {};
    stock[garment][size] = (stock[garment][size] || 0) + quantity;

    renderStock();
    addStockForm.classList.add("hidden");
});

// ======================================================
// DOMContentLoaded
// ======================================================
document.addEventListener("DOMContentLoaded", () => {
    renderDashboard();
    renderStock();
});
