from typing import Optional, Tuple

from django.db.models.query import QuerySet

from ebay.category.helpers import (
    get_category_aspects,
    get_properties,
    get_property_values,
)
from ebay.category.models import EbayCategory
from ebay.listing.models import EbayListing
from rest_framework.exceptions import ValidationError

from zonesmart.marketplace.models import Channel


class Validator:
    """
    Base validator class for custom validation.
    """

    def __init__(self):
        self.errors = list()
        self.break_validation = False

    def validate(self) -> Optional[list]:
        """
        Gets all validate methods and executes all until break_validation is False.
        :returns Errors from each validation.
        """
        # Get validators (cls methods)
        validators = [
            method
            for method in dir(self.__class__)
            if callable(getattr(self.__class__, method))
            and method.startswith("validate_")
        ]
        # Call each validator (cls method)
        for validator in validators:
            if not self.break_validation:
                method = getattr(self.__class__, validator)
                method(self)
            else:
                break
        # Return errors
        return self.errors


class EbayAspectValueValidator(Validator):
    def __init__(self, applicable_aspects: dict, validate_cardinality: bool = False):
        super().__init__()
        self.applicable_aspects = applicable_aspects
        self.validate_cardinality = validate_cardinality
        self.aspect_msg_name = (
            "Аспект листинга" if self.validate_cardinality else "Спецификация продукта"
        )
        self.formatted_aspects = self.get_formatted_aspects()

    def get_formatted_aspects(self):
        raise NotImplementedError("get_formatted_aspects() method is not implemented!")

    def validate_applicable_values(self):  # noqa: C901
        not_applicable_aspects_values = dict()
        cardinality_names = list()
        for name, values in self.formatted_aspects.items():
            # Check only if name in applicable aspects.
            if name in self.applicable_aspects:
                constraint: dict = self.applicable_aspects[name]["aspectConstraint"]
                mode: str = constraint["aspectMode"]
                # Validate cardinality
                if self.validate_cardinality:
                    cardinality: str = constraint["itemToAspectCardinality"]
                    # Check if only SINGLE value can be passed into the aspect,
                    # but multiply values passed.
                    if cardinality == "SINGLE" and len(values) > 1:
                        cardinality_names.append(name)
                        continue
                # Check only if mode is not FREE_TEXT.
                if mode != "FREE_TEXT":
                    applicable_values = self.applicable_aspects[name]["aspectValues"]
                    not_applicable_values = list()
                    # Parse not applicable values
                    for value in values:
                        if value not in applicable_values:
                            not_applicable_values.append(value)
                    # If not applicable values exists,
                    # then create dict with applicable & not applicable values
                    if not_applicable_values:
                        data = {
                            "not_applicable": set(not_applicable_values),
                            "applicable": applicable_values,
                        }
                        not_applicable_aspects_values[name] = data
        # If not applicable values exists append errors.
        if not_applicable_aspects_values:
            self.errors.append(
                *[
                    f'{self.aspect_msg_name} "{name}" содержит неподдерживаемые значения: '
                    f'{", ".join(not_applicable_data["not_applicable"])}. '
                    f'Поддерживаемые значения: {", ".join(not_applicable_data["applicable"])}'
                    for name, not_applicable_data in not_applicable_aspects_values.items()
                ]
            )
        if self.validate_cardinality:
            if cardinality_names:
                for name in cardinality_names:
                    self.errors.append(
                        f'{self.aspect_msg_name} "{name}" не может принимать несколько значений. '
                        f"Пожалуйста, выберите одно."
                    )


