import json
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# --------------------------------------------------
# Configuration de la page
# --------------------------------------------------

st.set_page_config(
    page_title="Mes films",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


components.html(
    """
    <script>
        const viewport = window.parent.document.querySelector(
            'meta[name="viewport"]'
        );

        if (viewport) {
            viewport.setAttribute(
                "content",
                "width=device-width, "
                + "initial-scale=1, "
                + "maximum-scale=5, "
                + "user-scalable=yes"
            );
        }
    </script>
    """,
    height=0,
)


# --------------------------------------------------
# Chargement des données
# --------------------------------------------------


@st.cache_data
def charger_films(chemin_json):
    """
    Charge un fichier JSON contenant une liste de films.

    Le fichier peut avoir la forme :
    [
        {...},
        {...}
    ]
    """

    with open(chemin_json, "r", encoding="utf-8") as fichier:
        donnees = json.load(fichier)

    return pd.DataFrame(donnees)


# Chemin vers ton fichier JSON
df = charger_films("data/site/data.json")


# --------------------------------------------------
# Fonctions utilitaires
# --------------------------------------------------


def formater_date(date):
    """Transforme 2003-11-18 en 18/11/2003."""

    if pd.isna(date):
        return "Date inconnue"

    try:
        return pd.to_datetime(date).strftime("%d/%m/%Y")
    except Exception:
        return str(date)


def formater_montant(valeur):
    """Affiche les budgets et revenus avec des séparateurs."""

    if pd.isna(valeur) or valeur == 0:
        return "Non renseigné"

    return f"{valeur:,.0f} $".replace(",", " ")


def afficher_liste(valeur):
    """
    Transforme une liste Python en texte.

    Exemple :
    ["Drame", "Crime"] -> "Drame • Crime"
    """

    if isinstance(valeur, list):
        return " • ".join(valeur)

    if pd.isna(valeur):
        return "Non renseigné"

    return str(valeur)


# --------------------------------------------------
# Barre latérale : recherche et filtres
# --------------------------------------------------

st.sidebar.title("🎬 Mes films")

recherche = st.sidebar.text_input(
    "Rechercher un film", placeholder="Titre, réalisateur..."
)

# Liste des genres disponibles
tous_les_genres = sorted(
    {
        genre
        for genres in df["genres"].dropna()
        for genre in genres
        if isinstance(genres, list)
    }
)

genre_selectionne = st.sidebar.multiselect("Filtrer par genre", options=tous_les_genres)

annees = sorted(df["year"].dropna().unique())

annee_min = int(min(annees))
annee_max = int(max(annees))

# Curseur permettant de sélectionner une plage d'années
plage_annees = st.sidebar.slider(
    "Filtrer par année",
    min_value=annee_min,
    max_value=annee_max,
    value=(annee_min, annee_max),
    step=1,
)


votes_disponibles = df["votes"].dropna()

votes_min_global = int(min(votes_disponibles))
votes_max_global = int(max(votes_disponibles))

col_min, col_max = st.sidebar.columns(2)

with col_min:
    votes_min = st.number_input(
        "Votes min", min_value=0, value=votes_min_global, step=100
    )

with col_max:
    votes_max = st.number_input(
        "Votes max", min_value=0, value=votes_max_global, step=100
    )


# --------------------------------------------------
# Application des filtres
# --------------------------------------------------

df_filtre = df.copy()

if recherche:

    # Évite que la recherche soit interprétée comme une expression régulière
    recherche = str.replace(recherche.strip(), ".", "")

    # Recherche dans les colonnes texte
    masque_titre = (
        df_filtre["title"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.replace(".", "")
        .str.contains(recherche, case=False, na=False, regex=False)
    )

    masque_titre_original = (
        df_filtre["original_title"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.replace(".", "")
        .str.contains(recherche, case=False, na=False, regex=False)
    )

    masque_mon_titre = (
        df_filtre["my_title"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.replace(".", "")
        .str.contains(recherche, case=False, na=False, regex=False)
    )

    masque_autre_titre = (
        df_filtre["other_title"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.replace(".", "")
        .str.contains(recherche, case=False, na=False, regex=False)
    )

    masque_realisateur = (
        df_filtre["director"]
        .fillna("")
        .astype(str)
        .str.contains(recherche, case=False, na=False, regex=False)
    )

    masque_synopsis = (
        df_filtre["overview"]
        .fillna("")
        .astype(str)
        .str.contains(recherche, case=False, na=False, regex=False)
    )

    # La colonne "cast" contient une liste.
    # On transforme chaque liste en texte avant la recherche.
    masque_distribution = (
        df_filtre["cast"]
        .apply(
            lambda distribution: (
                " ".join(distribution) if isinstance(distribution, list) else ""
            )
        )
        .str.contains(recherche, case=False, na=False, regex=False)
    )

    # Un film est conservé si le terme est trouvé
    # dans au moins une des colonnes.
    df_filtre = df_filtre[
        masque_titre
        | masque_titre_original
        | masque_mon_titre
        | masque_autre_titre
        | masque_realisateur
        | masque_synopsis
        | masque_distribution
    ]


if genre_selectionne:
    df_filtre = df_filtre[
        df_filtre["genres"].apply(
            lambda genres: (
                isinstance(genres, list)
                and any(genre in genres for genre in genre_selectionne)
            )
        )
    ]


df_filtre = df_filtre[df_filtre["year"].between(plage_annees[0], plage_annees[1])]

df_filtre = df_filtre[df_filtre["votes"].between(votes_min, votes_max)]


# --------------------------------------------------
# En-tête
# --------------------------------------------------

col_titre, col_tri = st.columns([4, 1])

with col_titre:

    st.title("🎬 Mes films")

    st.caption(f"{len(df_filtre)} film(s) affiché(s)")


with col_tri:

    tri_selectionne = st.selectbox(
        "Trier par",
        options=[
            "Note (meilleure)",
            "Note (moins bonne)",
            "Titre (A → Z)",
            "Titre (Z → A)",
            "Année (plus récent)",
            "Année (plus ancien)",
        ],
    )

st.divider()


# --------------------------------------------------
# Tri des résultats
# --------------------------------------------------

if tri_selectionne == "Titre (A → Z)":

    df_filtre = df_filtre.sort_values(by="title", ascending=True)


elif tri_selectionne == "Titre (Z → A)":

    df_filtre = df_filtre.sort_values(by="title", ascending=False)


elif tri_selectionne == "Année (plus récent)":

    df_filtre = df_filtre.sort_values(by="year", ascending=False)


elif tri_selectionne == "Année (plus ancien)":

    df_filtre = df_filtre.sort_values(by="year", ascending=True)


elif tri_selectionne == "Note (meilleure)":

    df_filtre = df_filtre.sort_values(by="rating", ascending=False)


elif tri_selectionne == "Note (moins bonne)":

    df_filtre = df_filtre.sort_values(by="rating", ascending=True)


# --------------------------------------------------
# Affichage des films
# --------------------------------------------------

st.markdown(
    """
    <style>

    /* Affiches */
    img {
        border-radius: 8px;
        transition: transform 0.2s;
    }

    img:hover {
        transform: scale(1.03);
    }

    /* Titre des films */
    h3 {
        font-size: 18px !important;
        margin-bottom: 0 !important;
    }
    
    /* Version ordinateur */
    .original-title {
        font-size: 15px;
        color: #B0B0B0;
        font-style: italic;
        margin-top: -12px;
        margin-bottom: 8px;
    }

    /* Affiche absente */
    .poster-manquant {
        height: 330px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        background-color: #292929;
        border-radius: 8px;
        color: #aaaaaa;
        font-size: 20px;
        text-align: center;
    }

    /* ----------------------------------------------
       Affichage mobile : 5 films par ligne
    ---------------------------------------------- */

    @media (max-width: 768px) {
        
            h1 {
                font-size: 26px !important;
                line-height: 1.1 !important;
            }

        div[data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            gap: 4px !important;
        }

        div[data-testid="stColumn"] {
            min-width: 0 !important;
            width: 25% !important;
            flex: 1 1 25% !important;
        }

        div[data-testid="stColumn"] h3 {
            font-size: 10px !important;
            line-height: 1.1 !important;
        }
        
        .original-title {
        font-size: 8px !important;
        line-height: 1.1 !important;
        margin-top: 2px !important;
        margin-bottom: 4px !important;
        }

        div[data-testid="stColumn"] p {
            font-size: 8px !important;
            line-height: 1.1 !important;
        }

        div[data-testid="stColumn"] button {
            font-size: 8px !important;
            padding: 2px !important;
        }
        
        /* --------------------------------------------------
        Bouton "Voir les détails"
        -------------------------------------------------- */

        /* Bouton de l'expander */
        div[data-testid="stExpander"] summary {
            font-size: 8px !important;
            line-height: 1.1 !important;
            padding: 4px 2px !important;
        }

        /* Texte du bouton */
        div[data-testid="stExpander"] summary p {
            font-size: 8px !important;
        }

        /* Icône/flèche de l'expander */
        div[data-testid="stExpander"] summary svg {
            width: 9px !important;
            height: 9px !important;
        }


        /* --------------------------------------------------
        Contenu de la fiche détaillée
        -------------------------------------------------- */

        /* Texte général dans l'expander */
        div[data-testid="stExpander"] div[data-testid="stMarkdownContainer"] {
            font-size: 8px !important;
            line-height: 1.25 !important;
        }

        /* Paragraphes : réalisateur, année, etc. */
        div[data-testid="stExpander"]
        div[data-testid="stMarkdownContainer"] p {
            font-size: 8px !important;
            line-height: 1.25 !important;
        }

        /* Titres Distribution, Synopsis et Mots-clés */
        div[data-testid="stExpander"]
        div[data-testid="stMarkdownContainer"] h4 {
            font-size: 10px !important;
            line-height: 1.15 !important;
            margin-top: 8px !important;
            margin-bottom: 3px !important;
        }

        /* Texte du synopsis */
        div[data-testid="stExpander"]
        div[data-testid="stMarkdownContainer"] p {
            overflow-wrap: anywhere;
            word-break: break-word;
        }

        /* Évite que le contenu dépasse de la colonne */
        div[data-testid="stExpander"] {
            min-width: 0 !important;
            width: 100% !important;
        }
    }
    
    /* ----------------------------------------------
    Mobile paysage : 5 films par ligne
    ---------------------------------------------- */

    @media (max-width: 1000px) and (orientation: landscape) {

        /* Titre de la page */
        h1 {
            font-size: 30px !important;
            line-height: 1.1 !important;
        }


        /* Conserve les 5 colonnes */
        div[data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            gap: 8px !important;
        }

        div[data-testid="stColumn"] {
            min-width: 0 !important;
            width: 25% !important;
            flex: 1 1 25% !important;
        }


        /* Titre des films */
        div[data-testid="stColumn"] h3 {
            font-size: 13px !important;
            line-height: 1.15 !important;
        }


        /* Titre original */
        .original-title {
            font-size: 10px !important;
            line-height: 1.1 !important;
            margin-top: 2px !important;
            margin-bottom: 5px !important;
        }


        /* Année, note, durée */
        div[data-testid="stColumn"] p {
            font-size: 10px !important;
            line-height: 1.1 !important;
        }


        /* Bouton Voir les détails */
        div[data-testid="stExpander"] summary {
            font-size: 10px !important;
            padding: 5px !important;
        }


        /* Contenu de l'expander */
        div[data-testid="stExpander"]
        div[data-testid="stMarkdownContainer"] {
            font-size: 10px !important;
            line-height: 1.25 !important;
        }


        div[data-testid="stExpander"]
        div[data-testid="stMarkdownContainer"] h4 {
            font-size: 12px !important;
        }
}

    </style>
    """,
    unsafe_allow_html=True,
)


if df_filtre.empty:

    st.warning("Aucun film ne correspond aux critères.")

else:

    # Affichage de 5 affiches par ligne
    nombre_colonnes = 4

    for debut in range(0, len(df_filtre), nombre_colonnes):

        ligne = df_filtre.iloc[debut : debut + nombre_colonnes]

        colonnes = st.columns(nombre_colonnes)

        for colonne, (_, film) in zip(colonnes, ligne.iterrows()):

            with colonne:

                # Affiche
                chemin_affiche = film.get("poster", None)

                if chemin_affiche and Path(chemin_affiche).exists():

                    st.image(chemin_affiche, use_container_width=True)

                else:

                    st.markdown(
                        """
                        <div class="poster-manquant">
                            🎬<br>
                            Affiche indisponible
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Titre
                st.markdown(f"### {film['title']}")

                # Titre original, plus petit mais visible
                titre_original = film.get("original_title")

                if pd.notna(titre_original) and titre_original != film["title"]:
                    st.markdown(
                        f"""
                        <div class="original-title">
                            {titre_original}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Informations principales
                st.caption(
                    f"{film['year']} "
                    f"• {film['runtime']} "
                    f"• ⭐ {film['rating']:.1f}"
                )

                # Genres
                st.write(afficher_liste(film["genres"]))

                # Bouton permettant d'ouvrir la fiche
                with st.expander("Détails"):

                    st.markdown(f"**Mon titre :** " f"{film['my_title']}")

                    st.markdown(f"**Autre titre :** " f"{film['other_title']}")

                    st.markdown(f"**Date de sortie :** " f"{formater_date(
                            film['release_date']
                        )}")

                    st.markdown(f"**Réalisateur :** " f"{film['director']}")

                    st.markdown(f"**Langue :** " f"{film['language']}")

                    st.markdown(f"**Pays :** " f"{film['country']}")

                    st.markdown(f"**Compositeur :** " f"{film['composer']}")

                    st.markdown(f"**Scénariste :** " f"{film['writer']}")

                    # Nombre de votes
                    votes = film.get("votes")

                    if pd.notna(votes):
                        votes = int(votes)

                        st.markdown(f"**Votes :** {votes:,}".replace(",", " "))
                    else:
                        st.markdown("**Votes :** Non renseigné")

                    st.markdown(f"**Budget :** " f"{formater_montant(
                            film['budget']
                        )}")

                    st.markdown(f"**Recettes :** " f"{formater_montant(
                            film['revenue']
                        )}")

                    st.markdown("#### Synopsis")

                    st.write(film["overview"])

                    st.markdown("#### Distribution")

                    st.write(afficher_liste(film["cast"]))

                    st.markdown("#### Mots-clés")

                    st.write(afficher_liste(film["keywords"]))
