import streamlit as st
from SPARQLWrapper import SPARQLWrapper, JSON
from pathlib import Path
from rdflib import Literal
from rdflib.namespace import XSD
import os
import pickle
import pandas as pd
import requests

PROJECT_DIR = Path(__file__).resolve().parent
SPARQL_ENDPOINT = os.getenv(
    "SPARQL_ENDPOINT",
    "http://localhost:3030/movies/sparql",
)
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
PLACEHOLDER_POSTER = "https://placehold.co/500x750?text=No+Image+Available"

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
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    if not TMDB_API_KEY or not movie_id:
        return PLACEHOLDER_POSTER

    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    try:
        response = requests.get(
            url,
            params={"api_key": TMDB_API_KEY, "language": "en-US"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except (requests.exceptions.RequestException, ValueError):
        pass

    return PLACEHOLDER_POSTER

# SPARQL Wrapper for Fuseki
def run_sparql_query(query):
    try:
        sparql = SPARQLWrapper(SPARQL_ENDPOINT)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        sparql.setTimeout(15)
        results = sparql.query().convert()
        return results["results"]["bindings"]
    except Exception:
        st.error(
            "Tidak dapat menjalankan query SPARQL. Pastikan Fuseki aktif, "
            "dataset `movies` tersedia, dan endpoint berikut dapat diakses: "
            f"`{SPARQL_ENDPOINT}`."
        )
        return []

def sparql_string(value):
    """Return a safely escaped xsd:string literal for a SPARQL query."""
    return Literal(str(value), datatype=XSD.string).n3()

def binding_value(binding, key, default="N/A"):
    return binding.get(key, {}).get("value", default)

# Load pre-processed movie data
movie_cache = PROJECT_DIR / "movie_list.pkl"
movie_csv = PROJECT_DIR / "Datasets" / "Movies_less.csv"

if movie_cache.exists():
    with movie_cache.open("rb") as file:
        movies = pickle.load(file)
else:
    movies = pd.read_csv(movie_csv, usecols=["title"])
    st.info(
        "`movie_list.pkl` belum tersedia; daftar judul dibaca langsung dari "
        "`Datasets/Movies_less.csv`. Jalankan `python generate_movie_list.py` "
        "untuk membuat cache."
    )

movie_list = (
    pd.Series(movies["title"])
    .dropna()
    .drop_duplicates()
    .sort_values()
    .to_numpy()
)

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
        title_literal = sparql_string(movie_title)

        # SPARQL query for movie details
        movie_query = f"""
        PREFIX ex: <http://example.org/movies#>

        SELECT ?title ?overview ?release_date ?runtime ?budget ?revenue
               ?director ?director_name ?movie_id ?actor_name
               ?country ?country_name ?language ?genre
        WHERE {{
            ?movie ex:title {title_literal} ;
                ex:overview ?overview ;
                ex:release_date ?release_date ;
                ex:runtime ?runtime ;
                ex:budget ?budget ;
                ex:revenue ?revenue ;
                ex:directedBy ?director ;
                ex:hasActor ?actor ;
                ex:producedIn ?country ;
                ex:original_language ?language ;
                ex:genre ?genre .
            ?actor ex:title ?actor_name .
            OPTIONAL {{ ?director ex:title ?director_name . }}
            OPTIONAL {{ ?country ex:title ?country_name . }}
            OPTIONAL {{ ?movie ex:movie_id ?stored_movie_id . }}
            BIND(
                IF(
                    BOUND(?stored_movie_id),
                    STR(?stored_movie_id),
                    STRAFTER(STR(?movie), "#Movie")
                ) AS ?movie_id
            )
        }}
        """

        movie_data = run_sparql_query(movie_query)

        if movie_data:
            movie = movie_data[0]

            # Display movie details
            movie_id = binding_value(movie, "movie_id", None)
            poster_url = fetch_poster(movie_id)

            # Two-column layout for poster and details
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(poster_url, width="stretch")
            with col2:
                st.markdown(f"### {movie_title}")
                st.write(f"**Overview**: {binding_value(movie, 'overview')}")
                st.write(f"**Release Date**: {binding_value(movie, 'release_date')}")
                st.write(f"**Runtime**: {binding_value(movie, 'runtime')} minutes")
                st.write(f"**Budget**: ${binding_value(movie, 'budget')}")
                st.write(f"**Revenue**: ${binding_value(movie, 'revenue')}")
                director_uri = binding_value(movie, "director")
                director_name = binding_value(movie, "director_name")
                st.write(f"**Director**: {director_name}")
                    
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

                country_names = {
                    binding_value(item, "country_name")
                    for item in movie_data
                    if binding_value(item, "country_name") != "N/A"
                }
                countries_text = ", ".join(sorted(country_names)) or "N/A"
                st.write(f"**Country**: {countries_text}")
                st.write(f"**Language**: {binding_value(movie, 'language')}")
                
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

            SELECT ?title ?overview ?movie_id
            WHERE {{
                ?movie ex:title ?title ;
                       ex:overview ?overview ;
                       ex:directedBy <{director_uri}> .
                OPTIONAL {{ ?movie ex:movie_id ?stored_movie_id . }}
                BIND(
                    IF(
                        BOUND(?stored_movie_id),
                        STR(?stored_movie_id),
                        STRAFTER(STR(?movie), "#Movie")
                    ) AS ?movie_id
                )
                FILTER(?title != {title_literal})
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
                    rec_poster = fetch_poster(rec_movie_id)
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

            SELECT DISTINCT ?title ?overview ?movie_id
            WHERE {{
                ?movie ex:title {title_literal} ;
                       ex:hasActor ?actor .
                ?other_movie ex:hasActor ?actor ;
                            ex:title ?title ;
                            ex:overview ?overview .
                OPTIONAL {{ ?other_movie ex:movie_id ?stored_movie_id . }}
                BIND(
                    IF(
                        BOUND(?stored_movie_id),
                        STR(?stored_movie_id),
                        STRAFTER(STR(?other_movie), "#Movie")
                    ) AS ?movie_id
                )
                FILTER(?title != {title_literal})
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
                    rec_poster = fetch_poster(rec_movie_id)
                    with cols[i]:
                        st.image(rec_poster, width=200)
                        st.write(f"**{movie_name}**")
                        st.caption(overview)
            else:
                st.write("No recommendations available for the actors.")

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
                       ex:budget ?budget .
                OPTIONAL { ?movie ex:movie_id ?stored_movie_id . }
                BIND(
                    IF(
                        BOUND(?stored_movie_id),
                        STR(?stored_movie_id),
                        STRAFTER(STR(?movie), "#Movie")
                    ) AS ?movie_id
                )
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
                       ex:runtime ?runtime .
                OPTIONAL { ?movie ex:movie_id ?stored_movie_id . }
                BIND(
                    IF(
                        BOUND(?stored_movie_id),
                        STR(?stored_movie_id),
                        STRAFTER(STR(?movie), "#Movie")
                    ) AS ?movie_id
                )
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
                       ex:revenue ?revenue .
                OPTIONAL { ?movie ex:movie_id ?stored_movie_id . }
                BIND(
                    IF(
                        BOUND(?stored_movie_id),
                        STR(?stored_movie_id),
                        STRAFTER(STR(?movie), "#Movie")
                    ) AS ?movie_id
                )
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

            SELECT ?country ?country_name (COUNT(?country) AS ?count)
            WHERE {
                ?movie ex:producedIn ?country .
                ?country ex:title ?country_name .
            }
            GROUP BY ?country ?country_name
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
                       ex:producedIn ?country .
                OPTIONAL { ?movie ex:movie_id ?stored_movie_id . }
                BIND(
                    IF(
                        BOUND(?stored_movie_id),
                        STR(?stored_movie_id),
                        STRAFTER(STR(?movie), "#Movie")
                    ) AS ?movie_id
                )
            }
            GROUP BY ?title ?movie_id
            ORDER BY DESC(?country_count)
            LIMIT 10
            """

        results = run_sparql_query(query)

        if results:
            cols = st.columns(5)

            for index, result in enumerate(results):
                with cols[index % 5]:
                    if "genre" in result:
                        st.write(f"**{binding_value(result, 'genre')}**")
                        st.write(f"Jumlah film: {binding_value(result, 'count')}")
                    elif "country" in result and "title" not in result:
                        st.write(f"**{binding_value(result, 'country_name')}**")
                        st.write(f"Jumlah film: {binding_value(result, 'count')}")
                    else:
                        movie_name = binding_value(result, "title")
                        movie_id = binding_value(result, "movie_id", None)
                        st.image(fetch_poster(movie_id), width=200)
                        st.write(f"**{movie_name}**")

                        if "budget" in result:
                            st.write(f"Budget: ${binding_value(result, 'budget')}")
                        elif "runtime" in result:
                            st.write(f"Runtime: {binding_value(result, 'runtime')} menit")
                        elif "revenue" in result:
                            st.write(f"Revenue: ${binding_value(result, 'revenue')}")
                        elif "country_count" in result:
                            st.write(
                                "Jumlah negara: "
                                f"{binding_value(result, 'country_count')}"
                            )
        else:
            st.write("No results found for the selected question.")
