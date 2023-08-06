import nabto_client.nabto as nabto
from nabto_client.session import NabtoSession

class NabtoTunnel:
    """
    Representation of a Nabto tunnel object.
    """
    def __init__(self, session: NabtoSession, localPort: int, nabtoHost: str, remoteHost: str, remotePort: int):
        """
        Creates a new Nabto tunnel object

        `session` is `NabtoSession` object. The session must be opened.

        `localPort` is the local TCP port to listen on. If the `localPort` number is 0
        the API will choose the port number.

        `nabtoHost` is the remote Nabto host to connect to.

        `remoteHost` is the host the remote endpoint establishes a TCP connection to

        `remotePort` is the TCP port to connect to on remoteHost.
        """
        self.session = session.session
        self.localPort = localPort
        self.nabtoHost = nabtoHost
        self.remoteHost = remoteHost
        self.remotePort = remotePort
        self.tunnel = nabto.Tunnel()

    def __enter__(self):
        return self.openTcp()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        self.tunnel = None

    def openTcp(self) -> int:
        """
        Opens a TCP tunnel to a remote server through a Nabto enabled device.
        
        Returns the local TCP port the tunnel was opened on.
        """
        return self.tunnel.openTcp(self.session, self.localPort, self.nabtoHost, self.remoteHost, self.remotePort)

    def close(self):
        """
        Closes an open tunnel.
        """
        self.tunnel.close()

    def status(self) -> int:
        """
        Retrieves the current status of the tunnel
        """
        return self.tunnel.status()

class TunnelStatus:
    """
    The TunnelStatus enumeration is telling the state of the tunnel
    and the underlying connection type for a stream carrying the tunnel
    """
    CLOSED              = -1
    """
    The tunnel is closed.
    """
    CONNECTING          = 0
    """
    The tunnel is connecting.
    """
    READY_FOR_RECONNECT = 1
    """
    The other end of the tunnel (the device) has disappeared.
    The client must connect again.
    """
    UNKNOWN             = 2
    """
    The tunnel is connected and the tunnel is running on an unrecognized
    connection type. This value indicates an internal error, since we
    always know the underlying connection type if it exists.
    """
    LOCAL               = 3
    """
    The tunnel is connected and the tunnel is running on a local
    connection (no Internet).
    """
    REMOTE_P2P          = 4
    """
    The tunnel is connected and the tunnel is running on a direct
    connection (peer-to-peer).
    """
    REMOTE_RELAY        = 5
    """
    The tunnel is connected and the tunnel is running on a fallback
    connection through the base-station.
    """
    REMOTE_RELAY_MICRO  = 6
    """
    The tunnel is connected and the tunnel is running on a connection
    that runs through a relay node on the Internet. The device is
    capable of using TCP/IP and the connection runs directly from the
    device to the relay node to the client.
    """