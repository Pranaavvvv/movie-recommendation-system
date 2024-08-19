import pickle
import streamlit as st
import requests

# Function to fetch movie poster using OMDB API
def fetch_poster(movie_title):
    api_key = 'f7a5c79b'  # Replace with your OMDB API key
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={api_key}"
    try:
        response = requests.get(url, timeout=30)  
        response.raise_for_status()  
        data = response.json()
        poster_url = data.get('Poster')
        if poster_url and poster_url != "N/A":
            return poster_url
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster: {e}")
    return None

# Function to recommend movies based on selected movie
def recommend(criteria, value):
    if criteria == 'Title':
        index = movies[movies['title'] == value].index[0]
    elif criteria == 'Cast':
        index = movies[movies['cast'].str.contains(value, na=False)].index[0]
    elif criteria == 'Genres':
        index = movies[movies['genres'].str.contains(value, na=False)].index[0]
    elif criteria == 'Crew':
        index = movies[movies['crew'].str.contains(value, na=False)].index[0]
    
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

# Load data
movies = pickle.load(open('artificats/movie_list.pkl', 'rb'))
s = pickle.load(open('artificats/similarity.pkl', 'rb'))

# Function to get unique and sorted list of items
def get_unique_sorted_list(lst):
    filtered_list = [item for item in lst if item and item.strip()]
    unique_list = sorted(set(filtered_list))
    return unique_list

# Prepare lists for selection
movie_list = get_unique_sorted_list(movies['title'].values)
cast_list = get_unique_sorted_list(movies['cast'].explode().dropna().values)
genre_list = get_unique_sorted_list(movies['genres'].explode().dropna().values)
crew_list = get_unique_sorted_list(movies['crew'].explode().dropna().values)

# Add "None" option to all lists
movie_list.insert(0, "None")
cast_list.insert(0, "None")
genre_list.insert(0, "None")
crew_list.insert(0, "None")

# Custom CSS for background image with blur effect and center alignment
st.markdown("""
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1e1e30;
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            position: relative;
            overflow: hidden;
            text-align: center;
        }
        
        body::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url('https://wallpaper-mania.com/wp-content/uploads/2018/09/High_resolution_wallpaper_background_ID_77701605548.jpg');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            filter: blur(0.75px);
            z-index: -1;
        }
        
        .stApp {
            background-color: rgba(5, 5, 5, 0.8); /* Add transparency */
            padding: 20px;
            border-radius: 20px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
            text-align: center;
            max-width: 600px;
            max-height: 450px;
            max-length:50%;
            width: 90%;
            margin:auto ;
        }

        .stSelectbox, .stButton {
            margin: auto;
        }

        .stButton button {
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# Streamlit app
st.header("Movies Recommendation System Using Machine Learning")

criteria = st.selectbox(
    'Select criteria for recommendation',
    ['Title', 'Cast', 'Genres', 'Crew']
)

if criteria == 'Title':
    selected_movie = st.selectbox(
        'Type or select a movie to get recommendation',
        movie_list
    )
    if selected_movie == "None":
        selected_movie = None

elif criteria == 'Cast':
    selected_cast = st.selectbox(
        'Type or select a cast to get recommendation',
        cast_list
    )
    if selected_cast == "None":
        selected_cast = None

elif criteria == 'Genres':
    selected_genre = st.selectbox(
        'Type or select a genre to get recommendation',
        genre_list
    )
    if selected_genre == "None":
        selected_genre = None

elif criteria == 'Crew':
    selected_crew = st.selectbox(
        'Type or select a crew to get recommendation',
        crew_list
    )
    if selected_crew == "None":
        selected_crew = None

if st.button('Show recommendations'):
    if criteria == 'Title' and selected_movie:
        recommended_movies, recommended_movies_poster = recommend(criteria, selected_movie)
    elif criteria == 'Cast' and selected_cast:
        recommended_movies, recommended_movies_poster = recommend(criteria, selected_cast)
    elif criteria == 'Genres' and selected_genre:
        recommended_movies, recommended_movies_poster = recommend(criteria, selected_genre)
    elif criteria == 'Crew' and selected_crew:
        recommended_movies, recommended_movies_poster = recommend(criteria, selected_crew)
    else:
        st.text("Please select a valid option.")

    if recommended_movies:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if len(recommended_movies) > 0:
                st.text(recommended_movies[0])
                st.image(recommended_movies_poster[0])

        with col2:
            if len(recommended_movies) > 1:
                st.text(recommended_movies[1])
                st.image(recommended_movies_poster[1])

        with col3:
            if len(recommended_movies) > 2:
                st.text(recommended_movies[2])
                st.image(recommended_movies_poster[2])

        with col4:
            if len(recommended_movies) > 3:
                st.text(recommended_movies[3])
                st.image(recommended_movies_poster[3])

        with col5:
            if len(recommended_movies) > 4:
                st.text(recommended_movies[4])
                st.image(recommended_movies_poster[4])
    else:
        st.text("No recommendations available.")
