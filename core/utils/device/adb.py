import logging
import os
import time

from core.enums.os_type import OSType
from core.log.log import Log
from core.settings import Settings
from core.utils.file_utils import File
from core.utils.process import Process
from core.utils.run import run
import re

ANDROID_HOME = os.environ.get('ANDROID_HOME')
ADB_PATH = os.path.join(ANDROID_HOME, 'platform-tools', 'adb')


class Adb(object):
    @staticmethod
    def run_adb_command(command, device_id=None, wait=True, timeout=60, fail_safe=False, log_level=logging.DEBUG):
        if device_id is None:
            command = '{0} {1}'.format(ADB_PATH, command)
        else:
            command = '{0} -s {1} {2}'.format(ADB_PATH, device_id, command)
        return run(cmd=command, wait=wait, timeout=timeout, fail_safe=fail_safe, log_level=log_level)

    @staticmethod
    def __get_ids(include_emulator=False):
        """
        Get IDs of available android devices.
        """
        devices = []
        output = Adb.run_adb_command('devices -l').output
        # Example output:
        # emulator-5554          device product:sdk_x86 model:Android_SDK_built_for_x86 device:generic_x86
        # HT46BWM02644           device usb:336592896X product:m8_google model:HTC_One_M8 device:htc_m8
        for line in output.splitlines():
            if 'model' in line and ' device ' in line:
                device_id = line.split(' ')[0]
                if include_emulator:
                    devices.append(device_id)
        return devices

    @staticmethod
    def get_logcat(device_id):
        """
        Dump the log and then exit (don't block).
        :param device_id: Device id.
        """
        return Adb.__run_adb_command(command='logcat -d', device_id=device_id, wait=True).output

    @staticmethod
    def clear_logcat(device_id):
        """
        Clear (flush) the entire log.
        :param device_id: Device id.
        """
        Adb.__run_adb_command(command='logcat -c', device_id=device_id, wait=True)
        Log.info("The logcat on {0} is cleared.".format(device_id))

    @staticmethod
    def restart():
        Log.info("Restart adb.")
        Adb.run_adb_command('kill-server')
        Process.kill(proc_name='adb')
        Adb.run_adb_command('start-server')

    @staticmethod
    def get_devices(include_emulators=False):
        # pylint: disable=unused-argument
        # TODO: Implement it!
        return []

    @staticmethod
    def is_running(device_id):
        """
        Check if device is is currently running.
        :param device_id: Device id.
        :return: True if running, False if not running.
        """
        if Settings.HOST_OS is OSType.WINDOWS:
            command = "shell dumpsys window windows | findstr mCurrentFocus"
        else:
            command = "shell dumpsys window windows | grep -E 'mCurrentFocus'"
        result = Adb.run_adb_command(command=command, device_id=device_id, timeout=10, fail_safe=True)
        return bool('Window' in result.output)

    @staticmethod
    def wait_until_boot(device_id, timeout=180, check_interval=3):
        """
        Wait android device/emulator is up and running.
        :param device_id: Device identifier.
        :param timeout: Timeout until device is ready (in seconds).
        :param check_interval: Sleep specified time before check again.
        :return: True if device is ready before timeout, otherwise - False.
        """
        booted = False
        start_time = time.time()
        end_time = start_time + timeout
        while not booted:
            time.sleep(check_interval)
            booted = Adb.is_running(device_id=device_id)
            if (booted is True) or (time.time() > end_time):
                break
        return booted

    @staticmethod
    def reboot(device_id):
        Adb.run_adb_command(command='reboot', device_id=device_id)
        Adb.wait_until_boot(device_id=device_id)

    @staticmethod
    def prevent_screen_lock(device_id):
        """
        Disable screen lock after time of inactivity.
        :param device_id: Device identifier.
        """
        Adb.run_adb_command(command='shell settings put system screen_off_timeout -1', device_id=device_id)

    @staticmethod
    def pull(device_id, source, target):
        return Adb.run_adb_command(command='pull {0} {1}'.format(source, target), device_id=device_id)

    @staticmethod
    def get_page_source(device_id):
        temp_file = os.path.join(Settings.TEST_OUT_HOME, 'window_dump.xml')
        File.delete(temp_file)
        Adb.run_adb_command(command='shell rm /sdcard/window_dump.xml', device_id=device_id)
        result = Adb.run_adb_command(command='shell uiautomator dump', device_id=device_id)
        if 'UI hierchary dumped to' in result.output:
            time.sleep(1)
            Adb.pull(device_id=device_id, source='/sdcard/window_dump.xml', target=temp_file)
            if File.exists(temp_file):
                result = File.read(temp_file)
                File.delete(temp_file)
                return result
            else:
                return ''
        else:
            # Sometimes adb shell uiatomator dump fails, for example with:
            # adb: error: remote object '/sdcard/window_dump.xml' does not exist
            # In such cases return empty string.
            return ''

    @staticmethod
    def is_text_visible(device_id, text, case_sensitive=False):
        element = Adb.get_element_by_text(device_id, text, case_sensitive)
        return element is not None

    @staticmethod
    def get_element_coordinates(element):
        bounds = element.attrib['bounds']
        bound_groups = re.findall(r"(\d+,\d+)", bounds)
        x = 0
        y = 0
        counter = 0
        for bound_group in bound_groups:
            arr_x_y = bound_group.split(",")
            x = x + int(arr_x_y[0])
            y = y + int(arr_x_y[1])
            counter = counter + 1
        return x/counter, y/counter

    @staticmethod
    def click_element_by_text(device_id, text, case_sensitive=False):
        element = Adb.get_element_by_text(device_id, text, case_sensitive)
        if element is not None:
            coordinates = Adb.get_element_coordinates(element)
            Adb.__run_adb_command(command="shell input tap " + str(coordinates[0]) + " " + str(coordinates[1]))
        else:
            assert False, 'Element with text ' + text + ' not found!'

    # noinspection PyPep8Naming
    @staticmethod
    def get_element_by_text(device_id, text, case_sensitive=False):
        import xml.etree.ElementTree as ET
        page_source = Adb.get_page_source(device_id)
        if page_source != '':
            xml = ET.ElementTree(ET.fromstring(page_source))
            elements = xml.findall(".//node[@text]")
            if elements:
                for element in elements:
                    if case_sensitive:
                        if text in element.attrib['text']:
                            return element
                    else:
                        if text.lower() in element.attrib['text'].lower():
                            return element
        return None

    @staticmethod
    def get_screen(device_id, file_path):
        File.delete(path=file_path)
        if Settings.HOST_OS == OSType.WINDOWS:
            Adb.run_adb_command(command='exec-out screencap -p > ' + file_path,
                                device_id=device_id,
                                log_level=logging.DEBUG)
        else:
            Adb.run_adb_command(command="shell screencap -p | perl -pe 's/\\x0D\\x0A/\\x0A/g' > " + file_path,
                                device_id=device_id)
        if File.exists(file_path):
            return
        else:
            raise Exception('Failed to get screen of {0}.'.format(device_id))

    @staticmethod
    def get_device_version(device_id):
        result = Adb.run_adb_command(command='shell getprop ro.build.version.release', device_id=device_id)
        if result.exit_code == 0:
            return result.output
        else:
            raise Exception('Failed to get version of {0}.'.format(device_id))

    @staticmethod
    def open_home(device_id):
        cmd = 'shell am start -a android.intent.action.MAIN -c android.intent.category.HOME'
        Adb.run_adb_command(command=cmd, device_id=device_id)
        Log.info('Open home screen of {0}.'.format(str(device_id)))

    @staticmethod
    def install(apk_path, device_id):
        """
        Install application.
        :param apk_path: File path to .apk.
        :param device_id: Device id.
        """
        result = Adb.run_adb_command(command='-s {0} install -r {1}'.format(device_id, apk_path), timeout=60)
        assert 'Success' in result.output, 'Failed to install {0}. Output: {1}'.format(apk_path, result.output)
        Log.info('{0} installed successfully on {1}.'.format(apk_path, device_id))

    @staticmethod
    def __list_path(device_id, package_id, path):
        """
        List file of application.
        :param device_id: Device identifier.
        :param package_id: Package identifier.
        :param path: Path relative to root folder of the package.
        :return: List of files and folders
        """
        command = 'shell run-as {0} ls -la /data/data/{1}/files/{2}'.format(package_id, package_id, path)
        output = Adb.__run_adb_command(command=command, device_id=device_id, log_level=logging.DEBUG, wait=True).output
        return output

    @staticmethod
    def file_exists(device_id, package_id, file_name, timeout=20):
        """file_exists
        Wait until path exists (relative based on folder where package is deployed) on emulator/android device.
        :param device_id: Device identifier.
        :param package_id: Package identifier.
        :param file_name: File you want to check if exists.
        :param timeout: Timeout in seconds.
        :return: True if path exists, false if path does not exists
        """
        t_end = time.time() + timeout
        found = False
        while time.time() < t_end:
            files = Adb.__list_path(device_id=device_id, package_id=package_id, path=file_name)
            if 'No such file or directory' not in files:
                found = True
                break
        return found
