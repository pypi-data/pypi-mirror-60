import os
import sys
from typing import Optional

from .filemanager import FileGenerator
from .utils import get_random_string


class Structure(object):
    def __init__(self, project_name: str, struct_type: str):
        self.project_name = project_name
        self.struct_type = struct_type

    def get_lib_path(self):
        for path in sys.path:
            if 'site-packages' in path:
                return path

    def install_dependencies(self):
        dependencies = [
            'zappa==0.47.1',
            'requests>=2.18.1',
            'validators',
            'pytz>=2018.4',
            'six==1.11.0',
            'boto',
            'boto3',
            'django-storages',
            'django-cors-headers',
            'cfn-flip==1.0.2',
            'eventmonitoring-client',
            'smart-integration-utils',
        ]
        with open('.req.txt', 'a') as f:
            for d in dependencies:
                f.write(d + '\n')
        os.system('pip install -r .req.txt')
        os.remove('.req.txt')

    def init_django_app(self):
        os.system(f'django-admin startproject {self.project_name}')

    def _gen_file(self, templates_path: str, name: str, params: Optional[dict] = None):
        file_path = f'{templates_path}/{name}'
        new_file_name = name.replace('base_', '').replace('.tpl', '').replace('_', '.')
        generator = FileGenerator(file_path, new_file_name, params)
        generator.write_file()

    def rewrite_basic_files(self):
        os.chdir(self.project_name)
        lib_path = self.get_lib_path()
        templates_path = lib_path + '/smart_cli/templates'
        params = {'project_name': self.project_name, 'secret_key': get_random_string()}
        for name in os.listdir(templates_path):
            if name.endswith('.tpl'):
                self._gen_file(templates_path, name, params)

    def generate_api_apps_files(self):
        os.chdir(self.project_name)
        os.mkdir('api')
        os.chdir(self.project_name + '/api')
        os.mkdir('migrations')
        lib_path = self.get_lib_path()
        templates_path = lib_path + '/smart_cli/templates/api/'

        with open('/api/migrations/__init__.py', 'w') as f:
            f.write('')

        for name in os.listdir(templates_path):
            if self.struct_type == 'oauth':
                if name == 'basic_views_py.tpl':
                    continue
                self._gen_file(templates_path, name)
            else:
                if name == 'oauth_views_py.tpl':
                    continue
                self._gen_file(templates_path, name)
