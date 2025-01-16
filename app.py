import pickle
import streamlit as st
import requests
from typing import List, Tuple, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
API_KEY = os.getenv('OMDB_API_KEY', 'f7a5c79b')
MOVIE_LIST_PATH = 'artifacts/movie_list.pkl'
SIMILARITY_PATH = 'artifacts/similarity.pkl'
POSTER_CACHE = {}

# Function to fetch movie poster using OMDB API
def fetch_poster(movie_title: str) -> Optional[str]:
    if movie_title in POSTER_CACHE:
        return POSTER_CACHE[movie_title]
    
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={API_KEY}"
    try:
        response = requests.get(url, timeout=30)  
        response.raise_for_status()  
        data = response.json()
        poster_url = data.get('Poster')
        if poster_url and poster_url != "N/A":
            POSTER_CACHE[movie_title] = poster_url
            return poster_url
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster for {movie_title}: {e}")
    return None

# Function to recommend movies based on selected criteria
def recommend(criteria: str, value: str) -> Tuple[List[str], List[str]]:
    if criteria == 'Title':
        index = movies[movies['title'] == value].index[0]
    elif criteria == 'Cast':
        index = movies[movies['cast'].str.contains(value, case=False, na=False)].index[0]
    elif criteria == 'Genres':
        index = movies[movies['genres'].str.contains(value, case=False, na=False)].index[0]
    elif criteria == 'Crew':
        index = movies[movies['crew'].str.contains(value, case=False, na=False)].index[0]
    else:
        raise ValueError(f"Invalid criteria: {criteria}")
    
    dist = sorted(list(enumerate(s[index])), reverse=True, key=lambda x: x[1])
    recommended_movies = []
    recommended_movies_poster = []
    for i in dist[1:6]:
        movie_title = movies.iloc[i[0]].title
        poster = fetch_poster(movie_title)
        if poster:
            recommended_movies_poster.append(poster)
            recommended_movies.append(movie_title)
    return recommended_movies, recommended_movies_poster

# Function to get unique and sorted list of items
def get_unique_sorted_list(lst: List[str]) -> List[str]:
    filtered_list = [item for item in lst if item and isinstance(item, str) and item.strip()]
    unique_list = sorted(set(filtered_list))
    return ["None"] + unique_list

# Load data
@st.cache_data
def load_data():
    try:
        movies = pickle.load(open(MOVIE_LIST_PATH, 'rb'))
        s = pickle.load(open(SIMILARITY_PATH, 'rb'))
        return movies, s
    except (FileNotFoundError, pickle.PickleError) as e:
        st.error(f"Error loading data: {e}")
        st.stop()

movies, s = load_data()

# Prepare lists for selection
movie_list = get_unique_sorted_list(movies['title'].values)
cast_list = get_unique_sorted_list(movies['cast'].explode().dropna().values)
genre_list = get_unique_sorted_list(movies['genres'].explode().dropna().values)
crew_list = get_unique_sorted_list(movies['crew'].explode().dropna().values)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    :root {
        --primary-color: #ff6b6b;
        --secondary-color: #4ecdc4;
        --background-color: #1a1a2e;
        --text-color: #f0f0f0;
        --card-color: #16213e;
    }

    body {
        font-family: 'Poppins', sans-serif;
        background-color: var(--background-color);
        color: var(--text-color);
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(91, 37, 178, 0.1) 0%, rgba(253, 167, 142, 0.1) 90%),
            radial-gradient(circle at 90% 80%, rgba(91, 37, 178, 0.1) 0%, rgba(253, 167, 142, 0.1) 100%);
        background-attachment: fixed;
    }
    
    .stApp {
        max-width: 1200px;
        margin: auto;
    }

    .main-container {
        background-color: rgba(26, 26, 46, 0.8);
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    h1 {
        color: var(--primary-color);
        text-align: center;
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }

    h2 {
        color: var(--secondary-color);
        text-align: center;
        font-size: 1.8rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }

    .stSelectbox > div > div {
        background-color: var(--card-color);
        color: var(--text-color);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }

    .stButton > button {
        background-color: var(--primary-color);
        color: var(--text-color);
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 50px;
        border: none;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .stButton > button:hover {
        background-color: var(--secondary-color);
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
    }

    .movie-card {
        background-color: var(--card-color);
        border-radius: 15px;
        padding: 1rem;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
        overflow: hidden;
    }

    .movie-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 12px 16px rgba(0, 0, 0, 0.2);
    }

    .movie-poster {
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }

    .movie-card:hover .movie-poster {
        transform: scale(1.05);
    }

    .movie-title {
        margin-top: 1rem;
        font-size: 1rem;
        font-weight: 600;
        color: var(--primary-color);
    }

    .loader {
        border: 5px solid var(--card-color);
        border-top: 5px solid var(--primary-color);
        border-radius: 50%;
        width: 50px;
        height: 50px;
        animation: spin 1s linear infinite;
        margin: auto;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }

    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }

    .criteria-container, .value-container {
        background-color: rgba(22, 33, 62, 0.7);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .criteria-label, .value-label {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: var(--secondary-color);
    }

    .footer {
        text-align: center;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.7);
    }
</style>
""", unsafe_allow_html=True)

# Streamlit app
st.markdown('<div class="main-container fade-in">', unsafe_allow_html=True)

st.markdown('<h1>🎬 CineMatch</h1>', unsafe_allow_html=True)
st.markdown('<h2>Your AI-Powered Movie Recommendation Engine</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="criteria-container">', unsafe_allow_html=True)
    st.markdown('<p class="criteria-label">Select recommendation criteria</p>', unsafe_allow_html=True)
    criteria = st.selectbox(
        '',
        ['Title', 'Cast', 'Genres', 'Crew'],
        key='criteria'
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="value-container">', unsafe_allow_html=True)
    st.markdown(f'<p class="value-label">Choose a {criteria.lower()}</p>', unsafe_allow_html=True)
    selected_value = st.selectbox(
        '',
        globals()[f"{criteria.lower()}_list"],
        key='selected_value'
    )
    st.markdown('</div>', unsafe_allow_html=True)

if st.button('🔍 Discover Your Next Favorite Movie', key='recommend_button'):
    if selected_value and selected_value != "None":
        with st.spinner(''):
            st.markdown('<div class="loader"></div>', unsafe_allow_html=True)
            st.markdown('<p style="text-align: center; margin-top: 1rem;">🎭 Lights, camera, action! Our AI is curating your personalized movie list...</p>', unsafe_allow_html=True)
            try:
                recommended_movies, recommended_movies_poster = recommend(criteria, selected_value)
                if recommended_movies:
                    st.markdown(f'<h2 class="fade-in">🍿 Top 5 Recommendations based on {selected_value}</h2>', unsafe_allow_html=True)
                    cols = st.columns(5)
                    for i, (movie, poster) in enumerate(zip(recommended_movies, recommended_movies_poster)):
                        with cols[i]:
                            st.markdown(f'<div class="movie-card fade-in" style="animation-delay: {i*0.1}s">', unsafe_allow_html=True)
                            st.image(poster, use_column_width=True, output_format="PNG", clamp=True, class_="movie-poster")
                            st.markdown(f'<p class="movie-title">{movie}</p>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.warning("🎬 Oops! We couldn't find any recommendations for your selection. Try another option!")
            except Exception as e:
                st.error(f"🚫 An error occurred: {e}")
    else:
        st.warning("🎥 Please select a valid option to start your cinematic journey!")

st.markdown('<div class="footer">', unsafe_allow_html=True)
st.markdown("🌟 Created with passion by Your Name | Powered by AI and the magic of cinema", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
