from ebay.category.models import EbayCategory
from ebay.category.tests.factories import EbayCategoryFactory

from zonesmart.tests.base import BaseViewSetTest


class EbayCategoryViewSetTest(BaseViewSetTest):
    url_path = "ebay:category:category"

    def get_ebay_category_list(self, query_params={}):
        url = self.get_url(postfix="list", query_params=query_params)
        return self.make_request(method="GET", url_path=url)

    def get_ebay_category(self, category_id):
        url = self.get_url(postfix="detail", id=category_id)
        return self.make_request(method="GET", url_path=url)

    def test_get_ebay_category_list(self):
        categories = [
            EbayCategoryFactory.create(
                category_id="lvl4_1", name="lvl4_1", level=4, is_leaf=True,
            ),
            EbayCategoryFactory.create(
                category_id="lvl5_1",
                parent_id="lvl4_1",
                level=5,
                variationsSupported=True,
                is_leaf=True,
            ),
            EbayCategoryFactory.create(
                category_id="lvl5_2",
                parent_id="lvl4_2",
                level=5,
                variationsSupported=False,
                is_leaf=False,
            ),
        ]

        query = EbayCategory.objects.all()
        self.assertEqual(len(categories), query.count())

        response = self.get_ebay_category_list()
        self.assertStatus(response)
        self.assertEqual(response.json()["count"], query.count())

        for level in [3, 4, 5]:
            response = self.get_ebay_category_list(query_params={"level": level})
            self.assertStatus(response)
            self.assertEqual(
                response.json()["count"], query.filter(level=level).count()
            )

        for variations_supported in [False, True]:
            response = self.get_ebay_category_list(
                query_params={"variations_supported": variations_supported}
            )
            self.assertStatus(response)
            self.assertEqual(
                response.json()["count"],
                query.filter(variationsSupported=variations_supported).count(),
            )

        for category_id in ["lvl3_1", "lvl4_1", "lvl5_1"]:
            response = self.get_ebay_category_list(
                query_params={"category_id": category_id}
            )
            self.assertStatus(response)
            self.assertEqual(
                response.json()["count"], query.filter(category_id=category_id).count(),
            )

    def test_get_ebay_category(self):
        category = EbayCategoryFactory.create()
        response = self.get_ebay_category(category_id=category.id)
        self.assertStatus(response)
        self.assertEqual(response.json()["id"], str(category.id))
