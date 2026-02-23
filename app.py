import streamlit as st
import pandas as pd
from ntscraper import Nitter
import folium
from streamlit_folium import st_folium
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
from unidecode import unidecode
import time

# Page Configuration
st.set_page_config(layout="wide", page_title="Monitoreo Seguridad Carretera México")

# Constants
SEARCH_TERMS = ['narcobloqueo', 'carretera bloqueada', 'quema de vehículos', 'enfrentamiento México']
CRITICAL_KEYWORDS = ['km', 'autopista', 'caseta', 'carretera', 'tramo', 'zona']

# Dictionary of coordinates for Mexican states and key cities
LOCATIONS = {
    'AGUASCALIENTES': [21.8853, -102.2916],
    'BAJA CALIFORNIA': [30.8406, -115.2838],
    'BAJA CALIFORNIA SUR': [26.0444, -111.6661],
    'CAMPECHE': [19.8301, -90.5349],
    'CHIAPAS': [16.7569, -93.1292],
    'CHIHUAHUA': [28.6353, -106.0889],
    'CIUDAD DE MÉXICO': [19.4326, -99.1332],
    'CDMX': [19.4326, -99.1332],
    'COAHUILA': [27.0587, -101.7068],
    'COLIMA': [19.2452, -103.7241],
    'DURANGO': [24.0277, -104.6532],
    'GUANAJUATO': [21.0190, -101.2574],
    'GUERRERO': [17.4392, -99.5451],
    'HIDALGO': [20.0911, -98.7624],
    'JALISCO': [20.6597, -103.3496],
    'MÉXICO': [19.4969, -99.7233],
    'ESTADO DE MÉXICO': [19.4969, -99.7233],
    'EDOMEX': [19.4969, -99.7233],
    'MICHOACÁN': [19.5665, -101.7068],
    'MORELOS': [18.6813, -99.1013],
    'NAYARIT': [21.7514, -104.8455],
    'NUEVO LEÓN': [25.5922, -99.9962],
    'OAXACA': [17.0732, -96.7266],
    'PUEBLA': [19.0414, -98.2063],
    'QUERÉTARO': [20.5888, -100.3899],
    'QUINTANA ROO': [19.1817, -88.4791],
    'SAN LUIS POTOSÍ': [22.1565, -100.9855],
    'SINALOA': [25.1721, -107.4795],
    'SONORA': [29.2972, -110.3309],
    'TABASCO': [17.9895, -92.9281],
    'TAMAULIPAS': [24.2669, -98.8363],
    'TLAXCALA': [19.3139, -98.2392],
    'VERACRUZ': [19.1738, -96.1342],
    'YUCATÁN': [20.9754, -89.6169],
    'ZACATECAS': [22.7709, -102.5832],
    'REYNOSA': [26.0806, -98.2884],
    'MATAMOROS': [25.8690, -97.5027],
    'LAREDO': [27.5036, -99.5076],
    'TIJUANA': [32.5149, -117.0382],
    'JUÁREZ': [31.6904, -106.4245],
    'ACAPULCO': [16.8531, -99.8237],
    'CANCÚN': [21.1619, -86.8515],
    'GUADALAJARA': [20.6597, -103.3496],
    'MONTERREY': [25.6866, -100.3161],
    'MAZATLÁN': [23.2494, -106.4111],
    'CULIACÁN': [24.8059, -107.3944],
    'CUERNAVACA': [18.9242, -99.2216],
    'TOLUCA': [19.2826, -99.6557],
    'PACHUCA': [20.1011, -98.7591],
    'SALTILLO': [25.4145, -101.0053],
    'TORREÓN': [25.5445, -103.4422],
    'HERMOSILLO': [29.0729, -110.9559],
    'MERIDA': [20.9674, -89.5926],
}

# Function stubs
def clean_text(text):
    """Cleans tweet text by removing URLs, RTs, and special characters."""
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'RT @\w+: ', '', text)  # Remove RTs
    text = re.sub(r'[^\w\s]', '', text)  # Remove special characters
    text = text.replace('\n', ' ').strip()
    return text

@st.cache_data(ttl=300)  # Cache results for 5 minutes
def scrape_tweets(terms=SEARCH_TERMS, limit=100):
    """Scrapes tweets using ntscraper."""
    scraper = Nitter(log_level=1, skip_instance_check=False)
    tweets_data = []

    # Combine search terms into a query string with OR
    query = " OR ".join(terms)

    try:
        # Scrape tweets
        scraped_tweets = scraper.get_tweets(query, mode='term', number=limit)

        if scraped_tweets and 'tweets' in scraped_tweets:
            for tweet in scraped_tweets['tweets']:
                tweets_data.append({
                    'Fecha': tweet['date'],
                    'Usuario': tweet['user']['username'],
                    'Texto': tweet['text'],
                    'Enlace': tweet['link']
                })
        else:
            st.warning("No se encontraron tweets o hubo un problema con la instancia de Nitter.")

    except Exception as e:
        st.error(f"Error al obtener tweets: {e}")
        return pd.DataFrame()

    df = pd.DataFrame(tweets_data)
    if not df.empty:
        df['Texto_Limpio'] = df['Texto'].apply(clean_text)

    return df

