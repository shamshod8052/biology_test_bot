from typing import Dict, Any, Optional, cast, Union

from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType
from aiogram.fsm.storage.redis import KeyBuilder, DefaultKeyBuilder
from django.core.cache import cache
from redis.typing import ExpiryT


class DjangoRedisStorage(BaseStorage):
    def __init__(
        self,
        key_builder: Optional[KeyBuilder] = None,
        state_ttl: Optional[ExpiryT] = None,
        data_ttl: Optional[ExpiryT] = None,
    ):
        self.key_builder = key_builder or DefaultKeyBuilder()
        self.state_ttl = state_ttl
        self.data_ttl = data_ttl

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        redis_key = self.key_builder.build(key, "state")
        if state is None:
            await cache.adelete(redis_key)
        else:
            await cache.aset(
                redis_key,
                str(state.state if isinstance(state, State) else state),
                self.state_ttl,
            )

    async def get_state(self, key: StorageKey) -> Optional[str]:
        redis_key = self.key_builder.build(key, "state")
        value = await cache.aget(redis_key)
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return cast(Optional[str], value)

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        redis_key = self.key_builder.build(key, "data")
        if not data:
            await cache.adelete(redis_key)
        else:
            # You can replace with your own serialization logic
            import json
            await cache.aset(redis_key, json.dumps(data), self.data_ttl)

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        redis_key = self.key_builder.build(key, "data")
        value = await cache.aget(redis_key)
        if value is None:
            return {}
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        import json
        return cast(Dict[str, Any], json.loads(value))

    async def delete_state(self, key: StorageKey) -> None:
        await cache.adelete(self.key_builder.build(key, "state"))

    async def delete_data(self, key: StorageKey) -> None:
        await cache.adelete(self.key_builder.build(key, "data"))

    async def close(self) -> None:
        # Django cache does not require closing, but if using a custom one:
        try:
            await cache.aclose()
        except AttributeError:
            pass
