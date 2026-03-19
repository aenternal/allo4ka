import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProfanityMatch:
    fragment: str
    normalized: str
    pattern: str


class ProfanityFilter:
    _word_pattern = re.compile(r"[a-zA-Zа-яА-ЯёЁ0-9_*-]+")
    _substitutions = str.maketrans(
        {
            "@": "а",
            "$": "с",
            "0": "о",
            "3": "з",
            "4": "ч",
            "6": "б",
            "8": "в",
        }
    )
    _latin_to_cyrillic = str.maketrans(
        {
            "a": "а",
            "b": "в",
            "c": "с",
            "e": "е",
            "k": "к",
            "m": "м",
            "h": "н",
            "o": "о",
            "p": "р",
            "t": "т",
            "x": "х",
            "y": "у",
        }
    )
    _patterns = {
        "eb": re.compile(r"(?:(?:у|за|вы|по|про|под|пере|недо|до|раз)?е+б+(?:а|о|у|и|ы|е|ё)?н*(?:н|нн)?(?:ый|ая|ое|ые|ого|ому|ым|ых|ость|уть|ут|утый|анная|аный)?)"),
        "pizd": re.compile(r"п+[иеё]?[зс]д(?:а|е|о|у|ы|ой|ат|еть|ец|юк|юл|юк[аи]?|атый|ю?д)"),
        "hui": re.compile(r"х+у+[йиеяё](?:н|в|л|т|щ|ш|р|м|к|д|с|ц)?(?:я|е|и|ю|ый|ая|ое|ые|ами|ах)?"),
        "blyad": re.compile(r"б+л+[яеё]д(?:ь|и|ь?ю|ский|ская|ское|ские|ство|оват|овать)?"),
        "mud": re.compile(r"м+у+д(?:а|о|и|е|ил|ил[ао]?|ак|ач|ень|озв|ила|ило|илак)"),
    }

    def normalize(self, text: str) -> str:
        text = text.lower().replace("ё", "е")
        text = text.translate(self._substitutions)
        text = text.translate(self._latin_to_cyrillic)
        text = re.sub(r"[^а-я0-9]+", " ", text)
        text = re.sub(r"(.)\1{2,}", r"\1\1", text)
        return text.strip()

    def find_matches(self, text: str) -> list[ProfanityMatch]:
        matches: list[ProfanityMatch] = []
        for raw_fragment in self._word_pattern.findall(text):
            normalized = self.normalize(raw_fragment)
            compact = normalized.replace(" ", "")
            if not compact:
                continue
            for name, pattern in self._patterns.items():
                if pattern.search(compact):
                    matches.append(
                        ProfanityMatch(fragment=raw_fragment, normalized=compact, pattern=name)
                    )
                    break
        return matches

    def contains_profanity(self, text: str) -> bool:
        return bool(self.find_matches(text))
