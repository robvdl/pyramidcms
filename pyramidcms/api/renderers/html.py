import json

from pyramid_jinja2 import renderer_factory


class BrowsableAPIRenderer(object):
    """
    If the API is browsed directly using a web browser, this renderer
    will be used to render HTML pages for navigating the API.
    """

    def __init__(self, info):
        """
        info.type and info.name both contain the name of the renderer,
        however we want to replace info.name with the template name,
        so that pyramid_jinja2 will know what template to render.
        """
        self.info = info

    def __call__(self, value, system):
        # the API view should return a Bundle
        bundle = value

        # if bundle.obj=None we use the list view, otherwise detail view
        if bundle.obj:
            self.info.name = 'api/obj_detail.jinja2'
        else:
            self.info.name = 'api/obj_list.jinja2'

        # format JSON nicely for display
        data = bundle.__json__(system.get('request'))
        bundle.json = json.dumps(data, indent=4, sort_keys=True)

        renderer = renderer_factory(self.info)
        return renderer({'bundle': bundle}, system)
