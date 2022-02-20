from models.decorators import *
from typing import Any, List, Union

from statham.schema.constants import Maybe
from statham.schema.elements import AnyOf, Array, Integer, Object, String
from statham.schema.property import Property


class Power(YamlDump):
    actions: Maybe[List[str]] = Property(Array(String()))


class CompositionItem(YamlDump, KVBase):
    pass


class Stats(YamlDump):
    build: Maybe[int] = Property(Integer())
    charge: Maybe[int] = Property(Integer())
    heal: Maybe[int] = Property(Integer())
    multishot: Maybe[int] = Property(Integer())
    support: Maybe[int] = Property(Integer())
    tank: Maybe[int] = Property(Integer())


class CardsItem(YamlDump, CardItemExt):
    pass


class Deck(YamlDump):
    name: Maybe[str] = Property(String())
    complexity: Maybe[int] = Property(Integer())
    composition: Maybe[List[CompositionItem]] = Property(Array(CompositionItem))
    stats: Maybe[Stats] = Property(Stats)
    cards: Maybe[List[CardsItem]] = Property(Array(CardsItem))


class ActionArrayItem(YamlDump):
    pass


class Flavour(YamlDump):
    text: Maybe[str] = Property(String())
    source: Maybe[str] = Property(String())


class Card(YamlDump, KVBase):
    actions: Maybe[List[Union[str, ActionArrayItem]]] = Property(Array(AnyOf(String(), ActionArrayItem)))
    flavour: Maybe[Flavour] = Property(Flavour)
    tags: Maybe[List[str]] = Property(Array(String()))
