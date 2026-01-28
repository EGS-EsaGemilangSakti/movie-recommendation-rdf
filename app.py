import streamlit as st
from SPARQLWrapper import SPARQLWrapper, JSON
from urllib.parse import unquote
import pickle
import requests

# Set page configuration
st.set_page_config(
    page_title="Movie Recommendation System Using RDF and SPARQL",
    page_icon="🎥",
    layout="wide",
)

# Header
st.header('MOVIE RECOMMENDATION SYSTEM', divider='rainbow')

# Footer CSS (Sticky only when scrolled to the bottom)
footer = """
<style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-image: linear-gradient(90deg,orange,yellow);
        text-align: center;
        color: white;
        padding: 5px 0;
        display: none;
    }
    .footer p {
        margin: 0;
        font-size: 14px;
    }
    .streamlit-container {
        padding-bottom: 80px;
    }
</style>

<div class="footer">
    <p>Developed by Team Itihaad</p>
</div>
<script>
    window.onscroll = function() {
        if ((window.innerHeight + window.scrollY) >= document.body.scrollHeight) {
            document.querySelector('.footer').style.display = 'block';
        } else {
            document.querySelector('.footer').style.display = 'none';
        }
    }
</script>
"""
st.markdown(footer, unsafe_allow_html=True)

# TMDB Poster API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8bb921015d2d20ee4b1b630ac130a216&language=en-US"
    try:
        data = requests.get(url).json()
        poster_path = data.get("poster_path")
        if poster_path:
            full_path = f"http://image.tmdb.org/t/p/w500{poster_path}"
            return full_path
        else:
            return "https://via.placeholder.com/500x750?text=No+Image+Available"
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster: {e}")
        return "https://via.placeholder.com/500x750?text=No+Image+Available"

# SPARQL Wrapper for Fuseki
sparql = SPARQLWrapper("http://localhost:3030/movies/sparql")

def run_sparql_query(query):
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]

# Load pre-processed movie data
movies = pickle.load(open("movie_list.pkl", "rb"))
movie_list = movies["title"].values

# Radio button to choose between searching for a movie or selecting a question
option = st.radio(
    "What would you like to do?",
    ("Search for a Movie", "Select a Predefined Question"),
)

