import os
import re
import pandas as pd


def import_movies_list(path):
    list_movies = os.listdir(path)
    for movie in list_movies:
        if re.search(r"\(\d{4}\)", movie) is None:
            list_movies.remove(movie)
            list_movies += os.listdir(os.path.join(path, movie))
    return pd.DataFrame({"gross_name": list_movies})


def clean_movies_list(df):
    df[["my_title", "realisateur", "other_title"]] = df["gross_name"].str.split(
        " - ", expand=True
    )
    df[["realisateur", "year"]] = df["realisateur"].str.split(r" \(", expand=True)
    df["year"] = df["year"].str.replace(r")", "")
    df["year"] = df["year"].astype(int)
    df["other_title"] = df["other_title"].str.replace(r")", "")
    df["other_title"] = df["other_title"].str.replace(r"(", "")
    df.drop(columns="gross_name", inplace=True)
    return df


def get_movies_list(path):
    df_movies = import_movies_list(path)
    df_movies_clean = clean_movies_list(df_movies)
    return df_movies_clean
