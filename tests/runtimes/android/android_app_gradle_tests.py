"""
Test for specific needs of Android runtime.
"""
# pylint: disable=invalid-name
import os

from core.base_test.tns_test import TnsTest
from core.utils.device.device import Device
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import File, Folder
from core.utils.wait import Wait
from core.settings.Settings import Emulators, Android, TEST_RUN_HOME, AppName
from data.templates import Template
from products.nativescript.tns import Tns

APP_NAME = AppName.DEFAULT
TAP_THE_BUTTON = 'Tap the button'


class AndroidRuntimeAppGradleTests(TnsTest):

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        cls.emulator = DeviceManager.Emulator.ensure_available(Emulators.DEFAULT)
        Folder.clean(os.path.join(TEST_RUN_HOME, APP_NAME))
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Tns.platform_add_android(APP_NAME, framework_path=Android.FRAMEWORK_PATH)

    def tearDown(self):
        TnsTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()
        Folder.clean(os.path.join(TEST_RUN_HOME, APP_NAME))

    def test_301_native_package_starting_with_in_are_working(self):
        """
         Test native packages starting with in could be accessed
        """
        # Change main-page.js so it contains only logging information
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1046',
                                 'main-page.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-page.js')
        File.copy(source=source_js, target=target_js, backup_files=True)
        # Change app app.gradle so it contains the dependencies to com.github.myinnos:AwesomeImagePicker:1.0.2
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1046',
                                 'app.gradle')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'app.gradle')
        File.copy(source=source_js, target=target_js, backup_files=True)
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Project successfully built', 'Successfully installed on device with identifier', self.emulator.id]

        Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=240, period=5)

        test_result = Wait.until(lambda: "###TEST PASSED###" in File.read(log.log_file), timeout=100, period=5)
        assert test_result, 'Native packages starting with in could not be accessed'

    def test_305_native_package_with_compile_app_gradle(self):
        """
         Test that native packages could be used with with compile in app.gradle
         https://github.com/NativeScript/android-runtime/issues/993
        """

        # Change main-page.js so it contains only logging information
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993',
                                 "compile", 'main-page.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-page.js')
        File.copy(source=source_js, target=target_js, backup_files=True)
        # Change app app.gradle so it contains the dependencies to com.github.myinnos:AwesomeImagePicker:1.0.2
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993',
                                 "compile", 'app.gradle')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'app.gradle')
        File.copy(source=source_js, target=target_js, backup_files=True)
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.emulator.id,
                   'Successfully synced application', '###TEST COMPILE PASSED###']

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)

        assert test_result, 'Native packages could not be used with compile in app.gradle'

    def test_306_native_package_with_implementation_app_gradle(self):
        """
         Test that native packages could be used with implementation in app.gradle
         https://github.com/NativeScript/android-runtime/issues/993
        """

        # Change main-page.js so it contains only logging information
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993',
                                 "implementation", 'main-page.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-page.js')
        File.copy(source=source_js, target=target_js, backup_files=True)
        # Change app app.gradle so it contains the dependencies to com.github.myinnos:AwesomeImagePicker:1.0.2
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993',
                                 "implementation", 'app.gradle')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'app.gradle')
        File.copy(source=source_js, target=target_js, backup_files=True)
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.emulator.id,
                   'Successfully synced application',
                   '###TEST IMPLEMENTATION PASSED###']

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        assert test_result, 'Native packages could not be used with implementation in app.gradle'

    def test_307_native_package_with_api_app_gradle(self):
        """
         Test that native packages could be used with api in app.gradle
         https://github.com/NativeScript/android-runtime/issues/993
        """

        # Change main-page.js so it contains only logging information
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993', "api",
                                 'main-page.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-page.js')
        File.copy(source=source_js, target=target_js, backup_files=True)
        # Change app app.gradle so it contains the dependencies to com.github.myinnos:AwesomeImagePicker:1.0.2
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993', "api",
                                 'app.gradle')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'app.gradle')
        File.copy(source=source_js, target=target_js, backup_files=True)
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.emulator.id,
                   'Successfully synced application', '###TEST API PASSED###']

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        assert test_result, 'Native packages could not be used with api in app.gradle'

    def test_319_build_project_with_foursquare_android_oauth(self):
        # Add foursquare native library as dependency
        source = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-755',
                              'app.gradle')
        target = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'app.gradle')
        File.copy(source=source, target=target, backup_files=True)

        # Build the project
        output = Tns.build_android(os.path.join(TEST_RUN_HOME, APP_NAME), verify=False)
        assert ':asbg:generateBindings', 'Static Binding Generator not executed'
        assert 'cannot access its superclass' not in output.output

    def test_420_include_gradle_flavor(self):
        # https://github.com/NativeScript/android-runtime/pull/937
        # https://github.com/NativeScript/nativescript-cli/pull/3467
        source = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-pr-937',
                              'app.gradle')
        target = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'app.gradle')
        File.copy(source=source, target=target, backup_files=True)

        Tns.build_android(os.path.join(TEST_RUN_HOME, APP_NAME), verify=False)

        assert File.exists(os.path.join(TEST_RUN_HOME, APP_NAME,
                                        "platforms", "android", "app", "build", "outputs", "apk", "arm64Demo", "debug",
                                        "app-arm64-demo-debug.apk"))
        assert File.exists(os.path.join(TEST_RUN_HOME, APP_NAME,
                                        "platforms", "android", "app", "build", "outputs", "apk", "arm64Full", "debug",
                                        "app-arm64-full-debug.apk"))
        assert File.exists(os.path.join(TEST_RUN_HOME, APP_NAME,
                                        "platforms", "android", "app", "build", "outputs", "apk", "armDemo", "debug",
                                        "app-arm-demo-debug.apk"))
        assert File.exists(os.path.join(TEST_RUN_HOME, APP_NAME,
                                        "platforms", "android", "app", "build", "outputs", "apk", "armFull", "debug",
                                        "app-arm-full-debug.apk"))
        assert File.exists(os.path.join(TEST_RUN_HOME, APP_NAME,
                                        "platforms", "android", "app", "build", "outputs", "apk", "x86Demo", "debug",
                                        "app-x86-demo-debug.apk"))
        assert File.exists(os.path.join(TEST_RUN_HOME, APP_NAME,
                                        "platforms", "android", "app", "build", "outputs", "apk", "x86Full", "debug",
                                        "app-x86-full-debug.apk"))

    def test_440_verify_no_class_not_found_exception_is_thrown(self):
        """
        ClassNotFound exception when calling nested static class with correct argument
        https://github.com/NativeScript/android-runtime/issues/1195
        """
        source_app_gradle = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1195',
                                         'app.gradle')
        target_app_gradle = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'app.gradle')
        File.copy(source=source_app_gradle, target=target_app_gradle, backup_files=True)

        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1195',
                                 'app.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'app.js')
        File.copy(source=source_js, target=target_js, backup_files=True)

        # `tns run android` and wait until app is deployed
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.emulator.id,
                   'Successfully synced application']
        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        assert test_result, 'Application not build correctly!'

        # Verify app looks correct inside emulator
        Device.wait_for_text(self.emulator, text=TAP_THE_BUTTON)

    def test_450_support_external_buildscript_config_in_app_res_android_folder(self):
        """
        Support external buildscript configurations - buildscript.gradle file placed in `App_Resources/Android` folder
        https://github.com/NativeScript/android-runtime/issues/1279
        """

        source_app_gradle = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1279',
                                         'app.gradle')
        target_app_gradle = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'app.gradle')
        File.copy(source=source_app_gradle, target=target_app_gradle, backup_files=True)

        source_build_script_gradle = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                                                  'android-runtime-1279', 'buildscript.gradle')

        target_build_script_gradle = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android')
        File.copy(source=source_build_script_gradle, target=target_build_script_gradle, backup_files=True)

        Tns.build_android(os.path.join(TEST_RUN_HOME, APP_NAME), verify=True)

    def test_452_assert_static_binding_generator_is_generating_correct_code(self):
        """
        Test static binding generator is generationg correct code
        https://github.com/NativeScript/android-runtime/issues/689
        """
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-689',
                                 'app.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'app.js')
        File.copy(source=source_js, target=target_js, backup_files=True)
        source_app_gradle = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-689',
                                         'app.gradle')
        target_app_gradle = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'app.gradle')
        File.copy(source=source_app_gradle, target=target_app_gradle, backup_files=True)

        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-689',
                                 'main-view-model.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-view-model.js')
        File.copy(source=source_js, target=target_js, backup_files=True)

        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Successfully synced application', 'on device', self.emulator.id,
                   'Test Pass!']
        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=320,
                                 period=5)
        assert test_result, 'Static binding generator did not generated code! Logs: ' + File.read(log.log_file)
