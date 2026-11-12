from rest_framework import serializers

from .models import Order, OrderItem


class ItemSerialize(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]


class OrderSerialize(serializers.ModelSerializer):
    products = ItemSerialize(many=True, write_only=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ["firstname", "lastname", "phonenumber", "address", "products"]

    def create(self, validated_data):
        item_data = validated_data.pop("products")
        order = Order.objects.create(**validated_data)

        for item in item_data:
            product = item["product"]
            OrderItem.objects.create(price=product.price, order_details=order, **item)
        return order
