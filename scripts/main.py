# %% Import packages

# %% Import paths
from config import *

# %% Import useful functions
from utils.import_data import *

# %% Core
df = import_movies_list(INPUT_PATH)
clean_movies_list(df)
