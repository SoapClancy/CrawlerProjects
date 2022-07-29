from __future__ import annotations

from bs4 import BeautifulSoup
import requests
from utils import HEADERS
from typing import List, Tuple
import re
import multiprocessing as mp
import time


def get_html_from_url(url: str) -> str:
    """
    Get the html from a given url
    :return The HTML source code of the url
    """
    try:
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 200:
            return response.text
        else:
            raise requests.RequestException

    except requests.RequestException as e:
        raise requests.RequestException(f"Encounter {e} for url={url}")


class ESPCPropertyInfo:
    """
    A class that stores all important information about a property
    """

    def __init__(self, *,
                 price_type: str = "",
                 price_val: int = -1,
                 title: str = "",
                 address: str = "",
                 postcode: str = "",
                 bed_num: int = -1,
                 bath_num: int = -1,
                 couch_num: int = -1,
                 floor_area: int = -1,
                 council_tax: str = "",
                 epc: str = "",
                 url: str = ""):
        """
        Constructor
        :param price_type: Price type, such as "Offers Over"
        :param price_val: Price value
        :param title: Title of the property
        :param address: Address of the property
        :param postcode: Postcode
        :param bed_num: Number of bedrooms
        :param bath_num: Number of bathrooms
        :param couch_num: Number of couches
        :param floor_area: Total floor area
        :param council_tax: Council tax band
        :param epc: Energy rating
        :param url: url of the property
        """
        self.price_type = price_type  # type: str
        self.price_val = price_val  # type: int
        self.title = title  # type: str
        self.address = address  # type: str
        self.postcode = postcode  # type: str
        self.bed_num = bed_num  # type: int
        self.bath_num = bath_num  # type: int
        self.couch_num = couch_num  # type: int
        self.floor_area = floor_area  # type: int
        self.council_tax = council_tax  # type: str
        self.epc = epc  # type: str
        self.url = url  # type: str

    def __repr__(self) -> str:
        return f"{self.price_type}: {self.price_val} at {self.postcode}"

    @classmethod
    def init_from_url(cls, url: str) -> ESPCPropertyInfo:
        """
        Directly initialise an object from url
        :return An ESPCPropertyInfo object
        """
        html = get_html_from_url(url)
        soup = BeautifulSoup(html, 'lxml')
        # %% Get the attribute values
        price = soup.select("div.price-wrap > div.pd-price")[0].text.split('£')
        price_type = price[0].strip().lower()
        price_val = int(price[1].strip().replace(",", ""))
        title = soup.select("div.pd-title > h1")[0].text.strip().lower()
        address = soup.select("div.pd-title > .address")[0].text.strip().lower()
        postcode = re.findall(r".*(eh\d+\s*\d+[a-z]+).*", address)
        if postcode.__len__() == 0:
            print(f"############################Unable to find postcode for {url}")
            postcode = ""
        else:
            postcode = postcode[0]

        searches = soup.select("div.pd-features > div.feature")
        # Bed, bath and couch numbers
        bed_num = -1
        bath_num = -1
        couch_num = -1
        for search in searches:
            img_src = search.select("img")[0].get("src")
            num = int(search.select(".number")[0].text)
            if "bed.svg" in img_src:
                bed_num = num
            elif "bath.svg" in img_src:
                bath_num = num
            elif "couch.svg" in img_src:
                couch_num = num
            else:
                raise ValueError(f"Unknown img_src={img_src}")

        # Floor area
        floor_area = soup.select("div.pd-metric > .icon-floor_area + strong")
        if floor_area.__len__() == 0:
            floor_area = -1
        else:
            floor_area = int(re.findall(r"(\d+).*", floor_area[0].text)[0])

        # Council tax
        council_tax = soup.select("div.pd-metric > .icon-home + strong")
        if council_tax.__len__() == 0:
            council_tax = ""
        else:
            council_tax = council_tax[0].text

        # EPC
        epc = soup.select("div.pd-metric > .icon-epc + strong")
        if epc.__len__() == 0:
            epc = ""
        else:
            epc = epc[0].text

        # The url may be appended by some unknown values which directs to the same site.
        # Get rid of them because the url will be used as a unique key for search
        url = url.split("?")[0]

        obj = cls(
            price_type=price_type,
            price_val=price_val,
            title=title,
            address=address,
            postcode=postcode,
            bed_num=bed_num,
            bath_num=bath_num,
            couch_num=couch_num,
            floor_area=floor_area,
            council_tax=council_tax,
            epc=epc,
            url=url
        )

        return obj


