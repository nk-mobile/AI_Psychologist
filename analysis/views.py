# Create your views here.
import os
import markdown  # <-- Импортируем markdown
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .models import ImgTest
from openai import OpenAI
import base64
from PIL import Image, ImageOps  # <-- Импортируем необходимые модули из Pillow
from io import BytesIO

# Инициализация клиента OpenAI с использованием переменной окружения
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), # <-- Используем os.getenv
    base_url="https://openai.api.proxyapi.ru/v1",
)

def resize_image(image_path, output_size=(400, 400)):
    """
    Изменяет размер изображения, сохраняя пропорции, и добавляет белые поля при необходимости.
    Сохраняет результат поверх оригинального файла.
    """
    try:
        with Image.open(image_path) as img:
            # Конвертируем в RGB, если изображение в другом режиме (например, RGBA, Palletted)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Масштабируем изображение, сохраняя пропорции, чтобы оно поместилось в output_size
            img.thumbnail(output_size, Image.Resampling.LANCZOS)

            # Создаем новое изображение с целевым размером и белым фоном
            new_img = Image.new("RGB", output_size, (255, 255, 255))

            # Вычисляем координаты для центрирования уменьшенного изображения
            x = (output_size[0] - img.width) // 2
            y = (output_size[1] - img.height) // 2

            # Вставляем уменьшенное изображение по центру
            new_img.paste(img, (x, y))

            # Сохраняем поверх оригинального файла
            # Используем JPEG, так как он поддерживается OpenAI Vision и обычно меньше по размеру
            new_img.save(image_path, 'JPEG', quality=85, optimize=True)

        return True
    except Exception as e:
        print(f"Ошибка при изменении размера изображения: {e}")
        return False

def analyze_image_with_gpt(image_path):
    """Анализ изображения через OpenAI Vision API"""
    # Открываем файл в двоичном режиме для кодирования в base64
    with open(image_path, "rb") as img:
        b64_img = "data:image/jpeg;base64," + base64.b64encode(img.read()).decode()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Ты психолог, анализируешь эмоциональное состояние по рисунку."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Определи основную эмоцию на рисунке (одно слово) и дай краткий психологический отчёт (до 5 строк)."
                    },
                    {"type": "image_url", "image_url": {"url": b64_img}}
                ]
            }
        ]
    )
    result = response.choices[0].message.content.strip()

    # ✅ Разбор: первая строка — эмоция, остальное — отчёт
    lines = [line.strip() for line in result.split("\n") if line.strip()]

    if len(lines) == 1:  # Если OpenAI вернул всё в одной строке
        if "." in lines[0]:
            emotion, report = lines[0].split(".", 1)
            emotion = emotion.strip()
            report = report.strip()
        else:
            emotion, report = lines[0], ""
    else:
        emotion = lines[0]
        report = "\n".join(lines[1:])

    return {"emotion": emotion[:100], "report": report[:500]}

@login_required
def upload_image(request):
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]

        # Сохраняем на диск
        fs = FileSystemStorage(location=settings.MEDIA_ROOT + "/drawings")
        filename = fs.save(image.name, image)
        file_path = f"drawings/{filename}"
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)

        # --- ДОБАВЛЕНО: Изменение размера изображения ---
        # Перед анализом изменяем размер изображения до 400x400
        resize_success = resize_image(full_path, (400, 400))
        if not resize_success:
             # Можно добавить сообщение об ошибке пользователю
             # messages.error(request, "Не удалось обработать изображение.")
             pass # Или просто продолжаем с оригинальным изображением
        # --- КОНЕЦ ДОБАВЛЕНИЯ ---

        # Отправляем в OpenAI Vision (теперь с измененным размером)
        analysis = analyze_image_with_gpt(full_path)

        ImgTest.objects.create(
            user=request.user,
            i_path=file_path,
            i_state=analysis["emotion"],
            i_comment=analysis["report"]
        )
        return redirect("image_history")

    return render(request, "analysis/upload.html")


@login_required
def image_history(request):
    # Получаем изображения
    images = ImgTest.objects.filter(user=request.user).order_by("-created_at")

    # --- ОБНОВЛЕНО: Преобразование Markdown в HTML для i_comment и i_state ---
    # Создаем новый список для хранения изображений с отформатированными полями
    images_with_html = []
    md = markdown.Markdown()  # Создаем экземпляр один раз для эффективности

    for img in images:
        # Преобразуем Markdown в HTML для комментария
        formatted_comment = md.convert(img.i_comment)
        # Преобразуем Markdown в HTML для эмоции/состояния
        formatted_state = md.convert(img.i_state)

        # Создаем словарь с новыми полями
        img_data = {
            'object': img,
            'i_id': img.i_id,
            'i_path': img.i_path,
            'i_state': img.i_state,  # Оригинальный текст
            'i_state_html': formatted_state,  # Отформатированный HTML
            'i_comment': img.i_comment,  # Оригинальный текст
            'i_comment_html': formatted_comment,  # Отформатированный HTML
            'created_at': img.created_at,
        }
        images_with_html.append(img_data)
    # --- КОНЕЦ ОБНОВЛЕНИЯ ---

    # Передаем в шаблон список с отформатированными полями
    return render(request, "analysis/history.html", {"images": images_with_html})