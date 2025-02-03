from abc import abstractmethod, ABC
from typing import Type

from pydantic import BaseModel


class Agent(BaseModel, ABC):
    name: str
    description: str

    input_schema: Type[BaseModel]
    output_schema: Type[BaseModel]

    @abstractmethod
    def run(self, data: BaseModel):
        """Here goes the actual implementation of the agent."""

    def push_event(self, event):
        pass
