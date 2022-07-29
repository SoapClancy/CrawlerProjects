import unittest
from SIMD import SIMDCrawler, SIMDInfoVariation


class TestSIMDInfoVariation(unittest.TestCase):
    def setUp(self) -> None:
        self.obj = SIMDCrawler(use_headless=False, version=2020)

    def tearDown(self) -> None:
        self.obj.browser.close()  # Close the browser

    def test_cal_variations(self):
        postcode = "EH9 1HF".lower()
        simd_info_2020 = self.obj.clear_and_search(postcode)
        self.obj.update_version(2016)
        simd_info_2016 = self.obj.clear_and_search(postcode)
        # TODO
        self.obj.update_version(2012)
        simd_info_2012 = self.obj.clear_and_search(postcode)

        simd_infos = [simd_info_2012, simd_info_2016, simd_info_2020]
        simd_variation = SIMDInfoVariation(postcode)
        simd_variation.cal_variations(simd_infos)


"""
class TestSIMDCrawler(unittest.TestCase):
    def setUp(self) -> None:
        self.obj = SIMDCrawler(use_headless=True, version=2020)

    def tearDown(self) -> None:
        self.obj.browser.close()  # Close the browser

    def test_clear_and_search_2020(self):
        self.obj.update_version(2020)
        postcode = "EH9 1HF".lower()
        simd_info = self.obj.clear_and_search(postcode)

        self.assertEqual("s01008616", simd_info.data_zone_id)
        self.assertEqual("Marchmont East and Sciennes".lower(), simd_info.data_zone_name)
        self.assertEqual("eh9 1hf", simd_info.postcode)
        self.assertEqual(6843, simd_info.overall_rank)
        self.assertEqual(10, simd_info.overall_rank_bar)
        self.assertEqual(6530, simd_info.income_rank)
        self.assertEqual(10, simd_info.income_rank_bar)
        self.assertEqual(6960, simd_info.employment_rank)
        self.assertEqual(10, simd_info.employment_rank_bar)
        self.assertEqual(6969, simd_info.health_rank)
        self.assertEqual(10, simd_info.health_rank_bar)
        self.assertEqual(5944, simd_info.edu_rank)
        self.assertEqual(9, simd_info.edu_rank_bar)
        self.assertEqual(106, simd_info.housing_rank)
        self.assertEqual(1, simd_info.housing_rank_bar)
        self.assertEqual(6819, simd_info.geo_access_rank)
        self.assertEqual(10, simd_info.geo_access_rank_bar)
        self.assertEqual(5540, simd_info.crime_rank)
        self.assertEqual(8, simd_info.crime_rank_bar)
        self.assertEqual(2020, simd_info.version)

    def test_clear_and_search_2016(self):
        self.obj.update_version(2016)
        postcode = "EH9 1HF".lower()
        simd_info = self.obj.clear_and_search(postcode)

        self.assertEqual("s01008616", simd_info.data_zone_id)
        self.assertEqual("Marchmont East and Sciennes".lower(), simd_info.data_zone_name)
        self.assertEqual("eh9 1hf", simd_info.postcode)
        self.assertEqual(6921, simd_info.overall_rank)
        self.assertEqual(10, simd_info.overall_rank_bar)
        self.assertEqual(6784, simd_info.income_rank)
        self.assertEqual(10, simd_info.income_rank_bar)
        self.assertEqual(6878, simd_info.employment_rank)
        self.assertEqual(10, simd_info.employment_rank_bar)
        self.assertEqual(6956, simd_info.health_rank)
        self.assertEqual(10, simd_info.health_rank_bar)
        self.assertEqual(6661, simd_info.edu_rank)
        self.assertEqual(10, simd_info.edu_rank_bar)
        self.assertEqual(106, simd_info.housing_rank)
        self.assertEqual(1, simd_info.housing_rank_bar)
        self.assertEqual(6908, simd_info.geo_access_rank)
        self.assertEqual(10, simd_info.geo_access_rank_bar)
        self.assertEqual(5737, simd_info.crime_rank)
        self.assertEqual(9, simd_info.crime_rank_bar)
        self.assertEqual(2016, simd_info.version)

    def test_clear_and_search_2012(self):
        self.obj.update_version(2012)
        postcode = "EH9 1HF".lower()
        simd_info = self.obj.clear_and_search(postcode)

        self.assertEqual("s01002002", simd_info.data_zone_id)
        self.assertEqual("Edinburgh, City of - Marchmont East and Sciennes".lower(), simd_info.data_zone_name)
        self.assertEqual("eh9 1hf", simd_info.postcode)
        self.assertEqual(6481, simd_info.overall_rank)
        self.assertEqual(10, simd_info.overall_rank_bar)
        self.assertEqual(6460, simd_info.income_rank)
        self.assertEqual(10, simd_info.income_rank_bar)
        self.assertEqual(6483, simd_info.employment_rank)
        self.assertEqual(10, simd_info.employment_rank_bar)
        self.assertEqual(6505, simd_info.health_rank)
        self.assertEqual(10, simd_info.health_rank_bar)
        self.assertEqual(6382, simd_info.edu_rank)
        self.assertEqual(10, simd_info.edu_rank_bar)
        self.assertEqual(482, simd_info.housing_rank)
        self.assertEqual(1, simd_info.housing_rank_bar)
        self.assertEqual(5705, simd_info.geo_access_rank)
        self.assertEqual(9, simd_info.geo_access_rank_bar)
        self.assertEqual(5155, simd_info.crime_rank)
        self.assertEqual(8, simd_info.crime_rank_bar)
        self.assertEqual(2012, simd_info.version)
"""
if __name__ == "__main__":
    unittest.main()