class EbayProductSpecificationsValidator(EbayAspectValueValidator):
    """
    Ebay product specifications validator.
    """

    def __init__(
        self,
        required_specification_names: list,
        applicable_aspects: dict,
        specifications_list: list = None,
    ):
        self.required_specification_names = required_specification_names
        self.specifications_list = specifications_list
        super().__init__(applicable_aspects=applicable_aspects)

    def get_formatted_aspects(self):
        name_and_values_summary = dict()
        for specifications in self.specifications_list:
            for s in specifications:
                name = s["name"]
                value = s["value"]
                if name not in name_and_values_summary:
                    name_and_values_summary[name] = [value]
                else:
                    name_and_values_summary[name].append(value)
        return name_and_values_summary

    def validate_is_names_are_the_same(self):
        """
        Validates specifications for names that they are the same.
        """
        names = [specification["name"] for specification in self.specifications_list[0]]
        names_len = len(names)
        for specification in self.specifications_list[1:]:
            if len(specification) == names_len and all(
                data["name"] in names for data in specification
            ):
                continue
            else:
                self.errors.append(
                    "Имена спецификаций не совпадают с именами друг друга."
                )
                break

    def validate_required_specification_names(self):
        """
        Validates specifications for required specification names.
        """
        if self.required_specification_names:
            for specification in self.specifications_list:
                if all(
                    required_name in [data["name"] for data in specification]
                    for required_name in self.required_specification_names
                ):
                    continue
                else:
                    self.errors.append(
                        f"Спецификации должны содержать обязательные значения: "
                        f'{", ".join(self.required_specification_names)}.'
                    )
                    break

    def validate_unique_values(self):
        """
        Validates unique variation values.
        """
        variations = [
            tuple(sorted(tuple(s.values()) for s in specification))
            for specification in self.specifications_list
        ]
        if len(variations) != len(set(variations)):
            self.errors.append(
                "Спецификации должны содержать уникальные значения и отличаться хотябы по одному значению."
            )
            self.break_validation = True


class EbayProductsValidator(Validator):
    """
    Ebay products validator.
    """

    def __init__(
        self,
        products: list,
        required_specification_names: list,
        applicable_aspects: dict,
        product_qs: QuerySet = None,
    ):
        super().__init__()
        self.products = products
        self.specifications_list = self.__get_specifications_list()
        self.required_specification_names = required_specification_names
        self.applicable_aspects = applicable_aspects
        self.product_qs = product_qs

    def __get_specifications_list(self) -> list:
        """
        Parses products for specification blocks list.
        :returns: Product specifications list.
        """
        return [product.get("specifications", None) for product in self.products]

    def validate_products_count(self):
        """
        Validates product count.
        """
        if len(self.products) < 1:
            action = "обновить" if self.product_qs else "создать"
            self.errors.append(f"Вы не можете {action} листинг без продуктов.")
            self.break_validation = True

    def validate_products_sku_duplicate(self):
        sku_list = list(product["sku"] for product in self.products)
        if len(sku_list) != len(set(sku_list)):
            self.errors.append({"sku": "SKU продукта должен быть уникальным."})
            self.break_validation = True

    def validate_specifications(self) -> None:
        """
        Validates specifications.
        """
        if len(self.products) > 1 and not all(self.specifications_list):
            self.errors.append(
                "Для множества продуктов обязательно должны быть указаны спецификации."
            )
            self.break_validation = True
        else:
            specifications_validator = EbayProductSpecificationsValidator(
                specifications_list=self.specifications_list,
                required_specification_names=self.required_specification_names,
                applicable_aspects=self.applicable_aspects,
            )
            specifications_errors = specifications_validator.validate()
            if specifications_errors:
                self.errors.append({"specifications": specifications_errors})


