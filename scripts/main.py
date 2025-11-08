# %% Import packages
# import requests
# from unidecode import unidecode
# import pandas as pd
import os

# %% Import paths
from config import *

# %% Import useful functions
from utils.import_data import *

# %% Core
df = get_movies_list(INPUT_PATH)
df.to_excel(os.path.join(INTERMEDIATE_PATH, "liste_films_bruts.xlsx"), index=False)
