ymaps.ready(init);

//КАРТА
function init() {
    var myMap = new ymaps.Map('map', {
        center: [55.753630, 37.620070], // Координаты Москвы
        zoom: 5 // Масштаб карты
    });

    var userPlacemark;
    var searchPlacemark;

    // Проверяем поддержку геолокации
    if (navigator.geolocation) {
        // Запрашиваем геопозицию пользователя
        navigator.geolocation.getCurrentPosition(success, error);
    } else {
        console.log('Геолокация не поддерживается вашим браузером.');
    }

    // Функция для обработки полученных координат
    function success(position) {
        var coordinates = [position.coords.latitude, position.coords.longitude];
        myMap.setCenter(coordinates); // Изменяем центр карты на текущие координаты пользователя
        if (userPlacemark) {
            myMap.geoObjects.add(userPlacemark);
        }
    }

    // Функция для обработки ошибок получения геопозиции
    function error() {
        console.log('Невозможно получить ваше местоположение. Используем координаты Москвы.');
    }

    var searchControl = new ymaps.control.SearchControl({
        options: {
            maxWidth: 200, // Максимальная ширина контейнера для результата поиска
            noPlacemark: true, // Скрыть ссылку "Открыть на картах"
            provider: 'yandex#search',
            results: 20
        }
    });

    myMap.controls.add(searchControl);

    // Удаляем вторую кнопку "Найти адрес или объект"
    myMap.controls.remove('searchControl');

    var places = ['достопримечательность'];

    places.forEach(function (place) {
        searchControl.search(place).then(function () {
            var results = searchControl.getResultsArray().slice(0, 9);
            var output = '<h2>' + place + '</h2>';

            results.forEach(result => {
                var name = result.properties.get('name');
                var address = result.properties.get('description') || result.properties.get('balloonContent') || 'Адрес отсутствует';
                output += '<div class="card"><h3>' + name + '</h3><p>' + address + '</p></div>';
            });

        });
    });

    // Обработчик события для поиска
    searchControl.events.add('load', function (e) {
        // Получение результатов поиска
        var results = e.get('target').getResultsArray();
        // Если найден хотя бы один результат, центрируем карту на первом результате
        if (results.length) {
            var firstResult = results[0];
            var coordinates = firstResult.geometry.getCoordinates();
            myMap.setCenter(coordinates); // Изменяем центр карты на координаты первого результата
        }
    });
}


//МЕНЮ БУРГЕР
document.addEventListener('DOMContentLoaded', function() {
    var burgerMenu = document.getElementById('burger-menu');
    var navMenu = document.getElementById('nav-menu');

    burgerMenu.addEventListener('click', function() {
        navMenu.classList.toggle('active');
    });
});

//Button
function toggleLogout(show) {
    var usernameElement = document.getElementById('username');
    if (show) {
      usernameElement.style.backgroundColor = 'white';
      usernameElement.style.color = 'black';
      usernameElement.style.border = '2px solid #000';
      usernameElement.style.borderRadius = '15px';
      usernameElement.innerHTML = 'Logout';
      usernameElement.setAttribute('href', usernameElement.getAttribute('data-logout-url'));
      setLogoutButtonWidth();
    } else {
      usernameElement.style.backgroundColor = 'black';
      usernameElement.style.color = 'white';
      usernameElement.style.border = '2px solid transparent';
      usernameElement.style.borderRadius = '15px';
      usernameElement.innerHTML = usernameElement.getAttribute('data-username');
      usernameElement.setAttribute('href', '{% url "login" %}');  // Или используйте ваш URL для входа
    }

}

document.addEventListener('DOMContentLoaded', () => {
    populateCountryDropdown();
    document.getElementById('country').addEventListener('change', handleCountryChange);
    document.getElementById('city').addEventListener('change', handleCityChange);
    document.getElementById('excurs-categories').addEventListener('change', handleCategoryChange);
    document.getElementById('search-button').addEventListener('click', handleSearch);
    document.getElementById('expand-button').addEventListener('click', toggleExpand);
});

let selectedCityId = null;
let selectedCategorySlug = null;

