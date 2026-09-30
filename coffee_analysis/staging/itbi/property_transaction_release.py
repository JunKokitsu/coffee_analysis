from dataclasses import dataclass
from datetime import date

PROPERTY_TRANSACTION_DOCUMENTS_ADDRESS = "https://prefeitura.sp.gov.br/documents/d/fazenda"


@dataclass(frozen=True)
class PropertyTransactionRelease:
    file_name: str
    publication_date: date

    def download_url(self) -> str:
        return f"{PROPERTY_TRANSACTION_DOCUMENTS_ADDRESS}/{self.file_name}"

    def competence_folder(self) -> str:
        return self.publication_date.isoformat()
