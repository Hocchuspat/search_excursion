
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();

            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);

            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop,
                    behavior: 'smooth' // Добавляем плавную анимацию
                });
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const toggleButtons = document.querySelectorAll('.toggle-button');

    toggleButtons.forEach(button => {
        button.addEventListener('click', function () {
            const codeContent = this.nextElementSibling;

            if (codeContent.style.display === 'block') {
                codeContent.style.display = 'none';
            } else {
                codeContent.style.display = 'block';
            }
        });
    });
});


// video_control.js
$(document).ready(function () {
    if (isAuthenticated) {
        var videoPlaying = false; // Переменная для отслеживания состояния видеопотока
        var buttonText = "Start"; // Текущий текст кнопки

        $("#startStream").click(function () {
            if (videoPlaying) {
                stopVideoStream();
            } else {
                startVideoStream();
            }
        });

        function startVideoStream() {
            var videoContainer = $("#videoContainer");
            videoContainer.html('<img id="videoStream" alt="Видеопоток">');

            // Добавляем класс для стилизации при активации видеопотока
            videoContainer.addClass("active");

            var imgElement = document.getElementById('videoStream');
            imgElement.src = "/video_feed/";  // Здесь должен быть правильный URL для видеопотока
            videoPlaying = true;

            // Change the color of the button when video starts
            $("#startStream").css({
                'background-color': '#C71585', // Change to the desired color
                'color': '#ffffff' // Change to the desired text color
            });

            // Change the text of the button to "Stop"
            buttonText = "Stop";
            $("#startStream").text(buttonText);
        }

        function stopVideoStream() {
            $.ajax({
                type: 'GET',
                url: '/stop_server_stream/',  // Путь к новому представлению, обрабатывающему остановку видеопотока на сервере
                success: function (data) {
                    var videoContainer = $("#videoContainer");
                    videoContainer.html('');

                    // Убираем класс для стилизации при остановке видеопотока
                    videoContainer.removeClass("active");

                    videoPlaying = false;

                    // Restore the original color of the button when video stops
                    $("#startStream").css({
                        'background-color': '', // Restore the original color
                        'color': '' // Restore the original text color
                    });

                    // Change the text of the button to "start/stop"
                    buttonText = "Start";
                    $("#startStream").text(buttonText);

                    location.reload();

                },
                error: function () {
                    // Обработка ошибки, если не удается остановить видеопоток на сервере
                    console.error('Failed to stop server stream.');
                }
            });
        }
    }
});


//Photo
$(document).ready(function () {
// Change color of the button after a photo is selected
    if (isAuthenticated) {
        //тут нужно изменить цет кнопки

        $('#photo').change(function () {
            if ($(this).val()) {
                $('#processButton').css({
                    'background-color': '#C71585', // Change to the desired color
                    'color': '#ffffff' // Change to the desired text color
                }).removeAttr('disabled');
            }
        });

        // Add additional functionality when the "Process" button is clicked
        $('#processButton').click(function (e) {
            e.preventDefault(); // Отменяем стандартное действие кнопки (отправка формы)

            // Add your custom logic here
            // For example, you can submit the form using AJAX
            uploadAndProcess($(this).data('url'));

            // Disable the button to prevent multiple clicks during processing
            $(this).attr('disabled', 'disabled').text('Processing...');



            // You can re-enable the button if needed after processing is complete
            // $('#processButton').removeAttr('disabled').text('Process');
        });

        function uploadAndProcess(url) {
            var formData = new FormData(document.getElementById('uploadForm'));

            fetch(url, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Обработка ответа сервера
                if (data.processed_image_path) {
                    // Отображение обработанного изображения
                    var processedImage = document.getElementById('processedImage');
                    processedImage.src = data.processed_image_path + '?time=' + new Date().getTime();
                    processedImage.style.display = 'block';
                } else {
                    console.error('Ошибка обработки изображения.');
                }
            })
            .catch(error => console.error('Error:', error))
            .finally(function () {
                // Re-enable the button and restore its original color after processing is complete
                $('#processButton').removeAttr('disabled').css({
                    'background-color': '#5434db', // Change to the desired color
                    'color': '#ffffff' // Change to the desired text color
                }).text('Process');
            });
        }
    }
});


$(document).ready(function () {
    if (!isAuthenticated) {
        // Для первой кнопки
        $('#processButton').click(function () {
            // Показываем сообщение
            $('#registrationMessage').fadeIn();

            // Блокируем кнопку
            $(this).attr('disabled', 'disabled');

            // Скрываем сообщение и разблокируем кнопку через 3 секунды
            setTimeout(function () {
                $('#registrationMessage').fadeOut();
                $('#processButton').removeAttr('disabled');

            }, 3000);
        });

        // Для второй кнопки
        $('#startStream').click(function () {
            // Показываем сообщение
            $('#registrationMessage_2').fadeIn();

            // Блокируем кнопку
            $(this).attr('disabled', 'disabled');

            // Скрываем сообщение и разблокируем кнопку через 3 секунды
            setTimeout(function () {
                $('#registrationMessage_2').fadeOut();
                $('#startStream').removeAttr('disabled');
            }, 3000);
        });
    }
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