import unittest
from code.core import parse_items,load_recipes,recommend,make_features

class TestRecommendation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.recipes=load_recipes()
    def test_aliases(self):
        self.assertEqual(parse_items('kiaušiniai, pomidorai'),{'kiaušinis','pomidoras'})
    def test_hard_vegetarian_filter(self):
        got=recommend(self.recipes,'vištiena, ryžiai, pomidorai, svogūnas',vegetarian=True,max_minutes=60)
        self.assertTrue(all(r['vegetarian'] for r in got))
    def test_hard_allergen_filter(self):
        got=recommend(self.recipes,'pienas, avižos, bananas, obuolys',allergies={'pienas'},max_minutes=60)
        self.assertTrue(all('pienas' not in r['allergens_set'] for r in got))
    def test_hard_time_filter(self):
        got=recommend(self.recipes,'grikiai, morka, svogūnas, paprika, kiaušinis',max_minutes=15)
        self.assertTrue(all(r['minutes']<=15 for r in got))
    def test_empty_fridge(self):self.assertEqual(recommend(self.recipes,''),[])
    def test_explanation(self):
        got=recommend(self.recipes,'kiaušinis, pomidoras, svogūnas',max_minutes=20)
        self.assertTrue(got)
        self.assertTrue(all(isinstance(r['missing'],list) for r in got))

if __name__=='__main__':unittest.main()
