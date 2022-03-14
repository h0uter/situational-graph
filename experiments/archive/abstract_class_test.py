
from abc import ABC, abstractmethod

class AbstractTest(ABC):

    @abstractmethod
    def __init__(self, x) -> None:
        self.x = x + 1


    
class ConcreteTest(AbstractTest):

    def __init__(self, x) -> None:
        super().__init__(x) # can ensure that every subclass has the same concrete implementation
        self.Q = x

    def test_method(self) -> None:
        print(self.x)
        print(self.Q)


if __name__ == "__main__":
    c = ConcreteTest(3)
    c.test_method()