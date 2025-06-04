import json
import os

import pytest

from typing import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.database.database import get_session
from app.main import app
from app.database.models import *
from config import PROJECT_ROOT

# URL для базы данных, размещаемой в оперативной памяти
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Инициализация основного объекта для взаимодействия с базой данных
engine = create_async_engine(
    url=TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },
    echo=False,
    poolclass=StaticPool
)

# Создание генератора сессий
AsyncTestingSessionFactory = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
    class_=AsyncSession,
)

# Создание зависимости для получения объекта сессии
async def override_get_session() -> AsyncGenerator:
    async with AsyncTestingSessionFactory() as session:
        yield session

# Переопределение зависимости для API
app.dependency_overrides[get_session] = override_get_session

@pytest_asyncio.fixture(autouse=True)
async def handle_test_database():
    async with engine.begin() as async_conn:
        await async_conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as async_conn:
        await async_conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
class TestAPI:

    @pytest.mark.asyncio
    async def test_bus_data_scenario(self):
        async_test_client = AsyncClient(base_url='http://test', transport=ASGITransport(app))
        async with async_test_client as tc:

            # Пустая база данных
            response = await tc.get('/bus_data/stops?source=local')
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 0

            # Создание 2 остановок
            with open(os.path.join(PROJECT_ROOT, "tests/test_api/files/stop1.json"), encoding='utf-8') as file:
                stop1 = json.load(file)
            with open(os.path.join(PROJECT_ROOT, "tests/test_api/files/stop2.json"), encoding='utf-8') as file:
                stop2 = json.load(file)
            response = await tc.post('/bus_data/stops?source=local', json=[stop1, stop2])
            assert response.status_code == 200
            data = response.json()
            db_stop1 = data[0]
            assert len(data) == 2

            # Удаление одной остановки
            response = await tc.request('delete', '/bus_data/stops?source=local', json=[db_stop1.get('id')])
            assert response.status_code == 200
            response = await tc.get('/bus_data/stops?source=local')
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

            # Создание 2 маршрутов
            with open(os.path.join(PROJECT_ROOT, "tests/test_api/files/route1.json"), encoding='utf-8') as file:
                route1 = json.load(file)
            with open(os.path.join(PROJECT_ROOT, "tests/test_api/files/route2.json"), encoding='utf-8') as file:
                route2 = json.load(file)
            response = await tc.post('/bus_data/routes?source=local', json=[route1, route2])
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            db_route1 = data[0]

            # Удаление одного маршрута
            response = await tc.request('delete', '/bus_data/routes?source=local', json=[db_route1.get('id')])
            assert response.status_code == 200
            response = await tc.get('/bus_data/routes?source=local')
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

            # Получение остановок вместе с маршрутами
            response = await tc.get('/bus_data/?source=local')
            assert response.status_code == 200
            data = response.json()
            stops = data.get('stops')
            routes = data.get('routes')
            assert len(stops) == 90
            assert len(routes) == 1

    @pytest.mark.asyncio
    async def test_traffic_flow_scenario(self):
        async_test_client = AsyncClient(base_url='http://test', transport=ASGITransport(app))
        async with async_test_client as tc:
            files = [
                ('speed_data_files', open(os.path.join(PROJECT_ROOT, "tests/test_api/files/test_spb_monday.json"), 'rb')),
                ('speed_data_files', open(os.path.join(PROJECT_ROOT, "tests/test_api/files/test_spb_tuesday.json"), 'rb')),
                ('speed_data_files', open(os.path.join(PROJECT_ROOT, "tests/test_api/files/test_spb_wednesday.json"), 'rb')),
                ('speed_data_files', open(os.path.join(PROJECT_ROOT, "tests/test_api/files/test_spb_thursday.json"), 'rb')),
                ('speed_data_files', open(os.path.join(PROJECT_ROOT, "tests/test_api/files/test_spb_friday.json"), 'rb')),
                ('speed_data_files', open(os.path.join(PROJECT_ROOT, "tests/test_api/files/test_spb_saturday.json"), 'rb')),
                ('speed_data_files', open(os.path.join(PROJECT_ROOT, "tests/test_api/files/test_spb_sunday.json"), 'rb')),
            ]
            response = await tc.post('/traffic_flow/data', data={'name': 'test'}, files=files)
            assert response.status_code == 200
            data = response.json()
            assert data.get('name') == 'test'

            response = await tc.get('/traffic_flow/data/list')
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            db_speed_data = data[0]

            # Создание маршрута
            with open(os.path.join(PROJECT_ROOT, "tests/test_api/files/route1.json"), encoding='utf-8') as file:
                route1 = json.load(file)
            response = await tc.post('/bus_data/routes?source=local', json=[route1])
            assert response.status_code == 200
            data = response.json()
            db_route1 = data[0]

            response = await tc.post('/traffic_flow/', json={
                "name": "Test Speed Profile",
                "routes_ids": [db_route1.get('id')],
                "speed_data_id": db_speed_data.get('id')
            })
            assert response.status_code == 200
            db_speed_profile = response.json()
            assert db_speed_profile.get('name') == 'Test Speed Profile'
            assert db_speed_profile.get('speed_data_id') == db_speed_data.get('id')
            assert db_route1.get('id') in db_speed_profile.get('routes')

            response = await tc.get('/traffic_flow/list')
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

            response = await tc.get(f'/traffic_flow/{db_speed_profile.get("id")}')
            assert response.status_code == 200

            response = await tc.delete(f'/traffic_flow/{db_speed_profile.get("id")}')
            assert response.status_code == 200
            response = await tc.get('/traffic_flow/list')
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 0

            response = await tc.delete(f'/traffic_flow/data/{db_speed_data.get("id")}')
            assert response.status_code == 200

            response = await tc.get('/traffic_flow/data/list')
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 0

    @pytest.mark.asyncio
    async def test_stops_clustering_scenario(self):
        async_test_client = AsyncClient(base_url='http://test', transport=ASGITransport(app))
        async with async_test_client as tc:
            files = {
                'clustering_data_file': open(
                    os.path.join(PROJECT_ROOT, "tests/test_api/files/test_clustering_data.json"), 'rb')
            }
            response = await tc.post('/stops_clustering/data', data={'name': 'test'}, files=files)
            assert response.status_code == 200
            data = response.json()
            assert data.get('name') == 'test'

            response = await tc.get('/stops_clustering/data/list')
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            db_clustering_data = data[0]

            generate_clustering_profile_params = {
                "name": "test",
                "params": {
                    "algorithm": "hdbscan_knn",
                    "min_score": 0.8,
                    "clustering_data_id": db_clustering_data.get('id')
                }
            }
            response = await tc.post('/stops_clustering/generate', json=generate_clustering_profile_params)
            assert response.status_code == 200
            db_temp_clustering_profiles = response.json()
            assert len(db_temp_clustering_profiles) > 0

            selected_clustering_profile = db_temp_clustering_profiles[0]
            selected_clustering_profile['name'] = 'Realized Clustering Profile Test'
            response = await tc.post('/stops_clustering/realize', json=selected_clustering_profile)
            assert response.status_code == 200
            data = response.json()
            assert data.get('name') == 'Realized Clustering Profile Test'
            realized_clustering_profile = data

            response = await tc.get('/stops_clustering/list')
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

            with open(os.path.join(PROJECT_ROOT, "tests/test_api/files/stop1.json"), encoding='utf-8') as file:
                stop1 = json.load(file)
            response = await tc.post('/bus_data/stops?source=local', json=[stop1])
            assert response.status_code == 200
            data = response.json()
            db_stop = data[0]

            response = await tc.post(f'/stops_clustering/{realized_clustering_profile.get("id")}', json=[db_stop.get('id')])
            assert response.status_code == 200
            data = response.json()
            assert len(data.get('clustered_stops')) == 1
            clustered_stop = data.get('clustered_stops')[0]
            assert 'cluster_index' in clustered_stop

            response = await tc.delete(f'/stops_clustering/{realized_clustering_profile.get("id")}')
            assert response.status_code == 200

            response = await tc.delete(f'/stops_clustering/data/{db_clustering_data.get("id")}')
            assert response.status_code == 200


