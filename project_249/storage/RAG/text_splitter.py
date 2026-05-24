from typing import List, Optional
import re


class TextSplitter:
    """
    文档分块器基类。
    
    用于将长文本分割成适合嵌入模型处理的小块（chunks）。
    每个块的大小由 chunk_size 控制，块之间可以有重叠（overlap）
    以保持上下文的连续性。
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        初始化文档分块器。
        
        参数：
            chunk_size: 每个块的最大字符数，默认为 500
            chunk_overlap: 相邻块之间的重叠字符数，默认为 50
                          重叠可以保持上下文的连续性
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size 必须大于 0")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap 不能为负数")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap 必须小于 chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        """
        将文本分割成多个块。
        
        这是基类的默认实现，子类可以重写此方法来实现
        更智能的分块策略（如按句子、段落边界分块）。
        
        参数：
            text: 要分割的文本
            
        返回：
            文本块列表
        """
        if not text or len(text.strip()) == 0:
            return []

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunk = text[start:end]
            chunks.append(chunk)

            if end == text_length:
                break

            start = end - self.chunk_overlap

        return chunks

    def split_documents(self, texts: List[str]) -> List[str]:
        """
        批量分割多个文档。
        
        参数：
            texts: 文档文本列表
            
        返回：
            所有文档分割后的文本块列表
        """
        all_chunks = []
        for text in texts:
            chunks = self.split_text(text)
            all_chunks.extend(chunks)
        return all_chunks


class CharacterTextSplitter(TextSplitter):
    """
    基于字符数量的文档分块器。
    
    这是最简单的分块策略，直接按字符数量分割。
    适合处理结构简单的文本。
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50, separator: str = "\n\n"):
        """
        初始化基于字符的分块器。
        
        参数：
            chunk_size: 每个块的最大字符数
            chunk_overlap: 相邻块之间的重叠字符数
            separator: 优先在该分隔符处分割，默认为双换行符（段落边界）
        """
        super().__init__(chunk_size, chunk_overlap)
        self.separator = separator

    def split_text(self, text: str) -> List[str]:
        """
        将文本分割成多个块，优先在段落边界处分割。
        
        策略：
        1. 首先尝试在段落边界（双换行符）处分割
        2. 如果段落仍然太大，再按字符数量分割
        
        参数：
            text: 要分割的文本
            
        返回：
            文本块列表
        """
        if not text or len(text.strip()) == 0:
            return []

        paragraphs = text.split(self.separator)
        chunks = []

        for paragraph in paragraphs:
            if not paragraph.strip():
                continue

            if len(paragraph) <= self.chunk_size:
                chunks.append(paragraph)
            else:
                sub_chunks = super().split_text(paragraph)
                chunks.extend(sub_chunks)

        return self._merge_small_chunks(chunks)

    def _merge_small_chunks(self, chunks: List[str]) -> List[str]:
        """
        合并过小的块，以提高嵌入质量。
        
        太小的块可能包含的语义信息不足，
        可以将相邻的小块合并成一个更大的块。
        
        参数：
            chunks: 文本块列表
            
        返回：
            合并后的文本块列表
        """
        if len(chunks) <= 1:
            return chunks

        merged = []
        current_chunk = ""

        for chunk in chunks:
            if len(current_chunk) + len(chunk) + len(self.separator) <= self.chunk_size:
                if current_chunk:
                    current_chunk += self.separator + chunk
                else:
                    current_chunk = chunk
            else:
                if current_chunk:
                    merged.append(current_chunk)
                current_chunk = chunk

        if current_chunk:
            merged.append(current_chunk)

        return merged


class SentenceTextSplitter(TextSplitter):
    """
    基于句子边界的文档分块器。
    
    比字符分块器更智能，会尽量在句子边界处分割，
    保持语义的完整性。
    """

    SENTENCE_END_PATTERN = r'(?<=[。！？.!?])\s+'

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        初始化基于句子的分块器。
        
        参数：
            chunk_size: 每个块的最大字符数
            chunk_overlap: 相邻块之间的重叠字符数
        """
        super().__init__(chunk_size, chunk_overlap)

    def split_text(self, text: str) -> List[str]:
        """
        将文本分割成多个块，优先在句子边界处分割。
        
        策略：
        1. 首先将文本分割成句子
        2. 然后将句子组合成不超过 chunk_size 的块
        
        参数：
            text: 要分割的文本
            
        返回：
            文本块列表
        """
        if not text or len(text.strip()) == 0:
            return []

        sentences = re.split(self.SENTENCE_END_PATTERN, text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return [text]

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= self.chunk_size:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)

                if len(sentence) > self.chunk_size:
                    sub_chunks = super().split_text(sentence)
                    chunks.extend(sub_chunks[:-1])
                    current_chunk = sub_chunks[-1] if sub_chunks else ""
                else:
                    current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk)

        return chunks


def get_default_splitter() -> TextSplitter:
    """
    获取默认的文档分块器实例。
    
    返回：
        使用默认参数的 SentenceTextSplitter 实例
    """
    return SentenceTextSplitter(chunk_size=500, chunk_overlap=50)


def split_file_content(file_path: str, splitter: Optional[TextSplitter] = None) -> List[str]:
    """
    读取文件内容并进行分块。
    
    参数：
        file_path: 文件路径
        splitter: 分块器实例，为 None 时使用默认分块器
        
    返回：
        文本块列表
        
    异常：
        FileNotFoundError: 文件不存在
        IOError: 读取文件失败
    """
    if splitter is None:
        splitter = get_default_splitter()

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return splitter.split_text(content)
