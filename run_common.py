import os

from core.enums.os_type import OSType
from core.log.log import Log
from core.settings import Settings
from core.utils.device.adb import Adb
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import File, Folder
from core.utils.git import Git
from core.utils.gradle import Gradle
from core.utils.npm import Npm
from data.templates import Template
from products.nativescript.preview_helpers import Preview
from products.nativescript.tns import Tns


def __cleanup():
    """
    Wipe TEST_OUT_HOME.
    """
    Folder.clean(os.path.join(Settings.TEST_RUN_HOME, 'node_modules'))
    Folder.clean(Settings.TEST_OUT_HOME)
    Folder.create(Settings.TEST_OUT_LOGS)
    Folder.create(Settings.TEST_OUT_IMAGES)
    Folder.create(Settings.TEST_OUT_TEMP)

    DeviceManager.Emulator.stop()
    if Settings.HOST_OS == OSType.OSX:
        DeviceManager.Simulator.stop()

    Adb.restart()
    Tns.kill()
    Gradle.kill()
    Gradle.cache_clean()


def __get_templates(branch=Settings.Packages.TEMPLATES_BRANCH):
    """
    Clone hello-world templates and pack them as local npm packages.
    :param branch: Branch of https://github.com/NativeScript/nativescript-app-templates
    """
    local_folder = os.path.join(Settings.TEST_SUT_HOME, 'templates')
    Git.clone(repo_url=Template.REPO, branch=branch, local_folder=local_folder)

    apps = [Template.HELLO_WORLD_JS, Template.HELLO_WORLD_TS, Template.HELLO_WORLD_NG, Template.MASTER_DETAIL_NG,
            Template.VUE_BLANK, Template.MASTER_DETAIL_VUE, Template.TAB_NAVIGATION_JS]
    for app in apps:
        template_name = app.name
        template_folder = os.path.join(local_folder, 'packages', template_name)
        out_file = os.path.join(Settings.TEST_SUT_HOME, template_name + '.tgz')
        Npm.pack(folder=template_folder, output_file=out_file)
        if File.exists(out_file):
            app.path = out_file
        else:
            raise IOError("Failed to clone and pack template: " + template_name)


def __get_runtimes():
    """
    Get {N} Runtimes in TEST_SUT_HOME.
    """

    # Copy or download tns-android
    android_package = os.path.join(Settings.TEST_SUT_HOME, 'tns-android.tgz')
    if '.tgz' in Settings.Packages.ANDROID:
        File.copy(source=Settings.Packages.ANDROID, target=android_package)
        Settings.Packages.ANDROID = android_package
    else:
        Npm.download(package=Settings.Packages.ANDROID, output_file=android_package)

    # Copy or download tns-ios
    if Settings.HOST_OS == OSType.OSX:
        ios_package = os.path.join(Settings.TEST_SUT_HOME, 'tns-ios.tgz')
        if '.tgz' in Settings.Packages.IOS:
            File.copy(source=Settings.Packages.IOS, target=ios_package)
            Settings.Packages.IOS = ios_package
        else:
            Npm.download(package=Settings.Packages.IOS, output_file=ios_package)


def __install_ns_cli():
    """
    Install NativeScript CLI locally.
    """

    # Copy NativeScript CLI (if used from local package)
    if '.tgz' in Settings.Packages.NS_CLI:
        cli_package = os.path.join(Settings.TEST_SUT_HOME, 'nativescript.tgz')
        File.copy(source=Settings.Packages.NS_CLI, target=cli_package)
        Settings.Packages.NS_CLI = cli_package

    # Install NativeScript CLI
    output = Npm.install(package=Settings.Packages.NS_CLI, folder=Settings.TEST_RUN_HOME)

    # Verify executable exists after install
    path = os.path.join(Settings.TEST_RUN_HOME, 'node_modules', '.bin', 'tns')
    assert File.exists(path), 'NativeScript executable not found at ' + path
    Settings.Executables.TNS = path

    # Verify installation output
    # noinspection SpellCheckingInspection
    assert 'postinstall.js' in output, 'Post install scripts not executed.'
    assert 'dev-post-install' not in output, 'Dev post install executed on installation.'


def __install_ng_cli():
    """
    Install Angular CLI globally.
    """
    Npm.uninstall(package='@angular/cli', option='-g')
    Npm.install(package=Settings.Packages.NG_CLI, option='-g')


def __install_schematics():
    """
    Install NativeScript Schematics globally.
    """
    Npm.uninstall(package='@nativescript/schematics', option='-g')
    Npm.install(package=Settings.Packages.NS_SCHEMATICS, option='-g')


def prepare(clone_templates=True, install_ng_cli=False, get_preivew_packages=False):
    Log.info('================== Prepare Test Run ==================')
    __cleanup()
    __install_ns_cli()
    __get_runtimes()
    if install_ng_cli:
        __install_ng_cli()
        __install_schematics()
    if clone_templates:
        __get_templates()
    if get_preivew_packages:
        Preview.get_app_packages()

    Log.settings()
