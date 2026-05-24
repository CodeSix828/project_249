# utils/token_counter.py
import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")
'''
line = "用于测试"
token_enc_list = encoding.encode(line)
print (len(token_enc_list), len(line))
print(token_enc_list)

#解码出单个token
for token_enc in token_enc_list:
    word = encoding.decode([token_enc])
    print((token_enc, word))
#解码还原出原始文本
print(encoding.decode(token_enc_list))
print("解码器加载完成......\n")
'''
def calc_token_num(text: str, encoding_name="cl100k_base") -> int:
    """使用encoding_name编码集计算文本字符串的token数"""
    encoding_name = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(text))
    return num_tokens

