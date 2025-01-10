from functools import partial

from crewai import Crew

from leea.protocol import AgentHello, RunRequest
from leea.transport import Transport


def callback(name, *args, **kwargs):
    print(f"{name} called")
    print(args)
    print(kwargs)


def run(agent_schema, crew: Crew):
    hello = AgentHello(
        name=agent_schema.name,
        description=agent_schema.description,
        input_schema=agent_schema.input_schema.model_json_schema()
    )
    transport = Transport(agent_schema.name)
    transport.handshake()
    transport.send(hello)

    crew.before_kickoff_callbacks.append(partial(callback, 'before_kickoff'))
    crew.after_kickoff_callbacks.append(partial(callback, 'after_kickoff'))
    crew.step_callback = partial(callback, 'step')
    crew.task_callback = partial(callback, 'task')

    print("Waiting for call")
    while True:
        msg = transport.receive()
        if isinstance(msg, RunRequest):
            crew.kickoff(msg.input)
