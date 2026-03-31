function upload() {
    const file = document.getElementById("fileInput").files[0];
    const format = document.getElementById("format").value;

    if (!file) {
        alert("Upload file first!");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("format", format);

    fetch("/process", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("output").textContent = data.result;
    })
    .catch(err => console.error(err));
}