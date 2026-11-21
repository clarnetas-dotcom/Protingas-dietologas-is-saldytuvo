# Protingas-dietologas-is-saldytuvo
ai darbas
[README.md](https://github.com/user-attachments/files/35216024/README.md)
# Protingas dietologas iš šaldytuvo

## Kas yra aplanke?

- `app.py` — paprasta Streamlit sąsaja (ingredientų įvedimas, laikas, vegetariškas pasirinkimas, alergenai, prioritetiniai produktai).
- `code/recipes_catalog.py` — 48 ranka sudarytų demonstracinių receptų katalogo šaltinis.
- `code/generate_data.py` — sukuria 480 šaldytuvo scenarijų ir recepto–scenarijaus porų rinkinį.
- `code/train_evaluate.py` — atlieka grupinį train/test atskyrimą, palygina bazinį metodą ir Random Forest, parenka slenkstį TIK mokymo validacijoje.
- `code/make_figures.py` — iš rezultato failų atkuria visus grafikus.
- `code/benchmark.py` — CPU rekomendacijų delsos matavimas (neapima sąsajos).
- `code/demo_cli.py` — komandų eilutės demonstracija (veikia ir be Streamlit).
- `code/core.py` — ingredientų normalizavimas, požymiai, saugos filtrai ir rekomendavimo funkcija.
- `data/` — 48 receptai, sintetinės poros, testinės prognozės ir metrikos.
- `models/` — išmokytas modelis (`joblib`, saugus tik naudojant savo sugeneruotą failą).
- `figures/` — grafikai ir sistemos schema.
- `tests/` — šeši vienetiniai testai.

## Paleidimas (Windows, PowerShell arba terminalas)

Reikia Python 3.10 arba naujesnės versijos. Projekto kataloge:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python code/generate_data.py
python code/train_evaluate.py
python code/make_figures.py
python code/demo_cli.py
python code/benchmark.py
python -m unittest discover -s tests -v
streamlit run app.py
```

Jeigu `streamlit` sąsaja neįsijungia, paleiskite `python -m streamlit run app.py`.

**Neprisijungus prie interneto:** po to, kai reikalingos bibliotekos jau įdiegtos, duomenų generavimas, modelis, grafikai ir demonstracija veikia be API ir tinklo. `demo_cli.py` remiasi iš anksto sugeneruotu modeliu.

## Kaip išbandyti?

Pavyzdiniai ingredientai: `kiaušiniai, pomidorai, agurkai, duona, sūris, ryžiai, morka, jogurtas`.
Nustatykite 30 min., pažymėkite vegetarišką pasirinkimą ir, pavyzdžiui, `pomidorai` nurodykite kaip greičiau sunaudotinus produktus.

Sistema pateikia iki penkių receptų ir kiekvienam nurodo turimą/trūkstamą ingredientų dalį, gaminimo laiką, apytikrį maistingumą ir pagrindinę gaminimo instrukciją.

### Dėl alergijų ir maisto saugos

Alergenų sąrašas kataloge yra supaprastintas ir nepatikrina prekės ženklo, kryžminės taršos ar konkretaus gaminio sudėties. Jei turite alergiją, tikrinkite pakuočių etiketes, o nepasikliaukite šios demonstracinės programos filtru. Programa **negali** nustatyti, ar produktas nebesaugus. `Tinka vartoti iki` data yra maisto saugos riba.

### Patikimumo ribos

- Duomenys ir jų tinkamumo žymos **sintetiniai**. Rezultatai nereiškia tokio pat tikslumo realių žmonių pasirinkimuose.
- 48 receptai nėra reprezentatyvi patiekalų duomenų bazė.
- 14 įvesties požymių apibūdina patogumą ir prieinamumą; jie nematuoja mitybos kokybės medicinine prasme.
- Modelio grąžinamas skaičius nėra patikima medicininė ar asmens pasitenkinimo tikimybė.
- Modelis neišmoko skaičiuoti tikslių porcijų, kalorijų poreikio, laikymo temperatūros ar išvengti kryžminės taršos.
- Vengimo filtrai (alergenai, vegetarizmas, laikas) veikia deterministiškai PRIEŠ prognozę.

## Šaltiniai

- WHO: https://www.who.int/news-room/fact-sheets/detail/healthy-diet
- EFSA (alergenai): https://www.efsa.europa.eu/en/safe2eat/food-allergens
- EFSA (datos): https://www.efsa.europa.eu/en/safe2eat/food-date-labelling
- USDA FoodData Central (būsimai patikimų verčių integracijai): https://fdc.nal.usda.gov/
- Scikit-learn dokumentacija: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
- Streamlit: https://docs.streamlit.io/get-started/installation