class EbayCategoryValidator(Validator):
    """
    Ebay category validator.
    """

    def __init__(
        self, category: EbayCategory, product_count: int, compatibilities_exists: bool
    ):
        super().__init__()
        self.category = category
        self.product_count = product_count
        self.compatibilities_exists = compatibilities_exists

    def validate_variation_supported(self) -> None:
        """
        Validates that's category is variation supported or not.
        If multiple product is specified, but category is not variation supported, adds an error.
        """
        if self.product_count > 1 and not self.category.variationsSupported:
            self.errors.append(
                {
                    "category": (
                        "Вы не можете создать группу товаров с категорией, которая не поддерживает вариации. "
                        "Пожалуйста, выберите категорию, которая поддерживает вариации."
                    )
                }
            )

    def validate_variation_supported_by_transport(self):
        """
        Validates that's category is transport supported and appends an error if variations exists.
        For now, variation supported transport categories is not working by eBay and disabled for a while
        in the out system.
        """
        if (
            self.product_count > 1
            and self.category.variationsSupported
            and self.category.transportSupported
        ):
            self.errors.append(
                {
                    "category": (
                        "Вы не можете создать группу товаров с категорей, которая поддерживает транспорт, "
                        "так как на текущий момент создание группы продуктов с транспортной категорией "
                        "не поддерживается системой eBay."
                    )
                }
            )

    def validate_transport_supported(self) -> None:
        """
        Validates that's category is transport supported or not.
        If compatibilities is exists, but category is not transport supported, adds an error.
        """
        if self.compatibilities_exists and not self.category.transportSupported:
            self.errors.append(
                {
                    "category": (
                        "Вы не можете указать совместимости деталей для продуктов с выбранной категорией, "
                        "так как она не поддерживает возможность указать совместимости деталей для транспорта. "
                        "Пожалуйста, выберите категорию, которая предоставляет возможность указать "
                        "совместимости деталей для транспорта."
                    )
                }
            )


class EbayListingAspectsValidator(EbayAspectValueValidator):
    """
    Ebay listing aspects validator.
    """

    def __init__(
        self, aspects: list, applicable_aspects: dict, required_aspect_names: list
    ):
        self.aspects = aspects
        self.required_aspect_names = required_aspect_names
        super().__init__(
            applicable_aspects=applicable_aspects, validate_cardinality=True
        )

    def get_formatted_aspects(self):
        """
        Parses aspects into human-readable and validation comfortable data.
        :returns: human-readable and comfortable for validation data
        """
        formatted_aspects = dict()
        for aspect in self.aspects:
            name = aspect["name"]
            value = aspect["value"]
            if name not in formatted_aspects:
                formatted_aspects[name] = [value]
            else:
                formatted_aspects[name].append(value)
        return formatted_aspects

    def validate_required_aspects(self):
        """
        Validates listing aspects for required names.
        """
        missed_aspects = list()
        # Collect list of missed aspect names
        for name in self.required_aspect_names:
            if name not in self.formatted_aspects:
                missed_aspects.append(name)
        # Append error if missed aspects is not empty list
        if missed_aspects:
            self.errors.append(
                {
                    "required": (
                        f"Необходимо указать обязательные аспекты листинга: "
                        f'{", ".join(self.required_aspect_names)}.'
                    )
                }
            )


class EbayCompatibilitiesValidator(Validator):
    def __init__(self, category: EbayCategory, compatibilities: list):
        super().__init__()
        self.category = category
        self.compatibilities = compatibilities
        is_success, message, property_list = get_properties(category)
        if is_success:
            self.property_list = property_list
            self.applicable_property_names = [p["name"] for p in self.property_list]
        else:
            self.errors.append(
                {"remote_api": f"Произошла ошибка на стороне eBay: {message}"}
            )
            self.break_validation = True

    def validate_values(self):
        # TODO: finish validation logic
        is_success, message, values = get_property_values(
            self.category, "Year", "Year:2019,Make:Honda"
        )
        self.errors.append(self.applicable_property_names)
        self.errors.append(values)


