"""Apytikris vietinio CPU rekomendavimo delsos matavimas (p50 ir p95)."""
from pathlib import Path
import sys,json,time
import numpy as np
import joblib
sys.path.insert(0,str(Path(__file__).resolve().parent))
from core import ROOT,load_recipes,recommend

def run(n=60):
    model=joblib.load(ROOT/'models'/'recipe_fit_rf.joblib')
    recipes=load_recipes()
    input_text='kiaušiniai, pomidorai, agurkai, duona, sūris, ryžiai, morka, jogurtas'
    for _ in range(5): recommend(recipes,input_text,model,max_minutes=30,vegetarian=True)
    samples=[]
    for _ in range(n):
        t=time.perf_counter()
        recommend(recipes,input_text,model,max_minutes=30,vegetarian=True)
        samples.append((time.perf_counter()-t)*1000)
    result={'runs':n,'p50_ms':round(float(np.percentile(samples,50)),2),'p95_ms':round(float(np.percentile(samples,95)),2),'max_ms':round(float(max(samples)),2),'scope':'Python recommend() CPU; be Streamlit UI ir tinklo; priklauso nuo kompiuterio'}
    (ROOT/'data'/'benchmark.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':run()
