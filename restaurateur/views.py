import requests
from .geocoder_logic import fetch_coordinates
from .distance_logic import count_restaurant_distance
from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from geopy.distance import distance

from foodcartapp.models import Order, Product, Restaurant, RestaurantMenuItem
from places.models import Places
from star_burger.settings import yandex_geocoder


class Login(forms.Form):
    username = forms.CharField(
        label="Логин",
        max_length=75,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Укажите имя пользователя"}
        ),
    )
    password = forms.CharField(
        label="Пароль",
        max_length=75,
        required=True,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Введите пароль"}
        ),
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={"form": form})

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(
            request,
            "login.html",
            context={
                "form": form,
                "ivalid": True,
            },
        )


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy("restaurateur:login")


def can_cook(order, restaurant):
    needed_products = [item.product for item in order.items.all()]
    if not needed_products:
        return False

    menu_products = [mi.product for mi in restaurant.menu_items.all()]

    for product in needed_products:
        if product not in menu_products:
            return False
    return True


def is_manager(user):
    return user.is_staff


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_products(request):
    restaurants = list(Restaurant.objects.order_by("name"))
    products = list(Product.objects.prefetch_related("menu_items"))

    products_with_restaurant_availability = []
    for product in products:
        availability = {
            item.restaurant_id: item.availability for item in product.menu_items.all()
        }
        ordered_availability = [
            availability.get(restaurant.id, False) for restaurant in restaurants
        ]

        products_with_restaurant_availability.append((product, ordered_availability))

    return render(
        request,
        template_name="products_list.html",
        context={
            "products_with_restaurant_availability": products_with_restaurant_availability,
            "restaurants": restaurants,
        },
    )


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_restaurants(request):
    return render(
        request,
        template_name="restaurants_list.html",
        context={
            "restaurants": Restaurant.objects.all(),
        },
    )


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_orders(request):
    order_data = []
    all_restaurants = list(Restaurant.objects.prefetch_related("menu_items__product"))
   
    orders = Order.objects.all().count_order_price().prefetch_related("items__product")
    
    all_places = Places.objects.filter(lat__isnull=False, lon__isnull=False)
    coords_by_address = {p.address: (p.lat, p.lon) for p in all_places}

    restaurants_with_coords = []
    for r in all_restaurants:
        if r.address in coords_by_address:
            restaurants_with_coords.append({
                'restaurant': r,
                'coords': coords_by_address[r.address] 
            })

    for order in orders:
        if order.status == "VI":
            continue

        if order.restaurant:
            capable_restaurants = [order.restaurant]
        else:
            capable_restaurants = [r for r in all_restaurants if can_cook(order, r)]
        
        client_coords = coords_by_address.get(order.address)
        
        restaurant_places = []
        
        if client_coords:
            client_lat, client_lon = client_coords
            
            for item in restaurants_with_coords:
                d = distance((client_lat, client_lon), item['coords']).km
                restaurant_places.append({
                    'restaurant': item['restaurant'], 
                    'distance': d
                })
            restaurant_places.sort(key=lambda item: item['distance'])
            
        else:
            client_api_coords = fetch_coordinates(yandex_geocoder, order.address)
            if client_api_coords:
                client_lon, client_lat = float(client_api_coords[0]), float(client_api_coords[1])
                
                for item in restaurants_with_coords:
                    distance_to_rest = distance((client_lat, client_lon), item['coords']).km
                    restaurant_places.append({
                        'restaurant': item['restaurant'], 
                        'distance': distance_to_rest
                    })
                restaurant_places.sort(key=lambda item: item['distance'])
                
                Places.objects.create(
                    address=order.address, 
                    lat=client_lat, 
                    lon=client_lon
                )
                
            

        order_data.append(
            {
                "id": order.id,
                "status": order.get_status_display(),
                "comments": order.comments,
                "total_price": order.total_price,
                "pay_order": order.get_pay_display(),
                "firstname": order.firstname,
                "lastname": order.lastname,
                "phonenumber": order.phonenumber,
                "address": order.address,
                "restaurant": restaurant_places,
                "capable_restaurants": capable_restaurants,
                "registrated_at": order.registrated_at,
                "called_at": order.called_at,
                "delivered_at": order.delivered_at,
            }
        )

    context = {"order_data": order_data}
    return render(request, "order_items.html", context=context)


def change_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return redirect("admin:foodcartapp_order_change", order.id)
