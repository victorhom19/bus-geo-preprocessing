import pytest

from app.schemas.enums import BusDataProvider
from app.services.bus_data.osm.osm_bus_data_provider import OSMBusDataProvider
from tests.test_services.bus_data.overpass_api_mock import OverpassApiMock


@pytest.mark.asyncio
class TestBusDataService:

    @pytest.mark.asyncio
    async def test_load_osm_empty_stops(self):
        """ Тест получения данных об остановках от OSM (пустой набор) """
        overpass_api_mock = OverpassApiMock()
        overpass_api_mock.load_empty()
        bbox = (30.38193643263723, 59.99855059711348, 30.39241435827749, 60.00717280149259)
        stops = await OSMBusDataProvider(overpass_api_mock=overpass_api_mock).get_stops_in_bbox(bbox)
        assert len(stops) == 0

    @pytest.mark.asyncio
    async def test_load_osm_base_stops(self):
        """ Тест получения данных об остановках от OSM (базовый сценарий) """
        overpass_api_mock = OverpassApiMock()
        overpass_api_mock.load_base_stops()
        bbox = (30.38193643263723, 59.99855059711348, 30.39241435827749, 60.00717280149259)
        stops = await OSMBusDataProvider(overpass_api_mock=overpass_api_mock).get_stops_in_bbox(bbox)
        assert len(stops) == 3
        stops_names = 'Остановка 1', 'Остановка 2', 'Остановка 3'
        for stop in stops:
            assert stop.name in stops_names

    @pytest.mark.asyncio
    async def test_load_osm_empty_routes(self):
        """ Тест получения данных о маршрутах OSM (пустой набор) """
        overpass_api_mock = OverpassApiMock()
        overpass_api_mock.load_empty()
        bbox = (30.38193643263723, 59.99855059711348, 30.39241435827749, 60.00717280149259)
        routes = await OSMBusDataProvider(overpass_api_mock=overpass_api_mock).get_routes_in_bbox(bbox)
        assert len(routes) == 0

    @pytest.mark.asyncio
    async def test_load_osm_base_routes(self):
        """ Тест получения данных о маршрутах OSM (базовый сценарий) """
        overpass_api_mock = OverpassApiMock()
        overpass_api_mock.load_base_routes()
        bbox = (30.37230429715162, 59.99280989676329, 30.39241435827749, 60.00717280149259)

        routes = await OSMBusDataProvider(overpass_api_mock=overpass_api_mock).get_routes_in_bbox(bbox)
        assert len(routes) == 1

        route = routes[0]
        assert route.name == 'Маршрут 1'

        assert len(route.stops) == 8

    @pytest.mark.asyncio
    async def test_load_osm_complex_geometry_routes(self):
        """ Тест получения данных о маршрутах OSM (усложненный сценарий для проверки трассировки геометрии) """
        overpass_api_mock = OverpassApiMock()
        overpass_api_mock.load_complex_geometry_routes()
        bbox = (30.381612209325752, 60.013091738149, 30.41004456678565, 60.02400742890481)

        routes = await OSMBusDataProvider(overpass_api_mock=overpass_api_mock).get_routes_in_bbox(bbox)
        assert len(routes) == 1

        route = routes[0]
        assert route.name == 'Маршрут 1'

        assert len(route.stops) == 3
        assert len(route.geometry) == 7

    @pytest.mark.asyncio
    async def test_load_osm_missing_data_routes(self):
        """ Тест получения данных о маршрутах OSM (усложненный сценарий для проверки восстановления данных) """
        overpass_api_mock = OverpassApiMock()
        overpass_api_mock.load_missing_data_routes()
        bbox = (30.37230429715162, 59.99280989676329, 30.39241435827749, 60.00717280149259)

        routes = await OSMBusDataProvider(overpass_api_mock=overpass_api_mock).get_routes_in_bbox(bbox)
        assert len(routes) == 1

        route = routes[0]
        assert route.name == 'Маршрут 1'

        assert len(route.stops) == 8

    @pytest.mark.asyncio
    async def test_load_osm_exceeding_routes(self):
        """ Тест получения данных о маршрутах OSM (маршруты вне ограничивающей рамки) """
        overpass_api_mock = OverpassApiMock()
        overpass_api_mock.load_exceeding_routes()
        bbox = (30.38193643263723, 59.99855059711348, 30.38865105619695, 60.00227097675528)

        routes = await OSMBusDataProvider(overpass_api_mock=overpass_api_mock).get_routes_in_bbox(bbox)
        assert len(routes) == 0

    @pytest.mark.asyncio
    async def test_load_osm_bad_routes(self):
        """ Тест получения данных о маршрутах OSM (есть некорректный маршрут) """
        overpass_api_mock = OverpassApiMock()
        overpass_api_mock.load_bad_routes()
        bbox = (30.37230429715162, 59.99280989676329, 30.39241435827749, 60.00717280149259)

        routes = await OSMBusDataProvider(overpass_api_mock=overpass_api_mock).get_routes_in_bbox(bbox)
        assert len(routes) == 1

    @pytest.mark.asyncio
    async def test_load_osm_base_stops_and_routes(self):
        """ Тест получения данных об остановках и маршрутах OSM (базовый сценарий) """
        overpass_api_mock = OverpassApiMock()
        overpass_api_mock.load_base_routes_reversed()
        bbox = (30.37230429715162, 59.99280989676329, 30.39241435827749, 60.00717280149259)

        result = await OSMBusDataProvider(overpass_api_mock=overpass_api_mock).get_bus_data_in_bbox(bbox)
        routes = result.routes

        assert len(routes) == 1
        route = routes[0]
        assert route.name == 'Маршрут 1'
        assert len(route.stops) == 8
