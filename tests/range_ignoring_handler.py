from tests.range_request_handler import RangeRequestHandler


class RangeIgnoringHandler(RangeRequestHandler):
    def do_GET(self) -> None:
        type(self).request_count += 1
        self._send_full_content()
