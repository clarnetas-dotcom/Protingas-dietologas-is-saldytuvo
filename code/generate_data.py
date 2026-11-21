"""Sintetiniai bandymų atvejai. Etiketės SIMULIUOTOS, ne dietologų ar vartotojų vertinimai."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from recipes_catalog import save_catalog
from core import load_recipes, make_features, FEATURES
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SEED=42

def build_cases(n_cases=480, pairs_per_case=12):
    rng=np.random.default_rng(SEED)
    recipes=load_recipes()
    all_items=sorted(set().union(*(r['ingredients_set'] for r in recipes)))
    rows=[]
    for case in range(n_cases):
        chosen=recipes[int(rng.integers(len(recipes)))]
        # Įprastas šaldytuvas: dalis patiekalo produktų, dar keli pašaliniai
        keep_probability=float(rng.uniform(0.35,0.98))
        inv={item for item in chosen['ingredients_set'] if rng.random()<keep_probability}
        n_extras=int(rng.integers(2,11))
        inv.update(rng.choice(all_items,size=min(n_extras,len(all_items)),replace=False).tolist())
        if len(inv)<2: inv.update(rng.choice(all_items,size=2,replace=False).tolist())
        urgent={x for x in inv if rng.random()<0.25}
        vegetarian=bool(rng.random()<0.29)
        max_minutes=int(rng.choice([15,20,30,40,50],p=[0.17,0.23,0.31,0.20,0.09]))
        allergies=set(rng.choice(['glitimas','pienas','kiaušiniai','žuvis','sezamai'],size=1).tolist()) if rng.random()<0.22 else set()
        recipe_idxs={int(chosen['id'])-1}
        # Keturi panašūs patiekalai leidžia tikrinti ne vien akivaizdžius neigiamus atvejus.
        similar=sorted(range(len(recipes)),key=lambda j:len(recipes[j]['ingredients_set'] & inv)/len(recipes[j]['ingredients_set']),reverse=True)
        recipe_idxs.update(similar[:4])
        recipe_idxs.update(map(int,rng.choice(len(recipes),size=pairs_per_case-5,replace=False)))
        for ix in sorted(recipe_idxs):
            r=recipes[ix]
            f=make_features(r,inv,max_minutes,vegetarian,allergies,urgent)
            # „Vartotojo tinkamumo“ simuliatorius: netiesinė tikslinė funkcija,
            # papildyta triukšmu. Nėra žmogaus išmatuota tiesa!
            utility=(2.30*f['coverage'] - 0.20*f['missing_n']
                     + 0.24*(f['time_margin']>=0)
                     + 0.09*(f['protein_g_est']>=20)
                     + 0.07*(f['veg_score']>=2)
                     + 0.16*(f['perishable_used']>0)
                     - 1.90*f['diet_conflict'] - 2.10*f['allergen_conflict']
                     - 0.28*(f['time_margin']<-10)
                     + rng.normal(0,0.25))
            label=int(utility>=1.27 and f['time_margin']>=0
                     and not f['diet_conflict'] and not f['allergen_conflict'])
            rows.append(dict(case_id=case,recipe_id=r['id'],label=label,**f))
    return pd.DataFrame(rows)

if __name__=='__main__':
    ROOT.joinpath('data').mkdir(exist_ok=True)
    n=save_catalog(ROOT/'data'/'recipes.csv')
    df=build_cases()
    df.to_csv(ROOT/'data'/'synthetic_pairs.csv',index=False)
    print('recipes',n,'cases',df.case_id.nunique(),'pairs',len(df),'positive',round(df.label.mean(),3))
