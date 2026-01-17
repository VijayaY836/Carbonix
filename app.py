import streamlit as st
import base64
from agents import initiate_swarm

# --- INITIAL CONFIG ---
st.set_page_config(page_title="CARBON AI | THIRAN 2026", layout="wide")

# --- IMAGE ENCODER ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

img_base64 = get_base64_of_bin_file('bg.png')

# --- SIDEBAR CONTROLS (The Dimmer Switch) ---
with st.sidebar:
    st.header("🎨 UI Settings")
    # Higher value = darker overlay = less image visibility
    bg_dimmer = st.slider("Background Dimmer", 0.0, 1.0, 0.6)
    container_opacity = st.slider("Container Opacity", 0.05, 0.5, 0.15)

# --- CSS: THE FINAL REX AESTHETIC ---
bg_style = f"""
    <style>
    /* Main Background - Image Only */
    .stApp {{
        background-image: url("data:image/png;base64,{img_base64 if img_base64 else ''}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* Dynamic Overlay to control translucency */
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, {bg_dimmer}); /* Controlled by Sidebar */
        z-index: -1;
    }}

    /* Futuristic Frosted Glass Containers */
    [data-testid="stVerticalBlock"] > div:has(div.stButton), .stMetric {{
        background: rgba(255, 255, 255, {container_opacity}) !important;
        padding: 20px !important;
        border-radius: 15px !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(0, 255, 204, 0.3) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }}

    /* Global Text Styles for maximum contrast */
    h1, h2, h3, p, span, label {{
        color: #fffff !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }}

    .stTextInput>div>div>input, .stNumberInput>div>div>input {{
        background-color: rgba(0, 0, 0, 0.5) !important;
        color: #ffffff !important;
        border: 1px solid #00ffcc !important;
    }}

    .stButton>button {{
        background-color: #00ffcc !important;
        color: #0f0c29 !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        transition: 0.3s;
    }}
    </style>
"""
st.markdown(bg_style, unsafe_allow_html=True)

# --- HEADER ---
st.title("CARBONIX - THE DYNAMIC CARBON ORCHESTRATOR")
st.subheader("Agentic Multi-Route Optimization Engine")

st.divider()

# --- MAIN INTERFACE ---
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.write("### 🚢 Shipment Manifest")
    origin = st.text_input("Origin Port", "Shanghai")
    dest = st.text_input("Destination Port", "Rotterdam")
    weight = st.number_input("Cargo Weight (MT)", value=100)
    
    if st.button("🚀 DEPLOY AGENT SWARM"):
        with st.status("Agents deliberating...", expanded=True) as status:
            st.write("🔍 Logistics Agent: Evaluating modal shifts...")
            st.write("🍃 Carbon Auditor: Calculating dynamic emissions...")
            result = initiate_swarm(origin, dest, weight)
            status.update(label="Optimization Complete!", state="complete")
        
        st.session_state['agent_result'] = result
        st.success("Recommendation Ready")

with col2:
    st.write("### 📊 Real-Time Trade-offs")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("CO2 Saved", "12.4 Tons", "-15%")
    m2.metric("Est. Cost", "$45,200", "+4%")
    m3.metric("Tax Impact", "$1,240", "Saved")
    
    st.divider()
    
    if 'agent_result' in st.session_state:
        st.write("### 🤖 Agent Final Deliberation")
        st.info(st.session_state['agent_result'])
    else:
        st.info("Ready for deployment. Adjust settings in the sidebar to optimize your view.")

# --- FOOTER ---
st.caption("Thiran 2026 | Powered by Agentic AI & Carbon-Aware Logic")