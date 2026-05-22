# 🗜️ PDF → TIFF Converter

> **A smart, web-based tool that converts large PDF files into compressed, size-controlled TIFF images — built with Streamlit and deployed on Streamlit Cloud.**

---

## 📌 Overview

**PDF → TIFF Converter** is a lightweight yet intelligent Streamlit application that takes a PDF file (3 MB or larger) and converts it into a multi-page grayscale TIFF, automatically adjusting quality settings to hit your target file-size limit. No local installation required once deployed — just open the URL and convert.

---

## ✨ Features

🎯 **Smart Size Targeting** — Set a target output size (in MB) using a slider, and the app automatically calculates the optimal DPI and JPEG quality combination to reach that goal.

🔁 **3-Attempt Auto-Retry** — If the first conversion attempt exceeds your target, the app automatically retries two more times with progressively lower DPI and quality settings, so you don't have to tweak anything manually.

🖤 **Grayscale TIFF Output** — All output is rendered in grayscale with JPEG compression inside the TIFF container, keeping file sizes lean while maintaining readability.

📐 **Dynamic Slider Range** — The target file size slider always adapts to the uploaded file's actual size, so you can never accidentally set an impossible target.

⚠️ **Smart Validation** — Files already under 3 MB are flagged immediately with a helpful message since they don't need compression.

📥 **One-Click Download** — After a successful conversion, a download button appears showing the final file size and page count.

---

## 🖥️ App Interface

The app uses a clean **two-column layout**:

| Left Column | Right Column |
|---|---|
| 📂 Upload your PDF file | ⚙️ Live conversion progress |
| 🎚️ Set your target size with a slider | ✅ Success / ❌ Failure result card |
| 🔴 "Convert to TIFF →" button | ⬇️ Download button (on success) |

---

## 🧠 How the Smart Compression Works

The core logic lives in `params_for_target()`. Rather than using fixed DPI or quality settings, the app **calculates them dynamically** based on the ratio between your target size and the original file size.

```
ratio = target_mb / pdf_size_mb
```

A higher ratio (meaning less compression needed) gives higher DPI (up to 200) and higher JPEG quality (up to 90). A lower ratio (heavy compression needed) gives lower DPI (as low as 72) and lower quality (as low as 20). Two automatic fallback attempts step down by ~12 units each for both DPI and quality if the first result is still too large.

---

## 📁 Project Structure

```
📦 pdf-tiff-converter/
├── 📄 pdf_to_tiff_app.py        ← Main Streamlit application
├── 📄 requirements.txt          ← Python dependencies
├── 📄 packages.txt              ← System-level dependencies (Poppler)
└── 📂 .streamlit/
    └── 📄 config.toml           ← Streamlit server configuration
```

---

## 🔧 Dependencies

### Python Libraries (`requirements.txt`)

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | ≥ 1.32.0 | Web app framework |
| `pdf2image` | ≥ 1.17.0 | Converts PDF pages to images |
| `Pillow` | ≥ 10.0.0 | Image processing and TIFF encoding |

### System Library (`packages.txt`)

| Package | Purpose |
|---|---|
| `poppler-utils` | Required by `pdf2image` to render PDF pages |

> ⚠️ **Important:** `poppler-utils` must be listed in `packages.txt` at the root of your repository. Streamlit Cloud reads this file and runs `apt-get install` automatically before starting your app.

---

## 🚀 Deploying to Streamlit Cloud

### What You Need Before Starting

You need a **GitHub account** and a **Streamlit Cloud account** (free at [share.streamlit.io](https://share.streamlit.io) — sign in with GitHub). Streamlit Cloud deploys directly from GitHub, not from file uploads.

---

### Step 1 — Create a GitHub Repository

Go to [github.com](https://github.com), click the **"+"** icon top-right, and choose **"New repository"**. Name it something like `pdf-tiff-converter`, set it to **Public** (required for the free tier), and click **"Create repository"**. Do not initialize it with a README since you'll be uploading your own files.

---

### Step 2 — Create the `.streamlit/config.toml` File

Before uploading, create a folder called `.streamlit` in your repo and inside it a file called `config.toml` with this content:

```toml
[server]
headless = true

[browser]
gatherUsageStats = false
```

This prevents Streamlit from showing unnecessary prompts on first load in the cloud environment.

---

### Step 3 — Upload All Files to the Repository

On the repository page click **"uploading an existing file"**, then drag and drop all four files at once:

```
pdf_to_tiff_app.py
requirements.txt
packages.txt
.streamlit/config.toml
```

Commit them with any message like `"initial upload"`.

---

### Step 4 — Deploy on Streamlit Cloud

Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub. Click **"New app"**, then fill in three fields:

- **Repository:** your repo name
- **Branch:** `main`
- **Main file path:** `pdf_to_tiff_app.py`

Click **"Deploy"**. Streamlit Cloud will install everything from `requirements.txt` and `packages.txt` automatically. The first build takes about **2 to 4 minutes**.

---

### Step 5 — Verify It Works

Once deployed, you'll get a public URL like `https://yourname-pdf-tiff-converter-xxx.streamlit.app`. Open it and test by uploading a PDF over 3 MB.

> 🔍 If you see an error mentioning `pdftoppm` or `poppler`, it means the `packages.txt` file was not picked up. Double-check that the filename is exactly `packages.txt` with no extension and that it sits at the **root** of the repository, not inside any folder.

---

## 💻 Running Locally

If you want to run the app on your own machine:

**1. Install system dependency (Poppler)**

```bash
# macOS
brew install poppler

# Ubuntu / Debian
sudo apt-get install poppler-utils

# Windows
# Download from https://github.com/oschwartz10612/poppler-windows/releases
# and add the "bin" folder to your PATH
```

**2. Install Python dependencies**

```bash
pip install -r requirements.txt
```

**3. Run the app**

```bash
streamlit run pdf_to_tiff_app.py
```

The app will open automatically at `http://localhost:8501`.

---

## 📋 Repository Structure Summary

All four files sit at the root level of the repository **except** `config.toml`, which goes inside a `.streamlit` folder:

```
pdf_to_tiff_app.py          ← root
requirements.txt            ← root
packages.txt                ← root
.streamlit/config.toml      ← one level deep
```

That's everything Streamlit Cloud needs — no Dockerfile, no server configuration, nothing else.

---

## 🙏 Acknowledgements

Built with [Streamlit](https://streamlit.io/) · PDF rendering powered by [Poppler](https://poppler.freedesktop.org/) via [pdf2image](https://github.com/Belval/pdf2image) · Image processing by [Pillow](https://python-pillow.org/)

---

*Made with ❤️ for fast, no-fuss PDF compression.*