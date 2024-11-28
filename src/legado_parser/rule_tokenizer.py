from typing import List, Optional, Tuple

class TokenizerError(Exception):
    pass

class Check:
    def __init__(self, text: str, stack: List[str], token_list: List[str]):
        self.text = text
        self.stack = stack
        self.token_list = token_list
        self.length = len(text)

    def ck(self, cursor: int, tmp_str: str, token_text: str = "", push_stack: str = "", stack_index: Optional[int] = None, stack_text: str= ""):
        if self.length < cursor + len(token_text):
            return cursor, tmp_str, False

        if token_text and self.text[cursor: cursor + len(token_text)].lower() == token_text:
            if stack_index is not None:
                if not self.stack or self.stack[stack_index] != stack_text:
                    return cursor, tmp_str, False
                self.stack.pop()
            elif push_stack:
                self.stack.append(push_stack)

            self.token_list.append(tmp_str)
            self.token_list.append(token_text)
            cursor += len(token_text)
            tmp_str = ""
            return cursor, tmp_str, True
        elif not token_text:
            if self.stack and self.stack[stack_index] == stack_text:
                self.stack.pop()
                return cursor, tmp_str, True

        return cursor, tmp_str, False

def _safe_substring(text: str, start: int, length: Optional[int] = None) -> str:
    if length is None:
        return text[start:] if start < len(text) else ""
    return text[start:start + length] if start + length <= len(text) else text[start:]


def tokenizer(text: str) -> List[str]:
    """
    阅读3.0规则分词器

    参数:
        text: 进行分词的文本

    返回:
        按分词顺序存储的语法单元列表
    """
    if not text:
        return []

    token_list: List[str] = []
    stack: List[str] = []
    cursor = 0
    length = len(text)
    tmp_str = ""

    try:
        ck = Check(text, stack, token_list).ck

        while cursor < length:
            char = text[cursor]
            tmp_str += char

            if char == "@":
                # @标记的复杂处理逻辑
                if (result := ck(cursor, tmp_str[:-1], "@get:{", "@get:{"))[2]:
                    cursor, tmp_str, __ = _process_block_marker_1(text, cursor, length, "@get:{")
                elif (result := ck(cursor, tmp_str[:-1], "@put:{", "@put:{"))[2]:
                    cursor, tmp_str, __ = _process_block_marker_1(text, cursor, length, "@put:{")
                elif (result := ck(cursor, tmp_str[:-1], "@css:"))[2]:
                    cursor, tmp_str, __ = result
                elif (result := ck(cursor, tmp_str[:-1], "@json:", "@json:"))[2]:
                    cursor, tmp_str, __ = result
                elif (result := ck(cursor, tmp_str[:-1], "@@"))[2]:
                    cursor, tmp_str, __ = result
                elif (result := ck(cursor, tmp_str[:-1], "@js:"))[2]:
                    cursor, tmp_str, __ = _process_js_block(text, cursor, length)
                elif text[cursor - 1] == "[":
                    cursor += 1
                elif stack and stack[-1].lower() == "@json:":
                    cursor += 1
                else:
                    token_list.append(tmp_str[:-1])
                    token_list.append("@")
                    cursor += 1
                    tmp_str = ""

            elif char == "{":
                # 处理块标记
                if (result := ck(cursor, tmp_str[:-1], "{{", "{{"))[2]:
                    cursor, tmp_str, __ = _process_double_brace_block(text, cursor, length)
                elif len(text) - 1 > cursor + 3 and text[cursor: cursor + 3] == "{$.":
                    stack.append("{")
                    token_list.append(tmp_str[:-1])
                    token_list.append("{")
                    cursor += 1
                    tmp_str = ""
                else:
                    cursor += 1

            elif char == "}":
                # 处理结束标记
                if (result := ck(cursor, tmp_str[:-1], "}", "", -1, "{"))[2]:
                    cursor, tmp_str, __ = result
                else:
                    cursor += 1

            elif char == "|":
                # 处理管道标记
                if stack and stack[-1] == "{{":
                    cursor += 1
                elif (result := ck(cursor, tmp_str[:-1], "||"))[2]:
                    cursor, tmp_str, __ = result
                else:
                    cursor += 1

            elif char == "&":
                # 处理与标记
                if len(text) - 1 < cursor + 1:
                    break
                elif text[cursor + 1] == "&" and not (stack and stack[0] != "@json:"):
                    token_list.append(tmp_str[:-1])
                    token_list.append("&&")
                    cursor += 2
                    tmp_str = ""
                else:
                    cursor += 1

            elif char == "%":
                # 处理百分号标记
                if len(text) - 1 < cursor + 1:
                    break
                elif text[cursor + 1] == "%" and not (stack and stack[0] != "@json:"):
                    token_list.append(tmp_str[:-1])
                    token_list.append(r"%%")
                    cursor += 2
                    tmp_str = ""
                else:
                    cursor += 1

            elif char == "<":
                # 处理JavaScript和标签标记
                if (result := ck(cursor, tmp_str[:-1], "<js>", "<js>"))[2]:
                    cursor, tmp_str, __ = _process_js_tag_block(text, cursor, length)
                else:
                    cursor += 1

            elif char == "\\":
                # 处理转义字符
                tmp_str += text[cursor + 1] if cursor + 1 < length else ""
                cursor += 2

            elif (char in {"+", "-", ":"}) and cursor == 0:
                # 处理特殊起始字符
                token_list.append(char)
                cursor += 1
                tmp_str = ""

            elif char == ":" and cursor == 1:
                # 处理特殊冒号
                token_list.append(char)
                cursor += 1
                tmp_str = ""

            elif char == "#":
                # 处理井号标记
                if (result := ck(cursor, tmp_str[:-1], "####"))[2]:
                    cursor, tmp_str, __ = result
                elif (result := ck(cursor, tmp_str[:-1], "##"))[2]:
                    cursor, tmp_str, __ = _process_double_hash_block(text, cursor, length)
                else:
                    cursor += 1

            elif char == "$":
                # 处理美元符号
                if len(text) - 1 < cursor + 1:
                    break
                if text[cursor + 1].isnumeric():
                    token_list.append(tmp_str[:-1])
                    token_list.append("$" + text[cursor + 1])
                    cursor += 2
                    tmp_str = ""
                else:
                    cursor += 1

            else:
                cursor += 1

        token_list.append(tmp_str)
        return list(filter(None, token_list))

    except Exception as e:
        raise TokenizerError(f"分词器处理出错: {e}") from e


