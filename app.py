import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import json

# ────────────────────────────────────────────────
# Page config – good for desktop + mobile
st.set_page_config(
    page_title="LastSeen",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed"  # clean on phones
)

# Dark theme colors
bg_color     = "#0e1117"
text_color   = "#e6edf3"
border_color = "#444c56"
box_bg       = "#161b22"
accent_high  = "#ff4b4b"
accent_med   = "#ffa500"
accent_low   = "#4caf50"

st.markdown(f"""
    <style>
        .stApp {{ background-color: {bg_color}; color: {text_color}; }}
        .stTabs [data-baseweb="tab-list"] {{ gap: 12px; background-color: {bg_color}; }}
        .stTabs [data-baseweb="tab"] {{
            height: 52px;
            background-color: {box_bg};
            border-radius: 6px 6px 0 0;
            padding: 10px 16px;
            color: {text_color};
        }}
        hr {{ border-color: {border_color}; }}
        .risk-high   {{ color: {accent_high} !important; font-weight: bold; font-size: 1.3em; }}
        .risk-medium {{ color: {accent_med}  !important; font-weight: bold; font-size: 1.3em; }}
        .risk-low    {{ color: {accent_low}   !important; font-weight: bold; font-size: 1.3em; }}
        .inspire-box {{
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 20px;
            background: {box_bg};
            margin: 16px 0;
            color: {text_color};
        }}
        .stAlert, .stMetricLabel, .stMetricValue {{ color: {text_color} !important; }}
        section[data-testid="stSidebar"] {{ background-color: {bg_color}; color: {text_color}; }}
        @media (max-width: 768px) {{ .stColumns {{ gap: 8px !important; }} }}
    </style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
st.title("🛡️ LastSeen")
st.caption("Protect digital identities from misuse after prolonged inactivity — privacy-first, user-controlled, trusted-verification approach.")

# ────────────────────────────────────────────────
# Session state defaults
if 'last_activity' not in st.session_state:
    st.session_state.last_activity = datetime.now()
    st.session_state.risk_score = 0
    st.session_state.trusted_contacts = ["friend@example.com"]
    st.session_state.account_status = "Active"
    st.session_state.activity_log = [datetime.now()]
    st.session_state.memorial_message = "In loving memory. Your story continues with dignity."
    st.session_state.thresholds = {'low_to_medium': 7, 'medium_to_high': 30}

# ────────────────────────────────────────────────
def calculate_risk():
    days = (datetime.now() - st.session_state.last_activity).days
    t = st.session_state.thresholds
    if days < t['low_to_medium']:
        return 0, "Low Risk – Active", "low", "✅", days
    elif days < t['medium_to_high']:
        return 50, "Medium Risk – Dormant", "medium", "⚠️", days
    else:
        return 100, "High Risk – Inactivity", "high", "🛑", days

risk_score, risk_level, risk_class, risk_icon, days_inactive = calculate_risk()
st.session_state.risk_score = risk_score

# ────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "⚙️ Settings", "🧪 Test"])

# ──────────────────────────────────────────────── Dashboard
with tab1:
    st.subheader("Real-time Status")
    cols = st.columns(4)
    cols[0].metric("Last Activity", st.session_state.last_activity.strftime("%Y-%m-%d %H:%M"))
    cols[1].metric("Days Inactive", days_inactive)
    cols[2].metric("Risk Score", f"{risk_score}%")
    cols[3].markdown(f"<div class='risk-{risk_class}'>{risk_icon} {risk_level}</div>", unsafe_allow_html=True)

    st.progress(risk_score / 100)

    if risk_score < 50:
        st.info(f"→ Medium risk in ≈ **{st.session_state.thresholds['low_to_medium'] - days_inactive} days**")
    if risk_score < 100:
        st.info(f"→ High risk in ≈ **{st.session_state.thresholds['medium_to_high'] - days_inactive} days**")

    if len(st.session_state.activity_log) > 1:
        df = pd.DataFrame({"Time": st.session_state.activity_log})
        st.subheader("Activity History")
        st.line_chart(df.set_index("Time").assign(Activity=1), height=180)

    if risk_score == 50:
        st.warning("Reduced activity detected. Are you okay?")
        if st.button("✅ Confirm I'm Here", use_container_width=True, type="primary"):
            now = datetime.now()
            st.session_state.last_activity = now
            st.session_state.activity_log.append(now)
            st.success("Confirmed! Risk reset.")
            st.rerun()

    if risk_score == 100:
        st.error("High inactivity – protection mode active")
        st.subheader("Trusted Contact Alerts")
        for contact in st.session_state.trusted_contacts:
            st.write(f"📧 Sent to **{contact}**")

        response = st.selectbox("Simulate Response", ["User is okay", "Concern confirmed"])
        if st.button("Submit Verification", type="primary"):
            if response == "User is okay":
                st.session_state.risk_score = 0
                st.session_state.account_status = "Active"
                st.success("Account restored.")
            else:
                st.session_state.account_status = "Locked - Awaiting Review"
                st.warning("Account protected.")
            st.rerun()

        st.subheader("Memorialization Preview")
        st.markdown(f"<div class='inspire-box'>{st.session_state.memorial_message}</div>", unsafe_allow_html=True)

    st.subheader("Active Safeguards")
    if "Locked" in st.session_state.account_status:
        st.markdown("🔒 **Locked** – No changes allowed")
    if risk_score == 100:
        st.markdown("🪦 **Memorial Mode** – Read-only tribute")
    if risk_score == 50:
        st.markdown("🔇 **Quiet Mode** – Notifications paused")

# ──────────────────────────────────────────────── Settings (live updates)
with tab2:
    st.subheader("Risk Thresholds")
    low = st.slider(
        "Low → Medium (days)",
        1, 30,
        st.session_state.thresholds['low_to_medium']
    )
    st.session_state.thresholds['low_to_medium'] = low

    high = st.slider(
        "Medium → High (days)",
        low + 1, 180,
        st.session_state.thresholds['medium_to_high']
    )
    st.session_state.thresholds['medium_to_high'] = high

    st.subheader("Trusted Contacts")
    for i, email in enumerate(st.session_state.trusted_contacts):
        c1, c2 = st.columns([5,1])
        c1.write(email)
        if c2.button("Remove", key=f"rm_{i}"):
            st.session_state.trusted_contacts.pop(i)
            st.rerun()

    new_email = st.text_input("Add Contact", placeholder="someone@example.com")
    if st.button("Add") and new_email:
        if "@" in new_email and "." in new_email:
            st.session_state.trusted_contacts.append(new_email.strip())
            st.success("Added")
            st.rerun()
        else:
            st.error("Invalid email")

    st.subheader("Backup / Restore")
    config = {
        "thresholds": st.session_state.thresholds,
        "contacts": st.session_state.trusted_contacts,
        "memorial": st.session_state.memorial_message
    }
    json_str = json.dumps(config, indent=2)
    st.download_button("Download Config", json_str, "lastseen_config.json", "application/json")

    uploaded = st.file_uploader("Upload Config", type=["json"])
    if uploaded:
        try:
            data = json.load(uploaded)
            st.session_state.thresholds = data.get("thresholds", st.session_state.thresholds)
            st.session_state.trusted_contacts = data.get("contacts", st.session_state.trusted_contacts)
            st.session_state.memorial_message = data.get("memorial", st.session_state.memorial_message)
            st.success("Restored")
            st.rerun()
        except:
            st.error("Invalid file")

# ──────────────────────────────────────────────── Test / Simulation
with tab3:
    st.subheader("Simulation Tools")
    if st.button("Reset Activity", type="primary", use_container_width=True):
        now = datetime.now()
        st.session_state.last_activity = now
        st.session_state.activity_log.append(now)
        st.session_state.risk_score = 0
        st.session_state.account_status = "Active"
        st.success("Activity reset")
        st.rerun()

    st.subheader("Time Jump (for testing)")
    days = st.slider("Jump forward days", 0, 365, 0)
    if st.button("Apply Time Jump") and days > 0:
        st.session_state.last_activity -= timedelta(days=days)
        st.success(f"→ Advanced {days} days")
        st.rerun()

# ──────────────────────────────────────────────── Footer
st.markdown("---")
st.caption("LastSeen • Privacy-first digital legacy protection")