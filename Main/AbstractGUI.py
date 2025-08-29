from abc import ABC, abstractmethod

class AbstractGUI(ABC):
    @abstractmethod
    def show_message(self, message: str) -> None:
        pass

    @abstractmethod
    def get_input(self, prompt: str) -> str:
        pass

    @abstractmethod
    def show_error(self, error: str) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass