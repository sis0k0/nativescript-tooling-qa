import os

from core.base_test.tns_test import TnsTest
from core.enums.device_type import DeviceType
from core.settings import Settings
from core.utils.device.device_manager import DeviceManager
from core.utils.device.emulator_info import EmulatorInfo


# noinspection PyMethodMayBeStatic
class DeviceTests(TnsTest):
    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()

    def setUp(self):
        TnsTest.setUp(self)

    def tearDown(self):
        DeviceManager.Emulator.stop()
        DeviceManager.Simulator.stop()
        TnsTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    def test_01_emulator(self):
        # Verify emulator is started properly
        emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)
        assert emu.type == DeviceType.EMU, 'Device should be of type DeviceType.EMU'
        assert emu.id == Settings.Emulators.DEFAULT.emu_id, 'Emulator should be booted on specified port.'
        assert emu.name == Settings.Emulators.DEFAULT.avd, 'Device name should match avd name from settings.'
        assert emu.version == Settings.Emulators.DEFAULT.os_version, 'Device version should match os_version.'
        assert emu.type == DeviceType.EMU

        # Verify Emulator.is_running returns true if emu is running
        valid_emu = EmulatorInfo(avd=Settings.Emulators.DEFAULT.avd,
                                 os_version=Settings.Emulators.DEFAULT.os_version,
                                 emu_id=Settings.Emulators.DEFAULT.emu_id)

        # Verify Emulator.is_running() return false when port or version or name are different.
        wrong_port_emu = EmulatorInfo(avd=Settings.Emulators.DEFAULT.avd,
                                      os_version=Settings.Emulators.DEFAULT.os_version,
                                      emu_id='emulator-5555')

        wrong_version_emu = EmulatorInfo(avd=Settings.Emulators.DEFAULT.avd,
                                         os_version=Settings.Emulators.EMU_API_19.os_version,
                                         emu_id=emu.id)

        is_running = DeviceManager.Emulator.is_running(valid_emu)
        assert is_running is True, 'Emulator.is_running() should return true if emulator is running'

        # Verify Emulator.is_running returns false when id or name do not match
        is_running = DeviceManager.Emulator.is_running(wrong_port_emu)
        assert is_running is False, 'Emulator.is_running() should return false if id is different.'

        is_running = DeviceManager.Emulator.is_running(wrong_version_emu)
        assert is_running is False, 'Emulator.is_running() should return false if os_version is different.'

    def test_02_multiple_emulators(self):
        # Verify multiple emulators can be started properly
        emu1 = DeviceManager.Emulator.ensure_available(Settings.Emulators.EMU_API_23)
        emu2 = DeviceManager.Emulator.ensure_available(Settings.Emulators.EMU_API_26)
        assert emu1.id == Settings.Emulators.EMU_API_23.emu_id
        assert emu2.id == Settings.Emulators.EMU_API_26.emu_id

        # Verify screen_match() method
        image_path = os.path.join(Settings.TEST_OUT_IMAGES, 'temp.png')
        emu1.get_screen(path=image_path)
        emu1.screen_match(expected_image=image_path, tolerance=1.0, timeout=10)
        emu2.screen_match(expected_image=image_path, tolerance=1.0, timeout=10)

    def test_100_detect_available_emulators(self):
        # Verify Emulator.is_available() return correct result
        assert DeviceManager.Emulator.is_available(avd_name=Settings.Emulators.DEFAULT.avd)
        assert not DeviceManager.Emulator.is_available(avd_name='fake')
