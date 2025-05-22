from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import VARCHAR

from app.db import DeclarativeBase


class Setting(DeclarativeBase):
    __tablename__ = "settings"

    key = Column(
        VARCHAR(255),
        primary_key=True,
        doc="Key of the setting",
    )
    value = Column(
        VARCHAR(255),
        nullable=False,
        doc="Value of the setting",
    )
    type = Column(
        VARCHAR(255),
        nullable=False,
        doc="Type of the setting",
    )

    def __repr__(self):
        columns = {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
        return (
            f'<{self.__tablename__}: '
            f'{", ".join(map(lambda x: f"{x[0]}={x[1]}", columns.items()))}>'
        )
