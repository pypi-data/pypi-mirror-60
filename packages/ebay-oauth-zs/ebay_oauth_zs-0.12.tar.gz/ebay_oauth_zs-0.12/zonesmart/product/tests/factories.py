from factory import Faker, SubFactory, fuzzy, post_generation
from factory.django import DjangoModelFactory, ImageField

from zonesmart.product.models import BaseProduct, ProductCodeType, ProductImage
from zonesmart.users.tests.factories import AdminFactory


class ProductImageFactory(DjangoModelFactory):
    image_file = ImageField(width=500, height=500, color="red")
    description = Faker("sentence")

    class Meta:
        model = ProductImage
        django_get_or_create = ["image_file"]


CODE_TYPES = ["ISBN", "UPC", "EAN"]


class ProductCodeTypeFactory(DjangoModelFactory):
    name = fuzzy.FuzzyChoice(CODE_TYPES)
    description = Faker("sentence")

    class Meta:
        model = ProductCodeType
        django_get_or_create = ["name"]


CURRENCY_CODES = ["USD", "RUB", "EUR"]


class BaseProductFactory(DjangoModelFactory):
    user = SubFactory(AdminFactory)
    main_image = SubFactory(ProductImageFactory)
    value = fuzzy.FuzzyFloat(1, 100, precision=5)
    currency = fuzzy.FuzzyChoice(CURRENCY_CODES)
    converted_from_value = fuzzy.FuzzyFloat(1, 1000, precision=3)
    converted_from_currency = fuzzy.FuzzyChoice(CURRENCY_CODES)
    sku = Faker("password")
    title = Faker("sentence")
    description = Faker("paragraph")
    quantity = fuzzy.FuzzyInteger(1, 5)
    product_id_code_type = SubFactory(ProductCodeTypeFactory)
    product_id_code = Faker("isbn13")

    @post_generation
    def extra_images(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for extra_image in extracted:
                self.extra_images.add(extra_image)

    class Meta:
        model = BaseProduct
        django_get_or_create = ["user", "title", "sku"]
