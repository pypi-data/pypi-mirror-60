import factory
from ebay.category.models import EbayCategory, EbayCategoryTree
from ebay.tests.factories import EbayDomainFactory


class EbayCategoryTreeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EbayCategoryTree
        django_get_or_create = ["domain"]

    domain = factory.SubFactory(EbayDomainFactory)
    category_tree_id = "0"
    category_tree_version = "121"


class EbayCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EbayCategory
        django_get_or_create = ["category_tree", "category_id"]

    category_tree = factory.SubFactory(EbayCategoryTreeFactory)
    category_id = "802"
    parent_id = "37842"
    level = "5"
    name = "Other Victorian Trade Cards"
    name_path = (
        "Collectibles / Advertising / Merchandise & Memorabilia / Victorian Trade Cards"
    )
    id_path = ""
    is_leaf = True
    variationsSupported = True
    transportSupported = False
