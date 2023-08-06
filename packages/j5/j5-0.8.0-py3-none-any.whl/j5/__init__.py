"""j5 Robotics API."""

from .backends import Environment
from .base_robot import BaseRobot
from .boards import BoardGroup

__all__ = [
    "BoardGroup",
    "BaseRobot",
    "Environment",
    "__version__",
    "__version_short__",
]

__version__ = "0.8.0"
__version_short__ = "0.8.0"
