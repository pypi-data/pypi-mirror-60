from factory import SubFactory

from zonesmart.marketplace.tests import factories


class AmazonMarketplaceFactory(factories.MarketplaceFactory):
    name = "Amazon America"
    unique_name = "amazon_north_america"


class AmazonDomainFactory(factories.DomainFactory):
    name = "US Amazon"
    code = "ATVPDKIKX0DER"
    marketplace = SubFactory(AmazonMarketplaceFactory)


class AmazonMarketplaceUserAccountFactory(factories.MarketplaceUserAccountFactory):
    marketplace = SubFactory(AmazonMarketplaceFactory)


class AmazonChannelFactory(factories.ChannelFactory):
    name = "American Amazon"
    marketplace_user_account = SubFactory(AmazonMarketplaceUserAccountFactory)
    domain = SubFactory(AmazonDomainFactory)
