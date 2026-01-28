# Movie Recommendation System Using RDF and SPARQL

A semantic web-based movie recommendation system that leverages RDF (Resource Description Framework) and SPARQL queries to build an intelligent recommendation engine. This project demonstrates the power of ontology-driven data representation and semantic reasoning.

## 🎯 Features

- **RDF-Based Knowledge Graph**: Structured representation of movies, actors, directors, countries, and their relationships
- **SPARQL Query Engine**: Advanced querying capabilities to find movies based on complex criteria
- **Interactive Web Interface**: User-friendly Streamlit application for browsing and discovering movies
- **Movie Recommendations**: Intelligent recommendations based on genre, cast, director, and other attributes
- **Semantic Relationships**: Rich semantic relationships between entities (actors, directors, production countries)
- **Extensible Ontology**: Well-defined ontology structure for easy extension and modification

## 📊 Project Structure

```
.
├── app.py                                   # Streamlit web application
├── rdf.py                                   # RDF graph generation and data loading
├── output_with_classes_and_properties.ttl   # Generated RDF ontology
├── Preproccessing.ipynb                     # Data preprocessing pipeline
├── Project Code.ipynb                       # Complete project implementation
├── README.md                                # Project documentation
├── requirements.txt                         # Python dependencies
└── Datasets/
    ├── Movies_less.csv                      # Movie dataset
    ├── Actors.csv                           # Actors data
    ├── Directors.csv                        # Directors data
    └── Countries.csv                        # Countries data
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Setup

1. **Clone the repository**

```bash
git clone https://github.com/your-username/movie-recommendation-rdf.git
cd movie-recommendation-rdf
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

## 📦 Dependencies

- **streamlit** - Web framework for creating interactive applications
- **rdflib** - Python library for RDF graph operations
- **SPARQLWrapper** - Python wrapper for SPARQL endpoints
- **pandas** - Data manipulation and analysis
- **isodate** - ISO 8601 date/time parsing

Install all dependencies:

```bash
pip install streamlit rdflib SPARQLWrapper pandas isodate
```

## 🚀 Usage

### Running the Web Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### Generating RDF Graph

To regenerate the RDF knowledge graph from CSV data:

```bash
python rdf.py
```

This will create/update the `output_with_classes_and_properties.ttl` file.

### Data Preprocessing

For data preprocessing and exploration, open the Jupyter notebook:

```bash
jupyter notebook Preproccessing.ipynb
```

## 📚 How It Works

### 1. **Data Loading and Preprocessing**

- CSV files containing movie, actor, director, and country information are loaded
- Data is cleaned and validated
- Dates are parsed and validated using ISO 8601 format

### 2. **RDF Graph Construction**

- An RDF graph is built using the rdflib library
- Four main classes are defined: Movie, Actor, Director, Country
- Relationships between entities are established using custom properties

### 3. **SPARQL Querying**

- The application communicates with the RDF graph using SPARQL
- Complex queries retrieve recommendations based on user preferences
- Filters include genre, cast, director, runtime, and ratings

### 4. **Recommendation Engine**

- Similarity metrics based on genres, cast, and directors
- Results are ranked and presented to the user
- Interactive filtering and sorting capabilities

## 📋 Ontology Classes and Properties

### Classes

- **Movie**: Represents a film with metadata
- **Actor**: Represents a performer
- **Director**: Represents a film director
- **Country**: Represents a production country

### Key Properties

- `title`, `overview`, `release_date`: Movie information
- `budget`, `revenue`: Financial data
- `runtime`, `vote_average`: Quality metrics
- `genre`, `original_language`: Categorical data
- `directedBy`, `hasActor`, `producedIn`: Relationships

## 📊 Sample Data

The project includes a curated dataset of 5,000 movies with:

- Complete cast information
- Director details
- Production countries
- Budget and revenue data
- IMDb ratings and metadata

## 🔍 Example Queries

The SPARQL queries in the application can find:

- Movies by specific actors or directors
- Films produced in certain countries
- Movies within a budget range
- Films with ratings above a threshold
- Genre-based recommendations

## 💡 Use Cases

- **Movie Enthusiasts**: Discover films based on favorite actors/directors
- **Data Scientists**: Study semantic web technologies and ontology design
- **Recommendation Systems**: Learn how to build intelligent suggestion engines
- **Knowledge Graphs**: Understand RDF, SPARQL, and semantic relationships

## 🔧 Configuration

Key configuration options in `app.py`:

- SPARQL endpoint configuration
- UI styling and layout
- Pagination settings
- Filter parameters

## 📝 Development

### Project Versions

- **V1**: Initial implementation with basic functionality
- **V2**: Enhanced features and improved query optimization
- **Final**: Production-ready version with full features

### Future Enhancements

- User-based collaborative filtering
- Machine learning-based recommendations
- Support for user ratings and feedback
- Advanced graph algorithms for similarity
- Performance optimization with caching

## 📄 License

This project is provided as-is for educational purposes.

## 👥 Contributors

Team Itihaad - University Project

## 📞 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Built with** ❤️ using Python, RDF, and SPARQL
