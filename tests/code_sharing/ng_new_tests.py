import os
import unittest

from core.base_test.tns_run_test import TnsRunTest
from core.enums.env import EnvironmentType
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.enums.styling_type import StylingType
from core.settings import Settings
from core.utils.file_utils import Folder
from core.utils.json_utils import JsonUtils
from data.apps import Apps
from data.const import Colors
from products.angular.ng import NG, NS_SCHEMATICS
from products.nativescript.app import App
from products.nativescript.tns import Tns
from products.nativescript.tns_assert import TnsAssert
from products.nativescript.tns_paths import TnsPaths


# noinspection PyMethodMayBeStatic
class NGNewTests(TnsRunTest):
    app_name = Settings.AppName.DEFAULT
    app_path = TnsPaths.get_app_path(app_name=app_name)

    def setUp(self):
        TnsRunTest.setUp(self)
        NG.kill()
        Folder.clean(self.app_path)

    def tearDown(self):
        NG.kill()
        TnsRunTest.tearDown(self)

    def test_001_simple(self):
        NGNewTests.create_and_run(shared=False)
        NGNewTests.build_release()

    def test_010_shared(self):
        NGNewTests.create_and_run(shared=True)
        NG.serve(project=self.app_name)
        NG.kill()
        NGNewTests.build_release()
        NG.serve(project=self.app_name, prod=True)

    def test_100_shared_with_sample(self):
        NGNewTests.create_and_run(shared=True, sample=True)

    def test_200_simple_no_theme(self):
        NGNewTests.create_and_run(shared=False, theme=False)

    def test_201_shared_with_sass(self):
        NGNewTests.create_and_run(shared=False, style=StylingType.SCSS)

    def test_202_shared_with_custom_source_dir_and_prefix(self):
        NGNewTests.create_and_run(shared=True, prefix='myapp', source_dir='mysrc', style=StylingType.CSS)

    @unittest.skip('Ignore because of https://github.com/NativeScript/nativescript-schematics/issues/157')
    def test_300_help_ng_new(self):
        output = NG.exec_command('new --collection={0} --help'.format(NS_SCHEMATICS)).output
        assert '--sample' in output
        assert 'Specifies whether a sample master detail should be generated' in output
        assert '--shared' in output
        assert 'Specifies whether to generate a shared project or a {N} only' in output
        assert '--source-dir (-sd)' in output
        assert 'The path of the source directory' in output
        assert '--style' in output
        assert 'The file extension to be used for style files. Supported are css and scss' in output
        assert '--theme' in output
        assert 'Specifies whether the {N} theme for styling should be included' in output
        assert '--webpack' in output
        assert 'Specifies whether the new application has webpack set up' in output

    @staticmethod
    def create_and_run(shared=True, sample=False, theme=True, style=None, prefix=None, source_dir=None, webpack=True):
        # Get test data based on app type
        app_data = Apps.SCHEMATICS_NS
        if shared:
            if sample:
                app_data = Apps.SCHEMATICS_SHARED_SAMPLE
            else:
                app_data = Apps.SCHEMATICS_SHARED

        # Create app
        NGNewTests.create_app(app_data=app_data, shared=shared, sample=sample, theme=theme, style=style,
                              prefix=prefix, source_dir=source_dir, webpack=webpack)

        # Update the app
        if Settings.ENV != EnvironmentType.LIVE:
            App.update(app_name=NGNewTests.app_name, modules=True, angular=True, typescript=True, web_pack=True)

        # Run the app
        NGNewTests.run_bundle(app_data=app_data, webpack=webpack, shared=shared, theme=theme,
                              emu=NGNewTests.emu, sim=NGNewTests.sim)

    @staticmethod
    def create_app(app_data, shared, sample, theme, style, prefix, source_dir, webpack):
        # Create shared project with sample data
        result = NG.new(collection=NS_SCHEMATICS, project=NGNewTests.app_name, theme=theme, shared=shared,
                        sample=sample, style=style, prefix=prefix, source_dir=source_dir, webpack=webpack)

        # Verify valid {N} app is created
        TnsAssert.created(app_name=NGNewTests.app_name, app_data=app_data, theme=theme, webpack=webpack)
        assert 'Directory is already under version control. Skipping initialization of git.' in result.output, \
            'Git init should be skipped because app is created already existing repo (the one with tests).'

        # Check sample
        if sample:
            # TODO: Implement it
            pass

        # Check theme
        if theme:
            assert App.is_dependency(app_name=NGNewTests.app_name, dependency='nativescript-theme-core')
        else:
            assert not App.is_dependency(app_name=NGNewTests.app_name, dependency='nativescript-theme-core')

        # Check styling
        if style is None or style is StylingType.CSS:
            assert 'app.css' in result.output
        else:
            assert 'app.android.scss' in result.output
            assert 'app.ios.scss' in result.output
            assert '_app-common.scss' in result.output
            assert '_app-variables.scss' in result.output

        # Check webpack
        if webpack:
            assert App.is_dev_dependency(app_name=NGNewTests.app_name, dependency='nativescript-dev-webpack')
        else:
            assert not App.is_dev_dependency(app_name=NGNewTests.app_name, dependency='nativescript-dev-webpack')

        # Check prefix
        if prefix is None:
            prefix = 'app'
        path = os.path.join(Settings.TEST_RUN_HOME, NGNewTests.app_name, 'angular.json')
        actual_prefix = JsonUtils.read(file_path=path)['projects'][NGNewTests.app_name]['prefix']
        assert str(actual_prefix) == prefix, 'Prefix not set in angular.json'

        # Check source dir exists (applicable only for shared projects).
        if shared:
            if source_dir is None:
                source_dir = 'src'
            assert Folder.exists(os.path.join(Settings.TEST_RUN_HOME, NGNewTests.app_name, source_dir))

    @staticmethod
    def run_bundle(app_data, webpack, shared, theme, emu, sim):
        # Run android (if webpack is available -> use --bundle)
        Tns.run(app_name=NGNewTests.app_name, platform=Platform.ANDROID, emulator=True, bundle=webpack)
        for text in app_data.texts:
            emu.wait_for_text(text=text, timeout=300)
            # Check if theme is really applied (only for non shared projects, shared is not good example to check)
            if not shared:
                blue_pixels = emu.get_pixels_by_color(color=Colors.LIGHT_BLUE)
                if theme:
                    assert blue_pixels > 1000, 'Default {N} theme is NOT applied on Android.'
                else:
                    assert blue_pixels == 0, 'Default {N} theme is applied, but it should not.'

        # Run ios (if webpack is available -> use --bundle)
        if Settings.HOST_OS is OSType.OSX:
            Tns.run(app_name=NGNewTests.app_name, platform=Platform.IOS, emulator=True, bundle=webpack)
            for text in app_data.texts:
                sim.wait_for_text(text=text, timeout=300)
                # Check if theme is really applied (only for non shared projects, shared is not good example to check)
                if not shared:
                    blue_pixels = emu.get_pixels_by_color(color=Colors.LIGHT_BLUE)
                    if theme:
                        assert blue_pixels > 1000, 'Default {N} theme is NOT applied on iOS.'
                    else:
                        assert blue_pixels == 0, 'Default {N} theme is applied, but it should not.'

    @staticmethod
    def build_release():
        Tns.build(app_name=NGNewTests.app_name, platform=Platform.ANDROID, release=True,
                  bundle=True, aot=True, uglify=True, snapshot=True)
        if Settings.HOST_OS is OSType.OSX:
            Tns.build(app_name=NGNewTests.app_name, platform=Platform.IOS, release=True, for_device=True,
                      bundle=True, aot=True, uglify=True)
