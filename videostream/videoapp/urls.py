from django.urls import path
from .views import index, custom_registration_view, logout_view, get_countries, get_cities, get_categories, get_excursions, favorite_page, send_email, add_to_favorites, get_favorites, remove_from_favorites
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', index, name='index'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('registration/', custom_registration_view, name='registration'),
    path('logout/', logout_view, name='logout'),
    path('get_countries/', get_countries, name='get_countries'),
    path('get_cities/<int:country_id>/', get_cities, name='get_cities'),
    path('get_categories/<int:city_id>/', get_categories, name='get_categories'),
    path('get_excursions/<int:city_id>/<str:category_slug>/', get_excursions, name='get_excursions'),
    path('favorite/', favorite_page, name='favorite_page'),
    path('send-email/', send_email, name='send_email'),
    path('add_to_favorites/', add_to_favorites, name='add_to_favorites'),
    path('get_favorites/', get_favorites, name='get_favorites'),
    path('remove_from_favorites/', remove_from_favorites, name='remove_from_favorites'),
]