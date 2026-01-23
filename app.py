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

img_base64 = get_base64_of_bin_file('bg1.png')

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("🎨 UI Settings")
    bg_dimmer = st.slider("Background Dimmer", 0.0, 1.0, 0.6)
    container_opacity = st.slider("Container Opacity", 0.05, 0.5, 0.15)
    
    st.divider()
    st.header("⚙️ Simulation Parameters")
    
    # Initialize shock tax if not set
    if 'shock_tax_value' not in st.session_state:
        st.session_state['shock_tax_value'] = 100
    
    col_tax1, col_tax2 = st.columns([2, 1])
    with col_tax1:
        carbon_tax_rate = st.number_input(
            "Carbon Tax ($/tonne CO2)", 
            value=st.session_state['shock_tax_value'], 
            step=10, 
            key="carbon_tax_input"
        )
    with col_tax2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        if st.button("⚠️ Regulatory Shock", use_container_width=True, help="Simulate sudden carbon tax increase (+40%)"):
            # Trigger shock scenario
            new_tax = int(carbon_tax_rate * 1.4)  # 40% increase
            st.session_state['shock_triggered'] = True
            st.session_state['original_tax'] = carbon_tax_rate
            st.session_state['shock_tax_value'] = new_tax
            st.rerun()
    
    # Show shock alert if triggered
    if st.session_state.get('shock_triggered', False):
        original = st.session_state.get('original_tax', 100)
        new = st.session_state.get('shock_tax_value', 140)
        increase_pct = ((new - original) / original) * 100
        
        st.error(f"""
        🚨 **REGULATORY SHOCK DETECTED**
        
        Carbon tax increased from ${original}/tonne → ${new}/tonne (+{increase_pct:.0f}%)
        
        System re-optimizing routes...
        """)
        
        # Clear shock flag after display
        if st.button("✓ Acknowledge & Continue", use_container_width=True):
            st.session_state['shock_triggered'] = False
            st.rerun()
    
    st.divider()
    
    # Trilemma Optimization Weights
    with st.expander("🎯 Trilemma Optimization Weights", expanded=False):
        st.markdown("""
        **Configure policy priorities** - adjust how the AI weighs competing objectives:
        """)
        
        st.markdown("##### Decision Framework")
        cost_weight = st.slider(
            "💰 Cost Priority",
            min_value=0.0,
            max_value=1.0,
            value=0.33,
            step=0.05,
            help="Higher = prioritize minimizing total logistics cost"
        )
        
        carbon_weight = st.slider(
            "🌱 Carbon Priority",
            min_value=0.0,
            max_value=1.0,
            value=0.33,
            step=0.05,
            help="Higher = prioritize minimizing CO₂ emissions"
        )
        
        time_weight = st.slider(
            "⚡ Time Priority",
            min_value=0.0,
            max_value=1.0,
            value=0.34,
            step=0.05,
            help="Higher = prioritize faster delivery"
        )
        
        # Show normalized weights
        total_weight = cost_weight + carbon_weight + time_weight
        if total_weight > 0:
            norm_cost = cost_weight / total_weight
            norm_carbon = carbon_weight / total_weight
            norm_time = time_weight / total_weight
            
            st.markdown(f"""
            **Normalized Weights:**
            - Cost: `{norm_cost:.2f}` ({norm_cost*100:.0f}%)
            - Carbon: `{norm_carbon:.2f}` ({norm_carbon*100:.0f}%)
            - Time: `{norm_time:.2f}` ({norm_time*100:.0f}%)
            """)
            
            # Store in session state
            st.session_state['trilemma_weights'] = {
                'cost': norm_cost,
                'carbon': norm_carbon,
                'time': norm_time
            }
        else:
            st.warning("⚠️ At least one weight must be > 0")
            st.session_state['trilemma_weights'] = {
                'cost': 0.33,
                'carbon': 0.33,
                'time': 0.34
            }
        
        st.info("💡 **Enterprise Use Case**: Different stakeholders (CFO, CSO, COO) can adjust priorities based on quarterly objectives or regulatory changes.")
    
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
        # Get trilemma weights from session state
        weights = st.session_state.get('trilemma_weights', {
            'cost': 0.33,
            'carbon': 0.33,
            'time': 0.34
        })
        
        # Get current carbon tax rate
        current_tax = st.session_state.get('carbon_tax_input', 100)
        
        with st.spinner("🤖 Agents analyzing routes..."):
            result = initiate_swarm(origin, dest, weight, trilemma_weights=weights, carbon_tax_rate=current_tax)
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
        optimal = result['optimal_decision']
        
        # 🔥 AGENT DECISION CARD - THE MONEY SHOT
        st.markdown("### 🤖 AGENT-SELECTED OPTIMAL STRATEGY")
        
        decision_card = f"""
        <div style="
            background: linear-gradient(135deg, rgba(0, 255, 204, 0.15) 0%, rgba(0, 200, 255, 0.15) 100%);
            border: 2px solid #00ffcc;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 0 30px rgba(0, 255, 204, 0.3);
        ">
            <h2 style="color: #00ffcc; margin-top: 0; font-size: 24px; text-shadow: 0 0 10px rgba(0, 255, 204, 0.5);">
                ✓ {optimal['selected_mode'].replace('_', ' ').upper()}
            </h2>
            <p style="font-size: 18px; color: #ffffff; margin: 10px 0;">
                <strong>Trilemma Score:</strong> <span style="color: #00ffcc;">{optimal['trilemma_score']}</span>
                <span style="color: #888; font-size: 14px; margin-left: 10px;">(lower is better)</span>
            </p>
            <hr style="border-color: rgba(0, 255, 204, 0.3); margin: 15px 0;">
            <div style="color: #ffffff; font-size: 16px; line-height: 1.8;">
                {'<br>'.join(f'• {reason}' for reason in optimal['reasoning'])}
            </div>
        </div>
        """
        st.markdown(decision_card, unsafe_allow_html=True)
        
        # Show current trilemma weights if customized
        current_weights = st.session_state.get('trilemma_weights', {})
        current_tax = result.get('carbon_tax_rate', 100)
        
        weight_text = ""
        if current_weights and current_weights != {'cost': 0.33, 'carbon': 0.33, 'time': 0.34}:
            weight_text = f"🎯 Weights: Cost {current_weights['cost']:.0%} | Carbon {current_weights['carbon']:.0%} | Time {current_weights['time']:.0%} • "
        
        st.caption(f"{weight_text}💰 Carbon Tax: ${current_tax}/tonne CO₂")
        
        st.divider()
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Route Comparison", "🌱 Emissions Analysis", "🏭 Port Status", "🤖 Agent Insights"])
        
        with tab1:
            st.markdown("#### Route Options Comparison")
            
            # Convert to DataFrame and add trilemma scores
            df = pd.DataFrame(route_data)
            
            # Highlight the selected mode
            selected_mode = optimal['selected_mode']
            
            # Display metrics with winner highlight
            cols = st.columns(len(route_data))
            for idx, route in enumerate(route_data):
                with cols[idx]:
                    mode_label = route['mode'].replace('_', ' ').title()
                    is_selected = route['mode'] == selected_mode
                    
                    if is_selected:
                        st.markdown(f"**🏆 {mode_label}**")
                    else:
                        st.markdown(f"**{mode_label}**")
                    
                    st.metric(
                        label="Total Cost",
                        value=f"${route['total_cost_usd']:,.0f}",
                        delta=f"{route['emissions_tonnes']} t CO₂"
                    )
                    st.caption(f"Trilemma: {route.get('trilemma_score', 'N/A')}")
            
            # Comparison table
            st.dataframe(
                df[['mode', 'distance_km', 'emissions_tonnes', 'total_cost_usd', 'transit_days', 'trilemma_score']].style.format({
                    'distance_km': '{:,.0f}',
                    'emissions_tonnes': '{:.2f}',
                    'total_cost_usd': '${:,.2f}',
                    'transit_days': '{:.1f}',
                    'trilemma_score': '{:.4f}'
                }).highlight_min(subset=['trilemma_score'], color='lightgreen'),
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
            
            # Show carbon tax impact
            current_tax = result.get('carbon_tax_rate', 100)
            st.info(f"💰 **Current Carbon Tax Rate:** ${current_tax}/tonne CO₂")
            
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
            
            # Carbon tax impact comparison
            fig_tax = px.bar(
                df,
                x='mode',
                y='carbon_tax_usd',
                title=f'Carbon Tax Impact (${current_tax}/tonne)',
                color='carbon_tax_usd',
                color_continuous_scale='Oranges'
            )
            fig_tax.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis_title='Mode',
                yaxis_title='Carbon Tax (USD)'
            )
            st.plotly_chart(fig_tax, use_container_width=True)
            
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