if option == "Search for a Movie":
    # Movie selection
    movie_title = st.selectbox('Type or select a movie to get recommendation', movie_list)

    # Show results button
    if st.button("Show Results"):
        # SPARQL query for movie details
        movie_query = f"""
        PREFIX ex: <http://example.org/movies#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?title ?overview ?release_date ?runtime ?budget ?revenue ?director ?movie_id ?actor_name ?country ?language ?genre
        WHERE {{
            ?movie ex:title "{movie_title}"^^xsd:string ;
                ex:overview ?overview ;
                ex:release_date ?release_date ;
                ex:runtime ?runtime ;
                ex:budget ?budget ;
                ex:revenue ?revenue ;
                ex:directedBy ?director ;
                ex:hasActor ?actor ;
                ex:producedIn ?country ;
                ex:original_language ?language ;
                ex:genre ?genre ;
                ex:movie_id ?movie_id .
            ?actor ex:title ?actor_name .
        }}
        """

        movie_data = run_sparql_query(movie_query)

        if movie_data:
            movie = movie_data[0]

            # Display movie details
            movie_id = movie.get('movie_id', {}).get('value', None)
            poster_url = fetch_poster(movie_id) if movie_id else "https://via.placeholder.com/500x750?text=No+Image+Available"

            # Two-column layout for poster and details
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(poster_url, use_column_width=True)
            with col2:
                st.markdown(f"### {movie_title}")
                st.write(f"**Overview**: {movie.get('overview', {}).get('value', 'N/A')}")
                st.write(f"**Release Date**: {movie.get('release_date', {}).get('value', 'N/A')}")
                st.write(f"**Runtime**: {movie.get('runtime', {}).get('value', 'N/A')} minutes")
                st.write(f"**Budget**: ${movie.get('budget', {}).get('value', 'N/A')}")
                st.write(f"**Revenue**: ${movie.get('revenue', {}).get('value', 'N/A')}")
                director_uri = movie.get('director', {}).get('value', 'N/A')
                if director_uri != 'N/A':
                    director_name = unquote(director_uri.split('Director')[-1].replace('_', ' ').strip())
                    st.write(f"**Director**: {director_name}")
                else:
                    st.write("**Director**: N/A")
                    
                actor_names = set()    
                for i in range(len(movie_data)):
                    movie_actors = movie_data[i]
                    # Process actors
                    actors = []
                    actor_binding = movie_actors.get('actor_name', [])
                    if isinstance(actor_binding, list):
                        for actor in actor_binding:
                            if isinstance(actor, dict):
                                actor_name = actor.get('value', 'N/A')
                                actors.append(actor_name)
                                actor_names.add(actor_name)
                            else:
                                actors.append(actor)
                                actor_names.add(actor)
                    else:
                        if isinstance(actor_binding, dict):
                            actor_name = actor_binding.get('value', 'N/A')
                            actors.append(actor_name)
                            actor_names.add(actor_name)
                        else:
                            actors.append(actor_binding)
                            actor_names.add(actor_binding)

                if actor_names:
                    st.write(f"**Actors**: {', '.join(actor_names)}")
                else:
                    st.write(f"**Actors**: N/A")

                country_url = movie.get('country', {}).get('value', 'N/A')
                if country_url != 'N/A':
                    country_name = country_url.split('/')[-1].replace('%20', ' ')
                    if country_name.startswith('Country'):
                        country_name = country_name.replace('Country', '').strip()
                else:
                    country_name = 'N/A'

                st.write(f"**Country**: {country_name}")
                st.write(f"**Language**: {movie.get('language', {}).get('value', 'N/A')}")
                
                genre_names = set()  
                for i in range(len(movie_data)):
                    movie_data_item = movie_data[i]
                    genre_binding = movie_data_item.get('genre', [])
                    if isinstance(genre_binding, list):
                        for genre in genre_binding:
                            if isinstance(genre, dict):
                                genre_name = genre.get('value', 'N/A')
                                genre_names.add(genre_name)
                            else:
                                genre_names.add(genre)
                    else:
                        if isinstance(genre_binding, dict):
                            genre_name = genre_binding.get('value', 'N/A')
                            genre_names.add(genre_name)
                        else:
                            genre_names.add(genre_binding)

                if genre_names:
                    st.write(f"**Genres**: {', '.join(genre_names)}")
                else:
                    st.write(f"**Genres**: N/A")

            # Recommendations: Movies by the same director
            st.subheader(":orange[Recommendations by Director]")
            director_query = f"""
            PREFIX ex: <http://example.org/movies#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT ?title ?overview ?movie_id
            WHERE {{
                ?movie ex:title ?title ;
                       ex:overview ?overview ;
                       ex:directedBy <{director_uri}> ;
                       ex:movie_id ?movie_id .
                FILTER(?title != "{movie_title}"^^xsd:string)
            }}
            LIMIT 5
            """
            director_recommendations = run_sparql_query(director_query)

            if director_recommendations:
                cols = st.columns(len(director_recommendations))  
                for i, recommendation in enumerate(director_recommendations):
                    movie_name = recommendation.get("title", {}).get("value", "N/A")
                    overview = recommendation.get("overview", {}).get("value", "N/A")
                    rec_movie_id = recommendation.get("movie_id", {}).get("value", None)
                    rec_poster = fetch_poster(rec_movie_id) if rec_movie_id else "https://via.placeholder.com/500x750?text=No+Image+Available"
                    with cols[i]:
                        st.image(rec_poster, width=200)
                        st.write(f"**{movie_name}**")
                        st.caption(overview)

            else:
                st.write("No recommendations available for the director.")

            # Recommendations: Movies by the same actor
            st.subheader(":orange[Recommendations by Actor]")
            actor_query = f"""
            PREFIX ex: <http://example.org/movies#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT DISTINCT ?title ?overview ?movie_id
            WHERE {{
                ?movie ex:title "{movie_title}"^^xsd:string ;
                       ex:hasActor ?actor .
                ?other_movie ex:hasActor ?actor ;
                            ex:title ?title ;
                            ex:overview ?overview ;
                            ex:movie_id ?movie_id .
                FILTER(?title != "{movie_title}"^^xsd:string)
            }}
            LIMIT 5
            """
            actor_recommendations = run_sparql_query(actor_query)

            if actor_recommendations:
                cols = st.columns(len(actor_recommendations))  
                for i, recommendation in enumerate(actor_recommendations):
                    movie_name = recommendation.get("title", {}).get("value", "N/A")
                    overview = recommendation.get("overview", {}).get("value", "N/A")
                    rec_movie_id = recommendation.get("movie_id", {}).get("value", None)
                    rec_poster = fetch_poster(rec_movie_id) if rec_movie_id else "https://via.placeholder.com/500x750?text=No+Image+Available"
                    with cols[i]:
                        st.image(rec_poster, width=200)
                        st.write(f"**{movie_name}**")
                        st.caption(overview)

        else:
            st.error("Movie not found!")

