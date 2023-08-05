
def strip_punchuation(s, all=False):
    """Removes punctuation from a string.
    :param s: The string.
    :param all: Remove all punctuation. If False, only removes punctuation from
        the ends of the string.
    """
    if all:
        return PUNCTUATION_REGEX.sub('', s.strip())
    else:
        return s.strip().strip(string.punctuation)


def itokenize(self, text, *args, **kwargs):
        """Return a generator that generates tokens "on-demand".
        .. versionadded:: 0.6.0
        :rtype: generator
        """
        return (t for t in self.tokenize(text, *args, **kwargs))


def lowerstrip(s, all=False):
    """Makes text all lowercase and strips punctuation and whitespace.
    :param s: The string.
    :param all: Remove all punctuation. If False, only removes punctuation from
        the ends of the string.
    """
    return strip_punchuation(s.lower().strip(), all=all)
