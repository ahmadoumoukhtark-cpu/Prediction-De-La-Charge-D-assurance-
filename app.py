"""
Interface Streamlit — Prédiction du coût d'assurance
Appelle l'API Flask déployée sur AWS ECS (POST /predict).
Lancer :  streamlit run app.py
"""
import os
 
import joblib
import pandas as pd
import requests
import streamlit as st
 
# ---------------------------------------------------------------------------
# 1. Configuration
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Prédiction d'assurance", page_icon="🛡️", layout="wide")
 
API_URL = os.getenv(
    "API_URL", "https://ap-592c77d497eb48e0a666c4f13703d2ee.ecs.eu-north-1.on.aws"
).rstrip("/")
CHEMIN_MODELE = "modele_gb.pkl"                 # optionnel : pour l'importance des variables
CHEMIN_CSV = "assurance/insurance.csv"           # optionnel : pour la page Analyse
MOYENNE_DATASET = 13270                          # moyenne des frais du dataset (1 338 lignes)
 
# Noms "lisibles" des colonnes attendues par le modèle
NOMS_VARIABLES = {
    "age": "Âge",
    "imc": "IMC",
    "sexe_Homme": "Sexe (homme)",
    "fumeur_Oui": "Fumeur",
    "region_Nord-Ouest": "Région Nord-Ouest",
    "region_Sud-Est": "Région Sud-Est",
    "region_Sud-Ouest": "Région Sud-Ouest",
}
 
