import json
import os
from datetime import datetime
from typing import List, Tuple

from sklearn.cluster import HDBSCAN
from sklearn.neighbors import KNeighborsClassifier
from tqdm import tqdm

from app.schemas.clustering_profile_schema import TruncatedClusteringProfileSchema
from app.schemas.stops_clustering import CorrespondenceNode, CorrespondenceEntry, StopsClusteringParams, \
    StopsClusteringAlgorithm, ClusteredCorrespondenceNode, ClusteredCorrespondenceEntry
from app.utils import utm_point_from_latlon
from config import SRC_PATH


class StopsClusteringProvider:
    """ Класс для кластеризации остановок """

    async def grid_search(self, params: StopsClusteringParams) -> List[TruncatedClusteringProfileSchema]:
        """ Генерация предварительных профилей кластеризации на основе поиска параметров по сетке """

        # Загрузка исходных узлов и матрицы корреспонденций из файлов
        file_storage_path = os.path.join(SRC_PATH, 'services/stops_clustering/files')
        file_path = os.path.join(file_storage_path, f"{params.clustering_data_id}.json")
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        nodes = [CorrespondenceNode(**json_node) for json_node in data.get('nodes')]
        correspondence = [CorrespondenceEntry(**json_corr) for json_corr in data.get('correspondence')]

        # Задание границ поиска параметров
        hdbscan_min_cluster_size_range = range(2, 52, 2)
        hdbscan_min_samples_range = range(2, 22, 2)

        # Перебор параметров с сохранением результатов
        results = {}
        params.algorithm_params = {}
        for hdbscan_min_cluster_size in tqdm(hdbscan_min_cluster_size_range):
            for hdbscan_min_samples in hdbscan_min_samples_range:
                params_copy = params.model_copy(deep=True)
                params_copy.algorithm_params['hdbscan_eps'] = 0
                params_copy.algorithm_params['hdbscan_min_cluster_size'] = hdbscan_min_cluster_size
                params_copy.algorithm_params['hdbscan_min_samples'] = hdbscan_min_samples
                params_copy.algorithm_params['knn_k'] = 10

                clustering_result = self.clusterize(nodes, params_copy)
                score, clusters_count = self.compute_score(clustering_result, correspondence)

                if params.min_score is not None and score < params.min_score:
                    continue

                if params.max_clusters_count is not None and clusters_count > params.max_clusters_count:
                    continue

                if results.get(clusters_count) is None or score > results[clusters_count][1]:
                    results[clusters_count] = (clusters_count, score, params_copy)

        # Фильтрация полученных профилей кластеризации
        sorted_results = sorted(results.values(), key=lambda x: x[0])
        sifted_results = []
        last_score = 0
        for r in sorted_results:
            clusters_count, score, _ = r
            if score > last_score:
                sifted_results.append(r)
                last_score = score

        return [
            TruncatedClusteringProfileSchema(
                name=f'Temp Clustering Profile #{i}',
                clusters_count=result_entry[0],
                clustering_score=result_entry[1],
                clustering_params=result_entry[2],
            ) for i, result_entry in enumerate(sifted_results)
        ]

    async def realize_clustering_profile(self, params: StopsClusteringParams) \
            -> Tuple[List[ClusteredCorrespondenceNode], List[ClusteredCorrespondenceEntry]]:
        """ Создание профиля кластеризации на основе предварительного """

        # Загрузка исходных узлов и матрицы корреспонденций из файлов
        file_storage_path = os.path.join(SRC_PATH, 'services/stops_clustering/files')
        file_path = os.path.join(file_storage_path, f"{params.clustering_data_id}.json")
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        nodes = [CorrespondenceNode(**json_node) for json_node in data.get('nodes')]
        correspondence = [CorrespondenceEntry(**json_corr) for json_corr in data.get('correspondence')]

        # Кластеризация узлов и перерасчёт матрицы транспортных корреспонденций
        clustered_nodes = self.clusterize(nodes, params)
        clustered_correspondence = self.build_correspondence_matrix(clustered_nodes, correspondence)

        return clustered_nodes, clustered_correspondence

    @classmethod
    def clusterize(cls, nodes: List[CorrespondenceNode], params: StopsClusteringParams) \
            -> List[ClusteredCorrespondenceNode]:
        """ Кластеризация исходных узлов """

        # Расчёт опорных точек на основе заданных параметров кластеризации
        anchor_nodes, anchor_labels, orphan_nodes = cls.__find_anchor_nodes(nodes, params)

        # Определение кластеров для не опорных точек
        orphan_labels = cls.fill_orphan(anchor_nodes, anchor_labels, orphan_nodes, params)

        clustered_reference_nodes = []

        # Создание соответствий между опорными точками и индексами кластеров
        for stop, label in zip(anchor_nodes, anchor_labels):
            clustered_reference_nodes.append(ClusteredCorrespondenceNode(**stop.dict(), cluster_index=label,
                                                                         is_anchor=True))

        # Создание соответствий между не опорными точками и индексами кластеров
        for stop, label in zip(orphan_nodes, orphan_labels):
            clustered_reference_nodes.append(ClusteredCorrespondenceNode(**stop.dict(), cluster_index=label,
                                                                         is_anchor=False))

        return clustered_reference_nodes

    @staticmethod
    def build_correspondence_matrix(clustered_nodes: List[CorrespondenceNode],
                                    correspondence: List[CorrespondenceEntry]) -> List[ClusteredCorrespondenceEntry]:
        """ Перерасчёт матрицы транспортных корреспонденций """

        clustered_correspondence_map = {}
        cluster_index_by_node_id = {node.id: node.cluster_index for node in clustered_nodes}

        for correspondence_entry in correspondence:
            # Определение индексов узлов отправления и прибытия
            node_from_id = correspondence_entry.node_from_id
            node_to_id = correspondence_entry.node_to_id

            # Определение соответствующих индексов кластеров отправления и прибытия
            cluster_from_index = cluster_index_by_node_id[node_from_id]
            cluster_to_index = cluster_index_by_node_id[node_to_id]

            # Определение дня недели и часового интервала
            weekday = datetime.strptime(correspondence_entry.timestamp, '%d.%m.%Y %H:%M').weekday()
            hour_interval = datetime.strptime(correspondence_entry.timestamp, '%d.%m.%Y %H:%M').hour

            # Формирование ключа
            key = (cluster_from_index, cluster_to_index, weekday, hour_interval)

            # Обновление значения корреспонденций
            if key not in clustered_correspondence_map:
                clustered_correspondence_map[key] = 0
            clustered_correspondence_map[key] += correspondence_entry.transitions

        clustered_correspondence = []

        # Формирование выходной матрицы корреспонденций
        for key, transitions in clustered_correspondence_map.items():
            cluster_from_index, cluster_to_index, weekday, hour_interval = key
            clustered_correspondence.append(
                ClusteredCorrespondenceEntry(
                    cluster_from_index=cluster_from_index,
                    cluster_to_index=cluster_to_index,
                    weekday=weekday,
                    hour_interval=hour_interval,
                    transitions=transitions
                )
            )

        return clustered_correspondence

    @classmethod
    def find_anchor_nodes(cls, nodes: List[CorrespondenceNode], params: StopsClusteringParams):
        """ Определение опорных точек"""

        # Конвертация координат референсных узлов в формат UTM
        reference_nodes_as_utm_points = [utm_point_from_latlon(node.lat, node.lon) for node in nodes]

        if params.algorithm is StopsClusteringAlgorithm.HDBSCAN_KNN:

            # Кластеризация алгоритмом HDBSCAN
            labels_after_hdbscan = cls.__hdbscan(
                min_cluster_size=params.algorithm_params.get('hdbscan_min_cluster_size'),
                eps=params.algorithm_params.get('hdbscan_eps'),
                min_samples=params.algorithm_params.get('hdbscan_min_samples'),
                points=reference_nodes_as_utm_points
            )

            # Группировка результатов кластеризации
            anchor_nodes = []
            anchor_labels = []
            orphan_nodes = []
            for node, label in zip(nodes, labels_after_hdbscan):
                if label != -1:
                    anchor_nodes.append(node)
                    anchor_labels.append(label)
                else:
                    orphan_nodes.append(node)
        else:
            raise ValueError("Non-existing clustering algorithm!")

        return anchor_nodes, anchor_labels, orphan_nodes

    @classmethod
    def fill_orphan(cls, anchor_nodes, anchor_labels, orphan_nodes, params):
        """ Определение кластеров для не опорных точек """

        # Конвертация координат референсных остановок в формат UTM (якорные и не-якорные остановки)
        anchor_nodes_as_utm_points = [utm_point_from_latlon(node.lat, node.lon) for node in anchor_nodes]
        orphan_nodes_as_utm_points = [utm_point_from_latlon(node.lat, node.lon) for node in orphan_nodes]

        # Назначение кластеров не-якорным точкам алгоритмом KNN
        orphan_labels = cls.__knn(
            k=params.algorithm_params.get('knn_k'),
            train_points=anchor_nodes_as_utm_points,
            train_labels=anchor_labels,
            points=orphan_nodes_as_utm_points
        )

        return orphan_labels

    @staticmethod
    def __hdbscan(min_cluster_size: int, eps: float, min_samples: int, points) -> List[int]:
        """ Алгоритм кластеризации HDBSCAN """

        hdbscan_clustering = HDBSCAN(
            cluster_selection_epsilon=eps,
            min_cluster_size=min_cluster_size,
            min_samples=int(min_samples),
        ).fit(points)

        return hdbscan_clustering.labels_

    @staticmethod
    def __knn(k: int, train_points, train_labels, points) -> List[int]:
        """ Алгоритм KNN """

        knn_classifier = KNeighborsClassifier(n_neighbors=k, weights='distance')
        knn_classifier.fit(train_points, train_labels)
        predicted_labels = knn_classifier.predict(points)

        return predicted_labels

    @classmethod
    def compute_score(cls, clustered_nodes: List[ClusteredCorrespondenceNode],
                            correspondence: List[CorrespondenceEntry]) -> Tuple[float, int]:
        """ Расчёт характеристик результата кластеризации (полноты и количества кластеров) """

        # Сопоставление остановок и идентификаторов кластеров
        label_by_node_id = {node.id: node.cluster_index for node in clustered_nodes}
        unique_labels = set([node.cluster_index for node in clustered_nodes])

        # Инициализация счётчиков перемещений (общего и между кластерами)
        total_transitions = 0
        external_transitions = 0

        # Обход матрицы корреспонденции
        for corr_entry in correspondence:

            # Получение идентификаторов транспортных зон посадки и высадки
            node_from_label = label_by_node_id[corr_entry.node_from_id]
            node_to_label = label_by_node_id[corr_entry.node_to_id]

            # Увеличение общего счётчика перемещений
            total_transitions += corr_entry.transitions

            if node_from_label != node_to_label:
                # Если транспортные зоны не совпадают - увеличение счётчика внешних перемещений
                external_transitions += corr_entry.transitions

        # Расчёт полноты и итогового количества кластеров
        score, number_of_clusters = external_transitions / total_transitions, len(unique_labels)

        return score, number_of_clusters
