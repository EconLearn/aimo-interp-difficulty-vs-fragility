"""Answer-preserving surface changes to a problem text (no model needed): a few letter swaps in ordinary words and one
irrelevant sentence. Maths ($...$, \\(...\\), numbers, single letters, capitalised names) is never touched."""
import random
import re

_MATH = re.compile(r"(\$\$.*?\$\$|\$[^$]*\$|\\\(.*?\\\)|\\\[.*?\\\])", re.S)
_WORD = re.compile(r"([a-z]{5,})([.,;:!?)]*)")
_NOTES = (
    "As a side note, this problem was discussed at a seminar attended by 37 students from 12 schools.",
    "For context, the problem comes from a collection of 48 exercises compiled over 15 years.",
    "Incidentally, the room where this was first posed had 23 chairs and 9 tables.",
    "By the way, the original handout for this problem was printed on 64 sheets in 2 colours.",
)


def typos(text, rng, rate=0.10):
    parts = _MATH.split(text)
    for i in range(0, len(parts), 2):                       # even pieces are outside maths
        words = re.split(r"(\s+)", parts[i])
        for j, w in enumerate(words):
            m = _WORD.fullmatch(w)
            if m and rng.random() < rate:
                s = m.group(1)
                k = rng.randrange(1, len(s) - 2)
                words[j] = s[:k] + s[k + 1] + s[k] + s[k + 2:] + m.group(2)
        parts[i] = "".join(words)
    return "".join(parts)


def distract(text, rng):
    note = rng.choice(_NOTES)
    parts = _MATH.split(text)
    m = re.search(r"(?<=[a-z]{3}[.!?])\s+(?=[A-Z])", parts[0])   # first sentence end before any maths
    if m:
        parts[0] = parts[0][:m.start()] + " " + note + " " + parts[0][m.end():]
        return "".join(parts)
    return note + " " + text


def perturb(text, seed, kind="typo_distract"):
    rng = random.Random(seed)
    out = text
    if "typo" in kind:
        out = typos(out, rng)
    if "distract" in kind:
        out = distract(out, rng)
    return out
