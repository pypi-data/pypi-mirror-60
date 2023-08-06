# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from typing import List

import re

task_details_from_tag_regex = re.compile(
    r"(^|\s+)(?P<task_tag>[Tt][Aa]#?(?P<id>\d+))(\s+|$)"
)


def find_ids(text: str, ids=None) -> List[str]:
    ids = ids or set([])
    id_, task_tag = _find_task_details(text)

    if id_:
        ids.add(id_)
        cleaned_text = _remove_task_from_text(text, task_tag)
        ids = find_ids(cleaned_text, ids)

    return sorted(list(ids))


def _find_task_details(text: str) -> (str, str):
    no_parentheses = re.sub(r"([()])", " ", text)
    res = re.search(task_details_from_tag_regex, no_parentheses)

    if res:
        group_dict = res.groupdict()
        return group_dict["id"], group_dict["task_tag"]

    return "", ""


def _remove_task_from_text(text: str, task_tag: str) -> str:
    return re.sub(task_tag, "", text)
