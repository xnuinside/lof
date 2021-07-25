import os

import pytest

from lof import parser

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize("format_name", ["json", "yaml"])
def test_parse_template_content(format_name):
    path = os.path.join(CURRENT_DIR, f"test_data/template.{format_name}")
    with open(path) as f:
        assert parser._parse_template(f, format_name) is not None
