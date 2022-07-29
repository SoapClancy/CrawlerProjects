import time

import pandas as pd
from selenium import webdriver
import getpass
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait as WAIT
from typing import Tuple, List


class SIMDInfo:
    def __init__(self, *,
                 data_zone_id: str = "",
                 data_zone_name: str = "",
                 postcode: str = "",
                 overall_rank: int = -1,
                 overall_rank_bar: int = -1,
                 income_rank: int = -1,
                 income_rank_bar: int = -1,
                 employment_rank: int = - 1,
                 employment_rank_bar: int = -1,
                 health_rank: int = -1,
                 health_rank_bar: int = -1,
                 edu_rank: int = -1,
                 edu_rank_bar: int = -1,
                 housing_rank: int = -1,
                 housing_rank_bar: int = -1,
                 geo_access_rank: int = -1,
                 geo_access_rank_bar: int = -1,
                 crime_rank: int = - 1,
                 crime_rank_bar: int = -1,
                 version: int):
        """
        Constructor
        :param data_zone_id: id of data zone as defined by simd.scot. e.g., S01008616
        :param data_zone_name: Name of the data zone. e.g.,
        :param postcode: Post code of the location
        :param overall_rank: The number of overall rank, e.g., 6843
        :param overall_rank_bar: The bar indicator of overall rank, e.g., 10
        :param income_rank: The number of income domain rank, e.g., 6530 (take int for float, e.g., 6530.5)
        :param income_rank_bar: The bar indicator of income domain rank, e.g., 10
        :param employment_rank: The number of employment domain rank, e.g., 6960
        :param employment_rank_bar: The bar indicator of employment domain rank, e.g., 10
        :param health_rank: The number of health domain rank, e.g., 6969
        :param health_rank_bar: The bar indicator of heath domain rank, e.g., 10
        :param edu_rank: The number of education/skill domain rank, e.g., 5944
        :param edu_rank_bar: The bar indicator of education/skill domain rank, e.g., 9
        :param housing_rank: The number of housing domain rank, e.g., 106
        :param housing_rank_bar: The bar indicator of housing domain rank, e.g., 1
        :param geo_access_rank: The number of geographic access domain rank, e.g., 6819
        :param geo_access_rank_bar: The bar indicator of geographic access domain rank, e.g., 10
        :param crime_rank: The number of crime rank, e.g., 5540
        :param crime_rank_bar: The bar indicator of crime rank, e.g., 8
        :param version: Year of the database, e.g., 2020
        """
        self.data_zone_id = data_zone_id  # type: str
        self.data_zone_name = data_zone_name  # type: str
        self.postcode = postcode  # type: str
        self.overall_rank = overall_rank  # type: int
        self.overall_rank_bar = overall_rank_bar  # type: int
        self.income_rank = income_rank  # type: int
        self.income_rank_bar = income_rank_bar  # type: int
        self.employment_rank = employment_rank  # type: int
        self.employment_rank_bar = employment_rank_bar  # type: int
        self.health_rank = health_rank  # type: int
        self.health_rank_bar = health_rank_bar  # type: int
        self.edu_rank = edu_rank  # type: int
        self.edu_rank_bar = edu_rank_bar  # type: int
        self.housing_rank = housing_rank  # type: int
        self.housing_rank_bar = housing_rank_bar  # type: int
        self.geo_access_rank = geo_access_rank  # type: int
        self.geo_access_rank_bar = geo_access_rank_bar  # type: int
        self.crime_rank = crime_rank  # type: int
        self.crime_rank_bar = crime_rank_bar  # type: int
        self.version = version  # type: int

    def __repr__(self) -> str:
        return f"Year={self.version} SIMD at {self.data_zone_name}, {self.postcode}"


