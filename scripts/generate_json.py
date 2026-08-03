from pathlib import Path
import json
import pandas as pd

##############################################################################
# CONFIGURATION
##############################################################################

INPUT_FILE = "../data/intermediate/liste_films_avec_infos_tmdb.xlsx"

# Où sera généré le site
OUTPUT_DIR = Path("../data/site/")
OUTPUT_JSON = OUTPUT_DIR / "data.json"

# Dossier contenant les affiches
POSTER_FOLDER = "data/affiches"


##############################################################################
# MAPPING DES COLONNES
##############################################################################

COLUMN_MAP = {
    "tmdb_id": "id",
    "title": "Titre",
    "original_title": "Titre original",
    "director": "Réalisateur",
    "year": "Année",
    "release_date": "Date de sortie",
    "duree": "Durée",
    "language": "Langue",
    "genres": "Genres",
    "vote_average": "Note TMDB",
    "vote_count": "Votes",
    "popularity": "Popularité",
    "budget": "Budget",
    "revenue": "Recettes",
    "pays_origine": "Pays",
    "casting": "Casting",
    "composer": "Compositeur",
    "writer": "Scénariste",
    "overview": "Résumé",
    "keywords": "Mots clés",
    "image": "Affiche",
}


##############################################################################
# OUTILS
##############################################################################


def clean_string(value):

    if pd.isna(value):
        return ""

    return str(value).strip()


def split_list(value):

    if pd.isna(value):
        return []

    value = str(value).strip()

    if value == "":
        return []

    return [x.strip() for x in value.split(";") if x.strip()]


def to_float(value):

    if pd.isna(value):
        return None

    value = str(value).replace(",", ".")

    try:
        return float(value)
    except Exception:
        return None


def to_int(value):

    if pd.isna(value):
        return None

    try:
        return int(value)
    except Exception:
        return None


##############################################################################
# LECTURE
##############################################################################

print("Lecture du dataframe...")

df = pd.read_excel(INPUT_FILE)


##############################################################################
# VERIFICATION DES COLONNES
##############################################################################

missing = []

for col in COLUMN_MAP.keys():

    if col not in df.columns:

        missing.append(col)

if missing:

    print("Colonnes manquantes :")

    for m in missing:
        print(" -", m)

    raise ValueError("Colonnes manquantes")


##############################################################################
# CONVERSION
##############################################################################

movies = []

print("Conversion...")

for _, row in df.iterrows():

    votes = row["vote_count"]
    if votes != votes:
        votes = 0

    movie = {
        "id": to_int(row["tmdb_id"]),
        "my_title": clean_string(row["my_title"]),
        "other_title": clean_string(row["other_title"]),
        "title": clean_string(row["title"]),
        "original_title": clean_string(row["original_title"]),
        "director": clean_string(row["director"]),
        "year": to_int(row["year"]),
        "release_date": clean_string(row["release_date"]),
        "runtime": clean_string(row["duree"]),
        "language": clean_string(row["language"]),
        "genres": split_list(row["genres"]),
        "rating": to_float(row["vote_average"]),
        "votes": to_int(votes),
        "popularity": to_float(row["popularity"]),
        "budget": to_float(row["budget"]),
        "revenue": to_float(row["revenue"]),
        "country": clean_string(row["pays_origine"]),
        "cast": split_list(row["casting"]),
        "composer": clean_string(row["composer"]),
        "writer": clean_string(row["writer"]),
        "overview": clean_string(row["overview"]),
        "keywords": split_list(row["keywords"]),
    }

    poster = clean_string(row["tmdb_id"])

    if poster != "":
        movie["poster"] = f"{POSTER_FOLDER}/{poster}.jpg"
    else:
        movie["poster"] = ""

    movies.append(movie)


##############################################################################
# TRI
##############################################################################

movies.sort(key=lambda m: (m["title"] or "").lower())


##############################################################################
# EXPORT
##############################################################################

OUTPUT_DIR.mkdir(exist_ok=True)

with open(OUTPUT_JSON, "w", encoding="utf8") as f:

    json.dump(movies, f, ensure_ascii=False, indent=2)

print()
print("-------------------------------------")
print(f"{len(movies)} films exportés")
print(f"Fichier : {OUTPUT_JSON}")
print("-------------------------------------")
