import cv2

def start():
    face_cascade = cv2.CascadeClassifier('face_detection.xml')

    video_capture = cv2.VideoCapture(1)

    while True:
        # Захват экрана
        ret, frame = video_capture.read()

        # Переводим в серое изображение
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Определяем положение лица на изображении
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=10,
            minSize=(40, 40)
        )

        # Рисуем прямоугольники вокруг лиц по полученным данным
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)

        # Выводим изображение
        cv2.imshow('Video', frame)

        # Прослушивание клавиши выхода
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Выключаем видео
    video_capture.release()
    # Закрываем окно
    cv2.destroyAllWindows()


if __name__ == '__main__':
    start()