class SIMDInfoVariation:
    """
    This class depends on list of SIMDInfo objects (from different year at the same postcode) and
    calculates the changes of different rank domains
    """

    def __init__(self, postcode: str):
        """
        Constructor
        :param postcode: Post code
        """
        self.postcode = postcode  # type: str

    def __repr__(self) -> str:
        return f"SMID changes at postcode={self.postcode}"

    def cal_variations(self, simd_infos: List[SIMDInfo]) -> pd.DataFrame:
        """
        This functions analyses a list of SIMDInfo objects (different years, the same postcode) and computes the changes
        :return A pd.DataFrame object representing the changes
        """
        # No need to calculate the changes in version, data_zone_id and data_zone_name
        not_interested_fields = {"version", "data_zone_id", "data_zone_name"}
        # Initialise a pd.DataFrame object
        data = pd.DataFrame(
            index=[f"{simd_infos[i].version}-{simd_infos[i + 1].version}" for i in range(simd_infos.__len__() - 1)],
            columns=[x for x in simd_infos[0].__dict__ if x not in not_interested_fields]
        )
        # TODO
        for i in range(simd_infos.__len__() - 1):
            prev_simd_info, now_simd_info = simd_infos[i], simd_infos[i + 1]
            assert prev_simd_info.postcode == now_simd_info.postcode == self.postcode
            for field in now_simd_info.__dict__:
                if field in not_interested_fields:
                    continue

                change = (now_simd_info.__getattribute__(field) - prev_simd_info.__getattribute__(field))  # type: int
                tt = 1


