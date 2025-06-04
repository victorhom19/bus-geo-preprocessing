from uuid import UUID, uuid4

import sqlalchemy.types
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class ClusteringData(Base):
    """ Модель данных для хранения файлов, содержащих исходные данные для кластеризации остановок """

    __tablename__ = 'clustering_data'

    id: Mapped[UUID] = mapped_column(sqlalchemy.types.Uuid, primary_key=True, default=uuid4)
    name: Mapped[str]
