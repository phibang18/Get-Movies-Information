import pandas as pd


def decode_genre(code_genre_list, labels_genres):
    result = []
    if type(code_genre_list) == list:
        for code in code_genre_list:
            result.append(labels_genres[code])
    return " ; ".join(result)


def process_data(df, labels_genres):

    df_temp = df.copy()

    df_temp["genres"] = df_temp.apply(
        lambda row: decode_genre(row["genre_ids"], labels_genres=labels_genres), axis=1
    )

    for genre in labels_genres.values():
        df_temp.loc[df_temp["genres"].str.contains(genre), genre] = "OUI"
        df_temp.loc[~df_temp["genres"].str.contains(genre), genre] = ""

    df_temp["duree"] = pd.to_datetime(df_temp.duree, unit="m").dt.strftime("%H:%M")

    df_temp.loc[(df_temp["budget"] == 0) | (df_temp["budget"].isna()), "budget"] = None
    df_temp.loc[(df_temp["revenue"] == 0) | (df_temp["revenue"].isna()), "revenue"] = (
        None
    )

    df_temp["language"] = df_temp["language"].str.upper()

    df_temp["title"] = df_temp["title"].combine_first(df_temp["my_title"])
    df_temp["original_title"] = df_temp["original_title"].combine_first(
        df_temp["other_title"]
    )
    df_temp["director"] = df_temp["director"].combine_first(df_temp["realisateur"])

    df_temp.drop(columns=["genre_ids", "realisateur"], inplace=True)

    df_temp = df_temp[
        [
            "tmdb_id",
            "my_title",
            "other_title",
            "title",
            "original_title",
            "director",
            "year",
            "release_date",
            "duree",
            "language",
            "genres",
            "vote_average",
            "vote_count",
            "popularity",
            "budget",
            "revenue",
            "pays_origine",
            "casting",
            "composer",
            "writer",
            "overview",
            "keywords",
        ]
        + list(labels_genres.values())
        + ["image"]
    ]

    return df_temp
