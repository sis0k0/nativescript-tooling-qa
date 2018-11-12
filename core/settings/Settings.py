import logging
import os
import platform

from core.enums.os_type import OSType
from core.utils.device.emulator_info import EmulatorInfo
from core.utils.device.simulator_info import SimulatorInfo


def get_os():
    if 'Windows' in platform.platform():
        return OSType.WINDOWS
    elif 'Darwin' in platform.platform():
        return OSType.OSX
    else:
        return OSType.LINUX


def get_project_home():
    home = os.getcwd()
    while not os.path.exists(os.path.join(home, 'requirements.txt')):
        home = os.path.split(home)[0]
    return home


LOG_LEVEL = logging.DEBUG

NS_GIT_ORG = 'NativeScript'

HOST_OS = get_os()

TEST_RUN_HOME = get_project_home()
TEST_SUT_HOME = os.path.join(TEST_RUN_HOME, 'sut')
TEST_OUT_HOME = os.path.join(TEST_RUN_HOME, 'out')
TEST_OUT_LOGS = os.path.join(TEST_OUT_HOME, 'logs')
TEST_OUT_IMAGES = os.path.join(TEST_OUT_HOME, 'images')

SSH_CLONE = os.environ.get('SSH_CLONE', False)


def resolve_package(name, variable, default='next'):
    tag = os.environ.get(variable, default)
    if '.tgz' not in tag:
        return name + '@' + tag
    else:
        return tag


class Executables(object):
    ns_path = os.path.join(TEST_RUN_HOME, 'node_modules', '.bin', 'tns')
    ng_path = os.path.join(TEST_RUN_HOME, 'node_modules', '.bin', 'ng')
    TNS = ns_path if os.path.isfile(ns_path) else 'tns'
    NG = ng_path if os.path.isfile(ng_path) else 'ng'


# noinspection SpellCheckingInspection
class Packages(object):
    NS_CLI = resolve_package(name='nativescript', variable="CLI_PATH")
    NS_SCHEMATICS = resolve_package(name='@nativescript/schematics', variable="NATIVESCRIPT_SCHEMATICS")
    NG_CLI = resolve_package(name='@angular/cli', variable="NG_CLI_PATH", default="latest")
    ANDROID = resolve_package(name='tns-android', variable='ANDROID_PATH')
    IOS = resolve_package(name='tns-ios', variable='IOS_PATH')
    MODULES = resolve_package(name='tns-core-modules', variable='MODULES_PATH')
    ANGULAR = resolve_package(name='nativescript-angular', variable='ANGULAR')
    WEBPACK = resolve_package(name='nativescript-dev-webpack', variable='WEBPACK')
    TYPESCRIPT = resolve_package(name='nativescript-dev-typescript', variable='TYPESCRIPT')
    SASS = resolve_package(name='nativescript-dev-sass', variable='SASS')


# noinspection SpellCheckingInspection
class Android(object):
    # Local runtime package
    FRAMEWORK_PATH = os.path.join(TEST_SUT_HOME, 'tns-android.tgz')

    # Signing options
    ANDROID_KEYSTORE_PATH = os.environ.get('ANDROID_KEYSTORE_PATH')
    ANDROID_KEYSTORE_PASS = os.environ.get('ANDROID_KEYSTORE_PASS')
    ANDROID_KEYSTORE_ALIAS = os.environ.get('ANDROID_KEYSTORE_ALIAS')
    ANDROID_KEYSTORE_ALIAS_PASS = os.environ.get('ANDROID_KEYSTORE_ALIAS_PASS')


class IOS(object):
    # Local runtime package
    FRAMEWORK_PATH = os.path.join(TEST_SUT_HOME, 'tns-ios.tgz')

    # Signing options
    DEVELOPMENT_TEAM = os.environ.get('DEVELOPMENT_TEAM')
    DEV_PROVISION = os.environ.get('DEV_PROVISION')
    DISTRIBUTION_PROVISION = os.environ.get('DISTRIBUTION_PROVISION')


class Emulators(object):
    EMU_API_19 = EmulatorInfo(avd=os.environ.get('EMU_API_19', 'Emulator-Api19-Default'), os_version=4.4, port='5560',
                              id='emulator-5560')
    EMU_API_23 = EmulatorInfo(avd=os.environ.get('EMU_API_23', 'Emulator-Api23-Default'), os_version=6.0, port='5562',
                              id='emulator-5562')
    EMU_API_26 = EmulatorInfo(avd=os.environ.get('EMU_API_26', 'Emulator-Api26-Google'), os_version=8.0, port='5564',
                              id='emulator-5564')
    EMU_API_28 = EmulatorInfo(avd=os.environ.get('EMU_API_28', 'Emulator-Api28-Google'), os_version=9.0, port='5566',
                              id='emulator-5566')
    DEFAULT = EMU_API_23


class Simulators(object):
    SIM_IOS10 = SimulatorInfo(name=os.environ.get('SIM_IOS10', 'iPhone7_10'), device_type='iPhone 7', sdk=10.0, id='')
    SIM_IOS11 = SimulatorInfo(name=os.environ.get('SIM_IOS11', 'iPhone7_11'), device_type='iPhone 7', sdk=11.2, id='')
    SIM_IOS12 = SimulatorInfo(name=os.environ.get('SIM_IOS12', 'iPhoneXR_12'), device_type='iPhone XR', sdk=12.0, id='')
    DEFAULT = SIM_IOS11


class AppName(object):
    DEFAULT = 'TestApp'
    DEFAULT_NG = 'TestApp'
    WITH_DASH = 'tns-app'
    WITH_SPACE = 'Test App'
