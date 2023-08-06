from django.core.management.base import BaseCommand

from amazon.category.actions import RemoteDownloadAmazonCategories

from zonesmart.marketplace.models import Domain
from zonesmart.utils.logger import get_logger

logger = get_logger(__name__)


class Command(BaseCommand):
    help = "Создание категорий товаров Amazon"

    def add_arguments(self, parser):
        parser.add_argument(
            "domain_name", help="Домен Amazon, категории которого будут загружены."
        )

    def handle(self, **options):
        domain_name = options.get("domain_name", None)
        report_id = options.get("report_id", "17760746651018226")

        action = RemoteDownloadAmazonCategories()
        try:
            domain_code = Domain.objects.get(name=domain_name).code
        except Domain.DoesNotExist as error:
            logger.error(str(error))
            raise ValueError(f'Домен с названием "{domain_name}" не найден.')
        action(domain_code=domain_code, report_id=report_id)
