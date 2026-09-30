class DataQualityError(Exception):
    def __init__(self, failure_lines: list[str]) -> None:
        super().__init__("qualidade de dados reprovada:\n" + "\n".join(failure_lines))
