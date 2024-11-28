from enum import Enum
from typing import List, Set

class RuleType(Enum):
    DefaultOrEnd = 0
    Xpath = 1
    Json = 2
    Js = 3
    Regex = 4
    RuleSymbol = 5
    End = 6
    Inner = 7
    Get = 8
    Put = 9
    Order = 10
    Unknown = 11
    Format = 12
    JsonInner = 13
    JoinSymbol = 14
    Page = 15

# 常量定义
RULE_SEPARATORS: Set[str] = {
    '@', '@@', '{{', '}}', '<js>', '</js>',
    '@js:', '@css:', '@xpath:', '@json:', '&&', '||',
    r'%%', '##', '###', '}', '@put:{', '@get:{', '+', '-', ':', '<', '>'
}
RULE_JOIN_SET: Set[str] = {'&&', '||', '%%', '##'}

# 分组规则常量
DEFAULT_SEPARATORS: Set[str] = {'@', '@css:', '@@'}
JS_SEPARATORS: Set[str] = {'<js>', '</js>', '@js:'}
JSON_SEPARATORS: Set[str] = {'@json:'}
REGEX_SEPARATORS: Set[str] = {'##', '###', ':', '####'}
ORDER_SEPARATORS: Set[str] = {'+', '-'}
INNER_SEPARATORS: Set[str] = {'{{', '}}'}
JSON_INNER_SEPARATORS: Set[str] = {'{'}
FORMAT_SEPARATORS: Set[str] = {'{{', '}}', '{', '}', '@get:{', '<', '>'}
PAGE_SEPARATORS: Set[str] = {'<', '>'}
JOIN_SEPARATORS: Set[str] = {'&&', '||', '%%'}


def is_number_token(token: str) -> bool:
    return len(token) == 2 and token[0] == '$' and token[1].isnumeric()


def get_rule_type(rules: List[str], index: int, hasEndRule: bool = False, contentIsJson: bool = False) -> RuleType:
    current_rule = rules[index]

    if current_rule in RULE_SEPARATORS:
        return RuleType.RuleSymbol

    if index > 0:
        prev_rule = rules[index - 1]

        if prev_rule in {'##', ':'}:
            return RuleType.Regex
        if is_number_token(current_rule):
            return RuleType.Regex
        if prev_rule in {'@css:', '@@'}:
            return RuleType.DefaultOrEnd
        if prev_rule in {'@js:', '<js>'}:
            return RuleType.Js
        if prev_rule == '@get:{':
            return RuleType.Get
        if prev_rule == '@put:{':
            return RuleType.Put
        if prev_rule == '{{':
            return RuleType.Inner
        if prev_rule == '{':
            return RuleType.JsonInner
        if prev_rule == '<':
            return RuleType.Page


    if current_rule.startswith('/') and not ('{{' in rules or '@get:{' in rules):
        return RuleType.Xpath
    if current_rule.startswith(('$.', '$[')):
        return RuleType.Json
    if contentIsJson:
        return RuleType.Json
    if hasEndRule and (index == len(rules) - 1 or rules[index + 1] in RULE_JOIN_SET):
        return RuleType.End

    return RuleType.DefaultOrEnd


def get_rule_type_for_group(rulesTokens: List[str], index: int) -> RuleType:
    current_token = rulesTokens[index]
    length = len(rulesTokens)

    # 自身预测
    if current_token in DEFAULT_SEPARATORS:
        return RuleType.DefaultOrEnd
    if current_token in JS_SEPARATORS:
        return RuleType.Js
    if current_token in JSON_SEPARATORS:
        return RuleType.Json
    if current_token in REGEX_SEPARATORS:
        return RuleType.Regex
    if current_token in ORDER_SEPARATORS and index == 0:
        return RuleType.Order
    if current_token in INNER_SEPARATORS:
        return RuleType.Format
    if current_token in JSON_INNER_SEPARATORS:
        return RuleType.Format
    if current_token in PAGE_SEPARATORS:
        return RuleType.Format
    if current_token in JOIN_SEPARATORS:
        return RuleType.JoinSymbol
    if current_token == '@get:{':
        return RuleType.Format
    if current_token == '@put:{':
        return RuleType.Put

    # 前向预测
    if index > 0:
        prev_token = rulesTokens[index - 1]
        if prev_token in DEFAULT_SEPARATORS:
            return RuleType.DefaultOrEnd
        if prev_token in {'##', '####', ':'}:
            return RuleType.Regex
        if prev_token in {'<js>', '@js:'}:
            return RuleType.Js
        if prev_token == '@put:{':
            return RuleType.Put
        if prev_token in FORMAT_SEPARATORS:
            return RuleType.Format
        if is_number_token(prev_token):
            return RuleType.Format
    if current_token == '}' and index >= 2:
        if rulesTokens[index - 2] in {'@get:{', '{'}:
            return RuleType.Format
        if rulesTokens[index - 2] == '@put:{':
            return RuleType.Put
    if is_number_token(current_token):
        return RuleType.Format

    # 后向预测
    if index + 1 < length:
        next_token = rulesTokens[index + 1]
        if next_token in {'{{', '{', '@get:{'}:
            return RuleType.Format
        if is_number_token(next_token):
            return RuleType.Format

    # 其他类型判断
    if current_token.startswith(('$.', '$[')):
        return RuleType.Json
    if current_token.startswith('/'):
        return RuleType.Xpath
    if index == 0 and length == 1:
        return RuleType.DefaultOrEnd

    return RuleType.DefaultOrEnd
