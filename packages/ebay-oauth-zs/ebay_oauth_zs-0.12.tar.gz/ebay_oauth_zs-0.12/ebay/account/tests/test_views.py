from ebay.tests.base import EbayViewSetTest

# from ebay.account.models import EbayUserRateLimits
# from rest_framework import status


class EbayUserRateLimitsViewSetTest(EbayViewSetTest):
    url_path = "ebay:account:user_rate_limits"

    def get_ebay_user_rate_limits_list(self):
        url = self.get_url(postfix="list")
        return self.make_request(method="GET", url_path=url)

    def get_ebay_user_rate_limits(self, rate_limits_id):
        url = self.get_url(id=rate_limits_id)
        return self.make_request(method="GET", url_path=url)

    def download_ebay_user_rate_limits_list(self):
        url = self.get_url(
            postfix="remote_download_list",
            marketplace_user_account_id=self.marketplace_user_account.id,
        )
        return self.make_request(method="GET", url_path=url)

    # def test_download_ebay_user_rate_limits_list(self):
    #     response = self.download_ebay_user_rate_limits_list()
    #     self.assertStatus(response, status=status.HTTP_201_CREATED)

    # def test_get_ebay_user_rate_limits_list(self):
    #     self.download_ebay_user_rate_limits_list()
    #     response = self.get_ebay_user_rate_limits_list()
    #     self.assertStatus(response)

    # def test_get_ebay_user_rate_limits(self):
    #     self.download_ebay_user_rate_limits_list()
    #     rate_limits_id = EbayUserRateLimits.objects.first().id
    #     response = self.get_ebay_user_rate_limits(rate_limits_id)
    #     self.assertStatus(response)
