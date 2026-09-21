from typing import Iterable

from scrapy.http import TextResponse

from locations.categories import Categories, Extras, apply_category, apply_yes_no
from locations.items import Feature
from locations.storefinders.communico import CommunicoSpider

# Locations which are not library branches.
NON_BRANCH_LOCATIONS = {
    "435",  # "Friends of the Library": the system's fundraising charity.
    "463",  # "Mobile Services": the bookmobile fleet, based at the King Road branch.
    "1521",  # "Library in the Community": outreach held at other venues.
    "2302",  # "Online Programs": online events rather than a place.
    "2942",  # "Virtual Space": online events rather than a place.
}


class ToledoLucasCountyPublicLibraryUSSpider(CommunicoSpider):
    name = "toledo_lucas_county_public_library_us"
    item_attributes = {"operator": "Toledo-Lucas County Public Library", "operator_wikidata": "Q7814140"}
    communico_client = "toledo"

    def pre_process_data(self, location: dict, **kwargs) -> None:
        if not location.get("locality"):
            # The city is written as a second address line, leaving "locality" empty.
            location["locality"] = location.get("line2") or ""
            location["line2"] = ""

    def post_process_item(self, item: Feature, response: TextResponse, location: dict, **kwargs) -> Iterable[Feature]:
        if location["id"] in NON_BRANCH_LOCATIONS:
            return

        branch = item.pop("name")
        item["branch"] = branch.removesuffix(" Library")
        # Branches are signed and mapped as e.g. "Birmingham Branch Library".
        item["name"] = branch if branch.endswith("Library") else "{} Branch Library".format(branch)

        if website := item.get("website"):
            item["website"] = website.replace("http://", "https://", 1)

        if "wifi" in (location.get("description") or "").casefold():
            apply_yes_no(Extras.WIFI, item, True)

        apply_category(Categories.LIBRARY, item)

        yield item
