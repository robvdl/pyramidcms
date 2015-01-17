"""
All models in are be imported here and added to __all__.

This satisfies pyflakes static code analysis, but it also used to
bootstrap the objects.model property for each model which is important.
"""

import sys

from .auth import User, Group, Permission

__all__ = [
    'User',
    'Group',
    'Permission',
]

for cls in __all__:
    model = getattr(sys.modules[__name__], cls)
    model.objects.model = model
