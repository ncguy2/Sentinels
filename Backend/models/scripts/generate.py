import sys
import statham.__main__
from pathlib import Path

decorator_header_added = None
def cleanup(file: Path):
    in_lines = file.read_text().splitlines()
    out_lines = []

    global decorator_header_added
    decorator_header_added = False

    def try_add_decorator():
        global decorator_header_added
        if decorator_header_added:
            return
        out_lines.insert(0, "from models.decorators import *")
        decorator_header_added = True

    idx = -1
    for line in in_lines:
        idx += 1
        if 1 < idx < len(in_lines) - 1:
            if len(line) == 0:
                if len(in_lines[idx - 1]) > 0 and len(in_lines[idx + 1]) > 0:
                    continue

        if line.startswith("class CompositionItem("):
            line = "class CompositionItem(Object, KVBase):"
            try_add_decorator()
        elif line.startswith("class Card("):
            line = "class Card(Object, KVBase):"
            try_add_decorator()
        elif line.startswith("class CardsItem("):
            line = "class CardsItem(Object, CardItemExt):"
            try_add_decorator()

        if line.startswith("class") and "Object" in line:
            line = line.replace("Object", "YamlDump")
            try_add_decorator()

        out_lines.append(line)

    file.write_text("\n".join(out_lines) + "\n")


def generate_models():
    models_root = Path(__file__).parent.parent
    root_in = models_root.parent.parent.parent / "Sentinels-data" / "schema"
    root_out = models_root

    for i in root_in.iterdir():
        if not i.name.endswith(".schema"):
            continue

        o = root_out / i.name.replace(".schema", ".py")

        sys.argv[1:] = ["--input", str(i), "--output", str(o)]
        statham.__main__.entry_point()
        cleanup(o)


if __name__ == '__main__':
    generate_models()
