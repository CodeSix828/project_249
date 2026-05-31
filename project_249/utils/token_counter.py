# utils/token_counter.py
import tiktoken

_encoding_cache = {}


def get_encoding(encoding_name="cl100k_base"):
    if encoding_name not in _encoding_cache:
        _encoding_cache[encoding_name] = tiktoken.get_encoding(encoding_name)
    return _encoding_cache[encoding_name]


def calc_token_num(text: str, encoding_name="cl100k_base") -> int:
    """使用encoding_name编码集计算文本字符串的token数"""
    encoding = get_encoding(encoding_name)
    num_tokens = len(encoding.encode(text))
    return num_tokens

