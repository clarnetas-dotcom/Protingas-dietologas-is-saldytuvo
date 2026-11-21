"""Paprasta vietinė sąsaja su Streamlit. Paleisti: streamlit run app.py"""
from pathlib import Path
import joblib
import streamlit as st
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "code"))
from core import ROOT,load_recipes,recommend

st.set_page_config(page_title='Protingas dietologas iš šaldytuvo',page_icon='🥗',layout='centered')
st.title('🥗 Protingas dietologas iš šaldytuvo')
st.caption('Mokomasis receptų rekomendavimo prototipas, ne medicininė konsultacija')
st.write('Įrašykite turimus produktus. Sistema pasiūlys patiekalus, nurodys, ko trūksta, ir atsižvelgs į ribojimus.')

@st.cache_resource
def load_model():
    path=ROOT/'models'/'recipe_fit_rf.joblib'
    return joblib.load(path) if path.exists() else None

@st.cache_data
def recipes():return load_recipes()

inventory=st.text_area('Ką turite?',value='kiaušiniai, pomidorai, agurkai, duona, sūris, ryžiai, morka, jogurtas',height=100)
max_time=st.slider('Kiek laiko galite skirti gaminimui?',10,60,30,5)
vegetarian=st.checkbox('Tik vegetariški patiekalai',value=False)
allergies=st.multiselect('Vengti alergenų (pavyzdinis filtras)',options=['glitimas','pienas','kiaušiniai','žuvis','riešutai','sezamai','soja'])
urgent=st.text_input('Kuriuos produktus norite sunaudoti pirmiausia?',value='pomidorai')
st.info('Svarbu: programėlė neatpažįsta sugedusio maisto ir netikrina kryžminės taršos. Vadovaukitės pakuočių žymėjimu, ypač „Tinka vartoti iki“.')
if st.button('Rasti patiekalus',type='primary'):
    result=recommend(recipes(),inventory,model=load_model(),max_minutes=max_time,vegetarian=vegetarian,allergies=allergies,urgent=urgent,top_k=5)
    if not result:
        st.warning('Pagal įvestus ingredientus ir ribojimus tinkamų variantų nerasta. Pridėkite produktų arba padidinkite gaminimo laiką.')
    for rank,r in enumerate(result,1):
        st.subheader(f"{rank}. {r['name']}")
        st.write(f"**Turite {r['coverage_pct']} % ingredientų** · {r['minutes']} min. · apytikriai {r['kcal_est']} kcal / porc. · ~{r['protein_g_est']} g baltymų")
        st.write('Turite:',', '.join(r['have']))
        st.write('Trūksta:',', '.join(r['missing']) if r['missing'] else 'Nieko')
        if r['urgent_used']:st.write('Galėsite sunaudoti:',', '.join(r['urgent_used']))
        st.write('Gaminimas:',r['steps'])
        st.caption(f"Modelio tinkamumo balas {r['confidence_score']:.2f}; nėra tikra tikimybė ir neturi medicininės reikšmės.")
        st.divider()
st.caption('Maistingumo vertės yra iliustracinės. Tikros porcijos, kiekiai ir prekės ženklai čia nenustatomi.')
