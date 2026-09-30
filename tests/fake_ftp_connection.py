from collections.abc import Callable

FAKE_FTP_FILE_CONTENT = b"conteudo do arquivo"


class FakeFtpConnection:
    created_connections: list["FakeFtpConnection"] = []

    def __init__(self, host: str, timeout: int) -> None:
        self.host = host
        self.timeout = timeout
        self.login_call_count = 0
        self.retrbinary_commands: list[str] = []
        FakeFtpConnection.created_connections.append(self)

    def __enter__(self) -> "FakeFtpConnection":
        return self

    def __exit__(self, *exception_info: object) -> None:
        return None

    def login(self) -> None:
        self.login_call_count += 1

    def retrbinary(self, command: str, callback: Callable[[bytes], object]) -> None:
        self.retrbinary_commands.append(command)
        callback(FAKE_FTP_FILE_CONTENT)
