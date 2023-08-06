# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest

from odoo_regex_set import task


@pytest.mark.parametrize(
    "input_,expected",
    [
        ("TA#6789", ["6789"]),
        ("TA#1234 TA#4567", ["1234", "4567"]),
        ("TA#1234, TA#4567", ["1234", "4567"]),
        ("TA#1234. TA#4567", ["1234", "4567"]),
        ("TA#1234! TA#4567!", ["1234", "4567"]),
        ("TA#1234 TA#4567 ta0987", ["0987", "1234", "4567"]),
        ("(TA#6890 TA#4567)", ["4567", "6890"]),
        (
                """
        TA#1234
        TA#4567
        ta0987
        """,
                ["0987", "1234", "4567"]
        )  # multilines,
    ]
)
def test_find_ids_found(input_, expected):
    """ Test the function accepts any numbers of tags"""
    assert task.find_ids(input_) == expected


@pytest.mark.parametrize(
    "input_",
    [
        "",  # empty string
    ]
)
def test_find_ids_empty(input_):
    assert not task.find_ids(input_)


@pytest.mark.parametrize(
    "input_,expected",
    [
        ("TA#6789", ("6789", "TA#6789")),
        ("TA#6789 TA#6789", ("6789", "TA#6789")),
        ("ta#6752", ("6752", "ta#6752")),
        ("TA6785", ("6785", "TA6785")),
        ("ta6751", ("6751", "ta6751")),
        ("Some text TA#6787 followed by some text", ("6787", "TA#6787")),
        ("(TA#6752)", ("6752", "TA#6752")),
        ("Une phrase avec le tag suivi par un point TA#6754", ("6754", "TA#6754"))
    ]
)
def test_find_task_details_success(input_, expected):
    assert task._find_task_details(input_) == expected


@pytest.mark.parametrize(
    "input_",
    [
        "",  # empty string
        "⁣TA#6789⁣",  # invisble spaces
        "6TA#5678",  # a number before the tag
        "tt#5678",  # not the correct tag
        "sometextnospaceTA#5678nospace",  # the tag with some text around without any spaces
        "TA#4567nospace",  # the tag followed by some text without space
        "34567TA4567nospace",  # some numbers a tag and some text after
        "3456TA#3456",  # some numbers then a tag
        "56789-TA#4567-45678",  # tag surrounded by -
        "4567-TA#4567$sometext"  # tag surrounded by special characters
        "^⁣TA#5647"  # tag with a special character before
    ]
)
def test_find_task_details_failure(input_):
    assert task._find_task_details(input_) == ("", "")


@pytest.mark.parametrize(
    "text,task_tag,expected",
    [
        ("", "", ""),
        ("TA#6789", "TA#6789", ""),
        ("TA#6789", "TA#1234", "TA#6789"),
        ("TA#1234 TA#6789", "TA#1234", " TA#6789"),
        ("TA#1234 TA#6789", "TA#6789", "TA#1234 "),
        ("TA#1234 TA#1234", "TA#1234", " "),  # remove the task tags but not the space :)
    ]
)
def test_remove_task_from_text(text, task_tag, expected):
    assert task._remove_task_from_text(text, task_tag) == expected
