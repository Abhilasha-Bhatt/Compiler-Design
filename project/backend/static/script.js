let results = {};
let previewHtml = "";
let currentView = "html";

let liveTimer = null;
let liveInFlight = false;
let previewWindow = null;

const RECENT_KEY = "mdci_recent_files_v1";
const RECENT_MAX = 6;

function setStatus(text, type) {
    const el = document.getElementById("status");
    if (!el) return;
    el.textContent = text;
    el.classList.remove("good", "bad");
    if (type) el.classList.add(type);
}

function setRunDisabled(disabled) {
    const btn = document.getElementById("runBtn");
    if (btn) btn.disabled = disabled;
}

function getEditorText() {
    const t = document.getElementById("markdownInput");
    return t ? t.value : "";
}

function escapeHtml(s) {
    return String(s)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

function applyInlineHighlight(lineEscaped) {
    let out = lineEscaped;

    // Images: ![alt](url)
    out = out.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (m, alt, url) => {
        return `<span class="tok-image">![${alt}](${url})</span>`;
    });

    // Links: [text](url)
    out = out.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (m, text, url) => {
        return `<span class="tok-link">[${text}](${url})</span>`;
    });

    // Inline code: `code`
    out = out.replace(/`([^`]+)`/g, (m, code) => {
        return `<span class="tok-code">\`${code}\`</span>`;
    });

    // Bold: **text**
    out = out.replace(/\*\*([^*]+)\*\*/g, (m, bold) => {
        return `<span class="tok-bold">**${bold}**</span>`;
    });

    // Italic: *text*
    out = out.replace(/\*([^*]+)\*/g, (m, italic) => {
        return `<span class="tok-italic">*${italic}*</span>`;
    });

    return out;
}