function populateCountryDropdown() {
    const selectElement = document.getElementById('country');
    selectElement.innerHTML = ''; // Очистим список перед загрузкой новых данных

    // Добавим пустой элемент в начало списка
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = '';
    selectElement.appendChild(defaultOption);

    fetch('/get_countries/')
        .then(response => response.json())
        .then(data => {
            data.sort((a, b) => a.name.localeCompare(b.name));

            data.forEach(country => {
                const option = document.createElement('option');
                option.value = country.id;
                option.textContent = country.name;
                selectElement.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function handleCountryChange() {
    const countryId = document.getElementById('country').value;
    populateCityDropdown(countryId);
}

function populateCityDropdown(countryId) {
    const selectElement = document.getElementById('city');
    selectElement.innerHTML = '';

    const defaultOption = document.createElement('option');
    defaultOption.value = '';

    selectElement.appendChild(defaultOption);

    fetch(`/get_cities/${countryId}/`)
        .then(response => response.json())
        .then(data => {
            data.sort((a, b) => a.name.localeCompare(b.name));

            data.forEach(city => {
                const option = document.createElement('option');
                option.value = city.id;
                option.textContent = city.name;
                selectElement.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function handleCityChange() {
    selectedCityId = document.getElementById('city').value;
    populateCategoryDropdown(selectedCityId);
}

function populateCategoryDropdown(cityId) {
    const selectElement = document.getElementById('excurs-categories');
    selectElement.innerHTML = '';

    const defaultOption = document.createElement('option');
    defaultOption.value = 'Выберите категорию';
    selectElement.appendChild(defaultOption);

    const allOption = document.createElement('option');
    allOption.value = 'all';
    allOption.textContent = 'Все';
    selectElement.appendChild(allOption);

    fetch(`/get_categories/${cityId}/`)
        .then(response => response.json())
        .then(data => {
            data.sort((a, b) => a.short_name.localeCompare(b.short_name));

            data.forEach(category => {
                const option = document.createElement('option');
                option.value = category.slug; // Используем slug в качестве значения
                option.textContent = category.short_name; // Отображаем short_name
                selectElement.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function handleCategoryChange() {
    selectedCategorySlug = document.getElementById('excurs-categories').value;
}

function handleSearch(event) {
    event.preventDefault();
    if (selectedCityId && selectedCategorySlug) {
        populateExcursions(selectedCityId, selectedCategorySlug);
    }
}

function populateExcursions(cityId, categorySlug) {
    const resultContainer = document.getElementById('result-container');
    const expandButton = document.getElementById('expand-button');
    resultContainer.innerHTML = '';
    resultContainer.classList.add('hidden');
    expandButton.classList.add('hidden');

    fetch(`/get_excursions/${cityId}/${categorySlug}/`)
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) {
                resultContainer.textContent = 'Экскурсий нет';
                resultContainer.style.fontSize = '3em';
                resultContainer.style.height = '80px'; // Установка размера текста в 3em
            } else {
                data.forEach(excursion => {
                    const excursionDiv = document.createElement('div');
                    excursionDiv.classList.add('excursion');

                    const title = document.createElement('h3');
                    title.textContent = excursion.title;

                    const price = document.createElement('p');
                    price.textContent = `Стоимость: ${excursion.price}`;

                    const rating = document.createElement('p');
                    rating.textContent = `Рейтинг: ${excursion.customers_review_rating}`;

                    const image = document.createElement('img');
                    image.src = excursion.image_big;
                    image.alt = excursion.title;

                    const detailsButton = document.createElement('a');
                    detailsButton.href = excursion.url;
                    detailsButton.textContent = 'Узнать подробнее';
                    detailsButton.classList.add('details-button');
                    detailsButton.target = '_blank';

                    const favoriteButton = document.createElement('button');
                    favoriteButton.textContent = 'Добавить в избранное';
                    favoriteButton.classList.add('favorite-button');
                    favoriteButton.addEventListener('click', () => {
                        addToFavorites(excursion);
                    });

                    excursionDiv.appendChild(title);
                    excursionDiv.appendChild(price);
                    excursionDiv.appendChild(rating);
                    excursionDiv.appendChild(image);
                    excursionDiv.appendChild(detailsButton);
                    excursionDiv.appendChild(favoriteButton); // Добавляем кнопку в карточку экскурсии
                    resultContainer.appendChild(excursionDiv);
                });

                if (data.length >= 4) {
                    expandButton.classList.remove('hidden'); // Показываем кнопку только при наличии 4 и более экскурсий
                }
            }

            resultContainer.classList.remove('hidden'); // Показываем контейнер в любом случае
        })
        .catch(error => {
            console.error('Error:', error);
            resultContainer.textContent = 'Произошла ошибка при загрузке данных';
        });
}


function addToFavorites(excursion) {
    // Убираем символ валюты из цены и преобразуем в число
    excursion.price = parseFloat(excursion.price.replace(/[^0-9.-]+/g, ''));

    fetch('/add_to_favorites/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(excursion)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function toggleExpand() {
    const resultContainer = document.getElementById('result-container');
    resultContainer.classList.toggle('expanded');
}

function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Показываем или скрываем кнопку "Вверх" в зависимости от положения прокрутки
window.onscroll = function() {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        document.getElementById("back-to-top").style.display = "block";
    } else {
        document.getElementById("back-to-top").style.display = "none";
    }
};

document.addEventListener("DOMContentLoaded", function() {
    // Находим все ссылки в меню, кроме кнопки избранного
    var menuLinks = document.querySelectorAll('header nav ul.menu a:not(#favorite-link):not(#username):not(.login-button)');

    // Обходим каждую ссылку
    menuLinks.forEach(function(menuLink) {
        // Добавляем обработчик события на клик
        menuLink.addEventListener('click', function(e) {
            // Проверяем, является ли ссылка кнопкой избранного
            if (menuLink.id !== 'favorite-link') {
                // Предотвращаем стандартное поведение ссылки
                e.preventDefault();

                // Получаем атрибут href ссылки
                var targetId = menuLink.getAttribute('href').substring(1); // Убираем символ # и получаем ID элемента

                // Находим элемент с соответствующим ID на странице
                var targetElement = document.getElementById(targetId);

                // Проверяем, существует ли такой элемент
                if (targetElement) {
                    // Вычисляем позицию элемента относительно верхнего края страницы
                    var targetPosition = targetElement.getBoundingClientRect().top;

                    // Добавляем смещение к позиции элемента
                    var offset = 120; // Здесь можете задать свое собственное значение смещения
                    targetPosition -= offset;

                    // Выполняем плавную прокрутку к элементу
                    window.scrollTo({
                        top: window.pageYOffset + targetPosition, // Прокручиваем на расстояние от текущего положения до целевого элемента с учетом смещения
                        behavior: 'smooth' // Добавляем плавность прокрутки
                    });
                }
            }
        });
    });
});

(function () {
    'use strict'

    // Получите все формы, к которым мы хотим применить пользовательские стили проверки Bootstrap
    var forms = document.querySelectorAll('.needs-validation')

    // Зацикливайтесь на них и предотвращайте отправку
    Array.prototype.slice.call(forms)
        .forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault()
                    event.stopPropagation()
                }

                form.classList.add('was-validated')
            }, false)
        })
})()