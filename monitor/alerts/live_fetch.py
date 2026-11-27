"""Direct HTTPS retrieval; no proxies, redirects, credentials or access bypass."""
import http.client
import ipaddress
import os
import socket
import ssl
from urllib.parse import urlsplit

MAX_BYTES = 500_000

class CollectionError(ValueError):
    pass

def fetch_category(url):
    # Exact URLs are provisioned by the deployment operator, not web users.
    approved = os.environ.get("APPROVED_CATEGORY_URLS", "").split()
    p = urlsplit(url)
    if (url not in approved or p.scheme != "https" or not p.hostname
            or p.username or p.password or p.fragment or p.port not in (None, 443)):
        raise CollectionError("Category URL is not approved.")
    addresses = socket.getaddrinfo(p.hostname, 443, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
        raise CollectionError("Category must resolve exclusively to public addresses.")
    # Pin the validated address while retaining hostname certificate validation.
    address = addresses[0][4][0]
    conn = http.client.HTTPSConnection(p.hostname, timeout=10, context=ssl.create_default_context())
    conn._create_connection = lambda unused, timeout, source_address=None: socket.create_connection((address, 443), timeout, source_address)
    try:
        conn.request("GET", (p.path or "/") + ("?" + p.query if p.query else ""), headers={"User-Agent": "DealRadar/1.0", "Accept": "text/html", "Accept-Encoding": "identity"})
        response = conn.getresponse()
        if response.status != 200 or response.headers.get_content_type() != "text/html":
            raise CollectionError("Retailer did not return an accessible HTML page.")
        if response.headers.get("Content-Encoding", "identity").lower() != "identity":
            raise CollectionError("Unsupported content encoding.")
        data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise CollectionError("Category response exceeds size limit.")
        return data.decode(response.headers.get_content_charset() or "utf-8", errors="replace")
    finally:
        conn.close()
