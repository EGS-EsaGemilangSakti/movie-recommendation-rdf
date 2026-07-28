"""Generate the movie title cache consumed by the Streamlit application."""

from pathlib import Path
import pickle

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
SOURCE_FILE = PROJECT_DIR / "Datasets" / "Movies_less.csv"
OUTPUT_FILE = PROJECT_DIR / "movie_list.pkl"


def main() -> None:
    movies = pd.read_csv(SOURCE_FILE)

    if "title" not in movies.columns:
        raise KeyError(f"Column 'title' was not found in {SOURCE_FILE}")

    movie_list = (
        movies.loc[:, ["title"]]
        .dropna(subset=["title"])
        .drop_duplicates(subset=["title"])
        .reset_index(drop=True)
    )

    with OUTPUT_FILE.open("wb") as file:
        pickle.dump(movie_list, file, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"Created {OUTPUT_FILE} with {len(movie_list)} movie titles.")


if __name__ == "__main__":
    main()
