from http.server import BaseHTTPRequestHandler


class RangeRequestHandler(BaseHTTPRequestHandler):
    content = b""
    request_count = 0

    def do_HEAD(self) -> None:
        type(self).request_count += 1
        self._send_headers_for_full_content()

    def do_GET(self) -> None:
        type(self).request_count += 1
        range_header = self.headers.get("Range")
        if range_header is not None:
            self._send_partial_content(range_header)
            return
        self._send_full_content()

    def _send_headers_for_full_content(self) -> None:
        self.send_response(200)
        self.send_header("Content-Length", str(len(type(self).content)))
        self.end_headers()

    def _send_full_content(self) -> None:
        self._send_headers_for_full_content()
        self.wfile.write(type(self).content)

    def _send_partial_content(self, range_header: str) -> None:
        start, end = self._parse_range(range_header)
        body = type(self).content[start:end + 1]
        self._send_partial_content_headers(len(body))
        self.wfile.write(body)

    def _send_partial_content_headers(self, body_length: int) -> None:
        self.send_response(206)
        self.send_header("Content-Length", str(body_length))
        self.end_headers()

    def _parse_range(self, range_header: str) -> tuple[int, int]:
        raw_range = range_header.removeprefix("bytes=")
        start_text, end_text = raw_range.split("-")
        return int(start_text), int(end_text)

    def log_message(self, format_str: str, *args: object) -> None:
        return None
