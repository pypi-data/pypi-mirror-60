import typing as t

from ..database import DataPoint
from ..exceptions import IncompatibleTriggerError

T_value = t.TypeVar("T_value")


class Trigger(t.Generic[T_value]):
    name: str

    async def start(self) -> None:
        return

    async def match(self, datapoint: DataPoint) -> bool:
        raise NotImplementedError

    async def extract(self, datapoint: DataPoint) -> T_value:
        raise NotImplementedError

    async def handle(self, datapoint: DataPoint) -> DataPoint:
        if not await self.match(datapoint):
            raise IncompatibleTriggerError("Not a relevant datapoint")
        else:
            value = await self.extract(datapoint)  # type: ignore
        return DataPoint(
            sensor_name=self.name,
            data=value,
            deployment_id=datapoint.deployment_id,
            collected_at=datapoint.collected_at,
        )


class Action:
    async def start(self) -> None:
        return

    async def handle(self, datapoint: DataPoint):
        raise NotImplementedError
