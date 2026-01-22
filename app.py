import streamlit as st
import base64
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from agents import initiate_swarm

# --- INITIAL CONFIG ---
st.set_page_config(page_title="CARBON AI | THIRAN 2026", layout="wide", initial_sidebar_state="expanded")

# --- IMAGE ENCODER ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

img_base64 = get_base64_of_bin_file('bg.png')

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("🎨 UI Settings")
    bg_dimmer = st.slider("Background Dimmer", 0.0, 1.0, 0.6)
    container_opacity = st.slider("Container Opacity", 0.05, 0.5, 0.15)
    
    st.divider()
    st.header("⚙️ Simulation Parameters")
    carbon_tax_rate = st.number_input("Carbon Tax ($/tonne CO2)", value=100, step=10)
    
    st.divider()
    st.info("**Thiran 2026**\nAgentic Carbon Optimization")

# --- CSS: ENHANCED AESTHETIC ---
bg_style = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{img_base64 if img_base64 else ''}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    .stApp::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, {bg_dimmer});
        z-index: -1;
    }}

    [data-testid="stVerticalBlock"] > div:has(div.stButton), .stMetric {{
        background: rgba(255, 255, 255, {container_opacity}) !important;
        padding: 20px !important;
        border-radius: 15px !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(0, 255, 204, 0.3) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }}

    h1, h2, h3, p, span, label {{
        color: #ffffff !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
    }}

    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>select {{
        background-color: rgba(0, 0, 0, 0.5) !important;
        color: #ffffff !important;
        border: 1px solid #00ffcc !important;
    }}

    .stButton>button {{
        background: linear-gradient(135deg, #00ffcc 0%, #00cc99 100%) !important;
        color: #0f0c29 !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
    }}
    
    .stButton>button:hover {{
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.6);
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: #00ffcc;
        padding: 8px 16px;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: rgba(0, 255, 204, 0.3);
    }}
    </style>
