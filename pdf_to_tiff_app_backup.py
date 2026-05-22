"""
PDF to TIFF Converter — Streamlit App
======================================
Converts any uploaded PDF to a multi-page TIFF under a user-selected size limit.

Technique used (same as what was proven to work):
  - pdf2image converts each PDF page to a grayscale PIL image at a given DPI
  - Pillow saves all pages as a single multi-page TIFF using JPEG-in-TIFF compression
  - If the output exceeds the target size, the app automatically retries up to 2 more times
    by lowering the JPEG quality (more aggressive compression each attempt)
  - No LLM, no API calls — 100% local, 100% free to run

How it works (hidden from UI — for developer reference only):
  Each PDF page is rendered at 120 DPI in grayscale, then saved as a single multi-page
  TIFF using JPEG-in-TIFF compression (quality 55 as first attempt). If the file exceeds
  the target size limit, the app retries automatically — twice — by reducing JPEG quality.
  Attempt 1: 120 DPI, JPEG quality 55 (standard sweet spot)
  Attempt 2: 120 DPI, JPEG quality 42 (reduced)
  Attempt 3: 100 DPI, JPEG quality 35 (aggressive)
  After 3 failed attempts it reports failure clearly.
  This is the same technique proven to work on complex scanned bank/form documents.

Run with:
    streamlit run pdf_to_tiff_app.py
"""

import io
import os
import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image

# ──────────────────────────────────────────────
# Page configuration — wide layout to fill screen
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="PDF → TIFF Converter",
    page_icon="🗜️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────
