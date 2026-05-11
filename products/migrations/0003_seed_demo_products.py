from decimal import Decimal

from django.db import migrations


DEMO_CATEGORIES = [
    ("Vegetables", "vegetables", "Fresh vegetables harvested for daily cooking."),
    ("Grains", "grains", "Staple grains and cereals from local farms."),
    ("Tubers", "tubers", "Filling roots and tubers for homes and food vendors."),
    ("Fruits", "fruits", "Ripe fruit and plantain ready for delivery."),
]


DEMO_PRODUCTS = [
    {
        "name": "Basket of Fresh Tomatoes",
        "slug": "basket-fresh-tomatoes",
        "category": "vegetables",
        "description": "Firm red tomatoes packed for stew, jollof, sauces, and market resale.",
        "price": Decimal("8500.00"),
    },
    {
        "name": "50kg Local Rice",
        "slug": "50kg-local-rice",
        "category": "grains",
        "description": "Clean long-grain local rice supplied directly from partner farms.",
        "price": Decimal("72000.00"),
    },
    {
        "name": "Crate of Bell Peppers",
        "slug": "crate-bell-peppers",
        "category": "vegetables",
        "description": "Mixed red and green peppers for restaurants, caterers, and homes.",
        "price": Decimal("18500.00"),
    },
    {
        "name": "Bundle of Ripe Plantain",
        "slug": "bundle-ripe-plantain",
        "category": "fruits",
        "description": "Sweet ripe plantain selected for frying, roasting, or family meals.",
        "price": Decimal("12500.00"),
    },
    {
        "name": "Dozen Yam Tubers",
        "slug": "dozen-yam-tubers",
        "category": "tubers",
        "description": "Heavy white yam tubers sorted for freshness and low bruising.",
        "price": Decimal("36000.00"),
    },
    {
        "name": "Paint Bucket of Garri",
        "slug": "paint-bucket-garri",
        "category": "grains",
        "description": "Crisp garri processed from cassava and packed for household supply.",
        "price": Decimal("9500.00"),
    },
]


def seed_demo_products(apps, schema_editor):
    Category = apps.get_model("products", "Category")
    MenuItem = apps.get_model("products", "MenuItem")

    categories = {}
    for name, slug, description in DEMO_CATEGORIES:
        category, _ = Category.objects.update_or_create(
            slug=slug,
            defaults={"name": name, "description": description},
        )
        categories[slug] = category

    for product in DEMO_PRODUCTS:
        MenuItem.objects.update_or_create(
            slug=product["slug"],
            defaults={
                "name": product["name"],
                "category": categories[product["category"]],
                "description": product["description"],
                "price": product["price"],
                "is_available": True,
            },
        )


def remove_demo_products(apps, schema_editor):
    MenuItem = apps.get_model("products", "MenuItem")
    Category = apps.get_model("products", "Category")

    MenuItem.objects.filter(slug__in=[item["slug"] for item in DEMO_PRODUCTS]).delete()
    Category.objects.filter(slug__in=[item[1] for item in DEMO_CATEGORIES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0002_menuitem_is_available_index"),
    ]

    operations = [
        migrations.RunPython(seed_demo_products, remove_demo_products),
    ]
