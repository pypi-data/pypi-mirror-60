"""
    Name: html.py
    Author: Charles Zhang <694556046@qq.com>
    Propose: A module to generate html code.
    Coding: UTF-8

    Change Log:
        **2020.01.29**
        Create this file!
"""


def str2html(src: str) -> str:
    """Switch normal string to a html type"""
    str_list = src.split("\n")
    while str_list[-1] == "\n" or str_list[-1] == "":
        str_list.pop()

    for i in range(len(str_list)):
        str_list[i] += "<br>"

    return "".join(str_list)


class Tag(object):
    """Tag

    A super class of all html tag class.

    Attributes:
        text: Text content.
        name: Tag name.
        subtag: Sub tags.
        attributes: Attributes of this tag.
    """

    def __init__(self, *subtag, **attributes):
        self.text = ""
        self.name = "tag"

        for tag in subtag:
            if not isinstance(tag, Tag):
                raise ValueError(str(tag) + "is not a subtag.")

        self.subtag = []
        for tag in subtag:
            self.subtag.append(tag)

        self.attributes = attributes

    def __str__(self):
        ret = []

        pre = ["".join(["<", self.name])]
        for key, value in self.attributes.items():
            pre.append("".join([" ", key, "=", "'", value, "'"]))
        pre.append(">")
        ret.append("".join(pre))

        if self.text:
            ret.append(self.text)

        for s in self.subtag:
            ret.append(str(s))

        ret.append("".join(["</", self.name, ">"]))

        return "".join(ret)

    def __lshift__(self, other):
        if not isinstance(other, Tag):
            raise ValueError(str(other) + "is not a subtag.")
        self.subtag.append(other)
        return self

    def print(self):
        print(str(self))

    def set_text(self, src: str):
        self.text = src
        return self


class body(Tag):
    def __init__(self, *subtag, **attributes):
        super().__init__(*subtag, **attributes)
        self.name = "body"


class div(Tag):
    def __init__(self, *subtag, **attributes):
        super().__init__(*subtag, **attributes)
        self.name = "div"


class font(Tag):
    def __init__(self, *subtag, **attributes):
        super().__init__(*subtag, **attributes)
        self.name = "font"


class h1(Tag):
    def __init__(self, *subtag, **attributes):
        super().__init__(*subtag, **attributes)
        self.name = "h1"


class h2(Tag):
    def __init__(self, *subtag, **attributes):
        super().__init__(*subtag, **attributes)
        self.name = "h2"


class h3(Tag):
    def __init__(self, *subtag, **attributes):
        super().__init__(*subtag, **attributes)
        self.name = "h3"


class h4(Tag):
    def __init__(self, *subtag, **attributes):
        super().__init__(*subtag, **attributes)
        self.name = "h4"


class h5(Tag):
    def __init__(self, *subtag, **attributes):
        super().__init__(*subtag, **attributes)
        self.name = "h5"


class h6(Tag):
    def __init__(self, *subtag, **attributes):
        super().__init__(*subtag, **attributes)
        self.name = "h6"


class head(Tag):
    def __init__(self, *subtag, **attributes):
        super().__init__(*subtag, **attributes)
        self.name = "head"


class html(Tag):
    def __init__(self, *subtag, **attributes):
        super().__init__(*subtag, **attributes)
        self.name = "html"


class p(Tag):
    def __init__(self, *subtag, **attributes):
        super().__init__(*subtag, **attributes)
        self.name = "p"


class table(Tag):
    def __init__(self, *subtag, **attributes):
        super().__init__(*subtag, **attributes)
        self.name = "table"


class th(Tag):
    def __init__(self, *subtag, **attributes):
        super().__init__(*subtag, **attributes)
        self.name = "th"


class title(Tag):
    def __init__(self, *subtag, **attributes):
        super().__init__(*subtag, **attributes)
        self.name = "title"


class tr(Tag):
    def __init__(self, *subtag, **attributes):
        super().__init__(*subtag, **attributes)
        self.name = "tr"


class td(Tag):
    def __init__(self, *subtag, **attributes):
        super().__init__(*subtag, **attributes)
        self.name = "td"
