from dataclasses import dataclass


@dataclass(frozen=True)
class QualityResult:
    table: str
    check: str
    passed: bool
    detail: str

    def as_row(self, competence: str) -> dict[str, str | bool]:
        return {"competencia": competence, "tabela": self.table, "verificacao": self.check, "aprovado": self.passed, "detalhe": self.detail}

    def failure_line(self) -> str:
        return f"{self.table} / {self.check}: {self.detail}"