"""
st.markdown(bg_style, unsafe_allow_html=True)

# --- HEADER ---
st.title("🌍 CARBONIX - AI CARBON ORCHESTRATOR")
st.subheader("Multi-Agent Optimization for Sustainable Logistics")
st.divider()

# --- MAIN INTERFACE ---
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.markdown("### 🚢 Shipment Configuration")
    
    # Route input mode
    input_mode = st.radio(
        "Route Selection Mode",
        ["📋 Quick Select (Demo Routes)", "✏️ Custom Input"],
        label_visibility="collapsed"
    )
    
    if input_mode == "📋 Quick Select (Demo Routes)":
        # Predefined routes for quick demo
        routes = [
            ("Shanghai", "Rotterdam"),
            ("Singapore", "London"),
            ("Mumbai", "Hamburg"),
            ("Dubai", "Amsterdam")
        ]
        route_names = [f"{o} → {d}" for o, d in routes]
        
        selected_route = st.selectbox("Select Route", route_names)
        route_idx = route_names.index(selected_route)
        origin, dest = routes[route_idx]
        
        st.caption("💡 Switch to Custom Input to enter your own routes")
    
    else:
        # Custom input mode
        col_a, col_b = st.columns(2)
        with col_a:
            origin = st.text_input("Origin Port/City", value="Shanghai", placeholder="e.g., Tokyo")
        with col_b:
            dest = st.text_input("Destination Port/City", value="Rotterdam", placeholder="e.g., New York")
        
        st.caption("💡 Custom routes use default distance calculations")
    
    # Cargo details
    weight = st.number_input("Cargo Weight (Metric Tonnes)", value=100, min_value=1, step=10)
    
    st.markdown("---")
    
    # Deploy button
    if st.button("🚀 DEPLOY AGENT SWARM", use_container_width=True):
        with st.spinner("🤖 Agents analyzing routes..."):
            result = initiate_swarm(origin, dest, weight)
            st.session_state['agent_result'] = result
            st.session_state['origin'] = origin
            st.session_state['dest'] = dest
            st.session_state['weight'] = weight
        st.success("✅ Analysis Complete!")
        st.rerun()

with col2:
    if 'agent_result' in st.session_state:
        result = st.session_state['agent_result']
        route_data = result['route_comparison']
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Route Comparison", "🌱 Emissions Analysis", "🏭 Port Status", "🤖 Agent Insights"])
        
        with tab1:
            st.markdown("#### Route Options Comparison")
            
            # Convert to DataFrame
            df = pd.DataFrame(route_data)
            
            # Display metrics
            cols = st.columns(len(route_data))
            for idx, route in enumerate(route_data):
                with cols[idx]:
                    mode_label = route['mode'].replace('_', ' ').title()
                    st.metric(
                        label=f"{mode_label}",
                        value=f"${route['total_cost_usd']:,.0f}",
                        delta=f"{route['emissions_tonnes']} t CO₂"
                    )
            
            # Comparison table
            st.dataframe(
                df[['mode', 'distance_km', 'emissions_tonnes', 'total_cost_usd', 'transit_days']].style.format({
                    'distance_km': '{:,.0f}',
                    'emissions_tonnes': '{:.2f}',
                    'total_cost_usd': '${:,.2f}',
                    'transit_days': '{:.1f}'
                }),
                use_container_width=True
            )
            
            # Cost breakdown chart
            fig_cost = go.Figure(data=[
                go.Bar(name='Base Cost', x=df['mode'], y=df['base_cost_usd']),
                go.Bar(name='Carbon Tax', x=df['mode'], y=df['carbon_tax_usd'])
            ])
            fig_cost.update_layout(
                barmode='stack',
                title='Cost Breakdown by Mode',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis_title='Transport Mode',
                yaxis_title='Cost (USD)'
            )
            st.plotly_chart(fig_cost, use_container_width=True)
        
        with tab2:
            st.markdown("#### Carbon Emissions Deep Dive")
            
            # Emissions comparison
            fig_emissions = px.bar(
                df,
                x='mode',
                y='emissions_tonnes',
                title='CO₂ Emissions by Transport Mode',
                color='emissions_tonnes',
                color_continuous_scale='Reds'
            )
            fig_emissions.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis_title='Mode',
                yaxis_title='Emissions (Tonnes CO₂)'
            )
            st.plotly_chart(fig_emissions, use_container_width=True)
            
            # Savings potential
            baseline = df[df['mode'] == 'sea']['emissions_tonnes'].values[0]
            best = df['emissions_tonnes'].min()
            savings = baseline - best
            savings_pct = (savings / baseline) * 100
            
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Baseline Emissions", f"{baseline:.2f} t CO₂")
            col_b.metric("Best Option", f"{best:.2f} t CO₂")
            col_c.metric("Potential Savings", f"{savings:.2f} t", f"-{savings_pct:.1f}%")
            
            # Environmental impact
            st.info(f"💡 **Environmental Insight**: Choosing the greenest option saves {savings:.2f} tonnes of CO₂, equivalent to removing {(savings/4.6):.1f} cars from the road for a year.")
        
        with tab3:
            st.markdown("#### Port Congestion & Risk Assessment")
            
            origin_status = result['origin_port_status']
            dest_status = result['dest_port_status']
            
            col_x, col_y = st.columns(2)
            
            with col_x:
                st.markdown(f"**Origin: {origin_status['port']}**")
                st.metric("Congestion Level", f"{origin_status['congestion_level']}/10", origin_status['status'])
                st.metric("Est. Delay", f"{origin_status['estimated_delay_days']} days")
                st.metric("Berth Availability", origin_status['berth_availability'])
            
            with col_y:
                st.markdown(f"**Destination: {dest_status['port']}**")
                st.metric("Congestion Level", f"{dest_status['congestion_level']}/10", dest_status['status'])
                st.metric("Est. Delay", f"{dest_status['estimated_delay_days']} days")
                st.metric("Berth Availability", dest_status['berth_availability'])
            
            # Risk gauge
            avg_congestion = (origin_status['congestion_level'] + dest_status['congestion_level']) / 2
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = avg_congestion,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Overall Route Risk"},
                gauge = {
                    'axis': {'range': [None, 10]},
                    'bar': {'color': "darkred"},
                    'steps': [
                        {'range': [0, 4], 'color': "lightgreen"},
                        {'range': [4, 7], 'color': "yellow"},
                        {'range': [7, 10], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 8
                    }
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=300
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with tab4:
            st.markdown("#### Agent Deliberation Output")
            st.markdown(result['agent_output'])
    
    else:
        st.info("👈 Configure your shipment and deploy the agent swarm to see analysis")
        st.markdown("""
        ### System Capabilities:
        - ✅ Multi-agent carbon optimization
        - ✅ Real-time cost-emission trade-off analysis
        - ✅ Port congestion risk assessment
        - ✅ Carbon tax impact modeling
        - ✅ Route comparison across sea/rail modes
        """)

# --- FOOTER ---
st.divider()
st.caption("🚀 Thiran 2026 | Powered by CrewAI Multi-Agent System | Carbon-Aware Logistics Intelligence")