"""
Bulk Email Sender — Streamlit Application
A modern, premium UI for sending bulk emails via Gmail, Outlook, Zoho, Yahoo,
or any custom SMTP server. Supports PDF/PPT attachments and auto-linked URLs.
"""

import os
import time
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from email_sender import send_single_email, EMAIL_PROVIDERS

# ── Load .env credentials as defaults ──────────────────────────────────────
load_dotenv()

# ── Streamlit Cloud compatibility ──────────────────────────────────────────
# On Streamlit Community Cloud, secrets are stored via the dashboard (not .env).
try:
    if hasattr(st, "secrets") and len(st.secrets) > 0:
        os.environ.setdefault("EMAIL_ADDRESS", st.secrets.get("EMAIL_ADDRESS", ""))
        os.environ.setdefault("EMAIL_PASSWORD", st.secrets.get("EMAIL_PASSWORD", ""))
except Exception:
    pass  # No secrets.toml — that's fine for local usage

# ── Page Configuration ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bulk Email Sender",
    page_icon="📧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS for Premium Look ────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── Global ────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background: linear-gradient(160deg, #0f0c29 0%, #1a1a40 40%, #24243e 100%);
    }

    /* ── Header ────────────────────────────────────── */
    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0;
        letter-spacing: -0.5px;
    }
    .hero-sub {
        text-align: center;
        color: #9ca3af;
        font-size: 1.05rem;
        margin-top: 4px;
        margin-bottom: 30px;
    }

    /* ── Glass Card ────────────────────────────────── */
    .glass-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 28px 26px;
        margin-bottom: 22px;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
    }
    .glass-card h3 {
        color: #e0e0ff;
        font-weight: 700;
        font-size: 1.15rem;
        margin-bottom: 14px;
    }

    /* ── Section Labels ────────────────────────────── */
    .section-label {
        color: #c0c0e8;
        font-weight: 600;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 1.6px;
        margin-bottom: 10px;
    }

    /* ── Stat Badges ───────────────────────────────── */
    .stat-row {
        display: flex;
        gap: 14px;
        margin-top: 8px;
        margin-bottom: 8px;
    }
    .stat-badge {
        flex: 1;
        text-align: center;
        padding: 16px 10px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .stat-badge.purple  { background: rgba(102, 126, 234, 0.12); }
    .stat-badge.green   { background: rgba(72, 199, 142, 0.12); }
    .stat-badge.red     { background: rgba(245, 101, 101, 0.12); }
    .stat-badge .number {
        font-size: 1.8rem;
        font-weight: 800;
        color: #fff;
        line-height: 1;
    }
    .stat-badge .label {
        font-size: 0.7rem;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 6px;
    }

    /* ── Log Area ──────────────────────────────────── */
    .log-entry {
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.82rem;
        padding: 5px 0;
        color: #c8c8e0;
        border-bottom: 1px solid rgba(255,255,255,0.03);
    }

    /* ── Buttons ───────────────────────────────────── */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 32px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        letter-spacing: 0.3px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3) !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.45) !important;
    }

    /* ── Progress bar ─────────────────────────────── */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb) !important;
        border-radius: 10px;
    }

    /* ── Inputs ────────────────────────────────────── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: #e0e0ff !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102,126,234,0.25) !important;
    }

    /* ── Slider ────────────────────────────────────── */
    .stSlider > div > div > div > div {
        background: #667eea !important;
    }

    /* ── File Uploader ─────────────────────────────── */
    .stFileUploader > div {
        background: rgba(255,255,255,0.03) !important;
        border: 2px dashed rgba(102,126,234,0.3) !important;
        border-radius: 14px !important;
    }

    /* ── Provider pills ────────────────────────────── */
    .provider-hint {
        font-size: 0.75rem;
        color: #8b8baf;
        margin-top: 6px;
        line-height: 1.5;
    }
    .provider-hint code {
        background: rgba(102,126,234,0.15);
        color: #a5b4fc;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.72rem;
    }

    /* ── Attachment chip ───────────────────────────── */
    .attach-chip {
        display: inline-block;
        background: rgba(102,126,234,0.12);
        border: 1px solid rgba(102,126,234,0.25);
        border-radius: 8px;
        padding: 6px 14px;
        font-size: 0.82rem;
        color: #c0c0e8;
        margin: 4px 4px 4px 0;
    }
    .attach-chip .icon { margin-right: 5px; }

    /* ── Link hint ─────────────────────────────────── */
    .link-hint {
        font-size: 0.75rem;
        color: #7b7b9e;
        margin-top: 4px;
        padding: 8px 12px;
        background: rgba(102,126,234,0.06);
        border-left: 3px solid #667eea;
        border-radius: 0 8px 8px 0;
    }

    /* ── Hide Streamlit Chrome ─────────────────────── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Helper: Save credentials to .env ───────────────────────────────────────
def save_to_env(email: str, password: str, provider: str):
    """Persist credentials to the local .env file."""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    with open(env_path, "w") as f:
        f.write("# Bulk Email Sender - Credentials\n")
        f.write("# These stay local and are never shared\n\n")
        f.write(f"EMAIL_ADDRESS={email}\n")
        f.write(f"EMAIL_PASSWORD={password}\n")
        f.write(f"EMAIL_PROVIDER={provider}\n")


# ══════════════════════════════════════════════════════════════════════════════
#  UI LAYOUT
# ══════════════════════════════════════════════════════════════════════════════

# ── Hero Header ────────────────────────────────────────────────────────────
st.markdown('<p class="hero-title">📧 Bulk Email Sender</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-sub">Upload a CSV, compose your message, attach files, and send in bulk — Gmail, Outlook, Zoho & more.</p>',
    unsafe_allow_html=True,
)

# ── Section 1: Email Provider & Credentials ────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<p class="section-label">🔐 Email Provider & Credentials</p>', unsafe_allow_html=True)

provider_names = list(EMAIL_PROVIDERS.keys())
saved_provider = os.getenv("EMAIL_PROVIDER", "Gmail")
default_idx = provider_names.index(saved_provider) if saved_provider in provider_names else 0

provider = st.selectbox(
    "Email Provider",
    provider_names,
    index=default_idx,
    help="Choose your email service. Select 'Custom SMTP' for any other provider.",
)

# Show provider-specific hints
provider_hints = {
    "Gmail": 'Use an <code>App Password</code> — generate one at <a href="https://myaccount.google.com/apppasswords" target="_blank" style="color:#667eea;">myaccount.google.com/apppasswords</a>',
    "Outlook / Hotmail": "Use your regular Outlook password. If 2FA is enabled, create an app password in your Microsoft account security settings.",
    "Zoho Mail": 'Use an <code>App Password</code> — generate one at <a href="https://accounts.zoho.com/home#security/security_pwd" target="_blank" style="color:#667eea;">Zoho Security Settings</a>',
    "Yahoo Mail": 'Use an <code>App Password</code> — generate one at <a href="https://login.yahoo.com/account/security" target="_blank" style="color:#667eea;">Yahoo Account Security</a>',
    "Custom SMTP": "Enter your SMTP server details below.",
}
st.markdown(f'<div class="provider-hint">💡 {provider_hints[provider]}</div>', unsafe_allow_html=True)

# Custom SMTP fields
if provider == "Custom SMTP":
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        custom_server = st.text_input("SMTP Server", placeholder="mail.example.com")
    with c2:
        custom_port = st.number_input("Port", value=587, min_value=1, max_value=65535)
    with c3:
        custom_ssl = st.selectbox("Security", ["STARTTLS (587)", "SSL (465)"])
    use_ssl = custom_ssl == "SSL (465)"
    smtp_server = custom_server
    smtp_port = int(custom_port)
else:
    preset = EMAIL_PROVIDERS[provider]
    smtp_server = preset["server"]
    smtp_port = preset["port"]
    use_ssl = preset["use_ssl"]

col1, col2 = st.columns(2)
with col1:
    email_address = st.text_input(
        "Email Address",
        value=os.getenv("EMAIL_ADDRESS", os.getenv("GMAIL_ADDRESS", "")),
        placeholder="you@example.com",
        help="Your full email address",
    )
with col2:
    email_password = st.text_input(
        "Password / App Password",
        value=os.getenv("EMAIL_PASSWORD", os.getenv("GMAIL_APP_PASSWORD", "")),
        type="password",
        placeholder="••••••••••••",
        help="Your email password or app-specific password",
    )

save_creds = st.checkbox("💾 Save credentials to .env for next time", value=False)
if save_creds and email_address and email_password:
    save_to_env(email_address, email_password, provider)

st.markdown("</div>", unsafe_allow_html=True)

# ── Section 2: CSV Upload ──────────────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<p class="section-label">📋 Recipient List</p>', unsafe_allow_html=True)

uploaded_csv = st.file_uploader(
    "Upload CSV with email addresses",
    type=["csv"],
    help="The CSV must contain an **'email'** column. Optionally add a **'name'** column to personalise each email with `{name}`.",
)

# recipient_list holds (name, email) tuples; name falls back to empty string
recipient_list = []  # list of (name: str, email: str)
if uploaded_csv is not None:
    try:
        df = pd.read_csv(uploaded_csv)
        col_map = {c.strip().lower(): c for c in df.columns}

        if "email" not in col_map:
            st.error("⚠️ No column named **'email'** found. Please check your CSV headers.")
        else:
            email_col = col_map["email"]
            name_col  = col_map.get("name")  # may be None if column absent

            valid_rows = df[df[email_col].astype(str).str.contains("@", na=False)].copy()
            for _, row in valid_rows.iterrows():
                email_val = str(row[email_col]).strip()
                name_val  = str(row[name_col]).strip() if name_col and pd.notna(row[name_col]) else ""
                recipient_list.append((name_val, email_val))

            has_names = name_col is not None
            name_info = f" · **name** column detected ✨" if has_names else " · No *name* column — add one to personalise greetings"
            st.success(f"✅ Found **{len(recipient_list)}** valid recipients{name_info}")
    except Exception as e:
        st.error(f"Failed to parse CSV: {e}")

# Keep a flat email list for backwards-compatible validation
email_list = [email for _, email in recipient_list]

st.markdown("</div>", unsafe_allow_html=True)

# ── Section 3: Compose ─────────────────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<p class="section-label">✍️ Compose Email</p>', unsafe_allow_html=True)

subject = st.text_input("Subject", placeholder="Your email subject line… (use {name} to personalise)")
body = st.text_area(
    "Body",
    height=180,
    placeholder="Hi {name},\n\nWrite your email body here…\n\nYou can use multiple lines.\nPaste any URL (e.g. https://example.com) and it will become a clickable link automatically.",
)

st.markdown(
    '<div class="link-hint">'
    '👤 <strong>Personalisation</strong> — Use <code>{name}</code> anywhere in the subject or body '
    'and it will be automatically replaced with each recipient\'s name from your CSV.<br>'
    '🔗 <strong>Links auto-detected</strong> — Paste any URL (e.g. <code>https://example.com</code>) '
    'and it becomes a clickable link in the email.'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)

# ── Section 4: Attachments ─────────────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<p class="section-label">📎 Attachments</p>', unsafe_allow_html=True)

uploaded_attachments = st.file_uploader(
    "Attach PDF or PowerPoint files",
    type=["pdf", "ppt", "pptx"],
    accept_multiple_files=True,
    help="Upload one or more PDF / PPT / PPTX files. Each recipient will receive a copy.",
)

# Show attachment chips
if uploaded_attachments:
    chips_html = ""
    total_size = 0
    for f in uploaded_attachments:
        size_mb = f.size / (1024 * 1024)
        total_size += size_mb
        icon = "📄" if f.name.endswith(".pdf") else "📊"
        chips_html += f'<span class="attach-chip"><span class="icon">{icon}</span>{f.name} ({size_mb:.1f} MB)</span>'
    st.markdown(chips_html, unsafe_allow_html=True)
    if total_size > 20:
        st.warning("⚠️ Total attachment size exceeds 20 MB. Some providers may reject large emails.")

st.markdown("</div>", unsafe_allow_html=True)

# ── Section 5: Settings ────────────────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<p class="section-label">⚙️ Send Settings</p>', unsafe_allow_html=True)

delay = st.slider(
    "Delay between emails (seconds)",
    min_value=0,
    max_value=30,
    value=2,
    step=1,
    help="Add a gap between sends to avoid rate-limiting. 2–5 seconds recommended.",
)

st.markdown("</div>", unsafe_allow_html=True)

# ── Section 6: Send Button & Progress ──────────────────────────────────────
st.markdown("---")

# Prepare attachments list
attachment_data = []
if uploaded_attachments:
    for f in uploaded_attachments:
        attachment_data.append((f.name, f.getvalue()))

# Validation checks
can_send = True
validation_messages = []

if not email_address:
    validation_messages.append("Email address is required")
    can_send = False
if not email_password:
    validation_messages.append("Password / App Password is required")
    can_send = False
if provider == "Custom SMTP" and not smtp_server:
    validation_messages.append("SMTP server is required for custom provider")
    can_send = False
if not email_list:
    validation_messages.append("Upload a CSV with at least one valid email")
    can_send = False
if not subject:
    validation_messages.append("Subject line is required")
    can_send = False
if not body:
    validation_messages.append("Email body is required")
    can_send = False

if validation_messages:
    st.info("📝 " + " · ".join(validation_messages))

# Send button
if st.button("🚀 Start Sending", disabled=not can_send, use_container_width=True):
    total = len(recipient_list)
    sent_ok = 0
    sent_fail = 0
    log_lines = []

    # Progress UI — using st.empty() so it re-renders live on every update
    progress_bar = st.progress(0, text="Preparing to send…")
    status_text = st.empty()
    log_area = st.empty()

    for i, (recipient_name, recipient) in enumerate(recipient_list):
        # Personalise subject & body for this specific recipient
        personalised_subject = subject.replace("{name}", recipient_name) if recipient_name else subject
        personalised_body    = body.replace("{name}", recipient_name)    if recipient_name else body

        # Update status before sending
        display_name = recipient_name if recipient_name else recipient
        status_text.info(f"📤 Sending to **{display_name}** &lt;{recipient}&gt; ({i + 1}/{total})… please wait")
        progress_bar.progress(
            (i) / total,
            text=f"Sending {i + 1} of {total}  —  ✅ {sent_ok}  ❌ {sent_fail}",
        )

        result = send_single_email(
            smtp_server=smtp_server,
            port=smtp_port,
            sender_email=email_address,
            app_password=email_password,
            recipient_email=recipient,
            subject=personalised_subject,
            body=personalised_body,
            use_ssl=use_ssl,
            attachments=attachment_data if attachment_data else None,
        )

        if result["success"]:
            sent_ok += 1
        else:
            sent_fail += 1

        # Append to log and re-render the entire log block
        log_lines.append(f'<div class="log-entry">{result["message"]}</div>')
        log_area.markdown("".join(log_lines), unsafe_allow_html=True)

        # Delay between emails (skip after the last one)
        if i < total - 1 and delay > 0:
            time.sleep(delay)

    # ── Final Stats ────────────────────────────────────────────────────
    progress_bar.progress(1.0, text="✨ All done!")
    status_text.success(f"✨ Finished — **{sent_ok}** sent, **{sent_fail}** failed")

    st.markdown(
        f"""
        <div class="stat-row">
            <div class="stat-badge purple">
                <div class="number">{total}</div>
                <div class="label">Total</div>
            </div>
            <div class="stat-badge green">
                <div class="number">{sent_ok}</div>
                <div class="label">Sent</div>
            </div>
            <div class="stat-badge red">
                <div class="number">{sent_fail}</div>
                <div class="label">Failed</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if sent_fail == 0:
        st.balloons()
        st.success("🎉 All emails sent successfully!")
    else:
        st.warning(f"⚠️ {sent_fail} email(s) failed. Check the log above for details.")


# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #6b7280; font-size: 0.8rem; padding-bottom: 20px;">
        <strong>Bulk Email Sender</strong> &nbsp;·&nbsp; Gmail · Outlook · Zoho · Yahoo · Custom SMTP &nbsp;·&nbsp; Credentials stored locally in <code>.env</code><br>
        <span style="font-size: 0.72rem; color: #4b5563;">
            Supports PDF & PowerPoint attachments &nbsp;·&nbsp; URLs auto-linked in emails
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)