# ---------------------------------------------------------------------------
# 2. Style (sidebar sombre + cartes blanches)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { background-color: #1F2240; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    .carte { background: #FFFFFF; border: 1px solid #E4E2F5; border-radius: 14px;
             padding: 1.2rem 1.4rem; margin-bottom: 1rem; }
    .resultat { background: #EEECFB; border-radius: 12px; padding: 1.2rem;
                text-align: center; }
    .resultat p { margin: 0; color: #4A4870; }
    .resultat h1 { margin: 0; font-size: 3rem; color: #1F2240; }
    </style>
    """,
    unsafe_allow_html=True,
)
 
 
# ---------------------------------------------------------------------------
# 3. Fonctions utilitaires
# ---------------------------------------------------------------------------
def api_en_ligne() -> bool:
    try:
        return requests.get(API_URL + "/", timeout=5).status_code < 500
    except requests.RequestException:
        return False
 
 
def predire(donnees: dict):
    """Envoie les données à l'API. Renvoie (montant, erreur)."""
    try:
        r = requests.post(f"{API_URL}/predict", json=donnees, timeout=15)
    except requests.RequestException:
        return None, "L'API ne répond pas (service AWS arrêté ?)."
    if r.status_code != 200:
        return None, f"Erreur {r.status_code} : {r.text}"
    reponse = r.json()
    # Adapte la clé au nom renvoyé par ton main.py
    for cle in ("charges_predites", "prediction", "charges"):
        if cle in reponse:
            valeur = reponse[cle]
            return float(valeur[0] if isinstance(valeur, list) else valeur), None
    return None, f"Réponse inattendue : {reponse}"
 
 
@st.cache_resource
def charger_modele():
    if os.path.exists(CHEMIN_MODELE):
        return joblib.load(CHEMIN_MODELE)
    return None
 
 
@st.cache_data
def charger_donnees():
    if os.path.exists(CHEMIN_CSV):
        return pd.read_csv(CHEMIN_CSV)
    return None
 
 
def categorie_imc(imc: float) -> str:
    if imc < 18.5:
        return "Maigreur"
    if imc < 25:
        return "Normal"
    if imc < 30:
        return "Surpoids"
    return "Obésité"
 
 
# ---------------------------------------------------------------------------
# 4. Barre latérale : navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🛡️ Prédiction d'assurance")
    page = st.radio(
        "Navigation",
        ["Prédiction", "Analyse des données",  "À propos"],
        label_visibility="collapsed",
    )
    st.markdown("<br>" * 8, unsafe_allow_html=True)
    st.markdown("**API AWS** : " + ("🟢 en ligne" if api_en_ligne() else "🔴 hors ligne"))
    st.caption("v1.0.0")
 
 
# ---------------------------------------------------------------------------
# 5. Page Prédiction
# ---------------------------------------------------------------------------
if page == "Prédiction":
    st.markdown(
        '<div class="carte"><h1 style="margin:0">🛡️ Prédiction du coût d\'assurance</h1>'
        '<p style="margin:0;color:#4A4870">Estimez les frais médicaux en fonction '
        "des informations du client.</p></div>",
        unsafe_allow_html=True,
    )
 
    col_form, col_res = st.columns([1, 1.1], gap="large")
 
    # ----- Formulaire -----
    with col_form:
        with st.container(border=True):
            st.subheader("👤 Informations du client")
            age = st.slider("Âge", 18, 64, 35)
            imc = st.slider("IMC (BMI)", 15.0, 55.0, 28.5, step=0.1)
            sexe = st.radio("Sexe", ["Homme", "Femme"], horizontal=True)
            fumeur = st.radio("Fumeur", ["Oui", "Non"], index=1, horizontal=True)
            region = st.selectbox("Région", ["Nord-Est", "Nord-Ouest", "Sud-Est", "Sud-Ouest"])
            clic = st.button("🚀 Prédire le coût", type="primary", use_container_width=True)
 
    donnees = {"age": age, "imc": imc, "sexe": sexe, "fumeur": fumeur, "region": region}
 
    if clic:
        with st.spinner("Appel de l'API sur AWS..."):
            montant, erreur = predire(donnees)
        st.session_state["montant"] = montant
        st.session_state["erreur"] = erreur
 
    # ----- Résultat -----
    with col_res:
        with st.container(border=True):
            st.subheader("💰 Résultat de la prédiction")
            montant = st.session_state.get("montant")
            erreur = st.session_state.get("erreur")
 
            if erreur:
                st.error(erreur)
            elif montant is None:
                st.info("Remplis le formulaire puis clique sur « Prédire le coût ».")
            else:
                st.markdown(
                    f'<div class="resultat"><p>Coût estimé de l\'assurance</p>'
                    f"<h1>{montant:,.0f} $</h1></div>".replace(",", " "),
                    unsafe_allow_html=True,
                )
                c1, c2 = st.columns(2)
                c1.metric("Vs moyenne", f"{MOYENNE_DATASET:,} $".replace(",", " "),
                          delta=f"{montant - MOYENNE_DATASET:,.0f} $".replace(",", " "),
                          delta_color="inverse")
                c2.metric("Catégorie IMC", categorie_imc(imc))
                st.info("💡 **Interprétation** : estimation du modèle Gradient Boosting "
                        "entraîné sur 1 338 assurés (dataset insurance).")
 
        # ----- Importance des variables (si le .pkl est présent) -----
        modele = charger_modele()
        if modele is not None and hasattr(modele, "feature_importances_"):
            with st.container(border=True):
                st.subheader("📊 Importance des variables")
                imp = pd.DataFrame({
                    "Variable": [NOMS_VARIABLES.get(c, c) for c in modele.feature_names_in_],
                    "Importance": modele.feature_importances_,
                }).sort_values("Importance", ascending=False).set_index("Variable")
                st.bar_chart(imp, horizontal=True, color="#5B4BD5")
 
    with st.expander("🔎 Requête envoyée à l'API"):
        st.code(f"POST {API_URL}/predict", language="text")
        st.json(donnees)
 
# ---------------------------------------------------------------------------
# 6. Page Analyse des données
# ---------------------------------------------------------------------------
elif page == "Analyse des données":
    st.title("📈 Analyse des données")
    df = charger_donnees()
    if df is None:
        st.warning(f"Fichier introuvable : {CHEMIN_CSV}. Adapte CHEMIN_CSV en haut du fichier.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Lignes", len(df))
        c2.metric("Colonnes", df.shape[1])
        c3.metric("Valeurs manquantes", int(df.isna().sum().sum()))
        st.dataframe(df.head(20), use_container_width=True)
        st.subheader("Statistiques")
        st.dataframe(df.describe(), use_container_width=True)
        colonne = st.selectbox("Distribution d'une colonne numérique",
                               df.select_dtypes("number").columns)
        st.bar_chart(df[colonne].value_counts(bins=20).sort_index(), color="#5B4BD5")
 
# ---------------------------------------------------------------------------
# 7. Page Performance du modèle
# ---------------------------------------------------------------------------
# 8. Page À propos
# ---------------------------------------------------------------------------
else:
    st.title("ℹ️ À propos")
    st.markdown(
        """
        **Projet** : prédiction des frais médicaux d'assurance (dataset insurance, Kaggle)
 
        **Pipeline** : Notebook → modèle Gradient Boosting → API Flask → Docker → AWS ECR → AWS ECS → interface Streamlit
 
        **Auteur** : Ahmadou Moukhtar
        """
    )