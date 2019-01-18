import os

from core.enums.app_type import AppType
from core.settings import Settings
from core.utils.file_utils import Folder
from core.utils.file_utils import File
from core.utils.json_utils import JsonUtils
from core.utils.perf_utils import PerfUtils


class TnsAssert(object):
    NODE_MODULES = 'node_modules'
    TNS_MODULES = os.path.join(NODE_MODULES, 'tns-core-modules')
    HOOKS = 'hooks'

    @staticmethod
    def created(app_name, output=None, app_data=None):

        # Assert app exists
        app_path = os.path.join(Settings.TEST_RUN_HOME, app_name)
        assert Folder.exists(app_path), 'Failed to create app. ' + os.linesep + app_path + ' do not exists!'

        # Assert output
        if output is not None:
            app = app_name.rsplit('/')[-1]
            assert 'Now you can navigate to your project with $ cd' in output
            assert 'After that you can preview it on device by executing $ tns preview' in output
            assert 'After that you can run it on device/emulator by executing $ tns run <platform>' not in output
            assert 'Project {0} was successfully created'.format(app) in output, 'Failed to create {0}'.format(app)

        # Assert app data
        if app_data is not None:
            # Assert app type
            assert File.exists(os.path.join(app_path, 'node_modules', 'tns-core-modules', 'package.json'))
            assert File.exists(os.path.join(app_path, 'node_modules', 'tns-core-modules', 'LICENSE'))
            assert File.exists(os.path.join(app_path, 'node_modules', 'tns-core-modules', 'xml', 'xml.js'))
            assert Folder.exists(os.path.join(app_path, 'node_modules', 'nativescript-theme-core'))
            assert Folder.exists(os.path.join(app_path, 'node_modules', 'nativescript-dev-webpack'))

            if app_data.type is AppType.JS:
                pass
            elif app_data.type is AppType.TS:
                assert File.exists(os.path.join(app_path, 'tsconfig.json'))
                assert File.exists(os.path.join(app_path, 'webpack.config.js'))
                assert File.exists(os.path.join(app_path, 'tsconfig.tns.json'))
                assert not File.exists(os.path.join(app_path, 'references.d.ts'))
                assert File.exists(os.path.join(app_path, 'node_modules', 'tns-core-modules', 'tns-core-modules.d.ts'))
                assert File.exists(os.path.join(app_path, TnsAssert.HOOKS, 'before-prepare', 'nativescript-dev-typescript.js'))
                assert File.exists(os.path.join(app_path, TnsAssert.HOOKS, 'before-watch', 'nativescript-dev-typescript.js'))
                pass
            elif app_data.type is AppType.NG:
                assert File.exists(os.path.join(app_path, 'tsconfig.json'))
                assert File.exists(os.path.join(app_path, 'webpack.config.js'))
                assert File.exists(os.path.join(app_path, 'tsconfig.tns.json'))
                assert not File.exists(os.path.join(app_path, 'references.d.ts'))
                assert File.exists(os.path.join(app_path, 'node_modules', 'tns-core-modules', 'tns-core-modules.d.ts'))
                assert File.exists(os.path.join(app_path, TnsAssert.HOOKS, 'before-prepare', 'nativescript-dev-typescript.js'))
                assert File.exists(os.path.join(app_path, TnsAssert.HOOKS, 'before-watch', 'nativescript-dev-typescript.js'))
                pass
            elif app_data.type is AppType.VUE:
                pass
            elif app_data.type is AppType.SHARED_NG:
                pass

            # Assert app id
            if app_data.id is not None:
                pass

            # Assert size
            if app_data.size is not None:
                app_size = Folder.get_size(app_path)
                assert PerfUtils.is_value_in_range(actual=app_size, expected=app_data.size.init,
                                                   tolerance=0.25), 'Actual project size is not expected!'

    @staticmethod
    def platform_added(app_name, platform, output):
        platform_string = str(platform)
        # Verify output
        assert 'Platform {0} successfully added'.format(platform_string) in output
        # Verify package.json
        app_path = os.path.join(Settings.TEST_RUN_HOME, app_name)
        package_json = os.path.join(app_path, 'package.json')
        json = JsonUtils.read(package_json)
        # noinspection SpellCheckingInspection
        assert json['nativescript']['tns-' + platform_string]['version'] is not None, \
            'tns-' + platform_string + ' not available in package.json of the app.'

    @staticmethod
    def build(app_name, platform=None, release=False, provision=Settings.IOS.DEV_PROVISION, for_device=False,
              bundle=False, aot=False, uglify=False, snapshot=False, log_trace=False, output=None, app_data=None):
        # Verify output and exit code
        assert 'Project successfully built.' in output

        # Assert app data
        if app_data is not None:
            # Assert app type
            if app_data.type is AppType.JS:
                pass
            elif app_data.type is AppType.TS:
                pass
            elif app_data.type is AppType.NG:
                pass
            elif app_data.type is AppType.SHARED_NG:
                pass

            # Assert size
            if app_data.size is not None:
                pass
