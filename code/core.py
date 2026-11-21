"""Rekomendacijų branduolys; neteikia individualių medicininių rekomendacijų."""
from __future__ import annotations
from pathlib import Path
import csv
import re
import unicodedata
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
FEATURES=['coverage','missing_n','present_n','prep_minutes','time_margin','is_vegetarian','wants_vegetarian','diet_conflict','allergen_conflict','protein_g_est','veg_score','perishable_used','recipe_size','fridge_size']
ALIASES={
    'kiaušiniai':'kiaušinis','kiaušinį':'kiaušinis','kiaušinių':'kiaušinis','kiaušini':'kiaušinis',
    'pomidorai':'pomidoras','pomidorų':'pomidoras','pomidorus':'pomidoras',
    'agurkai':'agurkas','agurkų':'agurkas','agurkus':'agurkas',
    'morkos':'morka','morkų':'morka','morkas':'morka',
    'bulvės':'bulvė','bulvių':'bulvė','bulves':'bulvė',
    'svogūnai':'svogūnas','svogūnų':'svogūnas',
    'pupelių':'pupelės','pupeles':'pupelės','pupelė':'pupelės',
    'avinžirnių':'avinžirniai','avinžirnius':'avinžirniai','avinžirnis':'avinžirniai',
    'ryžių':'ryžiai','ryzius':'ryžiai','ryžius':'ryžiai',
    'grikių':'grikiai','grikius':'grikiai',
    'makaronų':'makaronai','makaronus':'makaronai',
    'avižinių dribsnių':'avižos','avižiniai dribsniai':'avižos','avižų':'avižos',
    'sūrio':'sūris','sūrį':'sūris', 'jogurto':'jogurtas','pieno':'pienas','varškės':'varškė',
    'vištienos':'vištiena','vištieną':'vištiena',
    'salotų lapai':'salotos','salotų':'salotos',
    'špinatų':'špinatai', 'brokolių':'brokoliai',
    'česnako':'česnakas','cukinijos':'cukinija','cukinijų':'cukinija',
    'paprikos':'paprika','paprikų':'paprika',
    'bananai':'bananas','bananų':'bananas', 'obuoliai':'obuolys','obuolių':'obuolys',
    'lašišos':'lašiša','tuno':'tunas','tuno konservai':'tunas',
    'fetos sūris':'feta','feta sūris':'feta',
    'alyvuogių aliejus':'aliejus', 'rudos pupelės':'pupelės',
}
PERISHABLE={'pomidoras','agurkas','salotos','špinatai','brokoliai','cukinija','paprika','morka','grybai','uogos','jogurtas','pienas','varškė','vištiena','žuvis','lašiša','kiaušinis'}

def norm_one(x):
    x=unicodedata.normalize('NFKC',str(x).lower().strip())
    x=re.sub(r'\s+',' ',x)
    return ALIASES.get(x,x)

def parse_items(text):
    if not isinstance(text,str):
        text=','.join(map(str,text))
    return set(norm_one(x) for x in re.split(r'[,;\n|]+',text) if x.strip())

def load_recipes(path=None):
    path=Path(path or ROOT/'data'/'recipes.csv')
    with path.open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    for r in rows:
        r['ingredients_set'] = parse_items(r['ingredients'])
        r['allergens_set'] = parse_items(r['allergens'])
        for key in ['minutes','vegetarian','kcal_est','protein_g_est','veg_score','id']:
            r[key]=int(r[key])
    return rows

def make_features(recipe, inventory, max_minutes=30, vegetarian=False, allergies=(), urgent=()):
    inventory = set(inventory)
    urgent = set(urgent)
    ins=recipe['ingredients_set']
    present=ins & inventory
    absent=ins - inventory
    blocked=recipe['allergens_set'] & set(allergies)
    c=int(bool(vegetarian and not recipe['vegetarian']))
    fields={
        'coverage':len(present)/len(ins),
        'missing_n':len(absent), 'present_n':len(present),
        'prep_minutes':int(recipe['minutes']),
        'time_margin':int(max_minutes)-int(recipe['minutes']),
        'is_vegetarian':int(recipe['vegetarian']),
        'wants_vegetarian':int(bool(vegetarian)),
        'diet_conflict':c,
        'allergen_conflict':int(bool(blocked)),
        'protein_g_est':recipe['protein_g_est'],
        'veg_score':recipe['veg_score'],
        'perishable_used':len(present & urgent),
        'recipe_size':len(ins),'fridge_size':len(inventory),
    }
    return fields

def vectorize(features):
    return np.asarray([[float(f[k]) for k in FEATURES] for f in features],dtype=float)

def baseline_predict(features):
    # Sąmoningai paprastas atskaitos taškas, be mokymo
    return np.asarray([int(f['coverage']>=0.70 and f['missing_n']<=1 and f['time_margin']>=0 and f['diet_conflict']==0 and f['allergen_conflict']==0) for f in features])

def recommend(recipes, inventory, model=None, max_minutes=30, vegetarian=False, allergies=(), urgent=(), top_k=5):
    inv=parse_items(inventory) if isinstance(inventory,str) else set(map(norm_one,inventory))
    urg=parse_items(urgent) if isinstance(urgent,str) else set(map(norm_one,urgent))
    allergy_set=parse_items(allergies) if isinstance(allergies,str) else set(allergies)
    if not inv: return []
    candidates=[]
    for r in recipes:
        f=make_features(r,inv,max_minutes,vegetarian,allergy_set,urg)
        # Griežtos taisyklės veikia PRIEŠ modelį (rizikų valdymas)
        if f['diet_conflict'] or f['allergen_conflict'] or f['time_margin']<0:
            continue
        if f['coverage']<0.30 or f['missing_n']>3:
            continue
        candidates.append((r,f))
    if not candidates:return []
    F=[x[1] for x in candidates]
    if model is None:
        scores=[0.65*f['coverage']+0.25*(f['missing_n']==0)+0.1*(f['perishable_used']>0) for f in F]
    else:
        scores=model.predict_proba(vectorize(F))[:,1].tolist()
    outputs=[]
    for (r,f),score in zip(candidates,scores):
        result=dict(r)
        result['confidence_score']=round(float(score),3)
        result['coverage_pct']=round(100*f['coverage'])
        result['have']=sorted(r['ingredients_set'] & inv)
        result['missing']=sorted(r['ingredients_set']-inv)
        result['urgent_used']=sorted(r['ingredients_set'] & inv & urg)
        outputs.append(result)
    return sorted(outputs,key=lambda x:(-x['confidence_score'],len(x['missing']),-len(x['urgent_used'])))[:top_k]