function highlightMarkdown(md) {
    const text = String(md || "").replace(/\r\n/g, "\n");
    const lines = text.split("\n");

    let inFence = false;
    const outLines = [];

    for (const rawLine of lines) {
        const line = rawLine;
        const trimmed = line.trim();

        // Code fences
        if (trimmed.startsWith("```")) {
            inFence = !inFence;
            const esc = escapeHtml(line);
            outLines.push(`<span class="tok-fence">${esc}</span>`);
            continue;
        }

        const esc = escapeHtml(line);

        if (inFence) {
            outLines.push(`<span class="tok-fence">${esc || " "}</span>`);
            continue;
        }

        // Headings: ### Title
        const headingMatch = line.match(/^(\#{1,6})\s+(.*)$/);
        if (headingMatch) {
            const hashes = headingMatch[1];
            const rest = headingMatch[2];
            outLines.push(
                `<span class="tok-heading">${escapeHtml(hashes)}</span> ${applyInlineHighlight(escapeHtml(rest))}`
            );
            continue;
        }

        // Blockquote: > text
        const quoteMatch = line.match(/^\>\s?(.*)$/);
        if (quoteMatch) {
            outLines.push(`<span class="tok-quote">&gt; ${applyInlineHighlight(escapeHtml(quoteMatch[1]))}</span>`);
            continue;
        }

        // Unordered list: - item
        const ulMatch = line.match(/^\-\s+(.*)$/);
        if (ulMatch) {
            outLines.push(`<span class="tok-list">&minus;</span> ${applyInlineHighlight(escapeHtml(ulMatch[1]))}`);
            continue;
        }

        // Ordered list: 1. item
        const olMatch = line.match(/^(\d+)\.\s+(.*)$/);
        if (olMatch) {
            outLines.push(`<span class="tok-list">${escapeHtml(olMatch[1])}.</span> ${applyInlineHighlight(escapeHtml(olMatch[2]))}`);
            continue;
        }

        // Default: inline-only
        outLines.push(applyInlineHighlight(esc));
    }

    return outLines.join("\n");
}

function syncHighlightScroll() {
    const textarea = document.getElementById("markdownInput");
    const highlight = document.getElementById("editorHighlight");
    if (!textarea || !highlight) return;
    highlight.scrollTop = textarea.scrollTop;
    highlight.scrollLeft = textarea.scrollLeft;
}

function updateHighlight() {
    const highlight = document.getElementById("editorHighlight");
    if (!highlight) return;
    highlight.innerHTML = highlightMarkdown(getEditorText());
    syncHighlightScroll();
}

function isPreviewWindowOpen() {
    return previewWindow && !previewWindow.closed;
}

function updatePreviewWindowHtml(htmlOrNull, errorOrNull) {
    if (!isPreviewWindowOpen()) return;

    if (errorOrNull) {
        previewWindow.document.open();
        previewWindow.document.write(
            `<!doctype html><html><head><meta charset="utf-8"><title>Preview</title></head>` +
            `<body style="margin:0;padding:18px;font-family:system-ui;background:#0b1020;color:#ff4d6d">` +
            `<h3 style="margin:0 0 10px 0">Preview error</h3>` +
            `<pre style="white-space:pre-wrap;word-break:break-word;color:#ffb3c0">${escapeHtml(errorOrNull)}</pre>` +
            `</body></html>`
        );
        previewWindow.document.close();
        return;
    }

    previewWindow.document.open();
    previewWindow.document.write(htmlOrNull || "<h3 style='font-family:system-ui'>No preview yet</h3>");
    previewWindow.document.close();
}

function highlightHtmlEscaped(escLine) {
    // Basic: highlight &lt;...&gt; tags + attributes + quoted strings
    return escLine
        .replace(/(&lt;\/?)([A-Za-z][A-Za-z0-9-]*)([^&]*?)(&gt;)/g, (m, p1, tag, rest, p4) => {
            let r = rest || "";
            r = r.replace(/([A-Za-z_:][A-Za-z0-9_:\-\.]*)(=)/g, `<span class="out-attr">$1</span><span class="out-punc">$2</span>`);
            r = r.replace(/(&quot;.*?&quot;|&#x27;.*?&#x27;)/g, `<span class="out-str">$1</span>`);
            return `<span class="out-punc">${p1}</span><span class="out-tag">${tag}</span>${r}<span class="out-punc">${p4}</span>`;
        })
        .replace(/(&quot;.*?&quot;|&#x27;.*?&#x27;)/g, `<span class="out-str">$1</span>`);
}

function highlightJsonEscaped(escLine) {
    // Very lightweight JSON lexer on an already-escaped line.
    let out = escLine;
    out = out.replace(/(&quot;(?:\\.|[^&])*?&quot;)(\s*:)?/g, (m, s, colon) => {
        if (colon) {
            return `<span class="out-key">${s}</span><span class="out-punc">${colon}</span>`;
        }
        return `<span class="out-str">${s}</span>`;
    });
    out = out.replace(/\b(-?\d+(?:\.\d+)?)\b/g, `<span class="out-num">$1</span>`);
    out = out.replace(/\b(true|false|null)\b/g, `<span class="out-bool">$1</span>`);
    out = out.replace(/([{}[\],])/g, `<span class="out-punc">$1</span>`);
    return out;
}

function highlightOutputLine(rawLine, view) {
    const esc = escapeHtml(rawLine);
    if (view === "html") return highlightHtmlEscaped(esc);
    if (view === "json") return highlightJsonEscaped(esc);
    return esc;
}

function renderCode(text, view) {
    const output = document.getElementById("output");
    if (!output) return;

    const s = (text === undefined || text === null) ? "" : String(text);
    const lines = s.split("\n");
    if (!lines.length) {
        output.textContent = "";
        return;
    }

    output.innerHTML = lines.map((line, idx) => {
        const colored = highlightOutputLine(line, view || currentView);
        return `<div class="code-line"><span class="code-ln">${idx + 1}</span><span class="code-txt">${colored}</span></div>`;
    }).join("");
}

function updateOutput(forceText) {
    const output = document.getElementById("output");
    if (!output) return;

    const val = (results && results[currentView]) ? results[currentView] : "";
    if (forceText && results && results.error) {
        renderCode(String(results.error), currentView);
        return;
    }
    const body = forceText ? (val || (results && results.error ? results.error : "")) : (val || "");
    if (!body && !forceText) {
        const placeholder = output.dataset ? output.dataset.placeholder : "";
        output.textContent = placeholder || "";
        return;
    }
    renderCode(body, currentView);
}

function clearEditor() {
    const input = document.getElementById("markdownInput");
    if (input) input.value = "";
    results = {};
    previewHtml = "";
    updateHighlight();
    updateOutput(true);
    setStatus("Ready");
}

async function process() {
    const text = getEditorText();

    const formData = new FormData();
    const blob = new Blob([text], { type: "text/plain" });
    formData.append("file", blob, "input.md");

    setRunDisabled(true);
    setStatus("Compiling…");

    try {
        const res = await fetch("/process", { method: "POST", body: formData });
        const payload = await res.json().catch(() => null);

        if (!res.ok) {
            results = payload || {};
            setStatus(`Failed (HTTP ${res.status})`, "bad");
            updateOutput(true);
            return;
        }

        results = payload || {};
        previewHtml = results.html || "";
        setStatus("Done", "good");
        updateOutput();
        if (isPreviewWindowOpen()) {
            updatePreviewWindowHtml(previewHtml || "", results && results.error ? String(results.error) : null);
        }
    } catch (err) {
        results = { error: String(err) };
        setStatus("Failed", "bad");
        updateOutput(true);
        if (isPreviewWindowOpen()) {
            updatePreviewWindowHtml(null, String(err));
        }
    } finally {
        setRunDisabled(false);
    }
}

function setView(view, el) {
    currentView = view;

    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    if (el) el.classList.add("active");

    updateOutput();
}

function scheduleLivePreview() {
    if (!isPreviewWindowOpen()) return;
    if (liveTimer) clearTimeout(liveTimer);
    liveTimer = setTimeout(() => {
        compileLivePreviewNow().catch(() => { /* ignore */ });
    }, 450);
}

async function compileLivePreviewNow() {
    if (liveInFlight) return;
    if (!isPreviewWindowOpen()) return;

    const text = getEditorText();
    const formData = new FormData();
    const blob = new Blob([text], { type: "text/plain" });
    formData.append("file", blob, "input.md");

    liveInFlight = true;
    try {
        const res = await fetch("/process_html", { method: "POST", body: formData });
        const payload = await res.json().catch(() => null);

        if (!res.ok) {
            previewHtml = "";
            results = payload || {};
            setStatus(`Preview failed (HTTP ${res.status})`, "bad");
            updatePreviewWindowHtml(null, results && results.error ? String(results.error) : `HTTP ${res.status}`);
            return;
        }

        previewHtml = payload && payload.html ? payload.html : "";
        results = results || {};
        setStatus("Preview updated", "good");
        updatePreviewWindowHtml(previewHtml || "", null);
    } finally {
        liveInFlight = false;
    }
}

function openPreview() {
    if (!isPreviewWindowOpen()) {
        previewWindow = window.open("", "mdci_preview");
        if (!previewWindow) {
            setStatus("Popup blocked (allow popups)", "bad");
            return;
        }
    }

    setStatus("Opening preview…", "good");
    compileLivePreviewNow().catch(() => {
        updatePreviewWindowHtml(null, "Failed to build preview");
    });
}

function downloadText(filename, text, mimeType) {
    const blob = new Blob([text || ""], { type: mimeType || "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();

    setTimeout(() => URL.revokeObjectURL(url), 1000);
}

async function exportAndDownload(kind) {
    if (!kind) return;

    setRunDisabled(true);
    setStatus("Preparing export…");

    try {
        const text = getEditorText();
        const formData = new FormData();
        const blob = new Blob([text], { type: "text/plain" });
        formData.append("file", blob, "input.md");

        const res = await fetch("/process", { method: "POST", body: formData });
        const payload = await res.json().catch(() => null);

        if (!res.ok) {
            results = payload || {};
            setStatus(`Export failed (HTTP ${res.status})`, "bad");
            updateOutput(true);
            return;
        }

        results = payload || {};
        previewHtml = results.html || previewHtml;

        setStatus("Export ready", "good");

        // Trigger real file download via backend route (avoids browser blob download restrictions).
        window.location.href = `/download_output?kind=${encodeURIComponent(kind)}`;
    } catch (err) {
        results = { error: String(err) };
        setStatus("Export failed", "bad");
        updateOutput(true);
    } finally {
        setRunDisabled(false);
    }
}

function handleExport(selectEl) {
    if (!selectEl || !selectEl.value) return;
    const kind = selectEl.value;
    // Reset right away so exporting the same option again still triggers onchange.
    selectEl.value = "";
    exportAndDownload(kind).catch(() => { /* ignore */ });
}

function downloadCurrent() {
    const map = {
        html: "html",
        typst: "typst",
        tokens: "tokens",
        ast: "ast",
        json: "json",
    };

    const kind = map[currentView] || "html";
    exportAndDownload(kind).catch(() => { /* ignore */ });
}

function loadRecentFiles() {
    try {
        const raw = localStorage.getItem(RECENT_KEY);
        if (!raw) return [];
        const parsed = JSON.parse(raw);
        if (!Array.isArray(parsed)) return [];
        return parsed;
    } catch {
        return [];
    }
}

function saveRecentFiles(list) {
    try {
        localStorage.setItem(RECENT_KEY, JSON.stringify(list));
    } catch {
        /* ignore */
    }
}

function renderRecentSelect() {
    const select = document.getElementById("recentSelect");
    if (!select) return;

    const list = loadRecentFiles();
    select.innerHTML = `<option value="">Recent</option>` + list
        .map((item, idx) => {
            const name = item && item.name ? item.name : `Recent ${idx + 1}`;
            return `<option value="${idx}">${escapeHtml(name)}</option>`;
        })
        .join("");
}

function addRecentFile(entry) {
    const list = loadRecentFiles();
    const safeEntry = {
        name: entry && entry.name ? entry.name : "input.md",
        content: entry && entry.content ? entry.content : "",
        ts: Date.now()
    };

    // Dedupe by content (best effort, but works for small inputs)
    const key = safeEntry.content.slice(0, 2000);
    const existingIdx = list.findIndex(it => (it && it.content ? it.content.slice(0, 2000) : "") === key);
    if (existingIdx >= 0) list.splice(existingIdx, 1);

    list.unshift(safeEntry);
    const trimmed = list.slice(0, RECENT_MAX);
    saveRecentFiles(trimmed);
    renderRecentSelect();
}

function loadRecent(indexStr) {
    const select = document.getElementById("recentSelect");
    if (select && indexStr) select.value = indexStr;

    const idx = parseInt(indexStr, 10);
    if (Number.isNaN(idx)) return;

    const list = loadRecentFiles();
    const item = list[idx];
    if (!item) return;

    const textarea = document.getElementById("markdownInput");
    if (textarea) textarea.value = item.content || "";

    results = {};
    previewHtml = "";

    updateHighlight();
    updateOutput(true);

    setStatus("Loaded recent", "good");
    if (currentView === "preview") {
        compileLivePreviewNow().catch(() => { /* ignore */ });
    }
}

function init() {
    updateHighlight();
    updateOutput();

    // Scroll sync for syntax highlighting layer
    const textarea = document.getElementById("markdownInput");
    if (textarea) {
        textarea.addEventListener("scroll", syncHighlightScroll);
        textarea.addEventListener("input", () => {
            updateHighlight();
            scheduleLivePreview();
        });
    }

    renderRecentSelect();

    // Load file contents into the editor + remember in Recent
    const fileInput = document.getElementById("fileInput");
    if (fileInput) {
        fileInput.addEventListener("change", () => {
            const file = fileInput.files && fileInput.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = () => {
                const content = String(reader.result || "");
                const textarea = document.getElementById("markdownInput");
                if (textarea) textarea.value = content;

                addRecentFile({ name: file.name, content });

                results = {};
                previewHtml = "";
                updateHighlight();
                updateOutput(true);

                setStatus("Loaded file", "good");
                if (currentView === "preview") {
                    compileLivePreviewNow().catch(() => { /* ignore */ });
                }

                // allow selecting the same file again
                fileInput.value = "";
            };

            reader.onerror = () => {
                setStatus("Failed to read file", "bad");
                fileInput.value = "";
            };

            reader.readAsText(file);
        });
    }

    // Shortcuts
    document.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
            e.preventDefault();
            process().catch(() => { /* ignore */ });
        }
        if ((e.ctrlKey || e.metaKey) && (e.key === "l" || e.key === "L")) {
            e.preventDefault();
            clearEditor();
        }
    });
}

// Expose functions used by HTML onclick handlers
window.process = process;
window.setView = setView;
window.clearEditor = clearEditor;
window.loadRecent = loadRecent;
window.handleExport = handleExport;
window.openPreview = openPreview;
window.downloadCurrent = downloadCurrent;

window.addEventListener("DOMContentLoaded", init);