def _process_block_marker_1(text: str, cursor: int, length: int, marker: str) -> Tuple[int, str, Optional[str]]:
    """处理特定的块标记"""
    cursor += len(marker)
    tmp_str = marker
    while cursor < length:
        char = text[cursor]
        tmp_str += char
        if char == "}":
            break
        cursor += 1
    return cursor + 1, tmp_str, None


def _process_double_brace_block(text: str, cursor: int, length: int) -> Tuple[int, str, Optional[str]]:
    """处理双重大括号块"""
    stack = ["{"]
    while cursor < length:
        cursor += 1
        char = text[cursor]
        if char == "{":
            stack.append("{")
        elif char == "}":
            if stack and stack[-1] == "{":
                stack.pop()
                if not stack:
                    break
    return cursor + 1, text[cursor - len(text) + 1:], None


def _process_js_block(text: str, cursor: int, length: int) -> Tuple[int, str, Optional[str]]:
    """处理JavaScript块"""
    while cursor < length:
        char = text[cursor]
        if char == "#":
            if cursor + 2 < length and text[cursor:cursor + 3] == "###":
                cursor += 3
                break
            elif cursor + 1 < length and text[cursor:cursor + 2] == "##":
                cursor += 2
        cursor += 1
    return cursor, text[cursor:], None


def _process_js_tag_block(text: str, cursor: int, length: int) -> Tuple[int, str, Optional[str]]:
    """处理JavaScript标签块"""
    while cursor < length:
        char = text[cursor]
        if char == "<":
            if cursor + 5 < length and text[cursor:cursor + 6] == "</js>":
                cursor += 6
                break
        cursor += 1
    return cursor, text[cursor:], None


def _process_double_hash_block(text: str, cursor: int, length: int) -> Tuple[int, str, Optional[str]]:
    """处理双井号块"""
    while cursor < length:
        char = text[cursor]
        if char == "#":
            if cursor + 2 < length and text[cursor:cursor + 3] == "###":
                cursor += 3
                break
            elif cursor + 1 < length and text[cursor:cursor + 2] == "##":
                cursor += 2
        elif char == "@":
            if cursor + 4 < length and text[cursor:cursor + 5] == "@js:":
                cursor = length
                break
        cursor += 1
    return cursor, text[cursor:], None

