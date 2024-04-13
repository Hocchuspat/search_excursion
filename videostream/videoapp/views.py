# views.py
from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse
import cv2
import numpy as np
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import logout
import os
import time
from django.http import JsonResponse



color = (0, 255, 0)
active_camera = None
class VideoCamera(object):
    def __init__(self):
        self.video = None
        self.faceNet = cv2.dnn.readNet("/Users/egorbelov/test4/videostream/videoapp/vesa/opencv_face_detector_uint8.pb", "/Users/egorbelov/test4/videostream/videoapp/vesa/opencv_face_detector.pbtxt")
        self.genderNet = cv2.dnn.readNet("/Users/egorbelov/test4/videostream/videoapp/vesa/gender_net.caffemodel", "/Users/egorbelov/test4/videostream/videoapp/vesa/gender_deploy.prototxt")
        self.ageNet = cv2.dnn.readNet("/Users/egorbelov/test4/videostream/videoapp/vesa/age_net.caffemodel", "/Users/egorbelov/test4/videostream/videoapp/vesa/age_deploy.prototxt")
        self.MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
        self.genderList = ['Male', 'Female']
        self.ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
        self.stopped = False  # Флаг для прерывания цикла
        self.initialize_camera()

    def initialize_camera(self):
        if self.video is not None:
            self.video.release()
        self.video = cv2.VideoCapture(0)
        self.stopped = False

    def __del__(self):
        self.stop()

    def get_frame(self):
        while not self.stopped:
            success, frame = self.video.read()
            if not success:
                break

            resultImg, faceBoxes = self.highlight_face(frame)
            for faceBox in faceBoxes:
                face = frame[max(0, faceBox[1]):
                             min(faceBox[3], frame.shape[0] - 1), max(0, faceBox[0])
                             :min(faceBox[2], frame.shape[1] - 1)]
                blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), self.MODEL_MEAN_VALUES, swapRB=False)
                self.genderNet.setInput(blob)
                genderPreds = self.genderNet.forward()
                gender = self.genderList[genderPreds[0].argmax()]

                self.ageNet.setInput(blob)
                agePreds = self.ageNet.forward()
                age = self.ageList[agePreds[0].argmax()]

                cv2.putText(resultImg, f'{gender}, {age}', (faceBox[0], faceBox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                            (0, 255, 255), 2, cv2.LINE_AA)

            ret, jpeg = cv2.imencode('.jpg', resultImg)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
            time.sleep(0.1)

    def stop(self):
        self.stopped = True
        if self.video.isOpened():
            self.video.release()

    def highlight_face(self, frame, conf_threshold=0.7):
        frame_opencv_dnn = frame.copy()
        frame_height = frame_opencv_dnn.shape[0]
        frame_width = frame_opencv_dnn.shape[1]
        blob = cv2.dnn.blobFromImage(frame_opencv_dnn, 1.0, (300, 300), [104, 117, 123], True, False)
        self.faceNet.setInput(blob)
        detections = self.faceNet.forward()
        face_boxes = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > conf_threshold:
                x1 = int(detections[0, 0, i, 3] * frame_width)
                y1 = int(detections[0, 0, i, 4] * frame_height)
                x2 = int(detections[0, 0, i, 5] * frame_width)
                y2 = int(detections[0, 0, i, 6] * frame_height)
                face_boxes.append([x1, y1, x2, y2])
                cv2.rectangle(frame_opencv_dnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frame_height / 150)), 8)
        return frame_opencv_dnn, face_boxes

    active_camera = None

def video_feed(request):
    global active_camera
    if active_camera is None or active_camera.stopped:
        active_camera = VideoCamera()
    return StreamingHttpResponse(active_camera.get_frame(), content_type="multipart/x-mixed-replace;boundary=frame")

def generate():
    camera = VideoCamera()
    for frame in camera.get_frame():
        yield frame
    camera.stop()


def stopServerStream(request):
    global active_camera
    if active_camera:
        active_camera.stop()
    return JsonResponse({'status': 'success'})


#Photo

faceProto = "/Users/egorbelov/test4/videostream/videoapp/vesa/opencv_face_detector.pbtxt"
faceModel = "/Users/egorbelov/test4/videostream/videoapp/vesa/opencv_face_detector_uint8.pb"
genderProto = "/Users/egorbelov/test4/videostream/videoapp/vesa/gender_deploy.prototxt"
genderModel = "/Users/egorbelov/test4/videostream/videoapp/vesa/gender_net.caffemodel"
ageProto = "/Users/egorbelov/test4/videostream/videoapp/vesa/age_deploy.prototxt"
ageModel = "/Users/egorbelov/test4/videostream/videoapp/vesa/age_net.caffemodel"

MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
genderList = ['Male', 'Female']
ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']

