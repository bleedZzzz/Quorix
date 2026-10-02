import pymupdf

from app.application.ingestion import PDFParser, SectionDetector, SemanticChunker


def test_pdf_parsing_and_chunking():
    # Create an in-memory PDF using PyMuPDF
    doc = pymupdf.open()
    page1 = doc.new_page()
    page1.insert_text(
        (50, 72),
        "Attention Is All You Need\n\nAbstract\nWe propose a new simple network architecture, the Transformer, based solely on attention mechanisms.\n\n1 Introduction\nRecurrent neural networks have been firmly established as state of the art approaches in sequence modeling.",
    )

    page2 = doc.new_page()
    page2.insert_text(
        (50, 72),
        "2 Model Architecture\nThe Transformer follows an overall architecture using stacked self-attention and point-wise, fully connected layers.\n\n3 Conclusion\nIn this work, we presented the Transformer, the first sequence transduction model based entirely on attention.",
    )

    pdf_bytes = doc.tobytes()
    doc.close()

    parser = PDFParser()
    parsed = parser.parse_bytes(pdf_bytes)

    assert parsed.page_count == 2
    assert len(parsed.pages) == 2
    assert "Transformer" in parsed.raw_text

    detector = SectionDetector()
    sections = detector.detect_sections(parsed.pages)
    assert len(sections) >= 2
    types = [s.section_type for s in sections]
    assert "abstract" in types or "introduction" in types

    chunker = SemanticChunker(target_chunk_size=50, chunk_overlap=10)
    chunks = chunker.chunk_document(parsed.pages, sections)

    assert len(chunks) > 0
    for chunk in chunks:
        assert len(chunk.content) > 0
        assert chunk.token_count > 0
        assert chunk.page_number in (1, 2)
