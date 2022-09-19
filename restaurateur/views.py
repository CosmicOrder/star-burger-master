from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from geopy import distance

from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem
from locations.models import Location
from locations.views import fetch_coordinates


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = Restaurant.objects.order_by('name')
    products = Product.objects.prefetch_related(
        'menu_items').select_related('category')

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:
        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in
               product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in
                                restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    available_restaurants = []
    batch_locations = []
    orders = Order.objects.prefetch_related('items__product') \
                          .select_related('restaurant_preparing_order')
    restaurant_menu_items = RestaurantMenuItem.objects \
        .select_related('restaurant') \
        .select_related('product')
    for order in orders:
        if order.restaurant_preparing_order:
            order.status = "Готовится"
            order.save()

        order_location = Location.objects.get(address=order.address)

        if order_location:
            order_lat, order_lon = order_location.lat, order_location.lon
        else:
            order_location = fetch_coordinates(settings.GEOCODER_API_KEY,
                                               order.address)

            Location.objects.create(
                address=order.address,
                lat=order_location[0],
                lon=order_location[1],
            )
            order_lat, order_lon = order_location[0], order_location[1]

        order_products = order.items.all()

        restaurants = [
            restaurant_menu_item.restaurant for
            order_product in
            order_products for restaurant_menu_item in restaurant_menu_items
            if restaurant_menu_item.product == order_product.product
        ]

        def get_available_restaurants(restaurants):
            order_available_restaurants = []
            restaurant_quantity = \
                {restaurant: restaurants.count(restaurant) for
                 restaurant in restaurants}
            for restaurant, quantity in restaurant_quantity.items():
                restaurant_location = Location.objects.get(
                    address=restaurant.address)
                if len(order_products) == quantity:
                    if restaurant_location:
                        restaurant_lat, restaurant_lon = \
                            restaurant_location.lat, \
                            restaurant_location.lon
                        restaurant.distance = distance.distance(
                            (restaurant_lat, restaurant_lon),
                            (order_lat, order_lon)).km
                    else:
                        restaurant_location = fetch_coordinates(
                            settings.GEOCODER_API_KEY,
                            restaurant.address)

                        batch_locations.append(Location(
                            address=restaurant.address,
                            lat=restaurant_location[0],
                            lon=restaurant_location[1],
                        ))

                        restaurant.distance = distance.distance(
                            (restaurant_location[0], restaurant_location[1]),
                            (order_lat, order_lon)).km

                    order_available_restaurants.append(restaurant)
                    # сортируем по дистанции до места доставки
                    order_available_restaurants = sorted(
                        order_available_restaurants,
                        key=lambda restaurant: restaurant.distance)
            return order_available_restaurants

        available_restaurants.append(get_available_restaurants(restaurants))

    Location.objects.bulk_create(batch_locations)
    orders = list(zip(Order.objects.fetch_with_order_price()
                           .select_related('restaurant_preparing_order'),
                      available_restaurants))

    return render(request,
                  template_name='order_items.html',
                  context={
                      'order_items': orders,
                  })
