class ExecutionContext:
    parent_id: str
    request_id: str
    session_id: str

    def __init__(self, session_id: str, request_id: str, parent_id: str = None):
        self.session_id = session_id
        self.request_id = request_id
        self.parent_id = parent_id
