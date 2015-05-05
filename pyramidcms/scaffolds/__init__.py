from pyramid.scaffolds import PyramidTemplate


class CMSProjectTemplate(PyramidTemplate):
    """
    A scaffold for a project using PyramidCMS.

    To create a project, use "prcreate -s pyramidcms <projectname>".
    """
    _template_dir = 'pyramidcms'
    summary = 'PyramidCMS project'
