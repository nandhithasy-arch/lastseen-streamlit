import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import json
import base64
import qrcode
from io import BytesIO

# ────────────────────────────────────────────────
# Page config – only dark theme
st.set_page_config(page_title="LastSeen", layout="wide", page_icon="🛡️")

# Fixed dark theme (only one theme now)
bg_color     = "#0e1117"     # deep dark background
text_color   = "#e6edf3"     # light readable text
muted_color  = "#adbac7"     # softer gray for captions
border_color = "#444c56"     # subtle borders
box_bg       = "#161b22"     # slightly lighter dark for boxes
accent_high  = "#ff4b4b"     # red for high risk
accent_med   = "#ffa500"     # orange for medium
accent_low   = "#4caf50"     # green for low

st.markdown(f"""
    <style>
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: 12px;
            background-color: {bg_color};
        }}
        .stTabs [data-baseweb="tab"] {{
            height: 52px;
            background-color: {box_bg};
            border-radius: 6px 6px 0 0;
            padding: 10px 16px;
            color: {text_color};
        }}
        hr {{
            border-color: {border_color};
        }}
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
        .stAlert, .stMetricLabel, .stMetricValue {{
            color: {text_color} !important;
        }}
        section[data-testid="stSidebar"] {{
            background-color: {bg_color};
            color: {text_color};
        }}
    </style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
st.title("🛡️ LastSeen")
st.caption("**Goal:** Protect digital identities from misuse after prolonged inactivity — using privacy-first metadata detection, user autonomy, graduated escalation, and trusted human verification.")

# ────────────────────────────────────────────────
# Session state defaults
defaults = {
    'last_activity': datetime.now(),
    'risk_score': 0,
    'trusted_contacts': ["friend@example.com"],
    'account_status': "Active",
    'activity_log': [datetime.now()],
    'memorial_message': "In loving memory of Nandhitha. Your story continues with dignity and love.",
    'thresholds': {'low_to_medium': 7, 'medium_to_high': 30}
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ────────────────────────────────────────────────
def calculate_risk():
    now = datetime.now()
    days = (now - st.session_state.last_activity).days
    t = st.session_state.thresholds
    
    if days < t['low_to_medium']:
        return 0,    "Low Risk – Active",    "low",    "✅", days
    elif days < t['medium_to_high']:
        return 50,   "Medium Risk – Dormant", "medium", "⚠️", days
    else:
        return 100,  "High Risk – Inactivity", "high",   "🛑", days

risk_score, risk_level, risk_class, risk_icon, days_inactive = calculate_risk()
st.session_state.risk_score = risk_score

# ────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard", 
    "⚙️ Settings", 
    "🧪 Test", 
    "🌟 Goal & Impact",
    "📚 References"
])

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

# ──────────────────────────────────────────────── Settings
with tab2:
    st.subheader("Risk Thresholds")
    t = st.session_state.thresholds
    t['low_to_medium'] = st.slider("Low → Medium (days)", 1, 30, t['low_to_medium'])
    t['medium_to_high'] = st.slider("Medium → High (days)", t['low_to_medium']+1, 180, t['medium_to_high'])
    if st.button("Save"):
        st.session_state.thresholds = t
        st.success("Updated")

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
    config_data = {
        "thresholds": st.session_state.thresholds,
        "contacts": st.session_state.trusted_contacts,
        "memorial": st.session_state.memorial_message
    }
    json_str = json.dumps(config_data, indent=2)
    st.download_button("Download Config", json_str, "lastseen_config.json", "application/json")
    
    uploaded = st.file_uploader("Upload Config", type=["json"])
    if uploaded:
        try:
            loaded = json.load(uploaded)
            st.session_state.thresholds = loaded.get("thresholds", defaults['thresholds'])
            st.session_state.trusted_contacts = loaded.get("contacts", defaults['trusted_contacts'])
            st.session_state.memorial_message = loaded.get("memorial", defaults['memorial_message'])
            st.success("Restored")
            st.rerun()
        except:
            st.error("Invalid file")

# ──────────────────────────────────────────────── Test
with tab3:
    st.subheader("Simulation")
    if st.button("Reset Activity", type="primary", use_container_width=True):
        now = datetime.now()
        st.session_state.last_activity = now
        st.session_state.activity_log.append(now)
        st.session_state.risk_score = 0
        st.session_state.account_status = "Active"
        st.success("Reset")
        st.rerun()
    
    st.subheader("Time Jump")
    days_jump = st.slider("Days forward", 0, 365, 0)
    if st.button("Apply"):
        if days_jump > 0:
            st.session_state.last_activity -= timedelta(days=days_jump)
            st.success(f"→ {days_jump} days later")
            st.rerun()

# ──────────────────────────────────────────────── Goal & Impact
with tab4:
    st.subheader("Core Goal")
    st.markdown("""
    **LastSeen exists to solve one clear problem:**  

    When someone stops using their digital accounts for a long time (illness, travel, death, etc.), those accounts become vulnerable to misuse, identity theft, or cause emotional pain to families who cannot access or close them.  

    This prototype shows a responsible, privacy-respecting way to:
    - Detect inactivity using only metadata (never content)
    - Give the user multiple chances to confirm they are okay
    - Involve trusted real people (not just algorithms) before taking strong actions
    - Protect dignity through graduated steps up to memorialization

    """)
    st.markdown("2026")

# ──────────────────────────────────────────────── References Tab
with tab5:
    st.subheader("📚 References & Research")
    st.caption("LastSeen is built on real evidence about digital legacy risks")
    
    st.markdown("""
    ### Key Sources on Digital Legacy & Inactivity Risks

    1. **Federal Trade Commission (FTC) Identity Theft Reports 2024–2025**  
       Over 1.1 million identity theft incidents reported in 2024, with losses >$12.5 billion. Dormant/deceased accounts are common entry points for fraud.  
       [View Report](https://oceanestatelaw.com/cybersecurity-estate-planning-how-to-protect-your-legacy-from-digital-theft)

    2. **Digital Legacy Dilemma – Why Your Data Doesn’t Die With You (2025)**  
       Shamsh Hadi, LinkedIn  
       [Read Article](https://www.linkedin.com/pulse/digital-legacy-dilemma-why-data-doesnt-die-you-shamsh-hadi-i5pwc)

    3. **eSafety Commissioner (Australia) – What Happens to Your Digital Accounts After You Die (2025)**  
       [Official Guide](https://www.esafety.gov.au/key-topics/digital-wellbeing/what-happens-to-your-digital-accounts-after-you-die)

    4. **ExpressVPN Research – Deceased Social Media Profiles Projection (2024)**  
       By 2100, deceased users may outnumber living ones on major platforms.  
       [Full Research](https://www.expressvpn.com/blog/will-deceased-accounts-on-social-media-outnumber-the-living)

    5. **IEEE Life – Digital Afterlife Planning for Your Online Accounts (2026)**  
       [Technical Paper](https://life.ieee.org/digital-afterlife-planning-for-your-online-accounts)

    6. **GoodTrust & Trend Micro – The Digital Afterlife Report (2025)**  
       [Report Summary](https://mygoodtrust.com/articles/the-digital-afterlife-why-your-online-assets-need-protection-too)

    ---
    – March 2026  
    Prototype for Poster Competition | Privacy-first digital protection
    """)

    st.info("💡 All links are clickable when you open the app.")

# Footer
st.markdown("---")
st.caption("LastSeen Prototype • Privacy-first digital protection • © 2026")