// ======================================================
// UI Utilities
// ======================================================
const $ = sel => document.querySelector(sel);
const $$ = sel => Array.from(document.querySelectorAll(sel));

// ======================================================
// Navigation (Server-side routing)
// ======================================================
// Navigation handled via server-side routes - no client-side section switching

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
    const today = formatDate(currentDate);
    $("#dashboard-date").textContent = today;
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


// ======================================================
// DOMContentLoaded
// ======================================================
document.addEventListener("DOMContentLoaded", () => {
    renderDashboard();

});
