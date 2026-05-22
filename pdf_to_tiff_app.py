"""
PDF to TIFF Converter — Streamlit App
"""

import io
import os
import math
import streamlit as st
from pdf2image import convert_from_bytes

st.set_page_config(
    page_title="PDF → TIFF Converter",
    page_icon="🗜️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; background: #f5f5f5 !important; }
    .stApp { background: #f5f5f5 !important; }
    #MainMenu, footer, header { visibility: hidden; }

    /* Outer wrapper: 80% wide, centred */
    .block-container {
        max-width: 82% !important;
        padding-top: 1.6rem !important;
        padding-bottom: 1rem !important;
        margin: 0 auto !important;
    }

    /* Top header bar */
    .top-bar {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        background: linear-gradient(90deg, #ED1C24 0%, #B01116 100%);
        border-radius: 14px;
        padding: 0.85rem 1.5rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 4px 18px rgba(176,17,22,0.25);
    }
    .top-bar-icon {
        font-size: 1.5rem;
        background: rgba(255,255,255,0.18);
        border-radius: 9px;
        width: 42px; height: 42px;
        display: flex; align-items: center; justify-content: center;
        flex-shrink: 0;
    }
    .top-bar-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #fff;
        letter-spacing: 0.01em;
    }

    .col-label {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #B01116;
        margin-bottom: 0.6rem;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed #e0c8c8 !important;
        border-radius: 10px !important;
        background: #fdf6f6 !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #ED1C24 !important;
    }
    [data-testid="stFileUploadDropzone"] { border: none !important; background: transparent !important; }

    /* File chip */
    .file-chip {
        background: #fff5f5;
        border-left: 3px solid #ED1C24;
        border-radius: 7px;
        padding: 0.4rem 0.9rem;
        font-size: 0.82rem;
        margin-top: 0.4rem;
        color: #444;
    }
    .fname { font-weight: 600; color: #231F20; }
    .fsize { color: #999; margin-left: 0.4rem; font-size: 0.76rem; }

    /* Error chip */
    .err-chip {
        background: #fff0f0;
        border-left: 3px solid #ED1C24;
        border-radius: 7px;
        padding: 0.5rem 0.9rem;
        font-size: 0.82rem;
        margin-top: 0.6rem;
        color: #991b1b;
        font-weight: 500;
    }

    /* Slider */
    [data-testid="stSlider"] { padding-top: 0 !important; }
    .stSlider > div > div > div > div { background: #ED1C24 !important; }
    .slider-label {
        font-size: 0.7rem; font-weight: 700; letter-spacing: 0.09em;
        text-transform: uppercase; color: #B01116; margin-bottom: 0.4rem;
    }
    .slider-info { font-size: 0.76rem; color: #aaa; margin-top: 0.2rem; }

    /* Divider */
    .hr { height: 1px; background: #f0e8e8; margin: 0.7rem 0; }

    /* Convert button */
    .stButton > button {
        background: linear-gradient(90deg, #ED1C24, #B01116) !important;
        color: #fff !important; border: none !important;
        border-radius: 9px !important; padding: 0.68rem 1.5rem !important;
        font-weight: 600 !important; font-size: 0.92rem !important;
        width: 100% !important; margin-top: 0.4rem !important;
        box-shadow: 0 3px 14px rgba(237,28,36,0.3) !important;
        transition: all 0.18s !important;
    }
    .stButton > button:hover:not(:disabled) { box-shadow: 0 5px 22px rgba(237,28,36,0.45) !important; transform: translateY(-1px); }
    .stButton > button:disabled { background: #e0d8d8 !important; color: #bbb !important; box-shadow: none !important; }

    /* Download button */
    [data-testid="stDownloadButton"] > button {
        background: linear-gradient(90deg, #1a6b35, #125228) !important;
        color: #fff !important; border: none !important;
        border-radius: 9px !important; padding: 0.68rem 1.5rem !important;
        font-weight: 600 !important; font-size: 0.92rem !important;
        width: 100% !important;
        box-shadow: 0 3px 14px rgba(26,107,53,0.28) !important;
        transition: all 0.18s !important; margin-top: 0.8rem !important;
    }
    [data-testid="stDownloadButton"] > button:hover { box-shadow: 0 5px 22px rgba(26,107,53,0.42) !important; transform: translateY(-1px); }

    /* Progress panel states */
    .idle-box {
        border: 2px dashed #f0d8d8; border-radius: 12px;
        padding: 2.5rem 1.5rem; text-align: center;
        color: #ccc; margin-top: 0.2rem;
    }
    .idle-icon { font-size: 2.4rem; margin-bottom: 0.7rem; }
    .idle-text { font-size: 0.86rem; color: #bbb; }

    /* Attempt badge */
    .abadge {
        display: inline-block; background: #fff0f0; color: #B01116;
        font-size: 0.73rem; font-weight: 600; padding: 2px 9px;
        border-radius: 20px; border: 1px solid #f5c0c2; margin-bottom: 0.35rem;
    }

    /* Result boxes */
    .success-box {
        background: #f0fdf4; border: 1.5px solid #86efac;
        border-radius: 10px; padding: 0.9rem 1.1rem;
        color: #166534; font-size: 0.84rem; margin-top: 0.5rem;
    }
    .fail-box {
        background: #fff5f5; border: 1.5px solid #fca5a5;
        border-radius: 10px; padding: 0.9rem 1.1rem;
        color: #991b1b; font-size: 0.84rem; margin-top: 0.5rem;
    }
    .stat-row { display: flex; gap: 0.4rem; flex-wrap: wrap; margin-top: 0.5rem; }
    .sp {
        background: #f5f0f0; border: 1px solid #ecdcdc;
        border-radius: 5px; padding: 0.2rem 0.55rem;
        font-size: 0.73rem; color: #666;
    }

    /* Progress */
    .stProgress > div > div { background: #ED1C24 !important; }
    .stProgress > div { background: #f0e0e0 !important; border-radius: 4px !important; }
    [data-testid="stAlert"] {
        background: #fffbeb !important; border: 1px solid #fcd34d !important;
        border-radius: 7px !important; color: #92400e !important; font-size: 0.8rem !important;
    }
    .stMarkdown p { color: #888; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)


# ── Conversion logic ───────────────────────────────────────────────────────────
# Dynamically derive (dpi, jpeg_quality) from target_mb so the slider
# genuinely changes the output quality, not just the acceptance threshold.

def params_for_target(target_mb: float, pdf_size_mb: float):
    """
    Return a list of (dpi, quality, label) attempts ordered from
    *highest quality that might still fit* down to most aggressive.

    The ratio target_mb/pdf_size_mb tells us how much we need to compress.
    We map that ratio to DPI (72–200) and JPEG quality (20–90).
    Then we add two fallback attempts with progressively lower settings.
    """
    ratio = target_mb / pdf_size_mb  # e.g. 0.5 means halve the size

    # Primary attempt: quality scales linearly with target ratio (capped)
    ratio_clamped = max(0.15, min(ratio, 1.0))
    primary_dpi = int(72 + ratio_clamped * (200 - 72))        # 72..200
    primary_q   = int(20 + ratio_clamped * (90 - 20))          # 20..90

    # Two fallback attempts each step down by ~15% quality and 10 DPI
    fb1_dpi = max(72,  primary_dpi - 12)
    fb1_q   = max(15,  primary_q   - 12)
    fb2_dpi = max(72,  fb1_dpi     - 12)
    fb2_q   = max(10,  fb1_q       - 12)

    return [
        (primary_dpi, primary_q,  f"Attempt 1 — {primary_dpi} DPI · quality {primary_q}"),
        (fb1_dpi,     fb1_q,      f"Attempt 2 — {fb1_dpi} DPI · quality {fb1_q}"),
        (fb2_dpi,     fb2_q,      f"Attempt 3 — {fb2_dpi} DPI · quality {fb2_q}"),
    ]


def convert_pdf_to_tiff(pdf_bytes, dpi, jpeg_quality, progress_bar, status_text):
    status_text.markdown("⚙️ Rendering pages...")
    pdf_pages = convert_from_bytes(pdf_bytes, dpi=dpi, grayscale=True)
    total = len(pdf_pages)
    for i in range(total):
        progress_bar.progress(int((i + 1) / total * 65))

    status_text.markdown(f"🎨 Grayscale conversion ({total} pages)...")
    gray = []
    for i, p in enumerate(pdf_pages):
        gray.append(p.convert("L"))
        progress_bar.progress(65 + int((i + 1) / total * 20))

    status_text.markdown("💾 Encoding TIFF...")
    buf = io.BytesIO()
    gray[0].save(
        buf, format="TIFF", save_all=True,
        append_images=gray[1:], compression="jpeg", quality=jpeg_quality,
    )
    progress_bar.progress(100)
    buf.seek(0)
    return buf, total


# ── TOP BAR ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-bar">
    <div class="top-bar-icon">🗜️</div>
    <div class="top-bar-title">PDF to TIFF Converter</div>
</div>
""", unsafe_allow_html=True)

# ── TWO COLUMNS ───────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1.35], gap="large")

# ─── LEFT: Controls ───────────────────────────────────────────────────────────
with col_left:
    st.markdown('<div class="col-label">📂 Upload &amp; Configure</div>', unsafe_allow_html=True)

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        label_visibility="collapsed",
    )

    # Validate file size and set dynamic slider range
    pdf_bytes = None
    pdf_size_mb = None
    file_error = None

    if uploaded_file is not None:
        pdf_bytes = uploaded_file.read()
        pdf_size_mb = len(pdf_bytes) / (1024 * 1024)

        if pdf_size_mb < 3.0:
            file_error = f"File is {pdf_size_mb:.2f} MB — already under 3 MB, no compression needed."
            pdf_bytes = None
        else:
            st.markdown(f"""
            <div class="file-chip">
                📄 <span class="fname">{uploaded_file.name}</span>
                <span class="fsize">{pdf_size_mb:.2f} MB</span>
            </div>
            """, unsafe_allow_html=True)

    if file_error:
        st.markdown(f'<div class="err-chip">⚠️ {file_error}</div>', unsafe_allow_html=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # Slider: range is always 2 MB → actual PDF size (so user can't pick > file size)
    slider_min = 2.0
    slider_max = round(pdf_size_mb, 1) if (pdf_size_mb and pdf_size_mb >= 3.0) else 10.0
    slider_default = min(3.0, slider_max)

    # Clamp stored value if a different (larger) file was previously loaded
    stored = st.session_state.get("target_mb", slider_default)
    if stored > slider_max:
        stored = slider_default

    st.markdown('<div class="slider-label">Target File Size Limit</div>', unsafe_allow_html=True)
    target_mb = st.slider(
        label="_",
        min_value=slider_min,
        max_value=slider_max,
        value=stored,
        step=0.5,
        format="%.1f MB",
        label_visibility="collapsed",
        key="target_mb",
        disabled=(pdf_bytes is None),
    )
    st.markdown(
        f'<div class="slider-info">Output will be compressed to fit within '
        f'<strong style="color:#ED1C24">{target_mb:.1f} MB</strong></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    convert_clicked = st.button(
        "Convert to TIFF →",
        disabled=(pdf_bytes is None),
        use_container_width=True,
    )


# ─── RIGHT: Progress & Result ─────────────────────────────────────────────────
with col_right:
    st.markdown('<div class="col-label">⚙️ Conversion Result</div>', unsafe_allow_html=True)

    if not convert_clicked or pdf_bytes is None:
        st.markdown("""
        <div class="idle-box">
            <div class="idle-icon">🕐</div>
            <div class="idle-text">Awaiting conversion…</div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Use the value stored in session_state — guaranteed to be what the user set
        # before the button rerun, not a reset default.
        confirmed_target = st.session_state.get("target_mb", target_mb)

        attempts = params_for_target(confirmed_target, pdf_size_mb)

        final_tiff   = None
        final_size   = None
        final_pages  = None
        success      = False

        for attempt_num, (dpi, quality, label) in enumerate(attempts, start=1):
            st.markdown(f'<div class="abadge">🔁 {label}</div>', unsafe_allow_html=True)
            pbar = st.progress(0)
            stxt = st.empty()

            try:
                buf, num_pages = convert_pdf_to_tiff(pdf_bytes, dpi, quality, pbar, stxt)
                size_mb = buf.getbuffer().nbytes / (1024 * 1024)
                stxt.empty()
                pbar.empty()

                if size_mb <= confirmed_target:
                    final_tiff  = buf
                    final_size  = size_mb
                    final_pages = num_pages
                    success     = True
                    st.markdown(f"""
                    <div class="success-box">
                        ✅ <strong>Conversion successful (attempt {attempt_num})</strong>
                        <div class="stat-row">
                            <span class="sp">📄 {num_pages} pages</span>
                            <span class="sp">📦 {size_mb:.2f} MB</span>
                            <span class="sp">{dpi} DPI · q{quality}</span>
                            <span class="sp">🎯 limit {confirmed_target:.1f} MB</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    break
                else:
                    left = len(attempts) - attempt_num
                    st.warning(f"Attempt {attempt_num}: {size_mb:.2f} MB > {confirmed_target:.1f} MB.{' Retrying…' if left else ''}")

            except Exception as e:
                stxt.empty()
                pbar.empty()
                left = len(attempts) - attempt_num
                st.warning(f"Attempt {attempt_num} failed: {e}.{' Retrying…' if left else ''}")

        if success and final_tiff is not None:
            out_name = os.path.splitext(uploaded_file.name)[0] + ".tiff"
            st.download_button(
                label=f"⬇️  Download TIFF  ·  {final_size:.2f} MB  ·  {final_pages} pages",
                data=final_tiff,
                file_name=out_name,
                mime="image/tiff",
                use_container_width=True,
            )
        else:
            st.markdown(f"""
            <div class="fail-box">
                <strong>❌ All 3 attempts exceeded {confirmed_target:.1f} MB.</strong><br><br>
                Try raising the size limit, or split the PDF into smaller parts first.
            </div>
            """, unsafe_allow_html=True)