def get_location_coordinates(text):
    """Extracts location from text and returns coordinates."""
    normalized_text = unidecode(text).upper()

    for location, coords in LOCATIONS.items():
        if unidecode(location) in normalized_text:
            return location, coords

    return None, None

def generate_wordcloud(text):
    """Generates a word cloud from text."""
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    return fig

def main():
    st.title("🚨 Monitoreo de Seguridad Carretera en México (Tiempo Real)")
    st.markdown("Análisis de riesgos en carreteras mediante datos de X (Twitter).")

    # Sidebar
    st.sidebar.header("Configuración")
    search_limit = st.sidebar.slider("Número de tweets a analizar", 10, 100, 50)

    if st.sidebar.button("Actualizar Datos"):
        st.cache_data.clear()
        st.rerun()

    use_demo_data = st.sidebar.checkbox("Usar datos de demostración", value=False)

    # Load data
    if use_demo_data:
        data = [
            {"Fecha": "2023-10-27 10:00:00", "Usuario": "usuario1", "Texto": "Reportan narcobloqueo en la carretera a Reynosa #Precaución", "Enlace": "http://twitter.com"},
            {"Fecha": "2023-10-27 10:05:00", "Usuario": "usuario2", "Texto": "Tráfico detenido por quema de vehículos en la autopista cerca de Celaya, Guanajuato.", "Enlace": "http://twitter.com"},
            {"Fecha": "2023-10-27 10:10:00", "Usuario": "usuario3", "Texto": "Todo tranquilo en la zona centro.", "Enlace": "http://twitter.com"},
            {"Fecha": "2023-10-27 10:15:00", "Usuario": "usuario4", "Texto": "Enfrentamiento armado en el km 45 de la carretera libre a Laredo.", "Enlace": "http://twitter.com"},
            {"Fecha": "2023-10-27 10:20:00", "Usuario": "usuario5", "Texto": "Bloqueo en la salida a Cuernavaca. Eviten la zona.", "Enlace": "http://twitter.com"},
        ]
        df = pd.DataFrame(data)
        df['Texto_Limpio'] = df['Texto'].apply(clean_text)
        st.info("Mostrando datos de demostración.")
    else:
        with st.spinner("Escaneando red social X..."):
            df = scrape_tweets(limit=search_limit)

    if not df.empty:
        # Layout: 2 Columns
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Tendencias (Nube de Palabras)")
            all_text = " ".join(df['Texto_Limpio'].tolist())
            if all_text:
                fig = generate_wordcloud(all_text)
                st.pyplot(fig)
            else:
                st.write("No hay suficiente texto para generar la nube de palabras.")

        with col2:
            st.subheader("Puntos Críticos Detectados")
            # Filter tweets with critical keywords (infrastructure + locations)
            # Create a regex pattern that includes critical keywords and location names
            location_names = [unidecode(loc).lower() for loc in LOCATIONS.keys()]
            all_keywords = CRITICAL_KEYWORDS + location_names

            # Use a regex pattern for more robust matching
            pattern = '|'.join([re.escape(k) for k in all_keywords])

            critical_mask = df['Texto_Limpio'].apply(lambda x: bool(re.search(pattern, unidecode(x).lower())))
            critical_df = df[critical_mask]

            if not critical_df.empty:
                for index, row in critical_df.iterrows():
                    with st.expander(f"Reporte: {row['Usuario']} - {row['Fecha']}"):
                        st.write(row['Texto'])
                        st.markdown(f"[Ver Tweet Original]({row['Enlace']})")
                        if any(keyword in row['Texto_Limpio'].lower() for keyword in ['bloqueo', 'incendio', 'balacera']):
                            st.error("⚠️ ALERTA DE ALTO RIESGO")
            else:
                st.success("No se detectaron puntos críticos en los últimos reportes.")

        # Map Section
        st.header("Mapa de Riesgos en Tiempo Real")

        m = folium.Map(location=[23.6345, -102.5528], zoom_start=5) # Center of Mexico

        markers_added = 0
        for index, row in df.iterrows():
            location_name, coords = get_location_coordinates(row['Texto'])
            if coords:
                folium.Marker(
                    coords,
                    popup=folium.Popup(f"<b>{row['Usuario']}</b>: {row['Texto']}", max_width=300),
                    tooltip=location_name,
                    icon=folium.Icon(color="red", icon="exclamation-triangle", prefix="fa")
                ).add_to(m)
                markers_added += 1

        st_folium(m, width=1200, height=600)

        if markers_added == 0:
            st.info("No se pudieron geolocalizar reportes específicos en el mapa.")

    else:
        st.warning("No se pudieron recuperar datos. Intenta nuevamente más tarde.")

if __name__ == "__main__":
    main()
