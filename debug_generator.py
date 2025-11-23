#!/usr/bin/env python
"""Debug generator output"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.generators.playwright_gen import PlaywrightGenerator
from src.core.element import Element


def create_test_element(**kwargs):
    defaults = {
        'index': 0,
        'uuid': 'test-uuid-123',
        'tag': 'input',
        'type': 'email',
        'id': 'email-field',
        'name': 'email',
        'placeholder': 'Enter email',
        'text': '',
        'classes': [],
        'attributes': {'type': 'email', 'id': 'email-field', 'name': 'email'},
        'selector': 'input[type=\"email\"][id=\"email-field\"]',
        'xpath': "//input[@id='email-field']",
        'visible': True,
        'enabled': True,
        'disabled': False,
    }
    defaults.update(kwargs)
    return Element(**defaults)


elements = [
    create_test_element(index=0, type="email", id="email-input", name="email"),
    create_test_element(index=1, type="password", id="password-input", name="password"),
    create_test_element(index=2, tag="button", type="submit", id="submit-btn", text="Submit"),
]

generator = PlaywrightGenerator()
code = generator.generate(elements, url="https://example.com/login")

print("="*60)
print("Generated Playwright Code:")
print("="*60)
print(code)
print("="*60)
