import datetime
from typing import Optional

from .transport import TransportFactory


class Asset:
    def __init__(
        self,
        transport_factory: TransportFactory,
        id: int,
        tag: str,
        name: str,
        precision: int,
        create_time: datetime.datetime,
        delete_time: Optional[datetime.datetime]
    ):
        self._transport_factory = transport_factory
        self._id: int = int(id)
        self._tag: str = str(tag).strip()
        self._name: str = str(name).strip()
        self._precision: int = int(precision)
        self._create_time: datetime.datetime = create_time
        self._delete_time: Optional[datetime.datetime] = delete_time


class Symbol:
    def __init__(
        self,
        transport_factory: TransportFactory,
        id: int,
        base_asset_id: int,
        quote_asset_id: int,
        create_time: datetime.datetime,
        delete_time: Optional[datetime.datetime]
    ):
        self._transport_factory = transport_factory
        self._id: int = int(id)
        self._base_asset_id: int = int(base_asset_id)
        self._quote_asset_id: int = int(quote_asset_id)
        self._create_time: datetime.datetime = create_time
        self._delete_time: Optional[datetime.datetime] = delete_time
