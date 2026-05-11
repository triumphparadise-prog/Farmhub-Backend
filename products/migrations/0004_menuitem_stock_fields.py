from django.db import migrations, models


def set_demo_stock(apps, schema_editor):
    MenuItem = apps.get_model("products", "MenuItem")
    stock_by_slug = {
        "basket-fresh-tomatoes": 40,
        "50kg-local-rice": 18,
        "crate-bell-peppers": 12,
        "bundle-ripe-plantain": 25,
        "dozen-yam-tubers": 8,
        "paint-bucket-garri": 30,
    }
    for slug, quantity in stock_by_slug.items():
        MenuItem.objects.filter(slug=slug).update(
            stock_quantity=quantity,
            low_stock_threshold=5,
            is_available=quantity > 0,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0003_seed_demo_products"),
    ]

    operations = [
        migrations.AddField(
            model_name="menuitem",
            name="low_stock_threshold",
            field=models.PositiveIntegerField(default=5),
        ),
        migrations.AddField(
            model_name="menuitem",
            name="stock_quantity",
            field=models.PositiveIntegerField(default=25),
        ),
        migrations.RunPython(set_demo_stock, migrations.RunPython.noop),
    ]
