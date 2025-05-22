from urllib.parse import urlparse


def get_hostname(url: str) -> str:
    """
    Extract the hostname from a given URL

    Args:
        url (str): The URL from which to extract the hostname

    Returns:
        str: The hostname extracted from the URL
    """
    return urlparse(url).netloc
