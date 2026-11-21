"""Ataskaitos grafikai iš tikrųjų apskaičiuotų eksperimentų."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
DARK='#173754';TEAL='#178c96';ORANGE='#dc874c'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':150})

def save(name):
    plt.tight_layout();plt.savefig(ROOT/'figures'/name,dpi=200,bbox_inches='tight',facecolor='white');plt.close()

def build():
    (ROOT/'figures').mkdir(exist_ok=True)
    df=pd.read_csv(ROOT/'data'/'synthetic_pairs.csv')
    te=pd.read_csv(ROOT/'data'/'test_predictions.csv')
    info=json.loads((ROOT/'data'/'metrics.json').read_text(encoding='utf-8'))
    # 1. klasių pasiskirstymas
    counts=df.label.value_counts().sort_index()
    plt.figure(figsize=(6.4,3.4))
    bars=plt.bar(['Netinkamas (0)','Tinkamas (1)'],[counts.get(i,0) for i in [0,1]],color=[DARK,TEAL],width=.55)
    plt.ylabel('Recepto ir šaldytuvo porų skaičius');plt.title('1 pav. Sintetinių žymų pasiskirstymas')
    for b in bars:plt.text(b.get_x()+b.get_width()/2,b.get_height()+25,str(int(b.get_height())),ha='center')
    save('01_klasiu_balansas.png')
    # 2. coverage vs label
    tmp=df.assign(coverage_band=pd.cut(df.coverage,bins=[-.001,.25,.5,.75,1.001],labels=['0–25 %','25–50 %','50–75 %','75–100 %']))
    fractions=tmp.groupby('coverage_band',observed=False).label.agg(['mean','count'])
    plt.figure(figsize=(6.4,3.4));bb=plt.bar(fractions.index.astype(str),fractions['mean']*100,color=TEAL,width=.6)
    for bar,n in zip(bb,fractions['count']):plt.text(bar.get_x()+bar.get_width()/2,bar.get_height()+1,f'n={n}',ha='center',fontsize=8)
    plt.ylim(0,110);plt.ylabel('Tinkamų porų dalis (%)');plt.xlabel('Turimų ingredientų dalis');plt.title('2 pav. Suderinamumas pagal ingredientų turėjimą')
    save('02_tinkamumas_ir_ingredientai.png')
    # 3. palyginimas
    metrics=['accuracy','precision','recall','f1']
    b=[info['models']['baseline'][x] for x in metrics];p=[info['models']['proposed'][x] for x in metrics]
    xx=np.arange(len(metrics));w=.34
    plt.figure(figsize=(7.4,3.8));plt.bar(xx-w/2,b,w,label='Bazinis: taisyklės',color=DARK);plt.bar(xx+w/2,p,w,label='Patobulintas: Random Forest',color=TEAL)
    plt.xticks(xx,['Accuracy','Precision','Recall','F1']);plt.ylim(0,1.08);plt.ylabel('Rodiklis (0–1)');plt.title('5 pav. Eksperimentų rezultatų palyginimas');plt.legend(loc='lower right',fontsize=8)
    for k,(bval,pval) in enumerate(zip(b,p)):
        plt.text(k-w/2,bval+.013,f'{bval:.3f}',ha='center',fontsize=8)
        plt.text(k+w/2,pval+.013,f'{pval:.3f}',ha='center',fontsize=8)
    save('03_modeliu_palyginimas.png')
    # 4. confusion
    mat=np.asarray(info['models']['proposed']['confusion_matrix'])
    plt.figure(figsize=(5,3.8));plt.imshow(mat,cmap='Blues',vmin=0)
    for (i,j),v in np.ndenumerate(mat):plt.text(j,i,str(v),ha='center',va='center',color='white' if v>mat.max()*.5 else DARK,fontweight='bold',fontsize=13)
    plt.xticks([0,1],['0: ne','1: taip']);plt.yticks([0,1],['0: ne','1: taip']);plt.xlabel('Modelio sprendimas');plt.ylabel('Sintetinė žyma');plt.title('6 pav. Random Forest klaidų matrica')
    save('04_klaidu_matrica.png')
    # 5. feature importance
    feat=sorted(info['feature_importances'].items(),key=lambda x:x[1],reverse=True)[:9]
    plt.figure(figsize=(7,4.6));plt.barh([x[0] for x in reversed(feat)],[x[1] for x in reversed(feat)],color=TEAL)
    plt.title('4 pav. Požymių svarba (Random Forest)');plt.xlabel('Santykinė svarba (Gini)')
    save('05_pozymiu_svarba.png')
    # 6. schema, be rankinio piešimo
    fig,ax=plt.subplots(figsize=(8.2,2.35));ax.set_xlim(0,12);ax.set_ylim(0,4);ax.axis('off')
    items=[('Ingredientų\nsąrašas',.1),('Valymas ir\nnorminimas',2.6),('Receptų\nkatalogas',5.1),('Ribojimų\ntikrinimas',7.6),('ML +\nrikiavimas',10.1)]
    for txt,x in items:
        ax.text(x+1,2,txt,ha='center',va='center',fontsize=10,color='white',fontweight='bold',bbox=dict(facecolor=DARK if x<7 else TEAL,edgecolor='none',boxstyle='round,pad=.75'))
    for j in range(len(items)-1):ax.annotate('',(items[j+1][1]-.08,2),(items[j][1]+2.10,2),arrowprops=dict(arrowstyle='->',lw=1.7,color=ORANGE))
    ax.text(6,0.55,'Išvestis: tinkamas patiekalas · turimi/trūkstami produktai · ribotumų paaiškinimas',ha='center',fontsize=9,color=DARK)
    save('06_veikimo_schema.png')
    print('figures built')
if __name__=='__main__':build()
