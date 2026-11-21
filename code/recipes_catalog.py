"""Rankiniu būdu sudarytas DEMONSTRACINIS receptų katalogas.

Maistingumo skaičiai apytikriai, neimportuoti iš USDA ir netinka medicininei mitybai.
"""
from pathlib import Path
import csv

# formatas: patiekalas; ingredientai |; minutės; vegetariškas 1/0; kcal~; baltymai g~; daržovės 0..3; kategorija; alergenai |; gaminimas
ROWS = '''Avižinė košė su bananu;avižos|pienas|bananas|cinamonas;12;1;330;12;0;pusryčiai;glitimas|pienas;Avižas pavirkite piene. Sudėkite pjaustytą bananą ir cinamoną.
Avižinė košė su obuoliu;avižos|pienas|obuolys|cinamonas;12;1;315;11;0;pusryčiai;glitimas|pienas;Išvirkite avižas, įmaišykite tarkuotą obuolį ir cinamoną.
Grikių košė su daržovėmis;grikiai|morka|svogūnas|paprika;25;1;350;10;3;pietūs;;Išvirkite grikius. Apkepkite daržoves, sumaišykite.
Kiaušinienė su pomidorais;kiaušinis|pomidoras|svogūnas;12;1;270;17;2;pusryčiai;kiaušiniai;Pakepinkite svogūną, pomidorą, supilkite plaktus kiaušinius.
Omletas su špinatais;kiaušinis|špinatai|pienas|sūris;15;1;340;23;1;pusryčiai;kiaušiniai|pienas;Kiaušinius išplakite su pienu, įdėkite špinatų ir sūrio, kepkite.
Varškė su uogomis;varškė|uogos|medus;5;1;260;25;0;pusryčiai;pienas;Varškę patiekite su uogomis ir trupučiu medaus.
Natūralus jogurtas su vaisiais;jogurtas|bananas|obuolys|avižos;7;1;300;12;0;pusryčiai;pienas|glitimas;Supjaustykite vaisius ir sumaišykite su jogurtu bei avižomis.
Pilno grūdo sumuštinis su avokadu;duona|avokadas|pomidoras|kiaušinis;10;1;390;14;1;pusryčiai;glitimas|kiaušiniai;Ant duonos dėkite avokadą, pomidorus ir virtą kiaušinį.
Sumuštinis su sūriu ir pomidoru;duona|sūris|pomidoras|salotos;7;1;310;14;2;pusryčiai;glitimas|pienas;Ant duonos dėkite sūrį, pomidorą ir salotų lapus.
Ryžių košė su obuoliu;ryžiai|pienas|obuolys|cinamonas;25;1;300;8;0;pusryčiai;pienas;Ryžius išvirkite piene, įdėkite obuolio ir cinamono.
Morkų ir obuolių salotos;morka|obuolys|jogurtas|citrina;10;1;180;4;1;užkandis;pienas;Sutarkuokite morkas ir obuolį, užpilkite jogurto ir citrinos.
Pomidorų ir agurkų salotos;pomidoras|agurkas|svogūnas|feta;10;1;220;9;3;užkandis;pienas;Supjaustykite daržoves, sumaišykite su feta.
Tunų ir pupelių salotos;tunas|pupelės|pomidoras|agurkas|citrina;12;0;390;34;2;pietūs;žuvis;Sumaišykite nusausintą tuną, pupeles ir daržoves.
Avinžirnių salotos;avinžirniai|agurkas|pomidoras|paprika|citrina;12;1;370;13;3;pietūs;;Sumaišykite avinžirnius, daržoves ir citrinos sultis.
Lęšių sriuba;lęšiai|morka|svogūnas|pomidoras;35;1;330;17;3;pietūs;;Išvirkite lęšius su smulkintomis daržovėmis.
Daržovių sriuba;bulvė|morka|svogūnas|brokoliai|žirneliai;30;1;230;7;3;pietūs;;Daržoves supjaustykite, užpilkite vandeniu ir išvirkite.
Moliūgų sriuba;moliūgas|bulvė|morka|svogūnas|grietinėlė;35;1;280;6;3;pietūs;pienas;Daržoves išvirkite, sutrinkite ir įpilkite grietinėlės.
Vištiena su ryžiais;vištiena|ryžiai|morka|brokoliai;35;0;540;40;2;pietūs;;Išvirkite ryžius, iškepkite vištieną ir pagaminkite daržoves.
Vištiena su grikiais;vištiena|grikiai|morka|svogūnas;35;0;520;41;2;pietūs;;Išvirkite grikius, apkepkite vištieną ir daržoves.
Makaronai su pomidorų padažu;makaronai|pomidoras|svogūnas|česnakas|sūris;25;1;480;17;2;pietūs;glitimas|pienas;Išvirkite makaronus, padažą paruoškite iš daržovių ir sūrio.
Makaronai su tunu;makaronai|tunas|pomidoras|svogūnas;20;0;515;30;2;pietūs;glitimas|žuvis;Išvirkite makaronus, sumaišykite su tunu ir pomidorais.
Ryžiai su kiaušiniu ir žirneliais;ryžiai|kiaušinis|žirneliai|morka|svogūnas;20;1;430;16;3;pietūs;kiaušiniai;Išvirtus ryžius trumpai pakepinkite su daržovėmis ir kiaušiniu.
Daržovių troškinys;bulvė|morka|paprika|cukinija|svogūnas;35;1;340;8;3;pietūs;;Daržoves kubeliais troškinkite ant silpnos ugnies.
Cukinijų blyneliai;cukinija|kiaušinis|miltai|jogurtas;25;1;370;16;1;pietūs;kiaušiniai|glitimas|pienas;Sutarkuokite cukiniją, išmaišykite su kiaušiniu bei miltais, apkepkite.
Bulviniai blynai;bulvė|kiaušinis|svogūnas|miltai|grietinė;30;1;450;11;1;pietūs;kiaušiniai|glitimas|pienas;Sutarkuokite bulves, įmaišykite kitas sudedamąsias dalis ir kepkite.
Varškėčiai;varškė|kiaušinis|miltai|jogurtas;25;1;410;25;0;pusryčiai;pienas|kiaušiniai|glitimas;Suminkykite tešlą, formuokite nedidelius blynelius ir kepkite.
Grikių salotos su feta;grikiai|feta|pomidoras|agurkas|špinatai;20;1;400;15;3;pietūs;pienas;Išvirkite grikius ir sumaišykite su daržovėmis bei feta.
Brokolių ir sūrio apkepas;brokoliai|kiaušinis|pienas|sūris;35;1;385;23;1;vakarienė;kiaušiniai|pienas;Brokolius apvirkite, užpilkite kiaušinio mišiniu ir apkepkite.
Vištienos salotos;vištiena|salotos|pomidoras|agurkas|jogurtas;25;0;360;38;3;vakarienė;pienas;Iškepkite vištieną ir sumaišykite su daržovėmis bei jogurtu.
Orkaitėje kepta žuvis su bulvėmis;žuvis|bulvė|citrina|brokoliai;40;0;460;35;1;vakarienė;žuvis;Žuvį su citrina kepkite orkaitėje, patiekite su bulvėmis ir brokoliais.
Kepta lašiša su ryžiais;lašiša|ryžiai|citrina|špinatai;35;0;540;35;1;vakarienė;žuvis;Lašišą kepkite, išvirkite ryžius, trumpai patroškinkite špinatus.
Omletas su grybais;kiaušinis|grybai|svogūnas|sūris;18;1;350;23;1;vakarienė;kiaušiniai|pienas;Apkepkite grybus ir svogūną, supilkite kiaušinius, užbarstykite sūrį.
Avinžirnių karis;avinžirniai|pomidoras|svogūnas|kokosų pienas|ryžiai;35;1;540;16;2;vakarienė;;Avinžirnius patroškinkite su pomidorais ir kokosų pienu, patiekite su ryžiais.
Pupelių troškinys;pupelės|pomidoras|paprika|svogūnas|morka;35;1;400;19;3;vakarienė;;Pupeles ir daržoves troškinkite, kol suminkštės.
Moliūgų ir lęšių troškinys;moliūgas|lęšiai|svogūnas|morka|pomidoras;40;1;370;16;3;vakarienė;;Supjaustytą moliūgą ir lęšius troškinkite su daržovėmis.
Kuskuso salotos;kuskusas|agurkas|pomidoras|feta|citrina;15;1;420;14;2;pietūs;glitimas|pienas;Kuskusą užplikykite, sumaišykite su daržovėmis ir feta.
Tortilija su vištiena;tortilija|vištiena|salotos|pomidoras|jogurtas;20;0;490;36;2;pietūs;glitimas|pienas;Tortiliją užpildykite iškepta vištiena, salotomis ir jogurtu.
Tortilija su pupelėmis;tortilija|pupelės|pomidoras|salotos|paprika;18;1;450;16;3;pietūs;glitimas;Tortiliją užpildykite pupelėmis ir šviežiomis daržovėmis.
Salotos su virtu kiaušiniu;kiaušinis|salotos|pomidoras|agurkas|duona;13;1;350;17;3;vakarienė;kiaušiniai|glitimas;Išvirkite kiaušinį, patiekite su salotomis ir duona.
Orkaitėje keptos daržovės;bulvė|morka|cukinija|paprika|svogūnas;40;1;350;8;3;vakarienė;;Daržoves supjaustykite, kepkite orkaitėje iki suminkštėjimo.
Varškės ir agurkų užtepėlė;varškė|agurkas|česnakas|duona;10;1;280;22;1;užkandis;pienas|glitimas;Varškę sumaišykite su agurkais ir česnaku, tepkite ant duonos.
Bananiniai blyneliai;bananas|kiaušinis|avižos|jogurtas;15;1;360;15;0;pusryčiai;kiaušiniai|glitimas|pienas;Sutrinkite bananą, įmaišykite kiaušinį ir avižas, kepkite.
Daržovių ryžiai;ryžiai|paprika|morka|žirneliai|svogūnas;25;1;380;10;3;vakarienė;;Išvirkite ryžius ir sumaišykite su trumpai keptomis daržovėmis.
Kiaušinio ir avokado salotos;kiaušinis|avokadas|salotos|pomidoras|citrina;15;1;410;16;2;vakarienė;kiaušiniai;Sumaišykite virtą kiaušinį, avokadą ir daržoves.
Tunų sumuštinis;tunas|duona|agurkas|jogurtas;10;0;360;29;1;užkandis;žuvis|glitimas|pienas;Ant duonos užtepkite jogurtu sumaišytą tuną, uždėkite agurko.
Pupelių užtepėlė;pupelės|česnakas|citrina|duona;10;1;320;13;0;užkandis;glitimas;Pupeles sutrinkite su česnaku ir citrina, tepkite ant duonos.
Skrudinta duona su hummusu;duona|avinžirniai|citrina|česnakas|sezamai;15;1;370;12;0;užkandis;glitimas|sezamai;Avinžirnius sutrinkite su citrina, česnaku ir sezamais, tepkite ant duonos.
Šiltos lęšių salotos;lęšiai|morka|špinatai|svogūnas|feta;30;1;390;19;3;vakarienė;pienas;Išvirtus lęšius sumaišykite su keptomis daržovėmis ir feta.'''

FIELDNAMES = ['id','name','ingredients','minutes','vegetarian','kcal_est','protein_g_est','veg_score','category','allergens','steps']

def save_catalog(out_path):
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [l.strip() for l in ROWS.splitlines() if l.strip()]
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        wr=csv.DictWriter(f, fieldnames=FIELDNAMES)
        wr.writeheader()
        for i,line in enumerate(lines,1):
            parts=line.split(';')
            if len(parts)!=10:
                raise ValueError(f'Blogas recepto formatas {i}: {len(parts)}')
            wr.writerow(dict(zip(FIELDNAMES,[i]+parts)))
    return len(lines)

if __name__=='__main__':
    print(save_catalog(Path(__file__).resolve().parents[1]/'data'/'recipes.csv'))
