import os
import unittest

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.adb import Adb
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import Folder
from data.sync_helpers import SyncHelpers
from data.templates import Template
from products.nativescript.tns import Tns


class TnsRunMasterDetailTests(TnsTest):
    app_name = Settings.AppName.DEFAULT
    source_project_dir = os.path.join(Settings.TEST_RUN_HOME, app_name)
    target_project_dir = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', app_name)
    emu = None
    sim = None

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()

        # Boot emulator and simulator
        cls.emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)
        if Settings.HOST_OS == OSType.OSX:
            cls.sim = DeviceManager.Simulator.ensure_available(Settings.Simulators.DEFAULT)

        # Create app
        Tns.create(app_name=cls.app_name, template=Template.MASTER_DETAIL_NG.repo, update=True)
        Tns.platform_add_android(app_name=cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS is OSType.OSX:
            Tns.platform_add_ios(app_name=cls.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)

        # Copy TestApp to data folder.
        Folder.copy(source=cls.source_project_dir, target=cls.target_project_dir)

    def setUp(self):
        TnsTest.setUp(self)
        Adb.open_home(self.emu.id)

        # "src" folder of TestApp will be restored before each test.
        # This will ensure failures in one test do not cause common failures.
        source_src = os.path.join(self.target_project_dir, 'src')
        target_src = os.path.join(self.source_project_dir, 'src')
        Folder.clean(target_src)
        Folder.copy(source=source_src, target=target_src)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()


class RunAndroidMasterDetailNGTests(TnsRunMasterDetailTests):
    def test_100_run_android(self):
        SyncHelpers.sync_master_detail_ng(self.app_name, Platform.ANDROID, self.emu)

    def test_200_run_android_bundle(self):
        SyncHelpers.sync_master_detail_ng(self.app_name, Platform.ANDROID, self.emu, bundle=True)

    def test_300_run_android_bundle_aot(self):
        SyncHelpers.sync_master_detail_ng(self.app_name, Platform.ANDROID, self.emu, bundle=True, aot=True)

    @unittest.skip('Ignore because of https://github.com/NativeScript/nativescript-angular/issues/1572')
    def test_310_run_android_bundle_uglify(self):
        SyncHelpers.sync_master_detail_ng(self.app_name, Platform.ANDROID, self.emu, bundle=True, uglify=True)

    def test_320_run_android_bundle_aot_and_uglify(self):
        SyncHelpers.sync_master_detail_ng(self.app_name, Platform.ANDROID, self.emu, bundle=True, aot=True, uglify=True)


@unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
class RunIOSMasterDetailNGTests(TnsRunMasterDetailTests):
    def test_100_run_ios(self):
        SyncHelpers.sync_master_detail_ng(self.app_name, Platform.IOS, self.sim)

    def test_200_run_ios_bundle(self):
        SyncHelpers.sync_master_detail_ng(self.app_name, Platform.IOS, self.sim, bundle=True)

    def test_300_run_ios_bundle_aot(self):
        SyncHelpers.sync_master_detail_ng(self.app_name, Platform.IOS, self.sim, bundle=True, aot=True)

    @unittest.skip('Ignore because of https://github.com/NativeScript/nativescript-angular/issues/1572')
    def test_310_run_ios_bundle_uglify(self):
        SyncHelpers.sync_master_detail_ng(self.app_name, Platform.IOS, self.sim, bundle=True, uglify=True)

    def test_320_run_ios_bundle_aot_and_uglify(self):
        SyncHelpers.sync_master_detail_ng(self.app_name, Platform.IOS, self.sim, bundle=True, aot=True, uglify=True)