import streamlit as st
import time
import requests
import folium
from streamlit_folium import st_folium
from folium import IFrame
from folium.features import CustomIcon
import pandas as pd
import os
from actuel import Data_actuel, Read_actuel, predict_actuel, filter_actuel
import plotly.graph_objects as go

# API Key for OpenWeather
api_key = "4edc9281ea0d683c6caf71c7fdfdb7fa"  # Replace with your actual API key

# Major cities in Morocco with their coordinates
cities_coords = {
    "Casablanca": [33.5731, -7.5898],
    "Tétouan": [35.5785, -5.3684],
    "Ifrane": [33.5324, -5.1074],
    "Ouarzazate": [30.9406, -6.9379],
    "Laayoune": [27.1253, -13.1625]
}

path_model = {
    'Casablanca': r"C:\Users\Lenovo\Desktop\BD Pr\lr_model_1_casablanca.model",
    'Tétouan': r"C:\Users\Lenovo\Desktop\BD Pr\lr_model_2_tétouan.model",
    'Ouarzazate': r"C:\Users\Lenovo\Desktop\BD Pr\lr_model_3_ouarzazate.model",
    'Ifrane': r"C:\Users\Lenovo\Desktop\BD Pr\lr_model_4_ifrane.model",
    'Laayoune': r"C:\Users\Lenovo\Desktop\BD Pr\lr_model_5_laayoune.model"
}

# Function to get weather data for a city
def get_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        icon = data['weather'][0]['icon']
        return icon
    else:
        print(f"Error retrieving data for {city}")
        return None

# Function to check update time
def check_update_time(last_update_time):
    current_time = time.time()
    update_interval = 15 * 60  # 15 minutes in seconds
    return current_time - last_update_time >= update_interval

# Function to run data updates
def update_data():
    Data_actuel()
    st.session_state.last_update_time = time.time()