def tokenizer_url(text: str) -> List[str]:
    """
        URL分词器，处理特定的URL格式和特殊标记

        参数:
            text: 待处理的URL文本

        返回:
            处理后的标记列表
        """
    if not text:
        return []

    token_list: List[str] = []
    stack: List[str] = []
    cursor = 0
    length = len(text)
    tmp_str = ""

    try:
        ck = Check(text, stack, token_list).ck

        while cursor < length:
            char = text[cursor]
            tmp_str += char

            # 处理特殊标记
            if char == "@":
                # JS标记处理
                if (result := ck(cursor, tmp_str[:-1], "@js:"))[2]:
                    cursor, tmp_str, __ = result
                    # 直接截取剩余文本
                    tmp_str = text[cursor:]
                    break
                else:
                    cursor += 1

            # 处理块标记
            elif char == "{":
                if (result := ck(cursor, tmp_str[:-1], "{{", "{{"))[2]:
                    cursor, tmp_str, __ = result
                    cursor = _process_block_marker(text, cursor, length, stack, "{", "}}")
                else:
                    cursor += 1

            # 处理JavaScript标记
            elif char == "<":
                if (result := ck(cursor, tmp_str[:-1], "<js>", "<js>"))[2]:
                    cursor, tmp_str, __ = result
                    cursor = _process_js_marker(text, cursor, length)

                # 处理通用的尖括号标记
                elif (result := ck(cursor, tmp_str[:-1], "<", "<"))[2]:
                    cursor, tmp_str, __ = result
                    cursor = _process_bracket_marker(text, cursor, length, ">")
                else:
                    cursor += 1

            # 处理转义字符
            elif char == "\\":
                tmp_str += text[cursor + 1] if cursor + 1 < length else ""
                cursor += 2

            else:
                cursor += 1

        token_list.append(tmp_str)
        return list(filter(None, token_list))

    except Exception as e:
        raise TokenizerError(f"URL分词器处理出错: {e}") from e


def tokenizer_inner(text: str) -> List[str]:
    """
        内部分词器，处理特定的内部标记和块结构

        参数:
            text: 待处理的内部文本

        返回:
            处理后的标记列表
        """
    if not text:
        return []

    token_list: List[str] = []
    stack: List[str] = []
    cursor = 0
    length = len(text)
    tmp_str = ""

    try:
        ck = Check(text, stack, token_list).ck

        while cursor < length:
            char = text[cursor]
            tmp_str += char

            # 处理块标记
            if char == "{":
                if (result := ck(cursor, tmp_str[:-1], "{{", "{{"))[2]:
                    cursor, tmp_str, __ = result
                    cursor = _process_block_marker(text, cursor, length, stack, "{", "}}")
                else:
                    stack.append("{")
                    cursor += 1

            else:
                cursor += 1

        token_list.append(tmp_str)
        return list(filter(None, token_list))

    except Exception as e:
        raise TokenizerError(f"内部分词器处理出错: {e}") from e


def split_page(text: str) -> List[str]:
    """
        页面分割器，处理特定的页面分割逻辑

        参数:
            text: 待处理的页面文本

        返回:
            处理后的标记列表
        """
    if not text:
        return []

    token_list: List[str] = []
    stack: List[str] = []
    cursor = 0
    length = len(text)
    tmp_str = ""

    try:
        ck = Check(text, stack, token_list).ck

        while cursor < length:
            char = text[cursor]
            tmp_str += char

            # 处理块标记
            if char == "{":
                if len(text) - 1 < cursor + 1:
                    break

                if text[cursor: cursor + 2] == "{{":
                    cursor += 1
                    cursor = _process_block_marker(text, cursor, length, stack, "{", "}}")

                else:
                    cursor += 1

            # 处理逗号分隔
            elif char == ",":
                if (result := ck(cursor, tmp_str[:-1], ","))[2]:
                    cursor, tmp_str, __ = result

            else:
                cursor += 1

        token_list.append(tmp_str)
        return list(filter(lambda x: x != ",", token_list))

    except Exception as e:
        raise TokenizerError(f"页面分割器处理出错: {e}") from e


def _process_block_marker(text: str, cursor: int, length: int, stack: List[str], open_marker: str,
                          close_marker: str) -> int:
    """
        处理通用的块标记

        参数:
            text: 源文本
            cursor: 当前游标位置
            length: 文本长度
            stack: 状态栈
            open_marker: 开放标记
            close_marker: 关闭标记

        返回:
            处理后的游标位置
        """
    while cursor < length:
        char = text[cursor]

        if char == open_marker:
            stack.append(open_marker)
            cursor += 1
        elif char == "}":
            if stack and stack[-1] == open_marker:
                stack.pop()
                cursor += 1
            elif len(text) - cursor > 1 and text[cursor:cursor + 2] == close_marker:
                cursor += 2
                break
            else:
                cursor += 1
        else:
            cursor += 1

    return cursor


def _process_js_marker(text: str, cursor: int, length: int) -> int:
    """
        处理JavaScript标记的特殊逻辑

        参数:
            text: 源文本
            cursor: 当前游标位置
            length: 文本长度

        返回:
            处理后的游标位置
        """
    while cursor < length:
        char = text[cursor]

        if char == "<":
            if len(text) - cursor > 5 and text[cursor:cursor + 6] == "</js>":
                cursor += 6
                break

        cursor += 1

    return cursor


def _process_bracket_marker(text: str, cursor: int, length: int, close_char: str) -> int:
    """
    处理通用的括号标记

    参数:
        text: 源文本
        cursor: 当前游标位置
        length: 文本长度
        close_char: 关闭字符

    返回:
        处理后的游标位置
    """
    while cursor < length:
        char = text[cursor]

        if char == close_char:
            break

        cursor += 1

    return cursor + 1