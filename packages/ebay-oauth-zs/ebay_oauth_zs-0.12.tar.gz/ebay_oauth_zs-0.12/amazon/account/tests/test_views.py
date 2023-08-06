# from amazon.data.enums import MarketplaceEnum

# from zonesmart.tests.base import BaseViewSetTest


# class AmazonAccountTest(BaseViewSetTest):
#     url_path = 'amazon:account:available_marketplaces'
#
#     def get_available_marketplaces(self):
#         url = self.get_url(postfix='list')
#         return self.make_request(method='GET', url_path=url)
#
#     def test_get_available_marketplaces(self):
#         response = self.get_available_marketplaces()
#         self.assertStatus(response)
#
#         marketplace_ids = response.json()['marketplace_ids']
#         self.assertNotEqual(len(marketplace_ids), 0)
#
#         all_marketplace_ids = [pair[0] for pair in MarketplaceEnum]
#         for marketplace_id in marketplace_ids:
#             self.assertIn(marketplace_id, all_marketplace_ids)
