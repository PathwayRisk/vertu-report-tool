"""
Vertu Motors — Daily Security Report Tool
==========================================
Run locally:   streamlit run app.py
Deploy:        push folder to GitHub → connect to Streamlit Community Cloud
"""

import streamlit as st
import anthropic
import tempfile, os, json, base64, re
from datetime import date, timedelta
from pypdf import PdfReader
from report_builder import build_pdf
from sites_config import SITES as SITE_REGISTRY, ARC_CENTRES

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Vertu Daily Report",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Styling ───────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #F6F8F8; }
    .block-container { padding-top: 2rem; max-width: 900px; }
    .report-header {
        background: #0E3D40; color: #E8B84B;
        padding: 1.2rem 1.8rem; border-radius: 8px;
        margin-bottom: 1.5rem;
    }
    .report-header h1 { color: #E8B84B; margin: 0; font-size: 1.4rem; font-weight: 700; }
    .report-header p  { color: #9EBABB; margin: 0.2rem 0 0; font-size: 0.85rem; }
    .step-box {
        background: white; border: 1px solid #D0DCDD;
        border-radius: 8px; padding: 1.2rem 1.5rem; margin-bottom: 1rem;
    }
    .step-label {
        font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.08em; color: #6B8284; margin-bottom: 0.3rem;
    }
    .step-title { font-size: 1rem; font-weight: 600; color: #0E3D40; margin-bottom: 0.8rem; }
    .event-card {
        background: #FEF0F0; border: 1px solid #F5C6C6;
        border-radius: 6px; padding: 0.7rem 1rem; margin-bottom: 0.5rem;
    }
    .event-card-audio {
        background: #FEFAF0; border: 1px solid #F0DFA0;
        border-radius: 6px; padding: 0.7rem 1rem; margin-bottom: 0.5rem;
    }
    .site-clear {
        background: #F0FAF4; border: 1px solid #A8D8B8;
        border-radius: 6px; padding: 0.5rem 1rem; margin-bottom: 0.4rem;
        color: #1E7A46; font-size: 0.85rem;
    }
    .site-nosignal {
        background: #FEFAF0; border: 1px solid #F0DFA0;
        border-radius: 6px; padding: 0.5rem 1rem; margin-bottom: 0.4rem;
        color: #B7860B; font-size: 0.85rem;
    }
    .badge-genuine { background:#FEF0F0; color:#C0392B; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:600; }
    .badge-false   { background:#F0FAF4; color:#1E7A46; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:600; }
    .badge-noact   { background:#EFF6FF; color:#1A5FA8; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:600; }
    .badge-keyholder { background:#FEFAF0; color:#B7860B; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:600; }
    div[data-testid="stDownloadButton"] button {
        background: #0E3D40 !important; color: #E8B84B !important;
        font-weight: 600; width: 100%; padding: 0.6rem;
    }
    .stButton > button { border-radius: 6px; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="report-header">
  <h1>🛡️ Pathway Risk Management</h1>
  <p>Vertu Motors — Daily Security Report Tool</p>
</div>
""", unsafe_allow_html=True)

# ── Session state defaults ────────────────────────────────────────────────────

if "extracted" not in st.session_state:
    st.session_state.extracted = None   # dict: site_data, report_date, report_period
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None

# ── Helpers ───────────────────────────────────────────────────────────────────

VALID_IDS = {s["id"] for s in SITE_REGISTRY}

def extract_pdf_text(uploaded_files) -> str:
    """Extract raw text from one or more uploaded PDF files."""
    all_text = []
    for f in uploaded_files:
        reader = PdfReader(f)
        pages = [page.extract_text() or "" for page in reader.pages]
        all_text.append(f"\n\n=== FILE: {f.name} ===\n\n" + "\n".join(pages))
    return "\n".join(all_text)

def call_claude(pdf_text: str, api_key: str) -> dict:
    """Send PDF text to Claude and get structured JSON back."""
    client = anthropic.Anthropic(api_key=api_key)

    site_list = "\n".join(
        f'  - id: "{s["id"]}" → name: "{s["name"]}"'
        for s in SITE_REGISTRY if s.get("active", True)
    )

    system = """You are a security monitoring data extraction assistant.
You extract structured event data from ARC (Alarm Receiving Centre) daily reports and return ONLY valid JSON — no prose, no markdown fences, no explanation.

Rules for extraction:
- Only include sites from the provided site list. Ignore any others.
- Map site names from the report to the correct id using fuzzy matching (e.g. "Ferrari Exeter (Vertu)" → "ferrari_exeter").
- For keyholder contact outcomes: always use "Keyholder notified" regardless of whether the call was answered, went to answerphone, or was not answered. Never mention individual names or call outcomes.
- Strip all internal ARC operator references, operator IDs, camera technical codes (e.g. T:Dahua(1) A:1), and monitoring company names (FENIX etc). The report is from Pathway Risk Management.
- Translate camera references like "C:3 Camera 3" to plain "Camera 3".
- status must be one of: "alert" (genuine incident), "warning" (activity but no genuine incident), "clear" (no activity), "no_signal" (no signal in 7+ days).
- badge must be one of: "Genuine incident", "False alarm", "No action", "Resolved", "Keyholder notified" — or empty string.
- level must be one of: "high", "medium", "low".
- For the report_date field, use the full date found in the report header (e.g. "Tuesday 13 May 2026").
- For report_period, describe the coverage window (e.g. "12 May (evening) – 13 May 2026").
- Sites not appearing in the report at all should be omitted from site_data (they will default to "clear").
- Sites explicitly noted as having no alarms in 7 days should be included with status "no_signal"."""

    user = f"""Extract all security events from the following ARC report text.

SITE LIST (only include these, matched by id):
{site_list}

Return a single JSON object with this exact schema:
{{
  "report_date": "string",
  "report_period": "string",
  "site_data": {{
    "<site_id>": {{
      "status": "alert|warning|clear|no_signal",
      "alarms": [
        {{
          "time": "HH:MM  DD/MM",
          "level": "high|medium|low",
          "main": "one-sentence description",
          "note": "follow-up detail or empty string",
          "badge": "Genuine incident|False alarm|No action|Resolved|Keyholder notified|"
        }}
      ],
      "audio": [
        {{
          "time": "HH:MM  DD/MM",
          "level": "high|medium|low",
          "main": "one-sentence description",
          "note": "brief note or empty string",
          "badge": ""
        }}
      ]
    }}
  }}
}}

ARC REPORT TEXT:
{pdf_text}"""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        messages=[{"role": "user", "content": user}],
        system=system,
    )

    raw = response.content[0].text.strip()
    # Strip any accidental markdown fences
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw)

def generate_pdf_bytes(extracted: dict) -> bytes:
    """Run the report builder and return PDF as bytes."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name

    build_pdf(
        output_path=tmp_path,
        report_date=extracted["report_date"],
        report_period=extracted["report_period"],
        site_data=extracted["site_data"],
    )

    with open(tmp_path, "rb") as f:
        pdf_bytes = f.read()
    os.unlink(tmp_path)
    return pdf_bytes

# ── Step 1 — API key ──────────────────────────────────────────────────────────

with st.container():
    st.markdown('<div class="step-box">', unsafe_allow_html=True)
    st.markdown('<div class="step-label">Step 1</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-title">API key</div>', unsafe_allow_html=True)

    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    st.markdown('</div>', unsafe_allow_html=True)

# ── Step 2 — Upload ───────────────────────────────────────────────────────────

with st.container():
    st.markdown('<div class="step-box">', unsafe_allow_html=True)
    st.markdown('<div class="step-label">Step 2</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-title">Upload ARC reports</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload PDF reports",
        type="pdf",
        accept_multiple_files=True,
        label_visibility="collapsed",
        help="Upload one or more daily ARC PDF reports. Multiple ARCs can be combined.",
    )

    if uploaded:
        for f in uploaded:
            st.caption(f"📄 {f.name}")

    col1, col2 = st.columns([2, 1])
    with col1:
        extract_btn = st.button(
            "Extract data from PDFs →",
            disabled=(not uploaded or not api_key),
            use_container_width=True,
            type="primary",
        )
    with col2:
        if st.button("Clear & start over", use_container_width=True):
            st.session_state.extracted = None
            st.session_state.pdf_bytes = None
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ── Extraction ────────────────────────────────────────────────────────────────

if extract_btn and uploaded and api_key:
    with st.spinner("Reading PDFs and extracting events with AI…"):
        try:
            pdf_text = extract_pdf_text(uploaded)
            result   = call_claude(pdf_text, api_key)
            st.session_state.extracted = result
            st.session_state.pdf_bytes = None  # reset any previous PDF
            st.rerun()
        except json.JSONDecodeError as e:
            st.error(f"AI returned unexpected format: {e}. Try again.")
        except Exception as e:
            st.error(f"Error: {e}")

# ── Step 3 — Review ───────────────────────────────────────────────────────────

if st.session_state.extracted:
    ext = st.session_state.extracted

    st.markdown('<div class="step-box">', unsafe_allow_html=True)
    st.markdown('<div class="step-label">Step 3 — Review extracted data</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="step-title">📅 {ext["report_date"]} &nbsp;·&nbsp; '
        f'<span style="font-weight:400;color:#6B8284">{ext["report_period"]}</span></div>',
        unsafe_allow_html=True,
    )

    site_data = ext.get("site_data", {})
    active_sites = [s for s in SITE_REGISTRY if s.get("active", True)]

    BADGE_HTML = {
        "Genuine incident": '<span class="badge-genuine">Genuine incident</span>',
        "False alarm":      '<span class="badge-false">False alarm</span>',
        "No action":        '<span class="badge-noact">No action</span>',
        "Resolved":         '<span class="badge-false">Resolved</span>',
        "Keyholder notified":'<span class="badge-keyholder">Keyholder notified</span>',
    }

    has_activity = False

    for reg in active_sites:
        sid  = reg["id"]
        name = reg["name"]
        ev   = site_data.get(sid, {})
        status = ev.get("status", "clear")

        if status in ("alert", "warning"):
            has_activity = True
            alarms = ev.get("alarms", [])
            audio  = ev.get("audio", [])

            with st.expander(f"**{name}**  {'🔴' if status=='alert' else '🟡'}", expanded=True):
                if alarms:
                    st.markdown("**Alarm activations**")
                    for a in alarms:
                        badge_html = BADGE_HTML.get(a.get("badge",""), "")
                        st.markdown(
                            f'<div class="event-card">'
                            f'<strong style="font-size:0.8rem;color:#6B8284">{a["time"]}</strong>&nbsp;&nbsp;'
                            f'{a["main"]} {badge_html}'
                            + (f'<br><span style="font-size:0.82rem;color:#3D5254">{a["note"]}</span>' if a.get("note") else "")
                            + '</div>',
                            unsafe_allow_html=True,
                        )
                if audio:
                    st.markdown("**Audio challenges**")
                    for a in audio:
                        st.markdown(
                            f'<div class="event-card-audio">'
                            f'<strong style="font-size:0.8rem;color:#6B8284">{a["time"]}</strong>&nbsp;&nbsp;'
                            f'{a["main"]}'
                            + (f'<br><span style="font-size:0.82rem;color:#3D5254">{a["note"]}</span>' if a.get("note") else "")
                            + '</div>',
                            unsafe_allow_html=True,
                        )
        elif status == "no_signal":
            st.markdown(
                f'<div class="site-nosignal">⚠️ <strong>{name}</strong> — No signal received in past 7 days</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="site-clear">✓ <strong>{name}</strong> — No activity</div>',
                unsafe_allow_html=True,
            )

    # Manual override expander
    with st.expander("✏️ Edit extracted data (advanced)", expanded=False):
        st.caption("Paste corrected JSON here if anything was extracted incorrectly.")
        edited = st.text_area(
            "JSON override",
            value=json.dumps(ext, indent=2),
            height=300,
            label_visibility="collapsed",
        )
        if st.button("Apply edits"):
            try:
                st.session_state.extracted = json.loads(edited)
                st.session_state.pdf_bytes = None
                st.success("Applied.")
                st.rerun()
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Step 4 — Generate ─────────────────────────────────────────────────────

    st.markdown('<div class="step-box">', unsafe_allow_html=True)
    st.markdown('<div class="step-label">Step 4</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-title">Generate & download report</div>', unsafe_allow_html=True)

    gen_col, dl_col = st.columns([1, 1])

    with gen_col:
        if st.button("Generate PDF report →", use_container_width=True, type="primary"):
            with st.spinner("Building PDF…"):
                try:
                    st.session_state.pdf_bytes = generate_pdf_bytes(st.session_state.extracted)
                    st.success("PDF ready to download ✓")
                except Exception as e:
                    st.error(f"PDF generation failed: {e}")

    with dl_col:
        if st.session_state.pdf_bytes:
            fname = f"Vertu_Security_Report_{ext['report_date'].replace(' ','_')}.pdf"
            st.download_button(
                label="⬇ Download PDF",
                data=st.session_state.pdf_bytes,
                file_name=fname,
                mime="application/pdf",
                use_container_width=True,
            )

    st.markdown('</div>', unsafe_allow_html=True)
