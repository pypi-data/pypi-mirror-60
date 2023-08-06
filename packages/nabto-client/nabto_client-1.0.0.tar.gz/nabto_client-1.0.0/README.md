# python-nabto-client

Python Wrapper for the Linux and macOS native Nabto Client SDKs.

## Requirements

* Python 3.6+
* `python3-dev` package for Debian distributions
* Linux or macOS (Windows is not supported - let us know if you need this!)

## Installation

Install using `pip`...

    pip install -i https://test.pypi.org/simple/ nabto-client

## Example

Let's take a look at a quick example of using `nabto_client` to open a session and a tunnel.

    import nabto_client

    NABTO_HOME_DIRECTORY = "/home/nabto/example"

    USER = "user"
    PASSWORD = "password"

    LOCAL_PORT = 7000
    NABTO_HOST = "example.appmyproduct.com"
    REMOTE_HOST = "localhost"
    REMOTE_PORT = 8000

    # Initializes the Nabto client API
    nabto_client.startup(NABTO_HOME_DIRECTORY)

    # Creates a Nabto self signed profile
    nabto_client.createSelfSignedProfile(USER, PASSWORD)

    with nabto_client.NabtoSession(USER, PASSWORD) as session:
        with nabto_client.NabtoTunnel(session, LOCAL_PORT, NABTO_HOST, REMOTE_HOST, REMOTE_PORT) as port:
            print(f'Opened tunnel on port {port}')
            ...

    # Releases any resources held by the Nabto client API
    nabto_client.shutdown()

### Tunnel status
The example above doesn't allow to query the current status of the tunnel because the context manager returns the port not the tunnel object.

If you want to query the tunnel status, don't use the context manager, instead create and open a tunnel like this:

    tunnel = nabto_client.NabtoTunnel(session, LOCAL_PORT, NABTO_HOST, REMOTE_HOST, REMOTE_PORT)
    print(f'Tunnel status is {tunnel.status()}') # -1 or TunnelStatus.CLOSED
    port = tunnel.openTcp()
    print(f'Opened tunnel on port {port}')
    print(f'Tunnel status is {tunnel.status()}') # 3 or TunnelStatus.LOCAL
    # ... do something with the tunnel
    tunnel.close()
    if nabto_client.TunnelStatus.CLOSED == tunnel.status():
        print(f'Tunnel is closed')

You can also run `example/cli.py` for an interactive example.

    python example/cli.py --device example.appmyproduct.com
