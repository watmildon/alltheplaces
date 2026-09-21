from typing import Iterable

from scrapy.http import TextResponse

from locations.categories import Categories, apply_category
from locations.items import Feature
from locations.storefinders.communico import CommunicoSpider

# Locations which are not library branches. Neither is listed with a branch
# code on broward.org, unlike every branch.
NON_BRANCH_LOCATIONS = {
    "2124",  # "Bienes Museum of the Modern Book": a collection inside the Main Library, sharing its address.
    "2125",  # "Broward County Law Library": the courthouse law library of the Seventeenth Judicial Circuit.
    "3416",  # "Online - Broward County Library": online services rather than a place.
}


class BrowardCountyLibraryUSSpider(CommunicoSpider):
    name = "broward_county_library_us"
    item_attributes = {"operator": "Broward County Library", "operator_wikidata": "Q4975894"}
    communico_client = "broward"

    def pre_process_data(self, location: dict, **kwargs) -> None:
        if location["id"] == "2142":
            # Lauderhill Central Park's second address line is a cross street,
            # "NE corner of Sunrise Blvd. & 441", not part of the address.
            location["line2"] = ""

    def post_process_item(self, item: Feature, response: TextResponse, location: dict, **kwargs) -> Iterable[Feature]:
        if location["id"] in NON_BRANCH_LOCATIONS:
            return

        apply_category(Categories.LIBRARY, item)

        yield item