faceNet = cv2.dnn.readNet(faceModel, faceProto)
genderNet = cv2.dnn.readNet(genderModel, genderProto)
ageNet = cv2.dnn.readNet(ageModel, ageProto)

def highlightFaceim(net, frame, conf_threshold=0.7):
    # делаем копию текущего кадра
    frameOpencvDnn = frame.copy()
    # высота и ширина кадра
    frameHeight = frameOpencvDnn.shape[0]
    frameWidth = frameOpencvDnn.shape[1]
    # преобразуем картинку в двоичный пиксельный объект
    blob = cv2.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)
    # устанавливаем этот объект как входной параметр для нейросети
    net.setInput(blob)
    # выполняем прямой проход для распознавания лиц
    detections = net.forward()
    # переменная для рамок вокруг лица
    faceBoxes = []
    # перебираем все блоки после распознавания
    for i in range(detections.shape[2]):
        # получаем результат вычислений для очередного элемента
        confidence = detections[0, 0, i, 2]
        # если результат превышает порог срабатывания — это лицо
        if confidence > conf_threshold:
            # формируем координаты рамки
            x1 = int(detections[0, 0, i, 3] * frameWidth)
            y1 = int(detections[0, 0, i, 4] * frameHeight)
            x2 = int(detections[0, 0, i, 5] * frameWidth)
            y2 = int(detections[0, 0, i, 6] * frameHeight)
            # добавляем их в общую переменную
            faceBoxes.append([x1, y1, x2, y2])
            # рисуем рамку на кадре
            cv2.rectangle(frameOpencvDnn, (x1, y1), (x2, y2), color, int(round(frameHeight / 150)), 8)

        faceBox = [x1, y1, x2, y2]
        # обрезаем изображение до области лица
        face = frame[y1:y2, x1:x2]
        # получаем пол и возраст
        gender, age = detectGenderAndAge(face)
        # рисуем рамку на кадре
        cv2.rectangle(frameOpencvDnn, (x1, y1), (x2, y2), color, int(round(frameHeight / 150)), 8)
        # добавляем информацию о поле и возрасте
        label = f'{genderList[gender]}, {ageList[age]}'
        cv2.putText(frameOpencvDnn, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2, cv2.LINE_AA)

    # возвращаем кадр с рамками
    return frameOpencvDnn, faceBoxes

def detectGenderAndAge(face):
    blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)

    # отправляем изображение лица в нейросеть для определения пола
    genderNet.setInput(blob)
    genderPreds = genderNet.forward()
    gender = genderPreds[0].argmax()

    # отправляем изображение лица в нейросеть для определения возраста
    ageNet.setInput(blob)
    agePreds = ageNet.forward()
    age = agePreds[0].argmax()

    # возвращаем индексы пола и возрастной категории
    return gender, age

def index(request):
    processed_image_path = request.GET.get('processed_image_path', None)
    return render(request, 'index.html', {'processed_image_path': processed_image_path})


def process_image(request):
    if request.method == 'POST':
        # Получите идентификатор пользователя (здесь используется user_id, но вы можете использовать другой идентификатор)
        user_id = request.user.id if request.user.is_authenticated else 'anonymous_user'

        # Получите имя пользователя (если пользователь аутентифицирован)
        user_name = request.user.username if request.user.is_authenticated else 'anonymous_user'

        img_data = request.FILES.get('photo', None)

        if not img_data:
            return JsonResponse({'error': 'Не предоставлены данные изображения'})

        try:
            img_bytes = img_data.read()
        except Exception as e:
            return JsonResponse({'error': f'Ошибка чтения изображения: {str(e)}'})

        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        resultImg, faceBoxes = highlightFaceim(faceNet, img)

        _, img_encoded = cv2.imencode('.jpg', resultImg)

        # Определите базовый путь к каталогу media/images_user
        base_user_images_directory = 'media/images_user'

        # Создайте подкаталог с именем пользователя
        user_images_directory = os.path.join(base_user_images_directory, user_name)

        # Проверьте, существует ли каталог пользователя, и создайте его, если нет
        if not os.path.exists(user_images_directory):
            os.makedirs(user_images_directory)

        # Генерируйте уникальное имя файла с использованием временной метки
        timestamp = str(int(time.time()))
        filename = f'processed_image_{timestamp}.jpg'

        # Составьте полный путь к файлу в images_user/имя_пользователя
        file_path = os.path.join(user_images_directory, filename)

        # Сохраните обработанное изображение в images_user/имя_пользователя
        with open(file_path, 'wb') as f:
            f.write(img_encoded.tobytes())

        # Получите URL сохраненного изображения в images_user/имя_пользователя
        processed_image_path = f'/{file_path}'

        return JsonResponse({'processed_image_path': processed_image_path})
    else:
        return JsonResponse({'error': 'Недопустимый метод запроса'})




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
