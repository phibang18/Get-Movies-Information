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
    df[["title", "director", "other_title"]] = df["gross_name"].str.split(
        " - ", expand=True
    )
    df[["director", "year"]] = df["director"].str.split(r" \(", expand=True)
    df["year"] = df["year"].str.replace(r")", "")
    df.drop(columns="gross_name", inplace=True)
    return df
