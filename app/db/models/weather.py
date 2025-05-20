from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import INTEGER, NUMERIC, TIMESTAMP, VARCHAR
from sqlalchemy.sql import func

from app.db import DeclarativeBase


class Central(DeclarativeBase):
    __tablename__ = "central"

    id = Column(
        INTEGER,
        primary_key=True,
        autoincrement=True,
        doc="Unique id of the string in table",
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Date and time when string in table was created",
    )
    temperature = Column(
        NUMERIC(precision=4, scale=1),
        nullable=False,
        doc="Temperature in Celsius",
    )
    humidity = Column(
        NUMERIC(precision=4, scale=1),
        nullable=False,
        doc="Humidity in %",
    )
    pressure = Column(
        NUMERIC(precision=6, scale=1),
        nullable=False,
        doc="Pressure in mmHg",
    )
    co2 = Column(
        INTEGER,
        nullable=False,
        doc="CO2 in ppm",
    )
    tvoc = Column(
        INTEGER,
        nullable=False,
        doc="TVOC in ppb",
    )

    def __repr__(self):
        columns = {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
        return (
            f'<{self.__tablename__}: '
            f'{", ".join(map(lambda x: f"{x[0]}={x[1]}", columns.items()))}>'
        )


class Outdoor(DeclarativeBase):
    __tablename__ = "outdoor"

    id = Column(
        INTEGER,
        primary_key=True,
        autoincrement=True,
        doc="Unique id of the string in table",
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Date and time when string in table was created",
    )
    temperature = Column(
        NUMERIC(precision=4, scale=1),
        nullable=False,
        doc="Temperature in Celsius",
    )
    humidity = Column(
        NUMERIC(precision=4, scale=1),
        nullable=False,
        doc="Humidity in %",
    )
    pressure = Column(
        NUMERIC(precision=6, scale=1),
        nullable=False,
        doc="Pressure in mmHg",
    )

    def __repr__(self):
        columns = {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
        return (
            f'<{self.__tablename__}: '
            f'{", ".join(map(lambda x: f"{x[0]}={x[1]}", columns.items()))}>'
        )


class ExternalWeather(DeclarativeBase):
    __tablename__ = "external_weather"

    id = Column(
        INTEGER,
        primary_key=True,
        autoincrement=True,
        doc="Unique id of the string in table",
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Date and time when string in table was created",
    )
    weather_description = Column(
        VARCHAR(255),
        nullable=False,
        doc="Description of the weather",
    )
    temperature_feels_like = Column(
        NUMERIC(precision=4, scale=1),
        nullable=False,
        doc="Feels like temperature in Celsius",
    )
    precipitation = Column(
        NUMERIC(precision=4, scale=1),
        nullable=False,
        doc="Precipitation in mm",
    )
    uv_index = Column(
        NUMERIC(precision=3, scale=1),
        nullable=False,
        doc="UV index",
    )
    wind_speed = Column(
        NUMERIC(precision=4, scale=1),
        nullable=False,
        doc="Wind speed in m/s",
    )

    def __repr__(self):
        columns = {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
        return (
            f'<{self.__tablename__}: '
            f'{", ".join(map(lambda x: f"{x[0]}={x[1]}", columns.items()))}>'
        )
