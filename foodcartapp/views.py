import phonenumbers
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
    order_detail = request.data
    try:
        # firstname check
        firstname = order_detail['firstname']
        if firstname is None:
            return Response({
                'error': 'firstname: Это поле не может быть пустым.',
            }, status=status.HTTP_400_BAD_REQUEST)
        elif not isinstance(firstname, str):
            return Response({
                'error': 'firstname: Not a valid string.',
            }, status=status.HTTP_400_BAD_REQUEST)
        # lastname check
        lastname = order_detail['lastname']
        if lastname is None:
            return Response({
                'error': 'lastname: Это поле не может быть пустым.',
            }, status=status.HTTP_400_BAD_REQUEST)
        # phonenumber check
        phonenumber = order_detail['phonenumber']
        if phonenumber is None:
            return Response({
                'error': 'phonenumber: Это поле не может быть пустым.',
            }, status=status.HTTP_400_BAD_REQUEST)
        elif phonenumber:
            parse_number = phonenumbers.parse(phonenumber)
            if not phonenumbers.is_valid_number(parse_number):
                return Response({
                    'error': 'phonenumber: Введен некорректный номер телефона.'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': 'phonenumber: Это поле не может быть пустым.'
            }, status=status.HTTP_400_BAD_REQUEST)
        # address check
        address = order_detail['address']
        if address is None:
            return Response({
                'error': 'address: Это поле не может быть пустым.',
            }, status=status.HTTP_400_BAD_REQUEST)
    except KeyError as ex:
        return Response({
            'error': f'{ex} обязательное поле',
        }, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.create(
        firstname=firstname,
        lastname=lastname,
        phonenumber=phonenumber,
        address=address,
    )

    try:
        products = order_detail['products']
    except KeyError:
        return Response({
            'error': 'products: Обязательное поле.'
        }, status=status.HTTP_400_BAD_REQUEST)

    if isinstance(products, list):
        if products:
            for order_item in products:
                product_id = order_item['product']
                if product_id <= len(Product.objects.all()):
                    OrderItem.objects.create(
                        order=order,
                        product=Product.objects.get(id=product_id),
                        quantity=order_item['quantity'],
                    )
                    return Response({
                        'success': True,
                    })
                else:
                    return Response({
                        'error': f'products: Недопустимый первичный ключ {product_id}'
                    }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': 'products: Этот список не может быть пустым.',
            }, status=status.HTTP_400_BAD_REQUEST)

    elif isinstance(products, str):
        return Response({
            'error': 'products: Ожидался list со значениями, но был '
                     'получен str.',
        }, status=status.HTTP_400_BAD_REQUEST)
    elif products is None:
        return Response({
            'error': 'products: Это поле не может быть пустым.',
        }, status=status.HTTP_400_BAD_REQUEST)
