import re

# noinspection PyUnresolvedReferences
from urllib.parse import unquote

from bs4 import BeautifulSoup, NavigableString
import requests
from pathlib import Path
import yaml
from models.character import Character, ImplicitPower
from models.deck import Deck, Flavour, Card, CompositionItem, Power
import multiprocessing

complexities = {}
is_mp = True


class ScrapeException(Exception):
    def __init__(self, url, base_exc):
        self.url = url
        self.base_exc = base_exc

    def __str__(self):
        return f"Error occurred when scraping {self.url}. [{type(self.base_exc).__name__}] {self.base_exc}"


def make_soup(html):
    soup = BeautifulSoup(html, "lxml")
    return soup


def read_url(url):
    print("Reading url: " + url)
    r = requests.get(url)
    return r.text


def next_sibling_of_tag(element, tag):
    if element.next_sibling is None:
        return None
    if element.next_sibling.tag == tag:
        return element.next_sibling
    return next_sibling_of_tag(element.next_sibling, tag)


def format(s):
    return unquote(s).replace("_", " ")


def sanitise(s):
    return s.replace("\r", "").replace("\n", "").replace("\t", "").replace(".", "").replace(":", "")


def _strip_null_or_empty_item(x):
    if isinstance(x, str):
        return not (x is None or len(x) == 0)
    return x is not None


def strip_null_or_empty(gen):
    return [x for x in gen if _strip_null_or_empty_item(x)]


def parse_action(a):
    # TODO support powers on cards
    # if a.startsWith("Power:"):
    #     p = Power({})
    #     p.actions = parse_actions(a)
    #     return p
    return a.strip()


def parse_actions(action_str):
    return strip_null_or_empty([sanitise(parse_action(x)) for x in action_str.split(".")])


def get_gallerybox(soup, tab_idx):
    g = soup.find_all("li", class_="gallerybox")
    yield from [x for x in g if f"tabs-content-{tab_idx}" in x.parent.parent.attrs["class"]]


def parse_ul_to_list(ul):
    l = []
    for c in ul.children:
        l.append(sanitise(c.text))
    return strip_null_or_empty(l)


def parse_relevant_incapacitated(soup, name):
    for x in get_gallerybox(soup, 2):
        c = x.find("center")
        if c is not None and c.b.text == name:
            return parse_ul_to_list(x.find("ul"))

    old_name = name
    if ":" in name:
        s = name.split(": ")
        name = f"{s[1]}: {s[0]}"

        # Try again after flipping the name
        for x in get_gallerybox(soup, 2):
            c = x.find("center")
            if c is not None and c.b.text == name:
                return parse_ul_to_list(x.find("ul"))

    return ["Error, cannot find incapacitated info", f"Tried {old_name} and {name}"]


def format_name(name):
    if "," in name:
        return name.split(",")[0]
    return name


def parse_variant(soup, gallery_item, deck_name):
    try:
        if "villain" in gallery_item.parent.parent.parent.parent.previous_sibling.previous_sibling.text.lower():
            return None
    except:
        pass

    text = gallery_item.find("div", class_="gallerytext")

    bolds = text.find_all("b")

    if len(bolds) < 3:
        return None

    name = bolds[0].text
    health = (bolds[1].text + bolds[1].next_sibling.text).split(":")[1].strip()
    power_name = bolds[2].text
    power_action = bolds[2].next_sibling.text

    c = Character({})
    c.deck = deck_name
    c.name = format_name(name)
    c.health = int(health)
    c.power = ImplicitPower({})
    c.power.name = sanitise(power_name)
    c.power.actions = strip_null_or_empty(parse_actions(power_action))
    c.incapacitated = strip_null_or_empty(parse_relevant_incapacitated(soup, name))

    return c


def parse_tags(root):
    return [x.strip() for x in root.text.split(",")]


def extract_amount(mult):
    try:
        m = re.search(r"x([0-9]+)", mult)
        if m is None:
            return 1
        return int(m.group(1))
    except ValueError:
        return 1


def parse_flavour_text(text):
    f = Flavour({})
    text = text.replace("Flavor-Text: ", "").strip().strip("\"\'\\")
    text = text.replace("\\u2019", "'")
    t = text.split(" - ")
    f.text = t[0]
    f.source = t[1] if len(t) > 1 else ""
    return f


