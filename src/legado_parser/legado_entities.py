import copy
from dataclasses import dataclass
from typing import Optional


@dataclass
class RuleBookInfoEntity:
    author: str
    cover_url: str
    intro: str
    kind: str
    last_chapter: str
    name: str
    word_count: int
    update_time: int
    can_re_name: str
    download_urls: str

    def __init__(self, rule_book_info: dict) -> None:
        self._rule_book_info = rule_book_info
        self.author = rule_book_info.get("author", "")
        self.cover_url = rule_book_info.get("coverUrl", "")
        self.intro = rule_book_info.get("intro", "")
        self.kind = rule_book_info.get("kind", "")
        self.last_chapter = rule_book_info.get("lastChapter", "")
        self.name = rule_book_info.get("name", "")
        self.word_count = rule_book_info.get("wordCount", 0)
        self.update_time = rule_book_info.get("updateTime", 0)
        self.can_re_name = rule_book_info.get("canReName", "")
        self.download_urls = rule_book_info.get("downloadUrls", "")


@dataclass
class RuleContentEntity:
    content: str
    replace_regex: str
    next_content_url: str
    web_js: str
    source_regex: str
    image_style: str
    pay_action: str

    def __init__(self, rule_content: dict) -> None:
        self._rule_content = rule_content
        self.content = rule_content.get("content", "")
        self.replace_regex = rule_content.get("sourceRegex", "")
        self.next_content_url = rule_content.get("nextContentUrl", "")
        self.web_js = rule_content.get("webJs", "")
        self.source_regex = rule_content.get("replaceRegex", "")
        self.image_style = rule_content.get("imageStyle", "")
        self.pay_action = rule_content.get("payAction", "")


@dataclass
class RuleExploreEntity:
    author: str
    book_list: str
    book_url: str
    cover_url: str
    intro: str
    kind: str
    last_chapter: str
    name: str
    word_count: str

    def __init__(self, rule_explore: dict) -> None:
        self._rule_explore = rule_explore
        self.author = rule_explore.get("author", "")
        self.book_list = rule_explore.get("bookList", "")
        self.book_url = rule_explore.get("bookUrl", "")
        self.cover_url = rule_explore.get("coverUrl", "")
        self.intro = rule_explore.get("intro", "")
        self.kind = rule_explore.get("kind", "")
        self.last_chapter = rule_explore.get("lastChapter", "")
        self.name = rule_explore.get("name", "")
        self.word_count = rule_explore.get("wordCount", "")


@dataclass
class RuleSearchEntity:
    author: str
    book_list: str
    book_url: str
    cover_url: str
    intro: str
    kind: str
    last_chapter: str
    name: str
    update_time: str
    word_count: str
    check_keyword: str

    def __init__(self, rule_search: dict) -> None:
        self._rule_search = rule_search
        self.author = rule_search.get("author", "")
        self.book_list = rule_search.get("bookList", "")
        self.book_url = rule_search.get("bookUrl", "")
        self.cover_url = rule_search.get("coverUrl", "")
        self.intro = rule_search.get("intro", "")
        self.kind = rule_search.get("kind", "")
        self.last_chapter = rule_search.get("lastChapter", "")
        self.name = rule_search.get("name", "")
        self.update_time = rule_search.get("updateTime", "")
        self.word_count = rule_search.get("wordCount", "")
        self.check_keyword = rule_search.get("checkKeyWord", "")


@dataclass
class RuleTocEntity:
    list: str
    name: str
    url: str
    next_url: str
    update_time: str
    pre_update_js: str
    is_volume: str
    is_vip: str
    is_pay: str

    def __init__(self, rule_toc: dict) -> None:
        self._rule_toc = rule_toc
        self.list = rule_toc.get("chapterList", "")
        self.name = rule_toc.get("chapterName", "")
        self.url = rule_toc.get("chapterUrl", "")
        self.next_url = rule_toc.get("nextTocUrl", "")
        self.update_time = rule_toc.get("updateTime", "")
        self.pre_update_js = rule_toc.get("preUpdateJs", "")
        self.is_volume = rule_toc.get("isVolume", "")
        self.is_vip = rule_toc.get("isVip", "")
        self.is_pay = rule_toc.get("isPay", "")


@dataclass
class BookSourceEntity:
    comment: str
    group: str
    name: str
    type: int
    url: str

    url_pattern: str
    custom_order: int
    enabled: bool
    enabled_cookie_jar: bool
    enabled_explore: bool
    explore_url: str
    header: str
    last_update_time: int
    login_url: str
    response_time: int

    rule_book_info: Optional[RuleBookInfoEntity]
    rule_content: Optional[RuleContentEntity]
    rule_explore: Optional[RuleExploreEntity]
    rule_search: Optional[RuleSearchEntity]
    rule_toc: Optional[RuleTocEntity]

    search_url: str
    weight: int

    def __init__(self, book_source: dict) -> None:
        self._book_source = copy.deepcopy(book_source)
        self.comment = book_source.get("bookSourceComment", "")
        self.group = book_source.get("bookSourceGroup", "")
        self.name = book_source.get("bookSourceName", "")
        self.type = book_source.get("bookSourceType", 0)
        self.url = book_source.get("bookSourceUrl", "")

        self.url_pattern = book_source.get("bookUrlPattern", "")
        self.custom_order = book_source.get("customOrder", 0)
        self.enabled = book_source.get("enabled", True)
        self.enabled_cookie_jar = book_source.get("enabledCookieJar", False)
        self.enabled_explore = book_source.get("enabledExplore", False)
        self.explore_url = book_source.get("exploreUrl", "")
        self.header = book_source.get("header", "")
        self.last_update_time = book_source.get("lastUpdateTime", 0)
        self.login_url = book_source.get("loginUrl", "")
        self.response_time = book_source.get("responseTime", 1500)

        self.rule_book_info = RuleBookInfoEntity(book_source.get("ruleBookInfo", {}))
        self.rule_content = RuleContentEntity(book_source.get("ruleContent", {}))
        self.rule_explore = RuleExploreEntity(book_source.get("ruleExplore", {}))
        self.rule_search = RuleSearchEntity(book_source.get("ruleSearch", {}))
        self.rule_toc = RuleTocEntity(book_source.get("ruleToc", {}))

        self.search_url = book_source.get("searchUrl", "")
        self.weight = book_source.get("weight", 0)

    def copy(self):
        return copy.deepcopy(self)