# Primary Red:   #ED1C24  (logo red)
# Deep Crimson:  #B01116
# Charcoal:      #231F20
# Off-white:     #FFF8F8
# Light grey:    #F5F0F0
# ──────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

    /* ── Reset & base ── */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        background-color: #FFF8F8 !important;
    }
    .stApp {
        background-color: #FFF8F8 !important;
        min-height: 100vh;
    }

    /* ── Hide Streamlit chrome ── */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        max-width: 100% !important;
    }

    /* ── Full-screen two-column shell ── */
    .app-shell {
        display: grid;
        grid-template-columns: 380px 1fr;
        min-height: 100vh;
        height: 100vh;
        overflow: hidden;
    }

    /* ── Left panel — red ── */
    .left-panel {
        background: linear-gradient(160deg, #ED1C24 0%, #B01116 60%, #8a0c10 100%);
        padding: 3rem 2.5rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
    }
    .left-panel::before {
        content: '';
        position: absolute;
        top: -80px; right: -80px;
        width: 320px; height: 320px;
        border-radius: 50%;
        background: rgba(255,255,255,0.05);
    }
    .left-panel::after {
        content: '';
        position: absolute;
        bottom: -60px; left: -60px;
        width: 240px; height: 240px;
        border-radius: 50%;
        background: rgba(255,255,255,0.04);
    }
    .brand-mark {
        font-family: 'Playfair Display', serif;
        font-weight: 900;
        font-size: 1.1rem;
        color: rgba(255,255,255,0.7);
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 2.5rem;
    }
    .panel-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.8rem;
        font-weight: 900;
        color: #ffffff;
        line-height: 1.1;
        margin-bottom: 1rem;
        position: relative;
        z-index: 1;
    }
    .panel-subtitle {
        color: rgba(255,255,255,0.75);
        font-size: 0.95rem;
        line-height: 1.6;
        position: relative;
        z-index: 1;
        margin-bottom: 2rem;
    }
    .feature-item {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        color: rgba(255,255,255,0.85);
        font-size: 0.88rem;
        margin-bottom: 0.65rem;
        position: relative;
        z-index: 1;
    }
    .feature-dot {
        width: 7px; height: 7px;
        border-radius: 50%;
        background: rgba(255,255,255,0.6);
        flex-shrink: 0;
    }
    .panel-footer {
        color: rgba(255,255,255,0.4);
        font-size: 0.75rem;
        position: relative;
        z-index: 1;
    }

    /* ── Right panel ── */
    .right-panel {
        background: #FFF8F8;
        padding: 3rem 4rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
        overflow-y: auto;
    }
    .right-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #231F20;
        margin-bottom: 0.4rem;
    }
    .right-sub {
        color: #6b6b6b;
        font-size: 0.92rem;
        margin-bottom: 2rem;
    }

    /* ── Upload zone ── */
    [data-testid="stFileUploader"] {
        border: 2px dashed #ED1C24 !important;
        border-radius: 12px !important;
        background: rgba(237, 28, 36, 0.03) !important;
        padding: 0.5rem !important;
        transition: border-color 0.2s, background 0.2s;
    }
    [data-testid="stFileUploader"]:hover {
        background: rgba(237, 28, 36, 0.06) !important;
    }
    [data-testid="stFileUploadDropzone"] {
        border: none !important;
    }

    /* ── Slider ── */
    [data-testid="stSlider"] {
        padding-top: 0.3rem !important;
    }
    .stSlider > div > div > div > div {
        background: #ED1C24 !important;
    }
    .slider-label {
        font-size: 0.88rem;
        font-weight: 500;
        color: #231F20;
        margin-bottom: 0.2rem;
    }
    .slider-hint {
        font-size: 0.78rem;
        color: #9a9a9a;
        margin-top: 0.1rem;
    }

    /* ── Convert button ── */
    .stButton > button {
        background: linear-gradient(90deg, #ED1C24, #B01116) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 2.5rem !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        letter-spacing: 0.3px !important;
        width: 100% !important;
        margin-top: 1.2rem !important;
        box-shadow: 0 4px 15px rgba(237, 28, 36, 0.3) !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        box-shadow: 0 6px 20px rgba(237, 28, 36, 0.45) !important;
        transform: translateY(-1px);
    }

    /* ── File info card ── */
    .file-card {
        background: #ffffff;
        border: 1px solid #f0e0e0;
        border-left: 4px solid #ED1C24;
        border-radius: 10px;
        padding: 0.8rem 1.2rem;
        margin: 0.8rem 0;
        font-size: 0.88rem;
        color: #231F20;
        box-shadow: 0 2px 8px rgba(237, 28, 36, 0.06);
    }

    /* ── Attempt badge ── */
    .attempt-badge {
        display: inline-block;
        background: #fff0f0;
        color: #B01116;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 20px;
        margin-bottom: 0.5rem;
        border: 1px solid #f5c0c2;
    }

    /* ── Success / failure boxes ── */
    .success-box {
        background: #f0fdf4;
        border: 1.5px solid #22c55e;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-top: 0.8rem;
    }
    .failure-box {
        background: #fff1f2;
        border: 1.5px solid #f43f5e;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-top: 0.8rem;
    }
    .stat-row {
        display: flex;
        gap: 0.7rem;
        margin-top: 0.7rem;
        flex-wrap: wrap;
    }
    .stat-pill {
        background: #f5f0f0;
        border-radius: 6px;
        padding: 0.3rem 0.8rem;
        font-size: 0.8rem;
        color: #555;
        font-family: 'DM Mono', monospace;
    }

    /* ── Download button override ── */
    [data-testid="stDownloadButton"] > button {
        background: linear-gradient(90deg, #231F20, #3a3535) !important;
        margin-top: 0.5rem !important;
        box-shadow: 0 4px 15px rgba(35, 31, 32, 0.2) !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        box-shadow: 0 6px 20px rgba(35, 31, 32, 0.35) !important;
    }

    /* ── Progress / status ── */
    .stProgress > div > div {
        background: #ED1C24 !important;
    }

    /* ── Divider ── */
    hr { border-color: #f0e0e0 !important; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Core conversion function
# ──────────────────────────────────────────────
def convert_pdf_to_tiff(pdf_bytes, dpi, jpeg_quality, progress_bar, status_text):
    """
    Converts PDF bytes → multi-page TIFF in memory.
    Uses grayscale rendering at the given DPI + JPEG-in-TIFF compression.

    Progress bar stages:
      Stage 1 — Rendering pages   (0% → 70%)
      Stage 2 — Grayscale convert (70% → 85%)
      Stage 3 — TIFF encoding     (85% → 100%)
    """

    # Stage 1: Render PDF pages via pdf2image / poppler
    status_text.markdown("⚙️ **Rendering PDF pages...**")
    pdf_pages = convert_from_bytes(pdf_bytes, dpi=dpi, grayscale=True)
    total_pages = len(pdf_pages)

    for i in range(total_pages):
        progress_bar.progress(int((i + 1) / total_pages * 70))

    # Stage 2: Explicit conversion to 8-bit luminance ("L" mode)
    status_text.markdown(f"🎨 **Converting {total_pages} pages to grayscale...**")
    grayscale_images = []
    for i, page in enumerate(pdf_pages):
        grayscale_images.append(page.convert("L"))
        progress_bar.progress(70 + int((i + 1) / total_pages * 15))  # 70→85%

    # Stage 3: Save as multi-page TIFF with JPEG-in-TIFF compression
    status_text.markdown("💾 **Encoding to TIFF (JPEG compression)...**")
    tiff_buffer = io.BytesIO()
    grayscale_images[0].save(
        tiff_buffer,
        format="TIFF",
        save_all=True,
        append_images=grayscale_images[1:],
        compression="jpeg",
        quality=jpeg_quality,
    )

    progress_bar.progress(100)
    tiff_buffer.seek(0)
    return tiff_buffer, total_pages


# ──────────────────────────────────────────────
# Three progressively aggressive attempts.
# The target max size is set by the user slider.
# ──────────────────────────────────────────────
ATTEMPTS = [
    {"dpi": 120, "jpeg_quality": 55, "label": "Attempt 1 — 120 DPI, JPEG quality 55 (standard)"},
    {"dpi": 120, "jpeg_quality": 42, "label": "Attempt 2 — 120 DPI, JPEG quality 42 (reduced)"},
    {"dpi": 100, "jpeg_quality": 35, "label": "Attempt 3 — 100 DPI, JPEG quality 35 (aggressive)"},
]


# ──────────────────────────────────────────────
# Layout: two columns simulating left/right panels
# ──────────────────────────────────────────────
left_col, right_col = st.columns([1.1, 2], gap="small")

# ── LEFT PANEL ──
with left_col:
    st.markdown("""
    <div class="left-panel">
        <div>
            <div class="panel-title">PDF to TIFF<br>Converter</div>
            <div class="panel-subtitle">
                Compress any scanned PDF into a compact multi-page TIFF — 
                fully automatic, fully private.
            </div>
            <div class="feature-item"><div class="feature-dot"></div> Grayscale JPEG-in-TIFF compression</div>
            <div class="feature-item"><div class="feature-dot"></div> Auto-retry with smarter compression</div>
            <div class="feature-item"><div class="feature-dot"></div> Progress tracking per stage</div>
            <div class="feature-item"><div class="feature-dot"></div> Adjustable target file size</div>
            <div class="feature-item"><div class="feature-dot"></div> Works on scanned bank documents</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── RIGHT PANEL ──
with right_col:
    st.markdown('<div class="right-title">Upload & Convert</div>', unsafe_allow_html=True)
    st.markdown('<div class="right-sub">Upload your PDF below, set your size target, and hit Convert.</div>', unsafe_allow_html=True)

    # ── File uploader ──
    uploaded_file = st.file_uploader(
        "Drop your PDF here or click to browse",
        type=["pdf"],
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        pdf_bytes = uploaded_file.read()
        pdf_size_mb = len(pdf_bytes) / (1024 * 1024)
        st.markdown(f"""
        <div class="file-card">
            📄 <strong>{uploaded_file.name}</strong> &nbsp;·&nbsp; {pdf_size_mb:.2f} MB
        </div>
        """, unsafe_allow_html=True)

    # ── Target size slider ──
    st.markdown('<div class="slider-label">🎯 Target file size limit (MB)</div>', unsafe_allow_html=True)
    max_size_mb = st.slider(
        label="Target size",
        min_value=2.0,
        max_value=10.0,
        value=3.0,
        step=0.5,
        label_visibility="collapsed",
    )
    st.markdown(
        f'<div class="slider-hint">The converter will aim to produce a TIFF under <strong>{max_size_mb:.1f} MB</strong>. '
        f'Higher limits = better image quality.</div>',
        unsafe_allow_html=True,
    )

    # ── Convert button (always visible, disabled until file uploaded) ──
    convert_clicked = st.button(
        "Convert to TIFF →",
        disabled=(uploaded_file is None),
        use_container_width=True,
    )

    # ── Conversion logic ──
    if convert_clicked and uploaded_file is not None:
        st.markdown("---")
        final_tiff = None
        final_size_mb = None
        final_pages = None
        success = False

        for attempt_num, params in enumerate(ATTEMPTS, start=1):
            st.markdown(f'<div class="attempt-badge">🔁 {params["label"]}</div>', unsafe_allow_html=True)

            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                tiff_buffer, num_pages = convert_pdf_to_tiff(
                    pdf_bytes=pdf_bytes,
                    dpi=params["dpi"],
                    jpeg_quality=params["jpeg_quality"],
                    progress_bar=progress_bar,
                    status_text=status_text,
                )

                size_bytes = tiff_buffer.getbuffer().nbytes
                size_mb = size_bytes / (1024 * 1024)

                status_text.empty()
                progress_bar.empty()

                if size_mb <= max_size_mb:
                    # ✅ Success
                    final_tiff = tiff_buffer
                    final_size_mb = size_mb
                    final_pages = num_pages
                    success = True

                    st.markdown(f"""
                    <div class="success-box">
                        <strong>✅ Conversion successful on attempt {attempt_num}!</strong><br>
                        <div class="stat-row">
                            <span class="stat-pill">📄 {num_pages} pages</span>
                            <span class="stat-pill">📦 {size_mb:.2f} MB</span>
                            <span class="stat-pill">🖼️ {params['dpi']} DPI · JPEG q{params['jpeg_quality']}</span>
                            <span class="stat-pill">🎯 Limit: {max_size_mb:.1f} MB</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    break
                else:
                    remaining = len(ATTEMPTS) - attempt_num
                    retry_msg = "Retrying with more compression..." if remaining > 0 else ""
                    st.warning(f"⚠️ Attempt {attempt_num} produced {size_mb:.2f} MB — exceeds {max_size_mb:.1f} MB limit. {retry_msg}")

            except Exception as e:
                status_text.empty()
                progress_bar.empty()
                remaining = len(ATTEMPTS) - attempt_num
                retry_msg = "Retrying..." if remaining > 0 else ""
                st.warning(f"⚠️ Attempt {attempt_num} failed with error: `{e}`. {retry_msg}")

        # ── Final outcome ──
        if success and final_tiff is not None:
            output_filename = os.path.splitext(uploaded_file.name)[0] + ".tiff"
            st.download_button(
                label=f"⬇️ Download TIFF  ({final_size_mb:.2f} MB · {final_pages} pages)",
                data=final_tiff,
                file_name=output_filename,
                mime="image/tiff",
                use_container_width=True,
            )
        else:
            st.markdown(f"""
            <div class="failure-box">
                <strong>❌ Conversion failed after 3 attempts.</strong><br><br>
                All three attempts produced a TIFF larger than {max_size_mb:.1f} MB, or encountered 
                an error. This can happen with very large PDFs or high-density colour imagery.<br><br>
                <strong>What you can try:</strong><br>
                • Increase the target size limit using the slider above.<br>
                • Split the PDF into smaller chunks before uploading.<br>
                • Convert colour pages to grayscale in Acrobat first.
            </div>
            """, unsafe_allow_html=True)