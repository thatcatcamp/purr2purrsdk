"""
copyright (c) 2023 CAT Camp
"""
# these can be overridden
import base64
import datetime
import json
import os
from dataclasses import dataclass
from enum import Enum

import jsons

CAMP_NAME = "rogue"
PURRSISTANT_ROOT = "./purrsistant"
DEFAULT_YEAR = "2023"
DEFAULT_TYPE = 1


class PurrException(Exception):
    def __init__(self, message="unknown error"):
        self.message = message
        super().__init__(self.message)


def is_encoded_right(s: str):
    if len(s) == 0:
        return True
    try:
        return base64.b64encode(base64.b64decode(s)) == s
    except Exception:
        return False


class Hooman:
    ID: str
    PlayaName: str
    Year: str
    Issuer: str

    def __init__(self, id_in: str, pn_in: str, year_in: str, issuer_in: str):
        self.ID = id_in
        self.Year = year_in
        self.Issuer = issuer_in
        self.PlayaName = pn_in


@dataclass
class ItemType(Enum):
    STAMP = 1
    PHOTO = 2


@dataclass
class PurrsistantItem:
    ID: str
    Camp_Name: str
    PostedGMTISO: str
    Type: ItemType
    Item: str
    Year: str

    def __init__(self, id_in: str, cn_in: str, item_in="", type_in=ItemType.STAMP):
        if len(id_in) < 8:
            raise PurrException("invalid hooman id")
        self.ID = id_in
        if len(id_in) < 4:
            raise PurrException("invalid camp")
        self.Camp_Name = cn_in
        # python dates suck more than js dates
        self.PostedGMTISO = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
        self.Year = DEFAULT_YEAR
        if len(item_in) > (1024 * 1024 * 8):
            raise PurrException("item is too large to upload - sorry")
        if not is_encoded_right(item_in):
            raise PurrException("item is not base64")
        self.Item = item_in
        self.Type = type_in

    def save(self):
        try:
            os.makedirs(PURRSISTANT_ROOT)
        except FileExistsError:
            pass
        print(self)
        with open(os.path.join(PURRSISTANT_ROOT, f"{self.ID}.json"), "wt") as f:
            json.dump(jsons.dump(self), f)


x = PurrsistantItem("XXXXXXXX", "X", "", ItemType.STAMP)
x.save()
