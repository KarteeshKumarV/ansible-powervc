import socket


def check_dns(host):
    """
    Resolve a hostname and return its IP address.

    Args:
        host (str): Hostname or IP address.

    Returns:
        dict: DNS resolution result.
    """

    try:
        ip_address = socket.gethostbyname(host)

        return {
            "success": True,
            "host": host,
            "ip_address": ip_address,
            "message": "DNS resolution successful"
        }

    except socket.gaierror as error:

        return {
            "success": False,
            "host": host,
            "message": "DNS resolution failed: {0}".format(str(error))
        }


def check_connectivity(host, port=22, timeout=5):
    """
    Check TCP connectivity to a host.

    Args:
        host (str): Hostname or IP address.
        port (int): TCP port.
        timeout (int): Connection timeout.

    Returns:
        dict: Connectivity result.
    """

    try:

        with socket.create_connection(
            (host, port),
            timeout=timeout
        ):

            return {
                "success": True,
                "host": host,
                "port": port,
                "message": "Connection successful"
            }

    except (socket.timeout, socket.error) as error:

        return {
            "success": False,
            "host": host,
            "port": port,
            "message": "Connection failed: {0}".format(str(error))
        }