class EbayListingValidator(Validator):
    """
    Ebay listing validator.
    """

    def __init__(
        self,
        category: EbayCategory,
        channel: Channel = None,
        aspects: list = None,
        products: list = None,
        compatibilities: list = None,
        instance: EbayListing = None,
        **kwargs,
    ):
        super().__init__()
        # Initialize required fields
        self.category = category
        self.channel = channel
        # Raise an error if channel is not specified for transportSupported category
        if self.category.transportSupported:
            assert self.channel, (
                "You should specify channel for transport supported category. "
                "Transport supported category requires an extra api call to retrieve data from Trading API "
                "with information about each aspect (aspectEnabledForVariations)."
            )
        # Get raw aspects data for category
        category_aspects_kwargs = {"category": category}
        if category.transportSupported:
            category_aspects_kwargs[
                "marketplace_user_account"
            ] = channel.marketplace_user_account
        success, message, self.raw_aspects_data = get_category_aspects(
            **category_aspects_kwargs
        )
        # Raise ValidationError if aspects retrieve call was unsuccessful
        if not success:
            raise ValidationError(detail={"category": message}, code="internal")
        # Initialize additional required fields
        self.products = products
        self.aspects = aspects
        self.compatibilities = compatibilities
        # Initialize instance
        self.instance = instance
        # Get formatted applicable aspects data from raw data
        self.applicable_aspects = self.__get_applicable_aspects()
        # Get required aspect for listing & products
        required_aspect_names = self.__get_required_aspects_names()
        (
            self.required_listing_aspect_names,
            self.required_product_specification_names,
        ) = required_aspect_names

    def __get_applicable_aspects(self) -> dict:
        """
        Parses raw aspects data into the human-readable and comfortable for check dictionary.
        :returns: applicable aspects for category in human-readable and comfortable for check dictionary.
        """
        return {
            aspect["localizedAspectName"]: {
                **aspect,
                "aspectValues": [
                    value["localizedValue"] for value in aspect["aspectValues"]
                ]
                if "aspectValues" in aspect
                else None,
            }
            for aspect in self.raw_aspects_data
        }

    def __get_required_aspects_names(self) -> Tuple[list, list]:
        """
        Parses applicable aspects for required aspects.
        :return: tuple with listing & product required aspect names.
        """
        required_listing_aspect_names = list()
        required_product_aspect_names = list()
        for name, data in self.applicable_aspects.items():
            constraint = data["aspectConstraint"]
            required = constraint["aspectRequired"]
            if required:
                if constraint["aspectEnabledForVariations"]:
                    required_product_aspect_names.append(name)
                else:
                    required_listing_aspect_names.append(name)
        return required_listing_aspect_names, required_product_aspect_names

    def validate_category(self) -> None:
        """
        Validates category.
        """
        # Calculate products count
        product_count = len(self.products) if self.products else 0
        # Append products count from db if listing instance is exists
        if self.instance:
            product_count += self.instance.products.count()
        # Init validator
        compatibilities_exists = True if self.compatibilities else False
        validator = EbayCategoryValidator(
            category=self.category,
            product_count=product_count,
            compatibilities_exists=compatibilities_exists,
        )
        # Get errors and append, if exists
        errors = validator.validate()
        if errors:
            self.errors.append({"category": errors})
            self.break_validation = True

    def validate_listing_aspects(self) -> None:
        """
        Validates listing aspects.
        """
        if self.aspects:
            validator = EbayListingAspectsValidator(
                aspects=self.aspects,
                applicable_aspects=self.applicable_aspects,
                required_aspect_names=self.required_listing_aspect_names,
            )
            errors = validator.validate()
            if errors:
                self.errors.append({"aspects": errors})

    def validate_products(self) -> None:
        """
        Validates products.
        """
        if self.products:
            kwargs = {
                "products": self.products,
                "required_specification_names": self.required_product_specification_names,
                "applicable_aspects": self.applicable_aspects,
            }
            if self.instance:
                kwargs.update({"product_qs": self.instance.products.all()})
            validator = EbayProductsValidator(**kwargs)
            errors = validator.validate()
            if errors:
                self.errors.append({"products": errors})
                self.break_validation = True

    def validate_compatibilities(self):
        if self.compatibilities:
            validator = EbayCompatibilitiesValidator(
                category=self.category, compatibilities=self.compatibilities
            )
            errors = validator.validate()
            if errors:
                self.errors.append({"compatibilities": errors})
