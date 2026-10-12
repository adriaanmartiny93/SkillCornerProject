"""Mapping from SkillCorner positions to role groups.

Similarity is only computed within a role group. LM / RM are the two central
midfielders of a midfield three in this data, so they form the CM group.

The mapping can be edited in the app; it is then stored in
`data/role_mapping.csv` and that file is the truth. A position that is in no
role is left out of the player table.
"""

import pandas as pd

from src.data.loaders import ROLE_MAPPING_PATH, load_stored, save_stored

DEFAULT_ROLE_POSITIONS = {
    "CB": ["CB", "LCB", "RCB"],
    "FB/WB": ["LB", "RB", "LWB", "RWB"],
    "DM": ["DM", "LDM", "RDM"],
    "CM": ["LM", "RM"],
    "AM": ["AM"],
    "W": ["LW", "RW", "LF", "RF"],
    "CF": ["CF"],
}


def role_positions() -> dict[str, list[str]]:
    """Role -> positions: the stored mapping, or the default if none is stored."""
    stored = load_stored(ROLE_MAPPING_PATH)
    if stored is None:
        return DEFAULT_ROLE_POSITIONS
    return {role: rows["position"].tolist() for role, rows in stored.groupby("role", sort=False)}


def position_to_role() -> dict[str, str]:
    return {position: role for role, positions in role_positions().items() for position in positions}


def save_role_positions(mapping: dict[str, list[str]]) -> None:
    rows = [(role, position) for role, positions in mapping.items() for position in positions]
    save_stored(pd.DataFrame(rows, columns=["role", "position"]), ROLE_MAPPING_PATH)
