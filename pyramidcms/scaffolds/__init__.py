from pyramid.scaffolds import PyramidTemplate

from pyramidcms.security import secret_key_generator


class CMSProjectTemplate(PyramidTemplate):
    """
    A scaffold for a project using PyramidCMS.

    To create a project, use "prcreate -s pyramidcms <projectname>".
    """
    _template_dir = 'pyramidcms'
    summary = 'PyramidCMS project'

    def pre(self, command, output_dir, vars):
        vars['secret_key'] = secret_key_generator(40)
        return super().pre(command, output_dir, vars)
