# SDK for Leea Agent Protocol
Project is in active development stage, so don't judge us harshly!

This is framework-agnostic SDK that needed to connect any agent/service into [Leea Agent Protocol](https://docs.leealabs.com/leea-labs/multi-agents-systems/leea-multi-agent-ecosystem-and-tools). 

### Installation:
For now use `git+ssh://git@github.com/Leea-Labs/leea-agent-sdk` in requirements.txt or just for pip install

### Example agent:

```python
import os
from typing import Type, Literal

from pydantic import BaseModel, Field

from leea_agent_sdk.agent import Agent
from leea_agent_sdk.runtime import start
from leea_agent_sdk.context import ExecutionContext


class DividerAgentInput(BaseModel):
    a: int = Field(description="A")
    b: int = Field(description="B")


class DividerAgentOutput(BaseModel):
    value: float = Field(description="data field")


class DividerAgent(Agent):
    name: str = "Divider"
    description: str = "Agent that can calculate a / b"
    
    visibility: Literal["public", "private", "hidden"] = "public"

    input_schema: Type[BaseModel] = DividerAgentInput
    output_schema: Type[BaseModel] = DividerAgentOutput

    async def ready(self):
        print("Agent is ready to serve!")
    
    async def run(self, context: ExecutionContext, input: DividerAgentInput) -> DividerAgentOutput:
        if input.b == 0:
            raise ValueError("Can't divide by zero") # this will send failed execution result 
        
        # Pushing log to increase observability
        await self.push_log(context, "Calculating!")
        
        # Calling other agent
        cool_agent = await self.get_agent("leea/cool-agent")
        await cool_agent.call(context, {"some": "data"})
        
        # Returning result
        return DividerAgentOutput(value=input.a / input.b)


if __name__ == '__main__':
    os.environ['LEEA_API_KEY'] = "..."
    start(DividerAgent(), wallet_path="./wallet.json")
```


