import json
import os

from tqdm import tqdm

from config import SRC_PATH
from app.services.traffic_flow.base_traffic_flow_provider import TrafficFlowSegment

# Скрипт предобработки данных загруженности дорог на основе отчётов TomTom Stats.
# * Исходные файлы отчётов в формате json размещаются в директории raw_data. Скрипт конвертирует файл отчёта в
# * файл json-файл со схемами сегментов, которые могут быть непосредственно применены к геометрии маршрута.
# * Выходные файлы сохраняются в директорию preprocessed_data.


HOURS = 24

if __name__ == '__main__':

    # Определение путей до директорий с исходными и выходными данными
    raw_data_path = os.path.join(SRC_PATH, 'services/traffic_flow/tomtom/raw_data')
    preprocessed_out_path = os.path.join(SRC_PATH, 'services/traffic_flow/tomtom/preprocessed_data')

    bbox = 30.34509360614633, 59.92272050364813, 30.439941343968666, 59.990767640018554

    # Обход исходных файлов
    for filename in os.listdir(raw_data_path):

        if not filename.startswith('spb'):
            continue

        # Проверка на существование выходного файла
        print(f"Processing {filename}:")
        out_file = os.path.join(preprocessed_out_path, 'test_' + filename)
        if os.path.exists(out_file):
            print(f"Skipping (exists in {out_file})")
            continue

        # Открытие файла
        print(f"Opening file...", end="")
        raw_data_file_path = os.path.join(raw_data_path, filename)
        with open(raw_data_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        print(f"\rDone!\t\t\t")

        # Парсинг сегментов
        segments = {h: [] for h in range(HOURS)}
        for raw_segment in tqdm(data.get('network').get('segmentResults')):

            # Парсинг точек сегмента
            point1 = raw_segment.get('shape')[0].get('latitude'), raw_segment.get('shape')[0].get('longitude')
            point2 = raw_segment.get('shape')[1].get('latitude'), raw_segment.get('shape')[1].get('longitude')

            point1_is_inside_bbox = bbox[1] <= point1[0] <= bbox[3] and bbox[0] <= point1[1] <= bbox[2]
            point2_is_inside_bbox = bbox[1] <= point1[0] <= bbox[3] and bbox[0] <= point1[1] <= bbox[2]

            if not point1_is_inside_bbox or not point2_is_inside_bbox:
                continue

            for hour in range(HOURS):
                # Определение скорости в зависимости от временного интервала
                speed = raw_segment.get('segmentTimeResults')[hour].get('averageSpeed')

                # Создание схемы сегмента
                segments[hour].append(TrafficFlowSegment(
                    first_point=point1,
                    second_point=point2,
                    speed=speed
                ).json())

        # Сохранение данных в выходной файл
        with open(out_file, 'w') as file:
            json.dump(segments, file)