class SIMDCrawler:
    """
    A class used to send request and parse its results from simd.scot
    """

    def __init__(self,
                 executable_path: str = None,
                 browser_name: str = "edge",
                 use_headless: bool = True,
                 initial_window_size: Tuple[int, int] = (1920, 1080), *,
                 version: int):
        """
        Constructor
        :param executable_path: Path to the executable
        :param browser_name: Name of the browser, currently only supports "edge"
        :param use_headless: Whether to use headless mode
        :param initial_window_size: The initial size of browser window to be set
        :param version: Representing year of the database
        """
        assert browser_name in {"edge", "chrome"}
        executable_path = executable_path or rf"C:\Users\{getpass.getuser()}\EdgeWebDriver\msedgedriver.exe"

        if browser_name == "edge":
            if use_headless:
                from msedge.selenium_tools import Edge
                from msedge.selenium_tools import EdgeOptions
                options = EdgeOptions()
                options.use_chromium = True
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')

                self.browser = Edge(executable_path=executable_path, options=options)
            else:
                self.browser = webdriver.Edge(executable_path=executable_path)
        else:
            raise NotImplementedError(f"Not implemented for {browser_name}")

        self.initial_window_size = initial_window_size  # type: Tuple[int, int]
        self.version = version  # type: int

    def __repr__(self) -> str:
        return f"Year={self.version} SIMD crawler"

    def update_version(self, version: int) -> None:
        """
        Setter for version field
        :param version: Representing year of the database
        """
        self.version = version

    def __get_index_url(self) -> str:
        """
        The main url of simd.scot. Should be parameterized by year
        :return the parameterized url
        """
        index_url = f"https://simd.scot/#/simd{self.version}/BTTTFTT/14/-3.2023/55.9450/"
        return index_url

    def __clear(self) -> None:
        """
        Click the "Clear selected data" button
        """
        wait_driver = WAIT(self.browser, 10)
        button = wait_driver.until(EC.presence_of_element_located((By.ID, "clearSelectedDataButton")))
        if "disabled" not in button.get_attribute("class"):
            button.click()

    def __get_inner_size(self) -> Tuple[int, int]:
        """
        Get the page content size, not the window size
        :return: Inner size
        """
        inner_width = self.browser.execute_script("return window.innerWidth")
        inner_height = self.browser.execute_script("return window.innerHeight")

        return inner_width, inner_height

    def __move_mouse_to_center_then_click(self) -> ActionChains:
        """
        Move mouse to center then click
        :return ActionChains object that can execute
        """
        action = ActionChains(self.browser).move_by_offset(self.__get_inner_size()[0] // 2,
                                                           self.__get_inner_size()[1] // 2).click()

        return action

    def __move_mouse_to_origin(self) -> ActionChains:
        """
        Move mouse to origin
        (Supposing no window size change or mouse movement after calling __move_mouse_from_origin_to_center)
        :return ActionChains object that can execute
        """
        action = ActionChains(self.browser).move_to_location(0, 0)

        return action

    def __start_search(self, postcode: str) -> None:
        """
        Fill the post code, then click the "Go" button
        :param postcode: Post code of the research
        """
        wait_driver = WAIT(self.browser, 10)
        # Fill the postcode
        postcode_box = wait_driver.until(EC.presence_of_element_located((By.ID, "postcode")))
        postcode_box.clear()
        postcode_box.send_keys(postcode)

        # Search
        go_button = wait_driver.until(EC.presence_of_element_located((By.ID, "postcodeButton")))
        go_button.click()

        self.__move_mouse_to_origin().perform()
        # Move mouse to the center and click
        self.__move_mouse_to_center_then_click().perform()

    def __read_results(self, postcode: str) -> SIMDInfo:
        """
        Read the results from the current window
        :param postcode: Post code of the research
        :return A search result representing by a SIMDInfo object
        """
        # wait_driver = WAIT(self.browser, 10)
        # data_zone_id = wait_driver.until(EC.visibility_of_element_located())
        data_zone_id = self.browser.find_element(By.ID, "datazoneid").text.strip().lower()

        # data_zone_name = wait_driver.until(EC.visibility_of_element_located((By.ID, "igname")))
        data_zone_name = self.browser.find_element(By.ID, "igname").text.strip().lower()

        overall_rank = -1
        overall_rank_bar = -1
        income_rank = -1
        income_rank_bar = -1
        employment_rank = -1
        employment_rank_bar = -1
        health_rank = -1
        health_rank_bar = -1
        edu_rank = -1
        edu_rank_bar = -1
        housing_rank = -1
        housing_rank_bar = -1
        geo_access_rank = -1
        geo_access_rank_bar = -1
        crime_rank = -1
        crime_rank_bar = -1

        for element in self.browser.find_elements(By.CSS_SELECTOR, "#componenttable > tbody > tr"):
            component_caption = element.find_element(By.CSS_SELECTOR, ".componentcaption").text.split(":")
            domain_name = component_caption[0].strip().lower()
            domain_rank = int(float(component_caption[1]))
            rank_bar = int(element.find_element(By.CSS_SELECTOR, ".componentcaption + div").text.strip())

            if "overall" in domain_name:
                overall_rank = domain_rank
                overall_rank_bar = rank_bar
            elif "income" in domain_name:
                income_rank = domain_rank
                income_rank_bar = rank_bar
            elif "employment" in domain_name:
                employment_rank = domain_rank
                employment_rank_bar = rank_bar
            elif "health" in domain_name:
                health_rank = domain_rank
                health_rank_bar = rank_bar
            elif "education" in domain_name:
                edu_rank = domain_rank
                edu_rank_bar = rank_bar
            elif "housing" in domain_name:
                housing_rank = domain_rank
                housing_rank_bar = rank_bar
            elif "geographic" in domain_name:
                geo_access_rank = domain_rank
                geo_access_rank_bar = rank_bar
            elif "crime" in domain_name:
                crime_rank = domain_rank
                crime_rank_bar = rank_bar
            else:
                raise RuntimeError(f"Unknown domain_name={domain_name}")

        simd_info = SIMDInfo(
            data_zone_id=data_zone_id,
            data_zone_name=data_zone_name,
            postcode=postcode,
            overall_rank=overall_rank,
            overall_rank_bar=overall_rank_bar,
            income_rank=income_rank,
            income_rank_bar=income_rank_bar,
            employment_rank=employment_rank,
            employment_rank_bar=employment_rank_bar,
            health_rank=health_rank,
            health_rank_bar=health_rank_bar,
            edu_rank=edu_rank,
            edu_rank_bar=edu_rank_bar,
            housing_rank=housing_rank,
            housing_rank_bar=housing_rank_bar,
            geo_access_rank=geo_access_rank,
            geo_access_rank_bar=geo_access_rank_bar,
            crime_rank=crime_rank,
            crime_rank_bar=crime_rank_bar,
            version=self.version
        )

        return simd_info

    def clear_and_search(self, postcode: str, retry=1) -> SIMDInfo:
        """
        Search by postcode
        :param postcode: Post code of the research
        :param retry
        :return: A SIMDInfo at the location of postcode
        """
        try:
            # Get request
            self.browser.get(self.__get_index_url())
            self.browser.set_window_size(*self.initial_window_size)
            self.browser.refresh()

            self.__clear()
            self.__start_search(postcode)
            time.sleep(retry // 3 + 0.1)
            simd_info = self.__read_results(postcode)

            return simd_info
        except:
            if retry > 10:
                raise Exception("Maximum retry encounter in clear_and_search")

            return self.clear_and_search(postcode, retry + 1)
