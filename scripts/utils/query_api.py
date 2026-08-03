import pandas as pd
import requests
from unidecode import unidecode


def clean_title(title):
    return unidecode(title).strip().lower()


def get_tmdb_info(
    title,
    key,
    year=None,
    language="fr-FR",
):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": key, "query": clean_title(title), "language": language}
    if year is not None:
        params["year"] = year
    r = requests.get(url, params=params)
    data = r.json()
    if data["results"]:
        if title == "Drive":
            result = data["results"][1]
        else:
            result = data["results"][0]
        return {
            "tmdb_id": result["id"],
            "original_title": result["original_title"],
            "title": result.get("title"),
            "overview": result.get("overview"),
            "release_date": result.get("release_date"),
            "vote_average": result.get("vote_average"),
            "vote_count": result.get("vote_count"),
            "popularity": result.get("popularity"),
            "genre_ids": result.get("genre_ids"),
            "language": result.get("original_language"),
            "image": result.get("poster_path"),
        }
    return None


def sucessive_search(title, title2, year, key):
    infos = None
    if title in ["The Handmaiden", "The other way around"]:
        infos = get_tmdb_info(title=title, year=year, language="en-US", key=key)
    if infos is not None:
        return infos
    else:
        infos = get_tmdb_info(title=title, year=year, language="fr-FR", key=key)
    if infos is not None:
        return infos
    else:
        infos = get_tmdb_info(title=title, year=year, language="en-US", key=key)
    if infos is not None:
        return infos
    else:
        infos = get_tmdb_info(title=title, year=year + 1, language="fr-FR", key=key)
    if infos is not None:
        return infos
    else:
        infos = get_tmdb_info(title=title, year=year + 1, language="en-US", key=key)
    if infos is not None:
        return infos
    else:
        infos = get_tmdb_info(title=title, year=year - 1, language="fr-FR", key=key)
    if infos is not None:
        return infos
    else:
        infos = get_tmdb_info(title=title, year=year - 1, language="en-US", key=key)
    if infos is not None:
        return infos
    else:
        infos = get_tmdb_info(title=title, language="fr-FR", key=key)
    if infos is not None:
        return infos
    else:
        infos = get_tmdb_info(title=title, language="en-US", key=key)
    if infos is not None:
        return infos
    else:
        if title2 is not None:
            infos = get_tmdb_info(title=title2, year=year, language="fr-FR", key=key)
    if infos is not None:
        return infos
    else:
        if title2 is not None:
            infos = get_tmdb_info(title=title2, year=year, language="en-US", key=key)
    if infos is not None:
        return infos
    else:
        if title2 is not None:
            infos = get_tmdb_info(
                title=title2, year=year + 1, language="fr-FR", key=key
            )
    if infos is not None:
        return infos
    else:
        if title2 is not None:
            infos = get_tmdb_info(
                title=title2, year=year + 1, language="en-US", key=key
            )
    if infos is not None:
        return infos
    else:
        if title2 is not None:
            infos = get_tmdb_info(
                title=title2, year=year - 1, language="fr-FR", key=key
            )
    if infos is not None:
        return infos
    else:
        if title2 is not None:
            infos = get_tmdb_info(
                title=title2, year=year - 1, language="en-US", key=key
            )
    if infos is not None:
        return infos
    else:
        if title2 is not None:
            infos = get_tmdb_info(title=title2, language="fr-FR", key=key)
    if infos is not None:
        return infos
    else:
        if title2 is not None:
            infos = get_tmdb_info(title=title2, language="en-US", key=key)

    if infos is not None:
        return infos
    return None


def get_movie_infos(movie_id, auth):
    url = (
        f"https://api.themoviedb.org/3/movie/{movie_id}"
        "?append_to_response=credits,keywords&language=fr-FR"
    )

    headers = {"accept": "application/json", "Authorization": auth}

    response = requests.get(url, headers=headers)

    if response.status_code != 404:

        response.raise_for_status()

        data = response.json()

        # Acteurs
        cast = " ; ".join(actor["name"] for actor in data["credits"]["cast"][:12])

        # Équipe technique
        crew = data["credits"]["crew"]

        directors = " ; ".join(
            person["name"] for person in crew if person["job"] == "Director"
        )

        composers = " ; ".join(
            person["name"]
            for person in crew
            if person["job"] == "Original Music Composer"
        )

        writers = " ; ".join(
            person["name"]
            for person in crew
            if person["job"] in ("Writer", "Screenplay")
        )

        # Keywords
        keywords = " ; ".join(
            keyword["name"] for keyword in data["keywords"]["keywords"]
        )

        return {
            "tmdb_id": movie_id,
            "budget": data["budget"],
            "revenue": data["revenue"],
            "duree": data["runtime"],
            "pays_origine": (
                data["origin_country"][0] if data["origin_country"] else None
            ),
            "casting": cast,
            "director": directors,
            "composer": composers,
            "writer": writers,
            "keywords": keywords,
        }


def get_movie_first_info(df, key):

    df_temp = df.copy()

    df_temp["tmdb_data"] = df_temp.apply(
        lambda row: sucessive_search(
            title=row["my_title"], title2=row["other_title"], year=row["year"], key=key
        ),
        axis=1,
    )
    df_temp = df_temp.join(df_temp["tmdb_data"].apply(pd.Series))
    df_temp.drop(columns="tmdb_data", inplace=True)

    return df_temp


def collect_info_tmdb(df, auth):

    df_temp = df.copy()

    infos = df_temp["tmdb_id"].apply(
        lambda movie_id: get_movie_infos(movie_id, auth=auth)
    )
    infos = infos.apply(pd.Series)
    infos = infos[infos["tmdb_id"].notna()].drop_duplicates()

    return infos


def get_all_info_tmdb(df, key, auth):

    df_temp = get_movie_first_info(df, key=key)
    infos = collect_info_tmdb(df_temp, auth=auth)
    df_final = df_temp.merge(
        infos,
        on="tmdb_id",
        how="left",
        validate="many_to_one",
    )
    return df_final


def get_genre_desc(auth):

    url = "https://api.themoviedb.org/3/genre/movie/list?language=fr"
    headers = {
        "accept": "application/json",
        "Authorization": auth,
    }
    response = requests.get(url, headers=headers)
    return pd.DataFrame(response.json()["genres"]).set_index("id").to_dict()["name"]
