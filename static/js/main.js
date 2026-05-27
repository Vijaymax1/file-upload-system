/* ══════════════════════════════════════════════
   FileVault — Frontend Logic
   ══════════════════════════════════════════════ */

(function () {
  "use strict";

  // ── Elements ──────────────────────────────────
  const dropZone   = document.getElementById("dropZone");
  const fileInput  = document.getElementById("fileInput");
  const filePreview = document.getElementById("filePreview");
  const previewThumb = document.getElementById("previewThumb");
  const previewName  = document.getElementById("previewName");
  const previewSize  = document.getElementById("previewSize");
  const clearBtn     = document.getElementById("clearFile");
  const uploadBtn    = document.getElementById("uploadBtn");
  const btnLabel     = document.getElementById("btnLabel");
  const uploadForm   = document.getElementById("uploadForm");

  if (!dropZone || !fileInput) return;  // Safety guard

  // ── Allowed Extensions (mirrors server config) ─
  const ALLOWED_IMG = new Set(["png", "jpg", "jpeg", "gif", "webp", "svg"]);
  const ALLOWED_DOC = new Set(["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "csv"]);
  const ALL_ALLOWED = new Set([...ALLOWED_IMG, ...ALLOWED_DOC]);

  // ── Helpers ───────────────────────────────────
  function getExt(filename) {
    const parts = filename.split(".");
    return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : "";
  }

  function humanSize(bytes) {
    if (bytes < 1024)       return `${bytes} B`;
    if (bytes < 1048576)    return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1073741824) return `${(bytes / 1048576).toFixed(1)} MB`;
    return `${(bytes / 1073741824).toFixed(1)} GB`;
  }

  function getFileEmoji(ext) {
    if (ALLOWED_IMG.has(ext))              return "🖼";
    if (ext === "pdf")                     return "📄";
    if (["doc","docx"].includes(ext))      return "📝";
    if (["xls","xlsx","csv"].includes(ext)) return "📊";
    if (["ppt","pptx"].includes(ext))      return "📑";
    return "📁";
  }

  // ── Render selected file preview ──────────────
  function showPreview(file) {
    const ext = getExt(file.name);

    previewName.textContent = file.name;
    previewSize.textContent = humanSize(file.size);

    // Clear previous content
    previewThumb.innerHTML = "";

    if (ALLOWED_IMG.has(ext) && file.type.startsWith("image/")) {
      const img = document.createElement("img");
      img.style.cssText = "width:100%;height:100%;object-fit:cover;border-radius:3px;";
      const reader = new FileReader();
      reader.onload = (e) => { img.src = e.target.result; };
      reader.readAsDataURL(file);
      previewThumb.appendChild(img);
    } else {
      previewThumb.textContent = getFileEmoji(ext);
      previewThumb.style.cssText = "display:flex;align-items:center;justify-content:center;font-size:1.4rem;";
    }

    filePreview.style.display = "flex";
  }

  // ── Update upload button state ─────────────────
  function updateButton(file) {
    if (!file) {
      uploadBtn.disabled = true;
      btnLabel.textContent = "Select a file to upload";
      return;
    }

    const ext = getExt(file.name);

    if (!ALL_ALLOWED.has(ext)) {
      uploadBtn.disabled = true;
      btnLabel.textContent = `".${ext}" not allowed`;
      return;
    }

    if (file.size > 16 * 1024 * 1024) {
      uploadBtn.disabled = true;
      btnLabel.textContent = "File exceeds 16 MB limit";
      return;
    }

    uploadBtn.disabled = false;
    btnLabel.textContent = `Upload ${file.name.length > 28 ? file.name.slice(0, 25) + "…" : file.name}`;
  }

  // ── Handle chosen file ─────────────────────────
  function handleFile(file) {
    if (!file) return;
    showPreview(file);
    updateButton(file);
  }

  // ── Clear selection ───────────────────────────
  function clearSelection() {
    fileInput.value = "";
    filePreview.style.display = "none";
    uploadBtn.disabled = true;
    btnLabel.textContent = "Select a file to upload";
  }

  // ── File input change ─────────────────────────
  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (file) handleFile(file);
  });

  // ── Clear button ──────────────────────────────
  clearBtn.addEventListener("click", clearSelection);

  // ── Drag-and-drop events ──────────────────────
  ["dragenter", "dragover"].forEach((evt) => {
    dropZone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropZone.classList.add("drop-zone--active");
    });
  });

  ["dragleave", "dragend"].forEach((evt) => {
    dropZone.addEventListener(evt, () => {
      dropZone.classList.remove("drop-zone--active");
    });
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drop-zone--active");

    const file = e.dataTransfer?.files[0];
    if (!file) return;

    // Inject into the input (so it submits with the form)
    const dt = new DataTransfer();
    dt.items.add(file);
    fileInput.files = dt.files;

    handleFile(file);
  });

  // ── Upload form submit — show loading state ───
  uploadForm.addEventListener("submit", (e) => {
    if (uploadBtn.disabled) {
      e.preventDefault();
      return;
    }
    uploadBtn.disabled = true;
    btnLabel.textContent = "Uploading…";
    uploadBtn.querySelector(".btn-upload__arrow").style.transform = "rotate(45deg)";
  });

  // ── Delete confirmation ───────────────────────
  window.confirmDelete = function (filename) {
    return window.confirm(`Delete "${filename}"?\n\nThis action cannot be undone.`);
  };

  // ── Auto-dismiss flash messages ───────────────
  document.querySelectorAll(".flash").forEach((el) => {
    setTimeout(() => {
      el.style.transition = "opacity 0.4s ease, transform 0.4s ease";
      el.style.opacity = "0";
      el.style.transform = "translateY(-6px)";
      setTimeout(() => el.remove(), 400);
    }, 5000);
  });

})();
