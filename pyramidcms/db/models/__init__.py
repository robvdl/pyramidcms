"""
All models in are be imported here and added to __all__.

This satisfies pyflakes static code analysis, but it also used to
bootstrap the objects.model property for each model which is important.
"""

from .auth import User, Group, Permission

__all__ = [
    User,
    Group,
    Permission
]

# This works fine for now, but not sure what we are going to do later
# when supporting models in user code instead of pyramidcms core.
for cls in __all__:
    cls.objects.model = cls
