from typing import Any
from typing import Dict


class Singleton(type):
    _instances: Dict[type, Any] = {}

    def __call__(cls: Any, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]
