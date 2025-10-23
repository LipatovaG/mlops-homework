# dance_creator.py - создаем анимацию танца Макарена!
import requests
import json
import base64
from PIL import Image
import io
import os


class DanceCreator:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.pose_api_url = "http://localhost:8001"

    def load_pose_database(self):
        """Загружаем базу поз из файла"""
        with open('../step3_rag/poses_database.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    def find_macarena_poses(self, poses_data):
        """Ищем позы для танца Макарена"""
        macarena_poses = []
        for pose in poses_data:
            if 'макарена' in pose['description'].lower():
                macarena_poses.append(pose)

        # Выводим найденные позы для отладки
        print("🔍 Найденные позы Макарены:")
        for i, pose in enumerate(macarena_poses):
            print(f"   {i}: {pose['description']}")

        return macarena_poses

    def create_pose_image(self, pose_data):
        """Создаем изображение для позы"""
        try:
            response = requests.post(
                f"{self.pose_api_url}/visualize",
                json={"pose": pose_data}
            )

            if response.status_code == 200:
                result = response.json()
                # Декодируем base64 в изображение
                img_data = base64.b64decode(result['image'])
                return Image.open(io.BytesIO(img_data))
            else:
                print(f"❌ Ошибка визуализации позы: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Ошибка подключения к Pose API: {e}")
            return None

    def create_macarena_animation(self):
        """Создаем анимацию танца Макарена"""
        print("💃 Создаем танец Макарена...")

        # 1. Загружаем базу поз
        poses = self.load_pose_database()
        print(f"📚 Загружено {len(poses)} поз")

        # 2. Ищем позы для Макарены
        macarena_poses = self.find_macarena_poses(poses)

        if not macarena_poses:
            print("❌ Не найдены позы для Макарены!")
            return False

        print(f"🎯 Найдено {len(macarena_poses)} поз для Макарены")

        # 3. Используем ВСЕ найденные позы Макарены
        sequence = macarena_poses

        print(f"🎬 Создаем последовательность из {len(sequence)} поз...")

        # 4. Создаем изображения для каждой позы
        images = []
        for i, pose in enumerate(sequence):
            print(f"  🖼️ Создаем позу {i + 1}/{len(sequence)}: {pose['description'][:30]}...")
            img = self.create_pose_image(pose['pose'])
            if img:
                images.append(img)
            else:
                print(f"   ❌ Не удалось создать изображение для позы {i + 1}")

        if len(images) < 2:
            print(f"❌ Создано только {len(images)} изображений, нужно минимум 2 для анимации!")
            return False

        # 5. Сохраняем как GIF анимацию
        print("📹 Сохраняем GIF анимацию...")

        try:
            # Сохраняем первое изображение и добавляем остальные
            images[0].save(
                'macarena_dance.gif',
                save_all=True,
                append_images=images[1:],
                duration=800,  # увеличим длительность для лучшей видимости
                loop=0,  # бесконечный цикл
                optimize=True
            )

            print("✅ Анимация сохранена как 'macarena_dance.gif'!")

            # Показываем размер файла
            file_size = os.path.getsize('macarena_dance.gif')
            print(f"📊 Размер файла: {file_size} байт")

            return True
        except Exception as e:
            print(f"❌ Ошибка при сохранении GIF: {e}")
            return False


def main():
    print("=" * 50)
    print("🕺 СОЗДАТЕЛЬ ТАНЦЕВ - ТАНЕЦ МАКАРЕНА")
    print("=" * 50)

    creator = DanceCreator()

    # Проверяем сервисы
    print("\n🔍 Проверяем сервисы...")
    try:
        # Проверяем Pose API
        health_response = requests.get(f"{creator.pose_api_url}/health")
        print(f"✅ Pose API: {health_response.status_code}")

        # Проверяем Ollama
        ollama_response = requests.get(f"{creator.ollama_url}/api/tags")
        print(f"✅ Ollama: {ollama_response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка проверки сервисов: {e}")
        return

    # Создаем анимацию
    print("\n" + "=" * 30)
    success = creator.create_macarena_animation()

    if success:
        print("\n🎉 ТАНЕЦ МАКАРЕНА УСПЕШНО СОЗДАН!")
        print("📁 Файл: 'macarena_dance.gif'")
        print("🎯 Задание выполнено!")

        # Проверяем, что файл действительно создан
        if os.path.exists('macarena_dance.gif'):
            print("✅ Файл 'macarena_dance.gif' найден в папке проекта!")
        else:
            print("❌ Файл 'macarena_dance.gif' не найден!")
    else:
        print("\n❌ Не удалось создать анимацию")


if __name__ == "__main__":
    main()
