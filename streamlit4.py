import streamlit as st
import requests
import speech_recognition as sr
import folium
from streamlit_folium import folium_static
import pandas as pd
import json
from mordecai3 import Geoparser

# Streamlit page configuration
st.set_page_config(page_title="Context Aware Geospatial Data Retrieval Using NLP/LLM", layout="wide")

# Sidebar for model selection
st.sidebar.title("Select Model")
model = st.sidebar.radio("Choose a model", ["GPT-4", "GPT-3.5", "LLaMA 2", "LLaMA 3"])

# Function to query the Flask backend
def query_backend(user_query, chat_history):
    try:
        response = requests.post(
            "http://localhost:5000/query",  # Ensure this matches the Flask server URL
            json={"query": user_query, "chat_history": chat_history}
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
        return {"answer": "Sorry, there was an issue with the server."}
    except ValueError as json_err:
        st.error(f"JSON decode error: {json_err} - {response.text}")
        return {"answer": "Sorry, I couldn't find an answer."}
    except Exception as err:
        st.error(f"An unexpected error occurred: {err}")
        return {"answer": "Sorry, an unexpected error occurred."}

# Initialize microphone and recognizer
recognizer = sr.Recognizer()

# Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Location data storage
if "locations" not in st.session_state:
    st.session_state.locations = []

# Function to handle speech recognition
def handle_speech():
    with sr.Microphone() as source:
        st.info("Listening... Speak something!")

        try:
            audio = recognizer.listen(source)
            user_input = recognizer.recognize_google(audio)

            result = query_backend(user_input, st.session_state.chat_history)
            answer = result.get("answer", "Sorry, I couldn't find an answer.")
            st.session_state.chat_history.append({"user": user_input, "bot": answer})

            # Initialize Geoparser
            geo = Geoparser()

            # Geoparse the answer to extract locations
            data = geo.geoparse_doc(answer)

            for entity in data.get('geolocated_ents', []):
                lat = entity.get('lat')
                lng = entity.get('lon')
                if lat and lng:
                    st.session_state.locations.append({"lat": lat, "lng": lng})

        except sr.UnknownValueError:
            st.warning("Oops! Didn't catch that. Could you speak again?")
        except sr.RequestError:
            st.error("Sorry, my speech service is down.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# User input
user_input = st.sidebar.text_input("Ask me anything:")

if st.sidebar.button("Send"):
    if user_input:
        result = query_backend(user_input, st.session_state.chat_history)
        answer = result.get("answer", "Sorry, I couldn't find an answer.")
        st.session_state.chat_history.append({"user": user_input, "bot": answer})

# Speech recognition button
if st.sidebar.button("Start Speech Recognition"):
    handle_speech()

# Display chat history
st.sidebar.subheader("Chat History")
for chat in st.session_state.chat_history:
    st.sidebar.markdown(f"*You:* {chat['user']}")
    st.sidebar.markdown(f"*Bot:* {chat['bot']}")

# Model information
st.sidebar.markdown("### Model Information")
st.sidebar.write(f"Using *{model}* for responses.")

# World Map display
st.title("World Map")

def draw_folium_map(locations):
    if locations:
        map_center = [locations[0]['lat'], locations[0]['lng']]
        folium_map = folium.Map(location=map_center, zoom_start=5)

        for loc in locations:
            folium.Marker(
                [loc['lat'], loc['lng']],
                popup=f"Latitude: {loc['lat']}, Longitude: {loc['lng']}"
            ).add_to(folium_map)

        return folium_map
    else:
        return folium.Map(location=[0, 0], zoom_start=2)

# Creating the map
if st.session_state.locations:
    folium_map = draw_folium_map(st.session_state.locations)
    folium_static(folium_map)
else:
    st.map()  # Displays a simple map if no locations found

# Unstructured Data Analysis and Geo Named Entity Recognition side by side
col1, col2 = st.columns([2, 1])  # Adjust column widths as needed

# Unstructured Data Analysis text box
with col1:
    st.write("#### Unstructured Data Analysis:")
    unstructured_input = st.text_area("Type your analysis here:")

# Geo Named Entity Recognition table
with col2:
    st.write("#### Geo Named Entity Recognition:")
    # Create an empty DataFrame for the table with column headers
    empty_data = {
        "Entity": [],
        "Coordinates": [],
        "Country": []
    }
    df_empty = pd.DataFrame(empty_data)
    # Display the empty table
    st.table(df_empty)

# Parse button for unstructured data analysis
if st.button('Parse'):
    if unstructured_input:
        # Initialize Geoparser
        geo = Geoparser()
        # Parse the input text
        parsed_data = geo.geoparse_doc(unstructured_input)

        # Debugging: Print the type and content of parsed_data
        st.write('Type of parsed_data:', type(parsed_data))
        st.write('Parsed Data:', parsed_data)

        # If parsed_data is a string, try to parse it as JSON
        if isinstance(parsed_data, str):
            try:
                parsed_data = json.loads(parsed_data)
                st.write('Parsed Data (from JSON):', parsed_data)
            except json.JSONDecodeError as e:
                st.error(f"JSON Decode Error: {e}")

        # Check the structure and access data appropriately
        geolocated_ents = parsed_data.get('geolocated_ents', [])
        if isinstance(geolocated_ents, list):  # Ensure it's a list
            try:
                parsed_df = pd.DataFrame([
                    {
                        "Entity": entity.get('name', 'N/A'),  # Use get to handle missing keys
                        "Coordinates": f"{entity.get('lat', 'N/A')}, {entity.get('lon', 'N/A')}",
                        "Country": entity.get('country_code3', 'N/A')
                    }
                    for entity in geolocated_ents if isinstance(entity, dict)
                ])
                st.table(parsed_df)

                # Update the map with parsed locations
                for entity in geolocated_ents:
                    if isinstance(entity, dict):
                        lat = entity.get('lat')
                        lng = entity.get('lon')
                        if lat and lng:
                            st.session_state.locations.append({"lat": lat, "lng": lng})
                
                # Redraw the map with new locations
                folium_map = draw_folium_map(st.session_state.locations)
                folium_static(folium_map)

            except KeyError as e:
                st.error(f"KeyError: {e}")
        else:
            st.warning('Parsed data is not in the expected format.')
    else:
        st.warning('Please enter text to parse.')

# Function to extract and plot the location of Bangalore
def extract_bangalore_location():
    geo = Geoparser()
    data = geo.geoparse_doc("give the latitude and longitude of bangalore")

    # Check if data is successfully parsed and contains location info
    if data and 'geolocated_ents' in data:
        for entity in data['geolocated_ents']:
            if entity.get('name') == 'Bangalore':
                lat = entity.get('lat')
                lng = entity.get('lon')
                if lat and lng:
                    st.session_state.locations.append({"lat": lat, "lng": lng})
                    st.success(f"Bangalore location found: Latitude {lat}, Longitude {lng}")
                    return
    st.error("Bangalore location not found.")

# Button to extract and plot the location of Bangalore
if st.sidebar.button("Extract Bangalore Location"):
    extract_bangalore_location()
    # Redraw the map with new locations
    if st.session_state.locations:
        folium_map = draw_folium_map(st.session_state.locations)
        folium_static(folium_map)
