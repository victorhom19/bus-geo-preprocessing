import json
import os
import re
from typing import List, Set, Tuple

from app.schemas.stops_clustering import CorrespondenceEntry, CorrespondenceNode
from config import SRC_PATH


class Parser:
    """ Класс для парсинга csv-файлов матрицы корреспонденций """

    DEFAULT_BBOX = (36.78499177246459, 55.13922739510518, 37.619934418769375, 55.6396477965032)

    @staticmethod
    def parse_stops(nodes_ids: Set[str], nodes_file_name: str = "data.csv") -> List[CorrespondenceNode]:
        """ Функция парсинга данных остановок в pydantic-схемы """

        nodes = []

        # Открытие файла
        nodes_file_path = os.path.join(SRC_PATH, "services/stops_clustering/raw_data", nodes_file_name)
        with open(nodes_file_path, "r") as file:

            # Пропуск строк с названиями столбцов
            file.readline()
            file.readline()

            while True:

                # Построчное чтение файла
                line = file.readline()

                # Выход если не осталось строк
                if not line:
                    break

                # Парсинг csv-строки
                splitted = [_.replace('"', '') for _ in line.split(';')]
                pattern = re.compile("^\{coordinates=\[(?P<lon>.*), (?P<lat>.*)], type=Point}$")
                match = pattern.match(splitted[8])
                lon = float(match.group('lon'))
                lat = float(match.group('lat'))
                node_id = str(splitted[1])

                # Проверка на вхождение в выбранную область и создание pydantic-схемы
                if node_id in nodes_ids:
                    entry = CorrespondenceNode(
                        id=node_id,
                        lon=lon,
                        lat=lat
                    )
                    nodes.append(entry)

        return nodes

    @staticmethod
    def parse_correspondence(correspondence_file_name: str = "data_correspondence.csv") \
            -> Tuple[List[CorrespondenceEntry], Set[str]]:
        """ Функция парсинга данных матрицы корреспонденции в pydantic-схемы """

        correspondence_entries = []

        correspondence_file_path = os.path.join(SRC_PATH, "services/stops_clustering/raw_data", correspondence_file_name)

        nodes_ids = set()

        # Открытие файла
        with open(correspondence_file_path, "r") as file:

            # Пропуск строк с названиями столбцов
            file.readline()

            while True:

                # Построчное чтение файла
                line = file.readline()

                # Выход если не осталось строк
                if not line:
                    break

                # Парсинг csv-строки и создание pydantic-схемы
                splitted = [_.replace('"', '') for _ in line.split(';')]
                entry = CorrespondenceEntry(
                    timestamp=splitted[0],
                    node_from_id=splitted[3],
                    node_to_id=splitted[4],
                    transitions=float(splitted[5].strip()),
                )
                correspondence_entries.append(entry)

                nodes_ids.add(splitted[3])
                nodes_ids.add(splitted[4])

        return correspondence_entries, nodes_ids


if __name__ == '__main__':

    correspondence_entries, nodes_ids = Parser.parse_correspondence('data_correspondence.csv')
    nodes = Parser.parse_stops(nodes_ids, 'data_nodes.csv')

    with open('./preprocessed/combined_data.json', "w", encoding="utf-8") as file:
        nodes_as_dict = [node.dict() for node in nodes]
        correspondence_entries_as_dict = [corr_entry.dict() for corr_entry in correspondence_entries]
        res = {
            'nodes': nodes_as_dict,
            'correspondence': correspondence_entries_as_dict
        }
        json.dump(res, file, indent=4, ensure_ascii=False)