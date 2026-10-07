import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException 
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, Order, OrderItem


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    order_data = request.data
    if isinstance(order_data, dict) and order_data != {}:
        print(order_data)
        name = order_data.get('firstname')
        last_name = order_data.get('lastname')
        phone_number_str = order_data.get('phonenumber')
        address = order_data.get('address')
        
        if not isinstance(all([name, last_name, phone_number_str, address]), str):
            return Response({'error': 'Одно из полей пустое'}, status=status.HTTP_400_BAD_REQUEST)
                    
        try:
            parsed_number = phonenumbers.parse(phone_number_str, "RU")
        except NumberParseException:
            return Response({'error': 'Некорректный номер телефона'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not phonenumbers.is_valid_number(parsed_number):
            return Response({'error': 'Некооректный номер телефона'}, status=status.HTTP_400_BAD_REQUEST)
        
        order = Order.objects.create(name=name, last_name=last_name, phone_number=phone_number_str, address=address)
            
        product = order_data.get('products')
        
        if product is None or product == []:
            return Response({'error': 'product не может быть пустым'}, status=status.HTTP_400_BAD_REQUEST)
    
        for item in product:
            if isinstance(item, dict) and Product.objects.filter(id=item['product']).exists():
                OrderItem.objects.create(order_details=order, products_id=item['product'], quantity=item['quantity'])
    
            else:
                return Response({'error': 'Products должен быть словарем или несуществующий товар'}, status=status.HTTP_400_BAD_REQUEST)
            
    else:
        return Response({'error': 'Заполните форму'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(order_data)
    

