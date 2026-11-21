"""Grupuotas testavimo skaidymas be to paties šaldytuvo scenarijaus nutekėjimo."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,roc_auc_score,confusion_matrix
from sklearn.model_selection import GroupShuffleSplit
from core import FEATURES,baseline_predict
ROOT=Path(__file__).resolve().parents[1]

def metrics(y_true,y_pred,scores):
    return {k:round(float(fn(y_true,y_pred,zero_division=0)),4) for k,fn in
            [('precision',precision_score),('recall',recall_score),('f1',f1_score)]} | {
            'accuracy':round(float(accuracy_score(y_true,y_pred)),4),
            'roc_auc':round(float(roc_auc_score(y_true,scores)),4),
            'confusion_matrix':confusion_matrix(y_true,y_pred,labels=[0,1]).tolist()}

def run():
    df=pd.read_csv(ROOT/'data'/'synthetic_pairs.csv')
    splitter=GroupShuffleSplit(n_splits=1,test_size=0.2,random_state=42)
    train_idx,test_idx=next(splitter.split(df,y=df.label,groups=df.case_id))
    tr=df.iloc[train_idx].copy();te=df.iloc[test_idx].copy()
    assert set(tr.case_id).isdisjoint(set(te.case_id))
    Xtr=tr[FEATURES].to_numpy(float);Xte=te[FEATURES].to_numpy(float)
    ytr=tr.label.to_numpy();yte=te.label.to_numpy()
    # 1 eksperimentas: taisyklė 70 % + daugiausia 1 trūkstamas produktas
    base=baseline_predict(te.to_dict('records'))
    base_score=(te['coverage']*.82 + .18*(te['time_margin']>=0)).to_numpy()
    # 2 eksperimentas: RandomForest. Slenkstis parenkamas TIK mokymo dalies validacijoje.
    params=dict(n_estimators=240,max_depth=9,min_samples_leaf=6,class_weight='balanced',random_state=42,n_jobs=-1)
    inner=GroupShuffleSplit(n_splits=1,test_size=0.25,random_state=24)
    fit_idx,val_idx=next(inner.split(tr,y=tr.label,groups=tr.case_id))
    val_model=RandomForestClassifier(**params)
    val_model.fit(Xtr[fit_idx],ytr[fit_idx])
    val_score=val_model.predict_proba(Xtr[val_idx])[:,1]
    thresholds=np.arange(.25,.901,.025)
    threshold=float(max(thresholds,key=lambda t:(f1_score(ytr[val_idx],(val_score>=t).astype(int)),t)))
    forest=RandomForestClassifier(**params)
    forest.fit(Xtr,ytr)
    prop_scores=forest.predict_proba(Xte)[:,1]
    prop=(prop_scores>=threshold).astype(int)
    result={
       'seed':42,'recipes':int(pd.read_csv(ROOT/'data'/'recipes.csv').shape[0]),
       'cases_all':int(df.case_id.nunique()),'pairs_all':int(len(df)),
       'cases_train':int(tr.case_id.nunique()),'cases_test':int(te.case_id.nunique()),
       'n_train':int(len(tr)),'n_test':int(len(te)),
       'positive_share_all':round(float(df.label.mean()),4),
       'positive_share_test':round(float(te.label.mean()),4),
       'threshold_from_train_validation':round(threshold,3),
       'models':{'baseline':metrics(yte,base,base_score),'proposed':metrics(yte,prop,prop_scores)},
       'feature_importances':{a:round(float(b),5) for a,b in zip(FEATURES,forest.feature_importances_)},
       'example_errors':[],'examples_success':[]}
    te=te.copy();te['prediction_baseline']=base;te['prediction_proposed']=prop;te['proposed_score']=prop_scores
    err=te[te['prediction_proposed']!=te.label].head(5)
    result['example_errors']=err[['case_id','recipe_id','coverage','missing_n','time_margin','diet_conflict','allergen_conflict','label','prediction_proposed','proposed_score']].round(3).to_dict('records')
    ok=te[te['prediction_proposed']==te.label].head(4)
    result['examples_success']=ok[['case_id','recipe_id','coverage','missing_n','label','prediction_proposed','proposed_score']].round(3).to_dict('records')
    (ROOT/'models').mkdir(exist_ok=True)
    joblib.dump(forest,ROOT/'models'/'recipe_fit_rf.joblib')
    (ROOT/'data'/'metrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    te.to_csv(ROOT/'data'/'test_predictions.csv',index=False)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result

if __name__=='__main__':run()
