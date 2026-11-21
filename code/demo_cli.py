from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import joblib
from core import ROOT,load_recipes,recommend

def main():
    model=joblib.load(ROOT/'models'/'recipe_fit_rf.joblib')
    recipes=load_recipes()
    inventory='kiaušiniai, pomidorai, agurkas, duona, sūris, ryžiai, morka, jogurtas'
    results=recommend(recipes,inventory,model,max_minutes=30,vegetarian=True,allergies=[],urgent='pomidorai, agurkas',top_k=5)
    print('Šaldytuve:',inventory)
    for r in results:
        print(f"- {r['name']} | modelio balas {r['confidence_score']:.2f} | turima {r['coverage_pct']}% | trūksta: {', '.join(r['missing']) or 'nieko'}")
if __name__=='__main__':main()
