import streamlit as st
import pandas as pd
import numpy as np
import joblib
import folium
from streamlit_folium import st_folium
import datetime
import altair as alt

import streamlit as st
import os

st.write("📂Files:")
st.write(os.listdir('.')) 
# ---------------------

# 1. PAGE CONFIGURATION & STYLING

st.set_page_config(
    page_title="NYC Road Network Analysis System",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Main Background */
    .main { background-color: #f4f6f9; }
    
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Analysis Card Container */
    .analysis-card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* Headers */
    h1 { color: #1f2937; font-family: 'Helvetica Neue', sans-serif; }
    h3 { color: #374151; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOAD RESOURCES

@st.cache_resource
def load_model():
    try:
        return joblib.load('nyc_taxi_model.pkl')
    except FileNotFoundError:
        return None

model = load_model()

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c


locations = {
    "Midtown (Times Sq)": (40.7580, -73.9855),
    "Upper East Side": (40.7736, -73.9566),
    "Downtown (Wall St)": (40.7074, -74.0113),
    "JFK Airport Hub": (40.6413, -73.7781),
    "Brooklyn Hub": (40.6782, -73.9442),
    "Queens Hub": (40.7282, -73.7949),
    "Harlem Center": (40.8079, -73.9457)
}

# 3. SIDEBAR

st.sidebar.title("🛠️ Simulation Controls")

st.sidebar.markdown("### 📍 Node Selection")
pickup_name = st.sidebar.selectbox("Origin Node", list(locations.keys()), index=0)
dropoff_name = st.sidebar.selectbox("Destination Node", list(locations.keys()), index=3)

st.sidebar.markdown("### ⏰ Temporal Conditions")
trip_date = st.sidebar.date_input("Date", datetime.date.today())


st.sidebar.markdown("**Simulation Hour**")
selected_hour = st.sidebar.slider("Hour of Day (0-23)", 0, 23, 14, help="Move the slider to simulate traffic at different times.")


trip_time = datetime.time(selected_hour, 0)
st.sidebar.warning(f"🕒 Simulating Traffic for: **{selected_hour}:00**")

pickup_coords = locations[pickup_name]
dropoff_coords = locations[dropoff_name]

# 4. MAIN DASHBOARD

st.title("🛣️ Road Network Performance Analysis")
st.markdown("Real-time prediction of network efficiency, congestion levels, and flow speed based on historical mobility data.")

if model is None:
    st.error(" Model file not found. Please run 'train_model.py' first.")
else:
     
    input_datetime = datetime.datetime.combine(trip_date, trip_time)
    dist_km = haversine_distance(pickup_coords[0], pickup_coords[1], dropoff_coords[0], dropoff_coords[1])
    
    input_df = pd.DataFrame({
        'pickup_longitude': [pickup_coords[1]],
        'pickup_latitude': [pickup_coords[0]],
        'dropoff_longitude': [dropoff_coords[1]],
        'dropoff_latitude': [dropoff_coords[0]],
        'distance_km': [dist_km],
        'hour': [input_datetime.hour],
        'day_of_week': [input_datetime.weekday()]
    })
    
    # Prediction
    pred_seconds = model.predict(input_df)[0]
    pred_minutes = pred_seconds / 60
    
    # Metrics
    free_flow_speed = 55 # km/h 
    ideal_time_minutes = (dist_km / free_flow_speed) * 60
    predicted_speed = dist_km / (pred_minutes / 60)
    
    efficiency_index = (predicted_speed / free_flow_speed) * 100
    if efficiency_index > 100: efficiency_index = 100
    congestion_level = 100 - efficiency_index

    #  KPI CARDS
    st.markdown("### 📊 Network Key Performance Indicators")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    kpi1.metric("⏱️ Estimated Duration", f"{int(pred_minutes)} min", f"{int(pred_seconds%60)} sec")
    kpi2.metric("📏 Route Distance", f"{dist_km:.2f} km")
    kpi3.metric("🚀 Flow Speed", f"{predicted_speed:.1f} km/h", delta=f"{predicted_speed-free_flow_speed:.1f} km/h", delta_color="normal")
    kpi4.metric("📉 Congestion Level", f"{congestion_level:.1f}%", delta="-Low" if congestion_level < 30 else "+High", delta_color="inverse")

    st.markdown("---")

    col_map, col_analysis = st.columns([1.3, 1], gap="large")

    with col_map:
        st.subheader("📍 Geospatial Network Visualization")
        
        route_color = "#4aed1c" 
        if congestion_level > 40: route_color = "#09efff" 
        if congestion_level > 60: route_color = "#670d03" 
            
        m = folium.Map(location=[(pickup_coords[0]+dropoff_coords[0])/2, (pickup_coords[1]+dropoff_coords[1])/2], 
                       zoom_start=11, tiles='CartoDB positron')
        
        
        folium.PolyLine([pickup_coords, dropoff_coords], color=route_color, weight=5, opacity=0.9).add_to(m)
        
       
        folium.Marker(pickup_coords, icon=folium.Icon(color="blue", icon="play", prefix='fa'), popup="Origin").add_to(m)
        folium.Marker(dropoff_coords, icon=folium.Icon(color="black", icon="flag", prefix='fa'), popup="Destination").add_to(m)
        
        st_folium(m, height=450, use_container_width=True)

    with col_analysis:
        st.subheader("📈 Efficiency & Flow Analysis")
        
        
        with st.container():
            
            if efficiency_index < 40:
                st.error(f"🚨 CRITICAL CONGESTION: Network operating at only {efficiency_index:.0f}% capacity.")
            elif efficiency_index < 70:
                st.warning(f"⚠️ MODERATE TRAFFIC: Expect delays of approx. {int(pred_minutes - ideal_time_minutes)} mins.")
            else:
                st.success("✅ FREE FLOW: Network operating at optimal capacity.")

            st.write("") 

           
            st.markdown("**Actual vs. Free-Flow Duration**")
            chart_data = pd.DataFrame({
                'Scenario': ['Ideal Condition', 'Current Prediction'],
                'Time (min)': [ideal_time_minutes, pred_minutes],
                'Color': ['#2ecc71', route_color]
            })
            
            bar_chart = alt.Chart(chart_data).mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10).encode(
                x=alt.X('Scenario', axis=alt.Axis(labelAngle=0)),
                y='Time (min)',
                color=alt.Color('Color', scale=None),
                tooltip=['Scenario', 'Time (min)']
            ).properties(height=200)
            
            st.altair_chart(bar_chart, use_container_width=True)

            
            st.write(f"**Network Efficiency Score: {efficiency_index:.1f}/100**")
            st.progress(int(efficiency_index))
            
            st.caption(f"This segment allows an average speed of {predicted_speed:.1f} km/h under selected conditions.")

    
    with st.expander("📄 Generate Detailed Report"):
        st.write(f"""
        ### Road Network Assessment Report
        * **Segment:** {pickup_name} to {dropoff_name}
        * **Date/Time:** {trip_date} at {trip_time}
        * **Analysis:**
            * The theoretical free flow travel time is **{ideal_time_minutes:.1f} min**.
            * The ML model predicts a travel time of **{pred_minutes:.1f} min**.
            * This represents a time loss of **{pred_minutes - ideal_time_minutes:.1f} min** due to network impedance.
            * Congestion Impact Factor: **{congestion_level:.2f}**

        """)
