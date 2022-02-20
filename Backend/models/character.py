from models.decorators import *
from typing import List

from statham.schema.constants import Maybe
from statham.schema.elements import Array, Integer, Object, String
from statham.schema.property import Property


class ImplicitPower(YamlDump):
    name: Maybe[str] = Property(String())
    actions: Maybe[List[str]] = Property(Array(String()))


class Character(YamlDump):
    name: Maybe[str] = Property(String())
    health: Maybe[int] = Property(Integer())
    deck: Maybe[str] = Property(String())
    power: Maybe[ImplicitPower] = Property(ImplicitPower)
    incapacitated: Maybe[List[str]] = Property(Array(String()))
