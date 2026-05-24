import pytest
from project_249 import TextSplitter, CharacterTextSplitter, SentenceTextSplitter, get_default_splitter


class TestTextSplitter:
    def test_init_with_valid_params(self):
        splitter = TextSplitter(chunk_size=500, chunk_overlap=50)
        assert splitter.chunk_size == 500
        assert splitter.chunk_overlap == 50

    def test_init_chunk_size_zero(self):
        with pytest.raises(ValueError):
            TextSplitter(chunk_size=0, chunk_overlap=0)

    def test_init_negative_overlap(self):
        with pytest.raises(ValueError):
            TextSplitter(chunk_size=100, chunk_overlap=-1)

    def test_init_overlap_equals_chunk_size(self):
        with pytest.raises(ValueError):
            TextSplitter(chunk_size=100, chunk_overlap=100)

    def test_split_empty_text(self):
        splitter = TextSplitter(chunk_size=100, chunk_overlap=10)
        chunks = splitter.split_text("")
        assert chunks == []

    def test_split_whitespace_only(self):
        splitter = TextSplitter(chunk_size=100, chunk_overlap=10)
        chunks = splitter.split_text("   \n\n   ")
        assert chunks == []

    def test_split_short_text(self):
        splitter = TextSplitter(chunk_size=100, chunk_overlap=10)
        text = "这是一段很短的文本。"
        chunks = splitter.split_text(text)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_split_with_overlap(self):
        splitter = TextSplitter(chunk_size=10, chunk_overlap=3)
        text = "abcdefghijklmnopqrst"
        chunks = splitter.split_text(text)
        assert len(chunks) > 1
        assert len(chunks[0]) == 10


class TestCharacterTextSplitter:
    def test_split_paragraphs(self):
        splitter = CharacterTextSplitter(chunk_size=50, chunk_overlap=10)
        text = "这是第一段，内容稍微长一点，超过合并的阈值。\n\n这是第二段，内容也比较长，确保不会被合并。\n\n这是第三段，同样足够长。"
        chunks = splitter.split_text(text)
        assert len(chunks) >= 2

    def test_split_long_paragraph(self):
        splitter = CharacterTextSplitter(chunk_size=20, chunk_overlap=5, separator="\n\n")
        text = "a" * 50
        chunks = splitter.split_text(text)
        assert len(chunks) > 1
        assert max(len(c) for c in chunks) <= 20

    def test_split_documents(self):
        splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=10)
        texts = [
            "这是第一个文档。",
            "这是第二个文档，稍微长一点。",
        ]
        chunks = splitter.split_documents(texts)
        assert len(chunks) >= 2


class TestSentenceTextSplitter:
    def test_split_sentences(self):
        splitter = SentenceTextSplitter(chunk_size=50, chunk_overlap=5)
        text = "这是第一句。这是第二句。这是第三句。这是第四句。这是第五句。"
        chunks = splitter.split_text(text)
        assert len(chunks) > 0

    def test_split_long_sentence(self):
        splitter = SentenceTextSplitter(chunk_size=20, chunk_overlap=5)
        text = "这是一个非常非常非常非常非常非常长的句子。"
        chunks = splitter.split_text(text)
        assert len(chunks) > 1

    def test_get_default_splitter(self):
        splitter = get_default_splitter()
        assert splitter is not None
        assert splitter.chunk_size == 500
        assert splitter.chunk_overlap == 50
