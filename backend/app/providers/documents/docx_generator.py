from io import BytesIO

from docx import Document
from docx.shared import Pt


def gerar_docx(conteudo: str) -> bytes:
    documento = Document()
    for linha in conteudo.split("\n"):
        paragrafo = documento.add_paragraph(linha)
        paragrafo.paragraph_format.space_after = Pt(2)

    buffer = BytesIO()
    documento.save(buffer)
    return buffer.getvalue()
