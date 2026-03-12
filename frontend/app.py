import streamlit as st
import pydeck as pdk
import pandas as pd
import requests
import time
import random
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIG & CUSTOM CSS (The Apple/SaaS Vibe) ---
st.set_page_config(page_title="Q-Traffic Enterprise", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* Sleek Typography & Background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    /* Premium Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        letter-spacing: 0.5px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 114, 255, 0.4);
    }
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #ffffff;
    }
    [data-testid="stMetricDelta"] {
        font-size: 1rem !important;
    }
    /* Dividers */
    hr {
        border-color: #30363d;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZATION & STATE ---
st.sidebar.title("🌍 Grid Operations")
locations = {
    "Silk Board": (12.9172, 77.6228),
    "Indiranagar 100ft": (12.9719, 77.6412),
    "Koramangala Sony World": (12.9345, 77.6214),
    "Whitefield Hope Farm": (12.9830, 77.7500)
}
selected_loc = st.sidebar.selectbox("Sector Selection", list(locations.keys()))
center_lat, center_lon = locations[selected_loc]
num_nodes = 10

def generate_grid():
    st.session_state.sim_running = False
    st.session_state.sim_finished = False
    st.session_state.tick = 0
    st.session_state.history = {"tick": [], "classical_wait": [], "ai_wait": [], "quantum_wait": []}
    st.session_state.junction_names = [f"Node_{i+1}" for i in range(num_nodes)]
    
    st.session_state.coords = {}
    for j in st.session_state.junction_names:
        st.session_state.coords[j] = {
            "ns": (center_lat + random.uniform(-0.015, 0.015), center_lon + random.uniform(-0.015, 0.015)),
            "ew": (center_lat + random.uniform(-0.015, 0.015), center_lon + random.uniform(-0.015, 0.015))
        }
        
    st.session_state.grids = {}
    for model in ["classical", "ai", "quantum"]:
        st.session_state.grids[model] = {
            j: {"ns_cars": random.randint(15, 40), "ew_cars": random.randint(15, 40), 
                "ns_wait": 0, "ew_wait": 0, "ns_green": True, "ew_green": False,
                "ns_green_time": 0, "ew_green_time": 0} for j in st.session_state.junction_names
        }

if st.sidebar.button("Initialize Sector Grid") or 'junction_names' not in st.session_state:
    generate_grid()

# --- HEADER ---st.markdown(f"<h1 style='text-align: center; color: white;'>⚛️ Q-TRAFFIC ENTERPRISE : {selected_loc.upper()}</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e;'>Quantum-Assisted Traffic Signal Optimization Engine</p>", unsafe_allow_html=True)

# --- CONTROLS ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("▶ START / 🛑 STOP LIVE SIMULATION", use_container_width=True):
        st.session_state.sim_running = not st.session_state.sim_running
        if not st.session_state.sim_running and st.session_state.tick > 0:
            st.session_state.sim_finished = True  # Trigger reports when stopped

# --- LIVE SIMULATION VIEW ---
if not st.session_state.get('sim_finished', False):
    
    st.markdown("### 📡 Live Geospatial Telemetry")
    map_data = []
    for j_name, loc in st.session_state.coords.items():
        q_grid = st.session_state.grids["quantum"][j_name]
        c_ns = [0, 255, 128, 200] if q_grid["ns_green"] else [255, 60, 60, 200]
        c_ew = [0, 255, 128, 200] if q_grid["ew_green"] else [255, 60, 60, 200]
        map_data.append({"junction": j_name, "dir": "N/S", "lat": loc["ns"][0], "lon": loc["ns"][1], "cars": q_grid["ns_cars"], "color": c_ns})
        map_data.append({"junction": j_name, "dir": "E/W", "lat": loc["ew"][0], "lon": loc["ew"][1], "cars": q_grid["ew_cars"], "color": c_ew})

    df_map = pd.DataFrame(map_data)
    view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=14.2, pitch=45)
    layer = pdk.Layer(
        "ColumnLayer", data=df_map, get_position=["lon", "lat"], get_elevation="cars",
        elevation_scale=4, radius=35, get_fill_color="color", pickable=True, auto_highlight=True,
    )
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{junction} {dir}: {cars} cars waiting"}))

    st.markdown("### 📊 Real-Time Optimization Engine")
    col_c, col_a, col_q = st.columns(3)

    def render_column(col, title, model_key, accent_color):
        with col:
            st.markdown(f"<h3 style='color: {accent_color};'>{title}</h3>", unsafe_allow_html=True)
            total_wait = sum(j["ns_wait"] + j["ew_wait"] for j in st.session_state.grids[model_key].values())
            total_cars = sum(j["ns_cars"] + j["ew_cars"] for j in st.session_state.grids[model_key].values())
            st.metric("Total Sector Wait Time", f"{total_wait} sec")
            st.metric("Vehicles in Queue", f"{total_cars}")
            
            with st.expander("Detailed Junction Telemetry"):
                for j_name in st.session_state.junction_names:
                    j_data = st.session_state.grids[model_key][j_name]
                    n_time = f"({j_data['ns_green_time']}s)" if j_data['ns_green'] else ""
                    e_time = f"({j_data['ew_green_time']}s)" if j_data['ew_green'] else ""
                    st.write(f"**{j_name}**")
                    st.write(f"{'🟢' if j_data['ns_green'] else '🔴'} NS: {j_data['ns_cars']} | Wait: {j_data['ns_wait']}s {n_time}")
                    st.write(f"{'🟢' if j_data['ew_green'] else '🔴'} EW: {j_data['ew_cars']} | Wait: {j_data['ew_wait']}s {e_time}")
                    st.write("---")

    render_column(col_c, "🏛️ Legacy (Classical)", "classical", "#ff7b72")
    render_column(col_a, "🤖 AI Heuristic", "ai", "#d2a8ff")
    render_column(col_q, "⚛️ Quantum QUBO", "quantum", "#79c0ff")

    # --- SIMULATION LOOP ---
    if st.session_state.sim_running:
        time.sleep(0.5)
        st.session_state.tick += 1
        
        new_traffic = {j: {"ns": random.randint(0, 3), "ew": random.randint(0, 3)} for j in st.session_state.junction_names}
        
        for model in ["classical", "ai", "quantum"]:
            for j_name in st.session_state.junction_names:
                grid = st.session_state.grids[model][j_name]
                grid["ns_cars"] += new_traffic[j_name]["ns"]
                grid["ew_cars"] += new_traffic[j_name]["ew"]
                if grid["ns_green"]:
                    grid["ns_cars"] = max(0, grid["ns_cars"] - 6)
                    grid["ns_wait"] = 0
                    grid["ew_wait"] += 1
                    grid["ns_green_time"] += 1
                    grid["ew_green_time"] = 0
                else:
                    grid["ew_cars"] = max(0, grid["ew_cars"] - 6)
                    grid["ew_wait"] = 0
                    grid["ns_wait"] += 1
                    grid["ew_green_time"] += 1
                    grid["ns_green_time"] = 0

        # Data Logging for Charts
        st.session_state.history["tick"].append(st.session_state.tick)
        st.session_state.history["classical_wait"].append(sum(j["ns_wait"] + j["ew_wait"] for j in st.session_state.grids["classical"].values()))
        st.session_state.history["ai_wait"].append(sum(j["ns_wait"] + j["ew_wait"] for j in st.session_state.grids["ai"].values()))
        st.session_state.history["quantum_wait"].append(sum(j["ns_wait"] + j["ew_wait"] for j in st.session_state.grids["quantum"].values()))

        payload = {"junctions": []}
        for j_name in st.session_state.junction_names:
            q_grid = st.session_state.grids["quantum"][j_name]
            payload["junctions"].append({
                "id": j_name, "ns_cars": q_grid["ns_cars"], "ew_cars": q_grid["ew_cars"],
                "ns_wait": q_grid["ns_wait"], "ew_wait": q_grid["ew_wait"],
                "ns_green": q_grid["ns_green"], "ew_green": q_grid["ew_green"],
                "ns_green_time": q_grid["ns_green_time"], "ew_green_time": q_grid["ew_green_time"]
            })
            
        try:
            res = requests.post("http://127.0.0.1:8000/simulate_all", json=payload)
            if res.status_code == 200:
                decisions = res.json()
                for model in ["classical", "ai", "quantum"]:
                    for j_name in st.session_state.junction_names:
                        st.session_state.grids[model][j_name]["ns_green"] = decisions[model][j_name]["ns"]
                        st.session_state.grids[model][j_name]["ew_green"] = decisions[model][j_name]["ew"]
        except Exception:
            pass

        st.rerun()

# --- POST-SIMULATION ANALYTICS REPORT ---
else:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #58a6ff;'>📈 Executive Simulation Report</h2>", unsafe_allow_html=True)
    
    # Calculate Business Metrics
    c_wait_total = sum(st.session_state.history["classical_wait"])
    q_wait_total = sum(st.session_state.history["quantum_wait"])
    
    time_saved_sec = c_wait_total - q_wait_total
    efficiency_inc = ((c_wait_total - q_wait_total) / max(1, c_wait_total)) * 100
    
    # Assumption: An idling car wastes ~1 liter per hour. 
    # Formula: (Seconds Saved) * (1 hour / 3600 sec) * (1 Liter)
    fuel_saved_liters = time_saved_sec / 3600.0
    carbon_prevented_kg = fuel_saved_liters * 2.31 # 2.31 kg of CO2 per liter of petrol

    rc1, rc2, rc3, rc4 = st.columns(4)
    rc1.metric("Quantum Efficiency Boost", f"+{efficiency_inc:.1f}%")
    rc2.metric("Total Commuter Time Saved", f"{time_saved_sec} sec")
    rc3.metric("Estimated Fuel Saved", f"{fuel_saved_liters:.2f} L")
    rc4.metric("CO2 Emissions Prevented", f"{carbon_prevented_kg:.2f} kg")
    
    st.write("---")
    
    # Chart 1: Time Series of Grid Congestion
    st.markdown("### Grid Congestion Over Time (Wait Time Penalty)")
    df_hist = pd.DataFrame(st.session_state.history)
    fig1 = px.line(df_hist, x="tick", y=["classical_wait", "ai_wait", "quantum_wait"],
                   labels={"value": "Total Wait Time (sec)", "tick": "Simulation Time (Ticks)", "variable": "Algorithm"},
                   color_discrete_map={"classical_wait": "#ff7b72", "ai_wait": "#d2a8ff", "quantum_wait": "#79c0ff"})
    fig1.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white", margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig1, use_container_width=True)
    
    col_chart1, col_chart2 = st.columns(2)
    
    # Chart 2: Total Fuel Burned (Bar Chart)
    with col_chart1:
        st.markdown("### Total Fuel Wasted by Idling (Liters)")
        fuel_data = pd.DataFrame({
            "Method": ["Legacy (Classical)", "AI (Heuristic)", "Quantum (QUBO)"],
            "Fuel Wasted (L)": [c_wait_total/3600, sum(st.session_state.history["ai_wait"])/3600, q_wait_total/3600]
        })
        fig2 = px.bar(fuel_data, x="Method", y="Fuel Wasted (L)", color="Method",
                      color_discrete_sequence=["#ff7b72", "#d2a8ff", "#79c0ff"])
        fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Chart 3: Performance Distribution (Donut)
    with col_chart2:
        st.markdown("### Total Traffic Bottleneck Distribution")
        fig3 = px.pie(fuel_data, values="Fuel Wasted (L)", names="Method", hole=0.5,
                      color_discrete_sequence=["#ff7b72", "#d2a8ff", "#79c0ff"])
        fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig3, use_container_width=True)
        
    if st.button("Reset Grid & Run Another Simulation"):
        generate_grid()
        st.rerun()