class ESPCCrawler:
    """
    A class used to send request and parse its results from espc.com
    """

    def __init__(self, location: str, min_beds: str, max_price: str, property_type: str, use_mp: bool = True):
        """
        Constructor
        :param location: locations parameter (constraint) for url of the GET request of espc.com
        :param min_beds: minbeds parameter (constraint) for url of the GET request of espc.com
        :param max_price: maxprice parameter (constraint) for url of the GET request of espc.com
        :param property_type: ptype parameter (constraint) for url of the GET request of espc.com:
        :param use_mp: Whether to use multiple processing
        """
        self.__location = location  # type: str
        self.__min_beds = min_beds  # type: str
        self.__max_price = max_price  # type: str
        self.__property_type = property_type  # type: str
        self.__use_mp = use_mp  # type: bool
        # This is a flag for iterator
        self.__i = 1  # type: int

    def __build_espc_page_url(self, page: int) -> str:
        """
        Build the url according to the constraints for certain page.
        Note that ps=50 is set by default. This will display 50 properties per page
        :param page: The page parameter in url request
        :return: The built url
        """
        url = f"https://espc.com/properties?p={page}\
&ps=50\
&locations={self.__location}\
&minbeds={self.__min_beds}\
&maxprice={self.__max_price}\
&ptype={self.__property_type}"
        print(f"url created for page={page}: {url}")
        return url

    # TODO: 增加一个方法 such that 它可以一次给出所有url，可选mp，而不仅仅是当前页的，这个好处是可以做成action chain然后mp
    @staticmethod
    def parse_all_property_urls_from_page_html(html: str) -> List[str]:
        """
        A utility function that parses all property urls from the HTML of a page
        :param html: HTML source code of a page
        :return List of all property urls of a page
        """
        soup = BeautifulSoup(html, 'lxml')
        parse = soup.select("div.infoWrap > a")
        urls = [f"https://espc.com{url.get('href')}" for url in parse]

        return urls

    @staticmethod
    def is_valid_page(html: str) -> bool:
        """
        A utility function that checks whether the HTML indicates a valid page
        :param html: HTML source code of a page
        :return A boolean indicating whether the page is valid of not
        """
        soup = BeautifulSoup(html, 'lxml')
        parse = soup.select("div.no-results")
        if parse.__len__() == 0:
            return True

        return False

    def get_html_from_page_num(self, page: int) -> str:
        """
        Send a GET request for specific page
        :param page: The page parameter in url request
        :return: HTML source code of a page
        """
        page_url = self.__build_espc_page_url(page)

        try:
            return get_html_from_url(page_url)
        except requests.RequestException as e:
            raise f"Encounter {e} on espc.com page={page}, url={page_url}"

    def __iter__(self) -> ESPCCrawler:
        self.__i = 1
        return self

    def __next__(self) -> List[ESPCPropertyInfo]:
        """
        This allows get a list of ESPCPropertyInfo objects as on current page and increase page number
        :return A list of ESPCPropertyInfo objects shown on the current page
        """
        page = self.__i
        html = self.get_html_from_page_num(page)
        if self.is_valid_page(html):
            property_urls = self.parse_all_property_urls_from_page_html(html)

            if self.__use_mp:
                # Use multiple processing to speed up
                pool = mp.Pool(mp.cpu_count())
                all_property_infos = pool.map(ESPCPropertyInfo.init_from_url, property_urls)
                # Once all the tasks have been completed the worker processes will exit.
                pool.close()
                pool.join()
            else:
                all_property_infos = [ESPCPropertyInfo.init_from_url(url) for url in property_urls]

            self.__i += 1
            return all_property_infos
        else:
            raise StopIteration

    def __getitem__(self, args: Tuple[int, int]) -> ESPCPropertyInfo:
        """
        Get the i-th property as ESPCPropertyInfo object on a certain page
        :param args: Index for i-th property and page number in the format of (i, page)
        :return The i-th property as ESPCPropertyInfo object on a certain page
        """
        i, page = args
        i -= 1  # Array index starts from 0
        html = self.get_html_from_page_num(page)
        if self.is_valid_page(html):
            try:
                property_urls = self.parse_all_property_urls_from_page_html(html)
                property_info = ESPCPropertyInfo.init_from_url(property_urls[i])
                return property_info
            except IndexError:
                raise IndexError(f"Unable to get {i}-th property on page={page}")
        else:
            raise ValueError(f"The html is invalid for page={page}")
