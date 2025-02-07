# SDK for Leea Agent Protocol
Project is in active development stage, so don't judge us harshly!

### Installation:
For now use `git+ssh://git@github.com/Leea-Labs/leea-agent-sdk` in requirements.txt or just for pip install

### Example agent:

```python
from typing import Type

from pydantic import BaseModel, Field

from leea_agent_sdk.agent import Agent
from leea_agent_sdk.runtime import start

class SummarizerAgentInput(BaseModel):
    a: int = Field(description="A")
    b: int = Field(description="B")


class SummarizerAgentOutput(BaseModel):
    value: int = Field(description="data field")


class SummarizerAgent(Agent):
    name: str = "Summarizer"
    description: str = "Agent that can calculate a + b"

    input_schema: Type[BaseModel] = SummarizerAgentInput
    output_schema: Type[BaseModel] = SummarizerAgentOutput

    async def run(self, request_id: str, input: SummarizerAgentInput) -> SummarizerAgentOutput:
        await self.push_log(request_id, "Calculating!")
        return SummarizerAgentOutput(value=input.a + input.b)


if __name__ == '__main__':
    start(SummarizerAgent())
```


