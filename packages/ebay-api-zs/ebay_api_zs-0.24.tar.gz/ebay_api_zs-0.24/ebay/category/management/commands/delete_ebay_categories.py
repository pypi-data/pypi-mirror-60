from django.core.management.base import BaseCommand

from ebay.category.models import EbayCategoryTree


class Command(BaseCommand):

    help = "Удаление категорий товаров eBay"

    def add_arguments(self, parser):
        parser.add_argument(
            "--domain_codes",
            nargs="*",
            required=False,
            help="Список доменов eBay, категории которых следует удалить.",
        )

    def handle(self, **options):
        domain_codes = options.get("domain_codes", [])
        trees = EbayCategoryTree.objects.all()
        if domain_codes:
            trees = trees.filter(domain__code__in=domain_codes)
            message = f"Все категории удалены для доменов: {domain_codes}."
        else:
            message = f"Все категории удалены для всех доменов."
        trees.delete()
        print(message)
