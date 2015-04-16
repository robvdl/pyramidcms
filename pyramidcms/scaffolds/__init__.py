import os
import codecs

from pyramid.scaffolds import PyramidTemplate


class PyramidCMSProjectTemplate(PyramidTemplate):
    _template_dir = 'pyramidcms'
    summary = 'PyramidCMS project'

    def secret_key_generator(self, length):
        """
        Generate a new secret key using length given.
        """
        return codecs.encode(os.urandom(length), 'hex').decode('utf-8')

    def pre(self, command, output_dir, vars):
        vars['secret_key'] = self.secret_key_generator(40)
        return super().pre(command, output_dir, vars)
