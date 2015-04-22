"""
All models need to be imported here and added to __all__.

This both satisfies pyflakes static code analysis for unused imports,
it is also used to provide an instance to each model on it's own manager
class instance, objects. (it bootstraps Model.objects.model basically)

We also need to import each model for alembic anyway, or they won't be
included in migrations which is not what we want, so this is a way that
all models always get imported when you import anything from db.models.
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
