PyramidCMS migrations
=====================

This directory only contains the migrations for pyramidcms and does not
contain an alembic environment itself.

The idea is that the app using pyramidcms has it's own alembic folder,
which contains the actual alembic environment.  That environment should
then run the migrations for both the cms and for the app itself.