# Main function to render the app
def main():
    st.markdown("""
        <style>
            [data-testid=stSidebar] {
                background-color: rgba(135, 206, 235, 0.5);
                padding: 20px;
                border-radius: 10px;
            }
            .centered {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .stButton>button {
                background-color: #5993C2;
                color: white;
                width: 100%;
                padding: 10px;
                border-radius: 5px;
            }
            .stSelectbox:first-of-type > div[data-baseweb="select"] > div {
                background-color: #5993C2;
                padding: 10px;
                border-radius: 5px;
                color: white;
            }
        </style>
    """, unsafe_allow_html=True)

    page_img = '''
        <style>
        [data-testid="stAppViewContainer"]{
            background-image: url("https://images.pexels.com/photos/1118873/pexels-photo-1118873.jpeg?cs=srgb&dl=pexels-jplenio-1118873.jpg&fm=jpg");
            background-size: cover;
        }
        [data-testid="stHeader"]{
            background-color: rgba(135, 206, 235, 0.5);
            background-size: cover;
        }
        </style>
    '''
    st.markdown(page_img, unsafe_allow_html=True)

    st.sidebar.markdown("""
        <div style='text-align: center;'>
            <img src='https://icons.iconarchive.com/icons/alecive/flatwoken/512/Apps-Weather-icon.png' style='width: 120px;'>
            <h1 style='color: #0055CC; font-weight: bold;'>Weather Forecasting</h1>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <style>
            div.stTextInput>div>div>input {
                background-color: #0066CC;
            }
        </style>
    """, unsafe_allow_html=True)

    cities = ["Casablanca", "Tétouan", "Ouarzazate", "Ifrane", "Laayoune"]
    city = st.sidebar.selectbox("", cities, key="city-selectbox")

    # Get the last update time from the session state
    last_update_time = st.session_state.get('last_update_time', 0)

    # Check if it's time to execute Data_actuel()
    if check_update_time(last_update_time):
        update_data()
        st.experimental_rerun()  # Rerun the app after data update

    # Set up session state for buttons
    if 'show_map' not in st.session_state:
        st.session_state.show_map = False
    if 'show_chart' not in st.session_state:
        st.session_state.show_chart = False

    if st.sidebar.button("Show Map"):
        st.session_state.show_map = True
        st.session_state.show_chart = False

    if st.sidebar.button("Show Temperature Chart"):
        st.session_state.show_map = False
        st.session_state.show_chart = True

    # Button to return to the default view
    if st.session_state.show_map or st.session_state.show_chart:
        if st.sidebar.button("Back to City Variables"):
            st.session_state.show_map = False
            st.session_state.show_chart = False

    if not st.session_state.show_map and not st.session_state.show_chart:
        if city:
            st.title(f"Weather Updates for {city}:")
            with st.spinner("Fetching weather data..."):
                df1 = Read_actuel()
                data1 = predict_actuel(df1, city, path_model[city])
                actuel_data = data1.toPandas()

                if actuel_data.get("cod") != 404:
                    description = actuel_data['Description']
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Temperature🌡️", f"{int(actuel_data['Temperature (°C)'])} °C")
                        st.metric("Temperature predict🌡️", f"{int(actuel_data['temperature_predict (°C)'])} °C")
                    with col2:
                        if (actuel_data['rain_1h (mm)'] > 0).any():
                            st.metric("Rain ☔", f"{actuel_data['rain_1h (mm)'].max()} mm")
                        else:
                            st.metric("Rain ☔", "N/A")
                        st.metric("Wind Speed 💨", "{:.2f} m/s".format(actuel_data['winds (m/s)'][0]))
                    with col3:
                        st.metric("Cloudiness ☁️", f"{int(actuel_data['Clouds']*100)} %")
                        st.metric("Humidity 💧", f"{int(actuel_data['Humidity']*100)} %")
                else:
                    st.error("City not found or an error occurred!")

    # Prepare data for the map and chart
    df = Read_actuel()
    df_processed_data = pd.DataFrame(columns=["City", "Timestamp", "Temperature (°C)", "winds (m/s)", "rain_1h (mm)", "Description", "Humidity", "Clouds", "features", "temperature_predict (°C)"])
    for city in cities:
        actuel_data_pr = predict_actuel(df, city, path_model[city])
        actuel_data_pd = actuel_data_pr.toPandas()
        df_processed_data = pd.concat([df_processed_data, actuel_data_pd], ignore_index=True)
        df_processed_data['temperature_predict (°C)'] = df_processed_data['temperature_predict (°C)'].astype(int)

    # Create a DataFrame for top cities
    columns = ["City", "Temperature (°C)", "Description", "temperature_predict (°C)", "icon", "coords"]
    top_cities = pd.DataFrame(columns=columns)

    for city, coords in cities_coords.items():
        icon = get_weather_data(city)
        if not df_processed_data[df_processed_data['City'] == city].empty:
            temp = df_processed_data.loc[df_processed_data['City'] == city, 'Temperature (°C)'].values[0]
            temp_pr = df_processed_data.loc[df_processed_data['City'] == city, 'temperature_predict (°C)'].values[0]
            weather_description = df_processed_data.loc[df_processed_data['City'] == city, 'Description'].values[0]
        else:
            temp = None
            temp_pr = None
            weather_description = None

        data = [city, temp, weather_description, temp_pr, icon, coords]
        city_data = pd.Series(data, index=columns)
        top_cities = pd.concat([top_cities, city_data.to_frame().T], ignore_index=True)

    # Local icon mapping
    icon_mapping = {
        "01d": "sun.png",
        "01n": "moon.png",
        "02d": "partly_cloudy_day.png",
        "02n": "partly_cloudy_night.png",
        "03d": "cloudy_day.png",
        "03n": "cloudy_night.png",
        "04d": "overcast_day.png",
        "04n": "overcast_night.png",
        "09d": "shower_rain_day.png",
        "09n": "shower_rain_night.png",
        "10d": "rain-day.png",
        "10n": "rain-night.png",
        "11d": "thunderstorm_day.png",
        "11n": "thunderstorm_night.png",
        "13d": "snow_day.png",
        "13n": "snow_night.png",
        "50d": "mist_day.png",
        "50n": "mist_night.png"
    }

    # Path to the folder containing local icons
    icon_folder = r"C:\Users\Lenovo\Desktop\BD Pr\icons"

    if st.session_state.show_map:
        # Create a map with folium
        map_center = [31.7917, -7.0926]
        m = folium.Map(location=map_center, zoom_start=6, tiles='CartoDB positron')

        # Add markers for each city
        for _, row in top_cities.iterrows():
            city = row['City']
            coords = row['coords']
            temp = row['Temperature (°C)']
            temp_pr = row['temperature_predict (°C)']
            weather_description = row['Description']
            icon = row['icon']

            custom_icon_path = os.path.join(icon_folder, icon_mapping.get(icon, "default.png"))

            popup_content = f"""
            <div style="font-size: 16px; text-align: center;">
                <strong>{city}</strong><br>
                Temperature: {temp}°C / Predicted: {temp_pr}°C<br>
                {weather_description}<br>
                <img src='{custom_icon_path}' width='50' height='50'>
            </div>
            """
            iframe = IFrame(html=popup_content, width=250, height=200)
            popup = folium.Popup(iframe, max_width=350)
            tooltip = f"{city}: {temp}°C / {temp_pr}°C, {weather_description}"

            folium.Marker(
                location=coords,
                popup=popup,
                tooltip=tooltip,
                icon=CustomIcon(custom_icon_path, icon_size=(50, 50))  # Increased icon size
            ).add_to(m)

        url_drapeau_maroc = "https://upload.wikimedia.org/wikipedia/commons/2/2c/Flag_of_Morocco.svg"

        # Utilisation de st.markdown avec du HTML pour inclure l'image dans le texte
        st.markdown(f"""
        ## **Carte météo** <img src="{url_drapeau_maroc}" width="50"/>
        """, unsafe_allow_html=True)
        # Ajout d'espace entre le titre et la carte météo
        st.write(" ")

        st_folium(m, width=800, height=600)

    if st.session_state.show_chart:

        st.markdown("## **Comparaison des températures**")

        # Ajout d'espace entre le titre et la carte météo
        st.write(" ")


        # Prepare data for the combined line chart
        chart_data = top_cities.melt(id_vars=["City"], value_vars=["Temperature (°C)", "temperature_predict (°C)"], var_name="Type", value_name="Temperature")

        # Use plotly.graph_objects to create an interactive line chart with different shades of red
        fig = go.Figure()

        # Add actual temperature trace
        fig.add_trace(go.Scatter(
            x=chart_data[chart_data['Type'] == 'Temperature (°C)']['City'],
            y=chart_data[chart_data['Type'] == 'Temperature (°C)']['Temperature'],
            mode='lines+markers',
            name='Actual Temperature',
            line=dict(color='red'),
            marker=dict(color='red')
        ))

        # Add predicted temperature trace
        fig.add_trace(go.Scatter(
            x=chart_data[chart_data['Type'] == 'temperature_predict (°C)']['City'],
            y=chart_data[chart_data['Type'] == 'temperature_predict (°C)']['Temperature'],
            mode='lines+markers',
            name='Predicted Temperature',
            line=dict(color='darkred'),
            marker=dict(color='darkred')
        ))

        fig.update_layout(
            xaxis_title='City',
            yaxis_title='Temperature (°C)',
            template='plotly_white',
            plot_bgcolor='rgba(135, 206, 235, 0.5)',  # Sky blue with 50% opacity
            paper_bgcolor='rgba(135, 206, 235, 0.5)'  # Sky blue with 50% opacity
        )

        # Display the plotly chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
