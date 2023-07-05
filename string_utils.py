import unicodedata

def halfwidth_to_fullwidth(text):
    fullwidth_text = ""
    for char in text:
        char_width = unicodedata.east_asian_width(char)
        if char_width == 'H':  # 半角字符
            fullwidth_char = chr(ord(char) + 0xFEE0)  # 转换为全角字符
            fullwidth_text += fullwidth_char
        else:
            fullwidth_text += char
    return fullwidth_text