elif option == "Select a Predefined Question":
    questions = [
        "Top 10 Movies by Budget",
        "Top 10 Movies by Runtime",
        "Top 10 Highest Revenue Movies",
        "Top 10 Most Popular Genres",
        "Top 10 Most Common Countries",
        "Top 10 Movies with the Most Countries of Origin",
    ]
    selected_question = st.selectbox('Select a Question', questions)

    # Execute query based on selected question
    if st.button("Show Results"):
        if selected_question == "Top 10 Movies by Budget":
            query = """
            PREFIX ex: <http://example.org/movies#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT ?title ?budget ?movie_id
            WHERE {
                ?movie ex:title ?title ;
                       ex:budget ?budget ;
                       ex:movie_id ?movie_id .
            }
            ORDER BY DESC(?budget)
            LIMIT 10
            """
        elif selected_question == "Top 10 Movies by Runtime":
            query = """
            PREFIX ex: <http://example.org/movies#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT ?title ?runtime ?movie_id
            WHERE {
                ?movie ex:title ?title ;
                       ex:runtime ?runtime ;
                       ex:movie_id ?movie_id .
            }
            ORDER BY DESC(?runtime)
            LIMIT 10
            """
        elif selected_question == "Top 10 Highest Revenue Movies":
            query = """
            PREFIX ex: <http://example.org/movies#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT ?title ?revenue ?movie_id
            WHERE {
                ?movie ex:title ?title ;
                       ex:revenue ?revenue ;
                       ex:movie_id ?movie_id .
            }
            ORDER BY DESC(?revenue)
            LIMIT 10
            """
        elif selected_question == "Top 10 Most Popular Genres":
            query = """
            PREFIX ex: <http://example.org/movies#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT ?genre (COUNT(?genre) AS ?count)
            WHERE {
                ?movie ex:genre ?genre .
            }
            GROUP BY ?genre
            ORDER BY DESC(?count)
            LIMIT 10
            """
        elif selected_question == "Top 10 Most Common Countries":
            query = """
            PREFIX ex: <http://example.org/movies#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT ?country (COUNT(?country) AS ?count)
            WHERE {
                ?movie ex:producedIn ?country .
            }
            GROUP BY ?country
            ORDER BY DESC(?count)
            LIMIT 10
            """
        elif selected_question == "Top 10 Movies with the Most Countries of Origin":
            query = """
            PREFIX ex: <http://example.org/movies#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT ?title (COUNT(?country) AS ?country_count) ?movie_id
            WHERE {
                ?movie ex:title ?title ;
                       ex:producedIn ?country ;
                       ex:movie_id ?movie_id .
            }
            GROUP BY ?title ?movie_id
            ORDER BY DESC(?country_count)
            LIMIT 10
            """

        results = run_sparql_query(query)

        if results:
            # Handling Top 10 Results
            rows = 2  # Two rows of results
            cols = st.columns(5)  # Each row contains a maximum of 5 movies

            for row_idx in range(rows):
                for col_idx in range(5):
                    index = row_idx * 5 + col_idx
                    if index < len(results):
                        result = results[index]
                        movie_name = result.get("title", {}).get("value", "N/A")
                        movie_id = result.get("movie_id", {}).get("value", None)
                        poster_url = fetch_poster(movie_id) if movie_id else "https://via.placeholder.com/500x750?text=No+Image+Available"

                        # Check if the result contains a count (like genre or country)
                        if "count" in result:
                            count_value = result["count"]["value"]
                            with cols[col_idx]:
                                st.write(f"**{movie_name}**")
                                st.write(f"Count: {count_value}")
                        else:
                            with cols[col_idx]:
                                st.image(poster_url, width=200)
                                st.write(f"**{movie_name}**")
        else:
            st.write("No results found for the selected question.")
