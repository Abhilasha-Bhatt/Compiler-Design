let results = {};
let currentView = "html";

function process() {
    const file = document.getElementById("fileInput").files[0];
    const text = document.getElementById("markdownInput").value;

    const formData = new FormData();

    if (file) {
        formData.append("file", file);
    } else {
        const blob = new Blob([text], { type: "text/plain" });
        formData.append("file", blob, "input.md");
    }

    fetch("/process", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        results = data;
        updateOutput();
    });
}

function setView(view, el) {
    currentView = view;

    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    el.classList.add("active");

    updateOutput();
}

function updateOutput() {
    const output = document.getElementById("output");
    const preview = document.getElementById("preview");

    if (currentView === "preview") {
        output.style.display = "none";
        preview.style.display = "block";
        preview.srcdoc = results["html"] || "<h3>No Preview</h3>";
    } else {
        preview.style.display = "none";
        output.style.display = "block";
        output.textContent = results[currentView] || "";
    }
}