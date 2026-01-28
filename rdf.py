import pandas as pd
from rdflib import Graph, Namespace, Literal, RDF, RDFS, URIRef
from rdflib.namespace import XSD
import urllib.parse
import isodate

# Define Namespaces
ex = Namespace("http://example.org/movies#")
g = Graph()
g.bind("ex", ex)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)

# Load the CSV files
movies = pd.read_csv("Datasets/Movies_less.csv")
actors = pd.read_csv("Datasets/Actors.csv")
countries = pd.read_csv("Datasets/Countries.csv")
directors = pd.read_csv("Datasets/Directors.csv")

# Helper function to create URIs
def create_uri(base, value):
    sanitized_value = urllib.parse.quote(value.replace('"', '').strip())
    return URIRef(f"{base}{sanitized_value}")

# Helper function to validate dates
def is_valid_date(date_string):
    try:
        date_string = str(date_string).strip()
        if not date_string or date_string.lower() == "nan":
            return False
        isodate.parse_date(date_string)
        return True
    except (ValueError, isodate.isoerror.ISO8601Error, TypeError):
        return False

# Define Classes
g.add((ex.Movie, RDF.type, RDFS.Class))
g.add((ex.Director, RDF.type, RDFS.Class))
g.add((ex.Actor, RDF.type, RDFS.Class))
g.add((ex.Country, RDF.type, RDFS.Class))

# Define Properties
properties = [
    (ex.title, ex.Movie, XSD.string),
    (ex.overview, ex.Movie, XSD.string),
    (ex.runtime, ex.Movie, XSD.decimal),
    (ex.budget, ex.Movie, XSD.integer),
    (ex.revenue, ex.Movie, XSD.integer),
    (ex.release_date, ex.Movie, XSD.date),
    (ex.vote_average, ex.Movie, XSD.decimal),
    (ex.vote_count, ex.Movie, XSD.integer),
    (ex.original_language, ex.Movie, XSD.string),
    (ex.directedBy, ex.Movie, ex.Director),
    (ex.hasActor, ex.Movie, ex.Actor),
    (ex.producedIn, ex.Movie, ex.Country),
    (ex.date_of_birth, [ex.Director, ex.Actor], XSD.date),
    (ex.country, [ex.Director, ex.Actor], ex.Country),
    (ex.net_worth, [ex.Director, ex.Actor], XSD.integer),
    (ex.continent, ex.Country, XSD.string),
    (ex.population, ex.Country, XSD.integer),
    (ex.capital, ex.Country, XSD.string),
    (ex.independence_date, ex.Country, XSD.date),
    (ex.official_language, ex.Country, XSD.string),
]

for prop, domain, range_ in properties:
    g.add((prop, RDF.type, RDF.Property))
    if isinstance(domain, list):
        for d in domain:
            g.add((prop, RDFS.domain, d))
    else:
        g.add((prop, RDFS.domain, domain))
    g.add((prop, RDFS.range, range_))

# Add movies to the RDF graph
for _, row in movies.iterrows():
    movie_uri = create_uri(ex.Movie, str(row["movie_id"]))
    g.add((movie_uri, RDF.type, ex.Movie))
    g.add((movie_uri, ex.title, Literal(row["title"], datatype=XSD.string)))
    g.add((movie_uri, ex.overview, Literal(row["overview"], datatype=XSD.string)))
    g.add((movie_uri, ex.runtime, Literal(row["runtime"], datatype=XSD.float)))
    g.add((movie_uri, ex.budget, Literal(row["budget"], datatype=XSD.integer)))
    g.add((movie_uri, ex.revenue, Literal(row["revenue"], datatype=XSD.integer)))
    g.add((movie_uri, ex.original_language, Literal(row["original_language"], datatype=XSD.string)))
    g.add((movie_uri, ex.release_date, Literal(row["release_date"], datatype=XSD.date)))

    for i in range(1, 6):
        genre = row.get(f"genre_{i}")
        if pd.notna(genre):
            g.add((movie_uri, ex.genre, Literal(genre, datatype=XSD.string)))

    for i in range(1, 6):
        country = row.get(f"Country_{i}")
        if pd.notna(country):
            country_uri = create_uri(ex.Country, country)
            g.add((movie_uri, ex.producedIn, country_uri))

    if pd.notna(row["Director"]):
        director_uri = create_uri(ex.Director, row["Director"])
        g.add((movie_uri, ex.directedBy, director_uri))

    for i in range(1, 4):
        actor = row.get(f"Actor_{i}")
        if pd.notna(actor):
            actor_uri = create_uri(ex.Actor, actor)
            g.add((movie_uri, ex.hasActor, actor_uri))

# Add actors to the RDF graph
for _, row in actors.iterrows():
    actor_uri = create_uri(ex.Actor, row["Actor"])
    g.add((actor_uri, RDF.type, ex.Actor))
    g.add((actor_uri, ex.title, Literal(row["Actor"], datatype=XSD.string)))
    g.add((actor_uri, ex.date_of_birth, Literal(row["Date of Birth"], datatype=XSD.date)))
    g.add((actor_uri, ex.country, Literal(row["Country"], datatype=XSD.string)))
    if pd.notna(row["Net Worth (USD)"]):
        g.add((actor_uri, ex.net_worth, Literal(row["Net Worth (USD)"], datatype=XSD.float)))

# Add directors to the RDF graph
for _, row in directors.iterrows():
    director_uri = create_uri(ex.Director, row["Director"])
    g.add((director_uri, RDF.type, ex.Director))
    g.add((director_uri, ex.title, Literal(row["Director"], datatype=XSD.string)))
    g.add((director_uri, ex.date_of_birth, Literal(row["Date of Birth"], datatype=XSD.date)))
    g.add((director_uri, ex.country, Literal(row["Country"], datatype=XSD.string)))
    if pd.notna(row["Net Worth (USD)"]):
        g.add((director_uri, ex.net_worth, Literal(row["Net Worth (USD)"], datatype=XSD.float)))

# Add countries to the RDF graph
for _, row in countries.iterrows():
    country_uri = create_uri(ex.Country, row["Country"])
    g.add((country_uri, RDF.type, ex.Country))
    g.add((country_uri, ex.title, Literal(row["Country"], datatype=XSD.string)))
    g.add((country_uri, ex.continent, Literal(row["Continent"], datatype=XSD.string)))
    g.add((country_uri, ex.population, Literal(row["Population"], datatype=XSD.integer)))
    g.add((country_uri, ex.capital, Literal(row["Capital"], datatype=XSD.string)))

    if is_valid_date(row["Independence Date"]):
        g.add((country_uri, ex.independence_date, Literal(row["Independence Date"], datatype=XSD.date)))
    else:
        g.add((country_uri, ex.independence_date, Literal(row["Independence Date"], datatype=XSD.string)))

# Serialize the RDF graph to Turtle format
rdf_turtle = g.serialize(format="turtle")

# Save to a file
with open("output_with_classes_and_properties.ttl", "w", encoding="utf-8") as file:
    file.write(rdf_turtle)
