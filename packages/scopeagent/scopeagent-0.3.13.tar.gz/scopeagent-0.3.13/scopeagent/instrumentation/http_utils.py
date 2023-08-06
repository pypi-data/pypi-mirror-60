MAXIMUM_HTTP_PAYLOAD_SIZE = 512

PUBLIC_HTTP_HEADERS = set(
    header.lower()
    for header in (
        'Content-Type',
        'Content-Length',
        'Content-Encoding',
        'Content-Language',
        'User-Agent',
        'Referer',
        'Accept',
        'Origin',
        'Access-Control-Allow-Origin',
        'Access-Control-Allow-Credentials',
        'Access-Control-Allow-Headers',
        'Access-Control-Allow-Methods',
        'Access-Control-Expose-Headers',
        'Access-Control-Max-Age',
        'Access-Control-Request-Headers',
        'Access-Control-Request-Method',
        'Date',
        'Expires',
        'Cache-Control',
        'Allow',
        'Server',
    )
)

REDACTED_HTTP_HEADERS = set(header.lower() for header in ('Authorization', 'Cookie', 'Set-Cookie'))


def filter_http_headers(headers, extra_http_headers=[]):
    filtered_headers = {}
    headers_to_include = PUBLIC_HTTP_HEADERS | set(header.lower() for header in extra_http_headers)
    for header, value in headers.items():
        if header.lower() in REDACTED_HTTP_HEADERS:
            filtered_headers[header] = '****'
        elif header.lower() in headers_to_include:
            filtered_headers[header] = value
    return filtered_headers
