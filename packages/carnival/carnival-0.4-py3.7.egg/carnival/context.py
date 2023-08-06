from typing import Any, Dict

from fabric import Connection

from carnival.role import Host
from carnival.core.tasks import Tasks


# Global context vars -----------------

# noinspection PyTypeChecker
conn: Connection = None
# noinspection PyTypeChecker
connected_host: Host = None
host_context = None
secrets: Dict[str, Any] = {}
tasks: Tasks = Tasks()


__all__ = [
    'conn',
    'connected_host',
    'host_context',
    'secrets',
    'tasks',
]
