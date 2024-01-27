import asyncssh

class ExposeTunnel:
    """This class represents a tunnel that is created between the local and remote ports, wrapper around :class:`asyncssh.SSHListener` containing
    the ip address and port that the server is listening on.

    :ivar ip: The ip address that the server is listening on.
    :ivar port: The port that the server is listening on.
    :ivar listener: The underlying :class:`asyncssh.SSHListener` that is listening for connections.

    :vartype ip: `str`
    :vartype port: `int`
    :vartype listener: :class:`asyncssh.SSHListener`
    """
    def __init__(self, ip: str, port: int, listener: asyncssh.SSHListener) -> None:
        self.ip = ip
        self.port = port
        self.listener = listener