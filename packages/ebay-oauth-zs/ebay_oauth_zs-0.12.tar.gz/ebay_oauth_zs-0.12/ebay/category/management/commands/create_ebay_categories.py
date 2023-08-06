from django.core.management.base import BaseCommand

from ebay.category.actions.category import RemoteDownloadEbayCategories
from ebay.category.actions.category_tree import (
    RemoteDownloadEbayDefaultCategoryTreeList,
)
from ebay.category.actions.transport import MarkCompatibilitySupportedCategories
from ebay.category.actions.variations import MarkVariationsSupportedCategories

from zonesmart.utils.logger import get_logger

logger = get_logger(__name__)


class Command(BaseCommand):
    help = "Создание категорий товаров eBay"

    def add_arguments(self, parser):
        parser.add_argument(
            "--domain_codes",
            nargs="*",
            required=False,
            help="список доменов eBay, для которых будут создаваться категории",
        )

    def handle(self, **options):
        domain_codes = options.get("domain_codes", [])
        logger.info("Загрузка деревьев категорий")
        RemoteDownloadEbayDefaultCategoryTreeList()(domain_codes=domain_codes)
        logger.info("Загрузка категорий")
        RemoteDownloadEbayCategories()()
        logger.info("Заполнения поля variationSupported")
        MarkVariationsSupportedCategories()()
        logger.info("Заполнения поля transportSupported")
        MarkCompatibilitySupportedCategories()()
