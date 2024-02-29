import requests
import os
import json
from alive_progress import alive_bar
import time

vk_token = ""  # сервисный ключ от приложения в VK


class VK:

    API_BASE_URL_VK = "https://api.vk.com/method/"

    def __init__(self):
        self.id_user = input("Ввод ID: ")

    def get_profile_photos(self):
        url = self.API_BASE_URL_VK + "photos.get"
        params = {
            "access_token": vk_token,
            "owner_id": self.id_user,
            "album_id": "profile",
            "extended": 1,
            "count": 5,
            "v": "5.131",
        }
        response = requests.get(url, params=params)
        return response.json()

    def get_all_photos(self):
        data = self.get_profile_photos()
        all_photo_count = data["response"]["count"]
        i = 0
        count = 50
        photos = []
        max_size_photo = {}

        if not os.path.exists("images_vk"):
            os.mkdir("images_vk")  # Папка на компьютере

        while i <= all_photo_count:
            if i != 0:
                data = self.get_profile_photos(offset=i, count=count)

            for photo in data["response"]["items"]:
                max_size = 0
                photos_info = {}
                for size in photo["sizes"]:
                    if size["height"] >= max_size:
                        max_size = size["height"]
                if photo["likes"]["count"] not in max_size_photo.keys():
                    max_size_photo[photo["likes"]["count"]] = size["url"]
                    photos_info["file_name"] = f"{photo['likes']['count']}.jpg"
                else:
                    max_size_photo[f"{photo['likes']['count']} + {photo['date']}"] = (
                        size["url"]
                    )
                    photos_info["file_name"] = (
                        f"{photo['likes']['count']}+{photo['date']}.jpg"
                    )
                photos_info["size"] = size["type"]  # Список всех фотографий
                photos.append(photos_info)

            for photo_name, photo_url in max_size_photo.items():
                with open("images_vk/%s" % f"{photo_name}.jpg", "wb") as file:
                    img = requests.get(photo_url)
                    file.write(img.content)
            print(f"Загружено {len(max_size_photo)} фото")
            i += count

        with open("photos.json", "w") as file:
            json.dump(photos, file, indent=4)  # Фото в файл .json


class Yandex:

    def __init__(self, ya_token):
        self.token = ya_token

    def folder_creation(self):
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"OAuth {ya_token}",
        }
        params = {"path": f"{folder_name}", "overwrite": "false"}
        response = requests.put(url=url, headers=headers, params=params)
        if response.status_code == 201:
            print("Папка создана")
        else:
            print("Папка уже существует")

    def upload(self, files_path: str):
        url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"OAuth {ya_token}",
        }
        params = {"path": f"{folder_name}/{file_name}", "overwrite": "true"}
        res = requests.get(url=url, headers=headers, params=params).json()
        with open(files_path, "rb") as file:
            try:
                requests.put(res["href"], files={"file": file})
            except KeyError:
                print(res)


downloader = VK()
downloader.get_all_photos()

ya_token = str(input("Введите ваш токен ЯндексДиск: "))
folder_name = str(
    input("Введите имя папки на Яндекс диске, в которую необходимо сохранить фото: ")
)
uploader = Yandex(ya_token)
uploader.folder_creation()

photos_list = os.listdir("images_vk")
count = 0
with alive_bar(len(photos_list)) as bar:
    for photo in photos_list:
        file_name = photo
        files_path = os.getcwd() + r"\images_vk\\" + photo
        result = uploader.upload(files_path)
        bar()
        time.sleep(0.2)
