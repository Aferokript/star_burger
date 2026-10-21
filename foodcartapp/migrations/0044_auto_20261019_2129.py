from django.db import migrations
from django.db.models import F


def add_price(apps, schema_editor):
    Items = apps.get_model('foodcartapp', 'OrderItem')
    Items.objects.update(price=F('product__price') * F('items__quantity'))
        

class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_orderitem_price'),
    ]

    operations = [
        migrations.RunPython(add_price)
    ]
