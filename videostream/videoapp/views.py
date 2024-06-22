# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import logout
import requests
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from .models import Excursion, Favorite
from django.views.decorators.csrf import csrf_exempt
import json

def index(request):
    return render(request, 'index.html')


def get_countries(request):
    url = 'https://api.sputnik8.com/v1/countries?api_key=9bc84ec26f47bf3005dc55434b4b796a&username=partners+tpo50@sputnik8.com'

    try:
        response = requests.get(url)
        data = response.json()
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)})

def get_cities(request, country_id):
    url = 'https://api.sputnik8.com/v1/cities?api_key=9bc84ec26f47bf3005dc55434b4b796a&username=partners+tpo50@sputnik8.com'

    try:
        response = requests.get(url)
        data = response.json()
        cities = [city for city in data if city['country_id'] == country_id]
        return JsonResponse(cities, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)})

def get_categories(request, city_id):
    url = f'https://api.sputnik8.com/v1/cities/{city_id}/categories?api_key=9bc84ec26f47bf3005dc55434b4b796a&username=partners+tpo50@sputnik8.com'

    try:
        response = requests.get(url)
        data = response.json()
        categories = []

        for category in data:
            sub_categories = category.get('sub_categories', [])
            for sub_category in sub_categories:
                categories.append({
                    'short_name': sub_category['short_name'],
                    'slug': sub_category['slug']
                })

        return JsonResponse(categories, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)})


def get_excursions(request, city_id, category_slug):
    url = f'https://api.sputnik8.com/v1/products?city_id={city_id}&category_slug={category_slug}&api_key=9bc84ec26f47bf3005dc55434b4b796a&username=partners+tpo50@sputnik8.com'
    try:
        response = requests.get(url)
        data = response.json()
        excursions = []

        for excursion in data:
            if not excursion['image_big']:  # Проверяем, если image_big пустой
                image_url = excursion.get('photo', '')  # Если пустой, читаем из photo
            else:
                image_url = excursion['image_big']

            excursions.append({
                'title': excursion['title'],
                'price': excursion['price'],
                'image_big': image_url,
                'url': excursion['url'],
                'customers_review_rating': excursion.get('customers_review_rating', 'Нет рейтинга')  # Добавляем поле rating
            })

        return JsonResponse(excursions, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)})

#Registr
def custom_login_view(request, **kwargs):
    if request.user.is_authenticated:
        messages.warning(request, 'Вы уже вошли в систему.')
        return redirect('')  # Замените 'home' на вашу домашнюю страницу

    # Пример: добавление всех пользователей в базу данных (если они еще не добавлены)
    all_users = User.objects.all()
    if not all_users.exists():
        # Добавление пользователей
        User.objects.create_user(username='user1', password='password1')
        User.objects.create_user(username='user2', password='password2')
        # ... добавьте своих пользователей по аналогии

    # Вызываем стандартное представление входа с переданными аргументами
    return LoginView.as_view(**kwargs)(request)



def custom_registration_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                print(f"User {user.username} successfully saved.")
                username = form.cleaned_data.get('username')
                messages.success(request, f'Account created for {username}')
                login(request, user)  # Автоматически входить после регистрации
                return redirect('index')  # Замените 'home' на вашу домашнюю страницу
            except Exception as e:
                print(f"Error saving user: {e}")
        else:
            print("Form is not valid.")
    else:
        form = UserCreationForm()

    return render(request, 'registration/registration.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def favorite_page(request):
    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user).select_related('excursion')
        return render(request, 'Favorite/favorite.html', {'favorites': favorites})
        # Логика обработки запроса
        #return render(request, 'Favorite/favorite.html')
    else:
        message = "Для доступа к избранному необходимо войти."
        return render(request, 'index.html', {'message': message})


def getUsername(request):
    if request.user.is_authenticated:
        return request.user.username
    else:
        return None



def send_email(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        surname = request.POST.get('surname', '')
        username = request.POST.get('username', '')
        city = request.POST.get('city', '')

        # Формируем текст письма
        message = f"Имя: {name}\nФамилия: {surname}\nИмя пользователя: {username}\nГород: {city}"

        # Отправляем письмо
        send_mail(
            'Новое сообщение с формы',
            message,
            'eigorbunov@mail.ru',  # Замените на свой адрес
            ['belov-yegor@mail.ru'],  # Замените на адрес получателя
            fail_silently=False,
        )
    return render(request, 'index.html')


@csrf_exempt
@login_required
def add_to_favorites(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            price = data.get('price')
            rating = data.get('customers_review_rating')
            image = data.get('image_big')
            url = data.get('url')

            # Найдем или создадим экскурсию
            excursion, created = Excursion.objects.get_or_create(
                title=title,
                defaults={'price': price, 'customers_review_rating': rating, 'image_big': image, 'url': url}
            )

            # Добавим в избранное
            favorite, created = Favorite.objects.get_or_create(user=request.user, excursion=excursion)
            if created:
                return JsonResponse({'status': 'success', 'message': 'Экскурсия добавлена в избранное'})
            else:
                return JsonResponse({'status': 'exists', 'message': 'Экскурсия уже в избранном'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса'})


@login_required
def get_favorites(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('excursion')
    excursions = [{
        'title': fav.excursion.title,
        'price': str(fav.excursion.price),
        'customers_review_rating': fav.excursion.customers_review_rating,
        'image_big': fav.excursion.image_big,
        'url': fav.excursion.url
    } for fav in favorites]
    return JsonResponse(excursions, safe=False)


@login_required
@csrf_exempt
def remove_from_favorites(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')

            # Находим экскурсию по названию
            excursion = Excursion.objects.get(title=title)
            favorite = Favorite.objects.get(user=request.user, excursion=excursion)
            favorite.delete()
            return JsonResponse({'status': 'success', 'message': 'Экскурсия удалена из избранного'})
        except Excursion.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Экскурсия не найдена'})
        except Favorite.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Экскурсия не в избранном'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса'})