def parse_deck(soup, name):
    second_tab_container = soup.find_all("div", class_="tabs-content-1")[1]
    dl_set = second_tab_container.find_all("dl")

    global complexities

    d = Deck({})
    d.name = name
    d.cards = []
    d.composition = []
    d.complexity = complexities[d.name] if d.name in complexities else "Unknown"

    for dl in dl_set:
        if dl.parent.parent == second_tab_container:
            if dl.previous_sibling.previous_sibling.b is None:
                continue
            tags = parse_tags(dl.previous_sibling.previous_sibling.b)
            for child in dl.children:
                if isinstance(child, NavigableString):
                    continue
                if child.b is None:
                    continue
                c = Card({})
                c.name = child.b.text
                amount = extract_amount(child.b.next_sibling.text)

                d.composition.append(CompositionItem({c.name: amount}))

                card_dds = child.find_all("dd")
                card_dds = [x for x in card_dds if x.find("dd") is None]
                c.actions = parse_actions(card_dds[0].text)
                c.flavour = parse_flavour_text(card_dds[-1].text)
                c.tags = tags
                d.cards.append({c.name: c})
    return d


def parse_page(url, name):
    soup = make_soup(read_url(url))

    for x in get_gallerybox(soup, 1):
        v = parse_variant(soup, x, name)
        if v is not None:
            yield v

    yield parse_deck(soup, name)


def group_by_type(heap):
    data = {}

    for e in heap:
        key = type(e)
        if key not in data:
            data[key] = []
        data[key].append(e)

    return data


def prepare_name_for_file(name: str):
    return name.lower().replace(" ", "_")


def handle_url(url, output_dir):
    name = re.search(r"\?title=(.*?)$", url)
    name = format(name.group(1))

    data = strip_null_or_empty(parse_page(url, name))
    map = group_by_type(data)

    char_file = output_dir / "characters" / f"char_{prepare_name_for_file(name)}.yaml"
    deck_file = output_dir / "decks" / f"deck_{prepare_name_for_file(name)}.yaml"

    # char_file.unlink(missing_ok=True)
    # deck_file.unlink(missing_ok=True)

    chars = [{"character": x.to_obj()} for x in map[Character]]
    decks = [{"deck": x.to_obj()} for x in map[Deck]]

    yaml.dump_all(chars, char_file.open(mode="w"), sort_keys=False, width=256, encoding="ASCII")
    yaml.dump_all(decks, deck_file.open(mode="w"), sort_keys=False, width=256, encoding="ASCII")


def parse_complexity(s):
    return int(s[len("Complexity "):])


def get_character_urls(summary_url):
    global complexities
    soup = make_soup(read_url(summary_url))

    table = soup.find("table")
    for row in table.tbody.children:
        if isinstance(row, NavigableString) or row.name != "tr":
            continue
        caption_div = row.find("div", class_="thumbcaption")
        if caption_div is None:
            continue
        a = [x for x in caption_div.find_all("a") if x.parent == caption_div][0]

        tds = row.find_all("td")

        # Check if it's a variant
        if "Parent Deck" in tds[1].text:
            continue

        comp_cell = tds[3]
        complexity_str = comp_cell.img.attrs["alt"] if comp_cell.img is not None else "Complexity 0"
        complexity = parse_complexity(complexity_str)

        if complexity == 0:
            continue

        name = a.attrs["title"]
        complexities[name] = complexity

        yield a.attrs["href"]

    return []


def handle_url_mp(payload):
    global complexities
    complexities = payload[2]
    if is_mp:
        try:
            handle_url(payload[0], payload[1])
        except Exception as e:
            raise ScrapeException(payload[0], e)
    else:
        handle_url(payload[0], payload[1])


if __name__ == '__main__':
    root_url = "https://sentinelswiki.com"
    summary_url = f"{root_url}/index.php?title=Heroes"
    urls = [f"{root_url}{x}" for x in get_character_urls(summary_url)]
    # urls = ["https://sentinelswiki.com/index.php?title=K.N.Y.F.E."]
    output_dir = Path(__file__).parent.parent.parent.parent / "Sentinels-data"

    mp_data = [(x, output_dir, complexities) for x in urls]

    if is_mp:
        with multiprocessing.Pool(16) as p:
            p.map(handle_url_mp, mp_data)
    else:
        for payload in mp_data:
            handle_url_mp(payload)

