from ebay.category import actions, models
from ebay.tests.base import EbayActionTest


class EbayCategoryTest(EbayActionTest):
    def setUp(self):
        super().setUp()
        self.domain_codes = ["EBAY_US", "EBAY_DE"]
        self.download_category_trees(domain_codes=self.domain_codes)
        self.category_tree_id = models.EbayCategoryTree.objects.get(
            domain=self.channel.domain
        ).category_tree_id

    def download_category_trees(self, domain_codes=[]):
        action = actions.RemoteDownloadEbayDefaultCategoryTreeList()
        action(domain_codes=domain_codes)

    def delete_trees(self):
        models.EbayCategoryTree.objects.all().delete()

    def download_categories(self, domain_codes=[]):
        action = actions.RemoteDownloadEbayCategories()
        action(domain_codes=domain_codes)

    def delete_categories(self):
        models.EbayCategory.objects.all().delete()

    def test_get_category_tree(self):
        self.perform_action(
            action_class=actions.GetEbayDefaultCategoryTree,
            marketplace_id=self.domain.code,
        )

    def test_download_category_tree(self):
        self.delete_trees()

        self.perform_action(
            action_class=actions.RemoteDownloadEbayDefaultCategoryTree,
            marketplace_id=self.domain.code,
        )
        self.assertNotEqual(models.EbayCategoryTree.objects.count(), 0)
        # check if tree was created only for one domain
        self.assertEqual(
            models.EbayCategoryTree.objects.count(),
            models.EbayCategoryTree.objects.filter(
                domain__code=self.domain.code
            ).count(),
        )

    def test_download_category_tree_list(self):
        self.delete_trees()
        # check if tree was created for each domain
        self.download_category_trees(domain_codes=self.domain_codes)
        self.assertEqual(
            models.EbayCategoryTree.objects.count(), len(self.domain_codes)
        )
        for domain_code in self.domain_codes:
            category_trees_num = models.EbayCategoryTree.objects.filter(
                domain__code=domain_code
            ).count()
            self.assertEqual(category_trees_num, 1)

        # download trees second time and check if their number is still the same
        self.download_category_trees(domain_codes=self.domain_codes)
        self.assertEqual(
            models.EbayCategoryTree.objects.count(), len(self.domain_codes)
        )

    def test_get_domain_categories(self):
        self.perform_action(
            action_class=actions.GetEbayDomainCategories,
            category_tree_id=self.category_tree_id,
        )

    def test_download_domain_categories(self):
        self.delete_categories()

        self.perform_action(
            action_class=actions.RemoteDownloadEbayDomainCategories,
            category_tree_id=self.category_tree_id,
        )
        self.assertNotEqual(models.EbayCategory.objects.count(), 0)
        # check if categories were created only for one domain
        self.assertEqual(
            models.EbayCategory.objects.count(),
            models.EbayCategory.objects.filter(
                category_tree__category_tree_id=self.category_tree_id,
            ).count(),
        )

    def test_download_categories(self):
        self.delete_categories()
        # download categories for all domain_codes
        self.download_categories(domain_codes=self.domain_codes)
        # check if each domain has categories
        for domain_code in self.domain_codes:
            categories_num = models.EbayCategory.objects.filter(
                category_tree__domain__code=domain_code,
            ).count()
            self.assertNotEqual(categories_num, 0)
        # downloading second time
        categories_num = models.EbayCategory.objects.count()

        self.download_categories(domain_codes=self.domain_codes)
        # check if number of categories is still the same
        self.assertEqual(models.EbayCategory.objects.count(), categories_num)

    def test_get_variations_supported_categories(self):
        self.perform_action(
            action_class=actions.GetVariationsSupportedCategories,
            marketplace_id=self.domain.code,
        )

    def test_mark_variations_supported_domain_categories(self):
        # download categories for all domain_codes
        self.download_categories(domain_codes=self.domain_codes)
        # mark variations supported categories
        self.perform_action(
            action_class=actions.MarkVariationsSupportedEbayDomainCategories,
            marketplace_id=self.domain.code,
        )
        self.assertNotEqual(
            models.EbayCategory.objects.filter(
                variationsSupported=True, category_tree__domain__code=self.domain.code,
            ).count(),
            0,
        )
        # check if variations supported categories were marked only for one domain
        self.assertEqual(
            models.EbayCategory.objects.filter(variationsSupported=True,).count(),
            models.EbayCategory.objects.filter(
                variationsSupported=True, category_tree__domain__code=self.domain.code,
            ).count(),
        )
