from typing import Iterable

from scrapy.http import TextResponse

from locations.categories import Categories, apply_category
from locations.items import Feature
from locations.storefinders.communico import CommunicoSpider

LOCATION_URL = "https://www.akronlibrary.org/locations/{}"
# Entries which are not libraries the public can visit.
NON_LIBRARIES = {
    "3204",  # "Mobile Services": the bookmobile and outreach division, filed at the Main Library address.
    "4336",  # "Virtual Meeting Room": online meetings rather than a place.
    "4352",  # "Zoom Program": online events rather than a place.
    "4551",  # "Akron History Center": a museum run by its own non-profit, with the library as a partner.
}


class AkronSummitCountyPublicLibraryUSSpider(CommunicoSpider):
    name = "akron_summit_county_public_library_us"
    item_attributes = {"operator": "Akron-Summit County Public Library", "operator_wikidata": "Q69487248"}
    communico_client = "akronlibrary"

    def pre_process_data(self, location: dict, **kwargs) -> None:
        if (line2 := location.get("line2") or "") and line2.casefold() == (location.get("locality") or "").casefold():
            # Kenmore, Portage Lakes and Richfield repeat their city as a second address line.
            location["line2"] = ""

    def post_process_item(self, item: Feature, response: TextResponse, location: dict, **kwargs) -> Iterable[Feature]:
        if location.get("id") in NON_LIBRARIES:
            return

        # No location publishes an "about_url". Every branch page is named after
        # the branch, e.g. "Fairlawn-Bath Branch Library" at /locations/fairlawn-bath.
        slug = (item.get("name") or "").removesuffix(" Branch Library").lower().replace(" ", "-")
        item["website"] = LOCATION_URL.format(slug)

        apply_category(Categories.LIBRARY, item)

        yield item
