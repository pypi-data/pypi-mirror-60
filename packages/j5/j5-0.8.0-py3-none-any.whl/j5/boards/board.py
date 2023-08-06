"""The base classes for boards and group of boards."""

import atexit
import logging
import os
import signal
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from types import FrameType
from typing import (
    TYPE_CHECKING,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    Set,
    Type,
    TypeVar,
    cast,
)

from j5.backends import CommunicationError, Environment

if TYPE_CHECKING:  # pragma: nocover
    from j5.components import Component  # noqa
    from typing import Callable, Union

    SignalHandler = Union[
        Callable[[signal.Signals, FrameType], None],
        int,
        signal.Handlers,
        None,
    ]

T = TypeVar('T', bound='Board')
U = TypeVar('U')  # See #489


class Board(metaclass=ABCMeta):
    """A collection of hardware that has an implementation."""

    # BOARDS is a set of currently instantiated boards.
    # This is useful to know so that we can make them safe in a crash.
    BOARDS: Set['Board'] = set()

    def __str__(self) -> str:
        """A string representation of this board."""
        return f"{self.name} - {self.serial}"

    def __new__(cls, *args, **kwargs):  # type: ignore
        """Ensure any instantiated board is added to the boards list."""
        instance = super().__new__(cls)
        Board.BOARDS.add(instance)
        return instance

    def __repr__(self) -> str:
        """A representation of this board."""
        return f"<{self.__class__.__name__} serial={self.serial}>"

    @property
    @abstractmethod
    def name(self) -> str:
        """A human friendly name for this board."""
        raise NotImplementedError  # pragma: no cover

    @property
    @abstractmethod
    def serial(self) -> str:
        """The serial number of the board."""
        raise NotImplementedError  # pragma: no cover

    @property
    @abstractmethod
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def make_safe(self) -> None:
        """Make all components on this board safe."""
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    @abstractmethod
    def supported_components() -> Set[Type['Component']]:
        """The types of component supported by this board."""
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    def make_all_safe() -> None:
        """Make all boards safe."""
        for board in Board.BOARDS:
            board.make_safe()

    @classmethod
    def get_board_group_from_environment(
            cls: Type[T],
            environment: Environment,
    ) -> 'BoardGroup[T, U]':
        """
        Get a board group from an environment.

        This method is on Board, rather than BoardGroup for typing purposes.
        """
        backend = environment.get_backend(cls)

        # Cast is needed here as environment doesn't return a known type.
        return BoardGroup.get_board_group(cls, cast(Type[U], backend))

    @staticmethod
    def _make_all_safe_at_exit() -> None:
        # Register make_all_safe to be called upon normal program termination.
        atexit.register(Board.make_all_safe)

        # Register make_all_safe to be called when a termination signal is received.
        old_signal_handlers: Dict[signal.Signals, SignalHandler] = {}

        def new_signal_handler(signal_type: signal.Signals, frame: FrameType) -> None:
            logging.getLogger(__name__).error("program terminated prematurely")
            Board.make_all_safe()
            # Do what the signal originally would have done.
            signal.signal(signal_type, old_signal_handlers[signal_type])
            os.kill(0, signal_type)  # 0 = current process

        for signal_type in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM):
            old_signal_handler = signal.signal(signal_type, new_signal_handler)
            old_signal_handlers[signal_type] = old_signal_handler


Board._make_all_safe_at_exit()


class BoardGroup(Generic[T, U]):
    """A group of boards that can be accessed."""

    def __init__(self, backend_class: Type[U]) -> None:
        self._backend_class = backend_class
        self._boards: Dict[str, T] = OrderedDict()

        self.update_boards()

    @classmethod
    def get_board_group(cls, _: Type[T], backend: Type[U]) -> 'BoardGroup[T, U]':
        """
        Get the board group with the given types.

        Whilst the first parameter value is not actually used in the function,
        we need it for typing purposes. This is similar to how a ProxyType
        works in Haskell.
        """
        return BoardGroup[T, U](backend)

    def update_boards(self) -> None:
        """Update the boards in this group to see if new boards have been added."""
        self._boards.clear()
        # See  #489 for type ignore explanation
        discovered_boards = self._backend_class.discover()  # type: ignore
        for board in sorted(discovered_boards, key=lambda b: b.serial):
            self._boards.update({board.serial: cast(T, board)})

    def singular(self) -> T:
        """If there is only a single board in the group, return that board."""
        num = len(self)
        if num == 1:
            return list(self._boards.values())[0]
        else:
            # See  #489 for type ignore explanation
            name = self._backend_class.board.__name__  # type: ignore
            raise CommunicationError(
                f"expected exactly one {name} to be connected, but found {num}",
            )

    def make_safe(self) -> None:
        """Make all of the boards safe."""
        for board in self._boards.values():
            board.make_safe()

    def __str__(self) -> str:
        """A string representation of the board group."""
        list_str = ', '.join(map(str, self._boards.values()))

        return f"Group of Boards - [{list_str}]"

    def __repr__(self) -> str:
        """A representation of this board."""
        return f"BoardGroup(backend_class={self._backend_class.__name__})"

    def __len__(self) -> int:
        """Get the number of boards in this group."""
        return len(self._boards)

    def __contains__(self, serial: str) -> bool:
        """Check if a board is in this group."""
        return serial in self._boards

    def __iter__(self) -> Iterator[T]:
        """
        Iterate over the boards in the group.

        The boards are ordered lexiographically by serial number.
        """
        return iter(self._boards.values())

    def __getitem__(self, serial: str) -> T:
        """Get the board from serial."""
        try:
            return self._boards[serial]
        except KeyError:
            if type(serial) != str:
                raise TypeError("Serial must be a string")
            raise KeyError(f"Could not find a board with the serial {serial}")

    @property
    def backend_class(self) -> Type[U]:
        """The Backend that this group uses for Boards."""
        return self._backend_class

    @property
    def boards(self) -> List[T]:
        """Get an unordered list of boards in this group."""
        return list(self._boards.values())
