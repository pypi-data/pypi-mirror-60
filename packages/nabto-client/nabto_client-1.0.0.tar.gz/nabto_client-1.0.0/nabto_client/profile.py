import nabto_client.nabto as nabto

def createSelfSignedProfile(id: str, password: str):
    """
    Creates a Nabto self signed profile with provided `id` (typically an email or user name)
    and the `password` which protects the private key

    The identity of such certificate cannot be trusted but the fingerprint of the
    certificate can be trusted in the device. After the profile has
    been created it can be used with a `NabtoSession`.
    """
    return nabto.nabtoCreateSelfSignedProfile(id, password)

def removeProfile(id: str):
    """
    Remove profile certificate for given `id`.
    """
    return nabto.nabtoRemoveProfile(id)

def getFingerprint(id: str) -> str:
    """
    Retrieve public key fingerprint for profile with specified `id`.
    """
    return nabto.nabtoGetFingerprint(id)
