import nabto_client.nabto as nabto


def startup(home_dir: str):
    """
    Initializes the Nabto client API.

    The nabtoStartup function must be invoked prior to invoking most of the
    other functions in the Nabto client API.

    Specify an alternative location of the Nabto home directory (for
    certificates and log files) in the `home_dir` parameter. The only
    requirement is that the parent directory must be writable by the
    user.
    """
    return nabto.nabtoStartup(home_dir)


def shutdown():
    """
    Terminates the Nabto client API.

    Releases any resources held by the Nabto client API.

    After each successful call to nabtoStartup call this function when the
    Nabto client API is no longer needed. This function can block for a
    small amount of time until all current sessions has closed properly.
    """
    return nabto.nabtoShutdown()

def versionString() -> str:
    """
    Get the Nabto software version (major.minor.patch[-prerelease tag]+build)
    """
    return nabto.nabtoVersionString()


class NabtoSession:
    """
    Representation of a Nabto session object.
    """
    def __init__(self, id: str, password: str):
        """
        Creates a new Nabto session object.

        `id` is the ID of an existing certificate. Either an email address or commonName
        
        `password` is the password for encrypted private key file. Specify
        an empty string for an unencrypted key file.
        """
        self.user = id
        self.password = password
        self.session = nabto.Session()

    def __enter__(self):
        self.open()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        self.session = None

    def open(self):
        """
        Starts a new Nabto session as context for RPC or tunnel
        invocation using the specified profile.
        """
        self.session.open(self.user, self.password)

    def close(self):
        """
        Closes the specified Nabto session and frees internal ressources.
        """
        self.session.close()

    def rpcSetDefaultInterface(self, interface: str):
        """
        Sets the default RPC interface to use when later invoking `NabtoSesion.rpcInvoke(url)`.
        """
        self.session.rpcSetDefaultInterface(interface)

    def rpcInvoke(self, url: str):
        """
        Retrieves data synchronously from specified `nabto://` URL on this session.
        """
        return self.session.rpcInvoke(url)
