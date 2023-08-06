# from re import Pattern, Match
from re import Match

from markdown import Markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.util import etree

__all__ = ["makeExtension"]

RATING_RE = r"\[rating: *([0-5]) *\]"


class RatingsProcessor(InlineProcessor):
    def handleMatch(self, m: Match, data):
        rating_parent = etree.Element("span")

        rating_value = int(m.group(1))

        for r in range(0, 5):
            class_ = "fa fa-star star-checked" if r < rating_value else "fa fa-star"
            rating_item = etree.Element("span", {"class": class_})
            rating_parent.append(rating_item)

        return rating_parent, m.start(0), m.end(0)


class RatingsExtension(Extension):
    def extendMarkdown(self, mdown: Markdown):
        mdown.registerExtension(self)
        mdown.inlinePatterns.register(RatingsProcessor(RATING_RE), "stars-rating", 75)


def makeExtension(**kwargs):
    return RatingsExtension(**kwargs)
