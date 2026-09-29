import math
from typing import TypeIs

MISSING_VALUE = "n/d"


class BrazilianNumberFormat:
    def currency(self, value: float | None) -> str:
        if not self._is_present(value):
            return MISSING_VALUE
        return f"R$ {self._localized(f'{value:,.2f}')}"

    def rounded_currency(self, value: float | None) -> str:
        if not self._is_present(value):
            return MISSING_VALUE
        return f"R$ {self._localized(f'{value:,.0f}')}"

    def integer(self, value: float | None) -> str:
        if not self._is_present(value):
            return MISSING_VALUE
        return self._localized(f"{value:,.0f}")

    def decimal(self, value: float | None) -> str:
        if not self._is_present(value):
            return MISSING_VALUE
        return self._localized(f"{value:,.1f}")

    def percentage(self, value: float | None) -> str:
        if not self._is_present(value):
            return MISSING_VALUE
        return f"{self._localized(f'{value * 100:,.1f}')}%"

    def signed_percentage(self, value: float | None) -> str:
        if not self._is_present(value):
            return MISSING_VALUE
        return f"{self._localized(f'{value * 100:+,.1f}')}%"

    def compact_currency(self, value: float | None) -> str:
        if not self._is_present(value):
            return MISSING_VALUE
        if abs(value) >= 2_000_000:
            return f"R$ {self._localized(f'{value / 1_000_000:,.1f}')} milhões"
        if abs(value) >= 1_000_000:
            return f"R$ {self._localized(f'{value / 1_000_000:,.1f}')} milhão"
        if abs(value) >= 1_000:
            return f"R$ {self._localized(f'{value / 1_000:,.1f}')} mil"
        return self.rounded_currency(value)

    def compact_integer(self, value: float | None) -> str:
        if not self._is_present(value):
            return MISSING_VALUE
        if abs(value) >= 1_000:
            return f"{self._localized(f'{value / 1_000:,.1f}')} mil"
        return self.integer(value)

    def _is_present(self, value: float | None) -> TypeIs[float]:
        return value is not None and not math.isnan(value)

    def _localized(self, formatted: str) -> str:
        translation = str.maketrans({",": ".", ".": ","})
        return formatted.translate(translation)
