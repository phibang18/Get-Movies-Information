# %% Import packages
import requests
import pandas as pd
from tqdm import tqdm
import os
from dotenv import load_dotenv

pd.set_option("display.max_columns", None)

# %% Import paths and useful functions
from utils.config import *
from utils.import_data import *
from utils.query_api import *
from utils.process_data import *

# %% Import params API
load_dotenv()
API_KEY = os.getenv("API_KEY")
AUTH = os.getenv("AUTH")
# %% Core
df = get_movies_list(INPUT_PATH)

df_control = pd.read_excel("../data/intermediate/liste_films_avec_infos_tmdb.xlsx")

df = df[~df["my_title"].isin(df_control["my_title"].unique().tolist())]

df = get_all_info_tmdb(df, key=API_KEY, auth=AUTH)
dico_genres = get_genre_desc(AUTH)
df = process_data(df, dico_genres)

# %%
output_dir = "../data/affiches"
os.makedirs(output_dir, exist_ok=True)

for idx, row in tqdm(df.iterrows(), total=len(df)):
    path = row["image"]
    url = f"https://image.tmdb.org/t/p/w1280/{path}"
    id = row["tmdb_id"]
    filename = os.path.join(output_dir, f"{id}.jpg")

    try:
        r = requests.get(url)
        r.raise_for_status()

        with open(filename, "wb") as f:
            f.write(r.content)

    except requests.RequestException:
        pass


df = pd.concat([df_control, df])

df.to_excel(
    os.path.join(INTERMEDIATE_PATH, "liste_films_avec_infos_tmdb.xlsx"), index=False
)
