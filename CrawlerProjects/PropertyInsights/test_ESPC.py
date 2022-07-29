import unittest
from ESPC import ESPCCrawler, ESPCPropertyInfo

# The first property on the first page of
# https://espc.com/properties?p=1&locations=edinburgh&minbeds=1plus&maxprice=210000&ptype=flat,house
EXPECTED_PROPERTY_INFO_1 = ESPCPropertyInfo(
    price_type="offers over",
    price_val=130000,
    title="1 bed top floor flat for sale in Dalry".lower(),
    address="15 (3F4), Downfield Place, Edinburgh, EH11 2EJ".lower(),
    postcode="eh11 2ej",
    bed_num=1,
    bath_num=1,
    couch_num=1,
    floor_area=43,
    council_tax="B",
    epc="C",
    url="https://espc.com/property/15-3f4-downfield-place-edinburgh-eh11-2ej/36101521"
)

# total number of page of
# https://espc.com/properties?p=1&locations=edinburgh&minbeds=1plus&maxprice=210000&ptype=flat,house
PAGE = 20

# The last property on the last page of
# https://espc.com/properties?p=1&locations=edinburgh&minbeds=1plus&maxprice=210000&ptype=flat,house
EXPECTED_PROPERTY_INFO_2 = ESPCPropertyInfo(
    price_type="offers over",
    price_val=197500,
    title="2 bed flat for sale in Gorgie".lower(),
    address="Two Bed, Embankment West 5 Elfin Square, EH11 3AF".lower(),
    postcode="eh11 3af",
    bed_num=2,
    bath_num=-1,
    couch_num=1,
    floor_area=-1,
    council_tax="",
    epc="",
    url="https://espc.com/property/two-bed-embankment-west-5-elfin-square-eh11-3af/35784393"
)


class TestESPCPropertyInfo(unittest.TestCase):
    def test_init_from_url(self):
        url = "https://espc.com/property/15-3f4-downfield-place-edinburgh-eh11-2ej/36101521"
        obj = ESPCPropertyInfo.init_from_url(url)

        for field in EXPECTED_PROPERTY_INFO_1.__dict__:
            self.assertEqual(EXPECTED_PROPERTY_INFO_1.__getattribute__(field), obj.__getattribute__(field))


class TestESPCCrawler(unittest.TestCase):
    """
    This class represents the ESPCCrawler test case
    """

    def setUp(self) -> None:
        """
        Define test variables
        """
        self.obj = ESPCCrawler("edinburgh", "1plus", "210000", "flat,house")

    def test_get_all_property_urls_on_page(self) -> None:
        # page 1
        page_source = self.obj.get_html_from_page_num(1)
        self.assertTrue(self.obj.is_valid_page(page_source))

        # page 1000
        page_source = self.obj.get_html_from_page_num(1000)
        self.assertFalse(self.obj.is_valid_page(page_source))

    def test__iter__1(self):
        for property_infos in self.obj:
            for property_info in property_infos:
                for field in EXPECTED_PROPERTY_INFO_1.__dict__:
                    self.assertEqual(EXPECTED_PROPERTY_INFO_1.__getattribute__(field),
                                     property_info.__getattribute__(field))
                break  # Only test the first one
            break

    def test__getitem__(self):
        for field in EXPECTED_PROPERTY_INFO_1.__dict__:
            self.assertEqual(EXPECTED_PROPERTY_INFO_1.__getattribute__(field),
                             self.obj[1, 1].__getattribute__(field))  # Only test the first one

    # Warning: this test takes a long time. Only uncommented if really necessary.
    def test__iter__2(self):
        last = None
        for property_infos in self.obj:
            for property_info in property_infos:
                last = property_info

        # Only test the last one
        # for field in EXPECTED_PROPERTY_INFO_2.__dict__:
        #     self.assertEqual(EXPECTED_PROPERTY_INFO_2.__getattribute__(field),
        #                      last.__getattribute__(field))


if __name__ == "__main__":
    unittest.main()
