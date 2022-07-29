from ESPC import ESPCCrawler, ESPCPropertyInfo
from SIMD import SIMDCrawler, SIMDInfoVariation, SIMDInfo
import pandas as pd
from typing import List
import json


def form_dataframe_and_save_all(properties: List[ESPCPropertyInfo],
                                simds_2020: List[SIMDInfo],
                                simds_2016: List[SIMDInfo],
                                simds_2012: List[SIMDInfo]):
    print("Writing results...")
    all_info = pd.DataFrame(
        index=range(properties.__len__()),
        columns=["title", "url", "postcode", "price_val", "price_type", "epc", "council_tax", "bed_num", "floor_area",
                 "simd_2012_overall_rank_bar", "simd_2016_overall_rank_bar", "simd_2020_overall_rank_bar"],
        data="",
        dtype=str
    )
    selected_info = pd.DataFrame(
        index=[],
        columns=["title", "url", "postcode", "price_val", "price_type", "epc", "council_tax", "bed_num", "floor_area",
                 "simd_2012_overall_rank_bar", "simd_2016_overall_rank_bar", "simd_2020_overall_rank_bar"],
        data="",
        dtype=str
    )

    for i, (property_info, simd_2020, simd_2016, simd_2012) in \
            enumerate(zip(properties, simds_2020, simds_2016, simds_2012)):
        row = {
            "title": property_info.title,
            "url": property_info.url,
            "postcode": property_info.postcode,
            "price_val": property_info.price_val,
            "price_type": property_info.price_type,
            "epc": property_info.epc,
            "council_tax": property_info.council_tax,
            "bed_num": property_info.bed_num,
            "floor_area": property_info.floor_area,

            "simd_2012_overall_rank_bar": simd_2012.overall_rank_bar,
            "simd_2016_overall_rank_bar": simd_2016.overall_rank_bar,
            "simd_2020_overall_rank_bar": simd_2020.overall_rank_bar,
        }

        for key, value in row.items():
            all_info.loc[i, key] = value

        if (min([simd_2012.overall_rank_bar, simd_2016.overall_rank_bar, simd_2020.overall_rank_bar]) >= 7) and \
                (not (int(property_info.price_val) > 180000 and "fixed" not in property_info.price_type)) and \
                (property_info.epc not in {"E", "D"}) and \
                (int(simd_2012.overall_rank_bar) <= int(simd_2016.overall_rank_bar) <= int(simd_2020.overall_rank_bar)):
            selected_info = pd.concat([selected_info, pd.DataFrame(index=[i], data=row)])

    all_info.to_csv("./all_info.csv")
    selected_info.to_csv("./selected_info.csv")


def simd_crawler_search(simd_crawler, postcode, version):
    simd_crawler.update_version(version)
    print(f"Adding SIMD {simd_crawler.version}")
    simd = simd_crawler.clear_and_search(postcode)
    return simd


def main():
    espc_crawler = ESPCCrawler("edinburgh", "1plus", "210000", "flat,house", use_mp=True)
    properties = []
    simds_2020, simds_2016, simds_2012 = [], [], []
    urls = set()  # Avoid duplication due to advertisement
    url_with_error = []
    try:
        simd_crawler = SIMDCrawler(use_headless=True, version=2020)
        for page, property_infos in enumerate(espc_crawler):
            print(f"Start on page={page + 1}")
            for property_info in property_infos:
                if property_info.url in urls:
                    continue
                else:
                    urls.add(property_info.url)

                try:
                    print(f"Getting results for property url={property_info.url}")
                    postcode = property_info.postcode
                    print(f"postcode = {postcode}")

                    simd_2020 = simd_crawler_search(simd_crawler, postcode, 2020)
                    simd_2016 = simd_crawler_search(simd_crawler, postcode, 2016)
                    simd_2012 = simd_crawler_search(simd_crawler, postcode, 2012)
                    # Append
                except Exception as e:
                    url_with_error.append(property_info.url)
                    # Save temp results
                    url_with_error_json = json.dumps(url_with_error)
                    with open('unresolved.json', 'w') as f:
                        json.dump(url_with_error_json, f)
                    form_dataframe_and_save_all(properties, simds_2020, simds_2016, simds_2012)

                    print("############################ERROR HAPPEN############################")
                    print(e)
                    continue
                finally:
                    pass

                properties.append(property_info)
                simds_2020.append(simd_2020)
                simds_2016.append(simd_2016)
                simds_2012.append(simd_2012)

    finally:
        url_with_error_json = json.dumps(url_with_error)
        with open('unresolved.json', 'w') as f:
            json.dump(url_with_error_json, f)
        form_dataframe_and_save_all(properties, simds_2020, simds_2016, simds_2012)


if __name__ == "__main__":
    main()
