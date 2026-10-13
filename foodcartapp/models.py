from django.db import models
import phonenumbers
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from phonenumbers.phonenumberutil import NumberParseException 
from rest_framework import serializers 
from rest_framework.serializers import ValidationError ,CharField, IntegerField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    firstname = models.CharField(max_length=30, null=False, verbose_name='Имя')
    lastname = models.CharField(max_length=30, null=False, verbose_name='Фамилия')
    phonenumber = PhoneNumberField(blank=True, null=False, verbose_name='Телефон')
    address = models.CharField(max_length=80, null=False, verbose_name='Адрес', db_index=True)
    
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        
        
    def __str__(self):
        return f"{self.firstname} {self.lastname} {self.address}"


class OrderItem(models.Model):
    order_details = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    products = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    
    
    class Meta:
        verbose_name = 'Детали'
        verbose_name_plural = 'Детали Заказа'
    
    
    def __str__(self):
        return f"{self.order_details}  {self.quantity}"
    

class ItemSerialize(serializers.Serializer):
    order_details = CharField()
    products = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = IntegerField()
    
    def validate(self, attrs):
        if not Product.objects.filter(id=attrs['products']).exists():
            raise ValidationError(
                'Несуществующее блюдо'
            )
        return attrs
    

class OrderSerialize(serializers.Serializer):
    firstname = CharField()
    lastname = CharField()
    phonenumber = CharField()
    address = CharField()
    item_data = ItemSerialize(many=True)
    
    
    def create(self, validated_data):
        item_data = validated_data.pop('item_data')
        order = Order.objects.create(**validated_data)
        
        for item in item_data:
            OrderItem.objects.create(order_details=order, **item)
            
       
       




    