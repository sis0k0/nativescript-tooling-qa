# pylint: disable=too-many-boolean-expressions
# pylint: disable=too-many-branches
import logging
import os
from time import sleep

from core.base_test.test_context import TestContext
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.log.log import Log
from core.settings import Settings
from core.utils.file_utils import Folder, File
from core.utils.npm import Npm
from core.utils.process import Process
from core.utils.run import run
from core.utils.json_utils import JsonUtils
from products.nativescript.app import App
from products.nativescript.tns_assert import TnsAssert
from products.nativescript.tns_logs import TnsLogs
from products.nativescript.tns_paths import TnsPaths


class Tns(object):
    @staticmethod
    def exec_command(command, cwd=Settings.TEST_RUN_HOME, platform=Platform.NONE, emulator=False, path=None,
                     device=None, release=False, for_device=False, provision=None, bundle=True,
                     hmr=True, aot=False, uglify=False, source_map=False, snapshot=False, log_trace=False,
                     just_launch=False, sync_all_files=False, clean=False,
                     options=None, wait=True, timeout=600):
        """
        Execute tns command.
        :param command: Tns command.
        :param cwd: Working directory.
        :param platform: Pass `platform <value>` to command.
        :param emulator: If true pass `--emulator` flag.
        :param path: Pass `--path <value>` to command.
        :param device: Pass `--device <value>` to command.
        :param release: If true pass `--release <all signing options>` to command.
        :param for_device: If true pass `--for-device` to command.
        :param provision: Pass `--provision <value>` to command.
        :param bundle: If true pass `--bundle` to command.
        :param hmr: If true pass `--hmr` to command.
        :param aot: If true pass `--env.aot` to command.
        :param uglify: If true pass `--env.uglify` to command.
        :param source_map: If true pass `--env.sourceMap` to command.
        :param snapshot: If true pass `--env.snapshot` to command.
        :param log_trace: If not None pass `--log <level>` to command.
        :param just_launch: If true pass `--justlaunch` to command.
        :param sync_all_files:  If true pass `--syncAllFiles` to command.
        :param clean:  If true pass `--clean` to command.
        :param options: Pass additional options as string.
        :param wait: If true it will wait until command is complete.
        :param timeout: Timeout for CLI command (respected only if wait=True).
        :return: ProcessInfo object.
        :rtype: core.utils.process_info.ProcessInfo
        """
        cmd = '{0} {1}'.format(Settings.Executables.TNS, command)
        if platform is not None:
            cmd = cmd + ' ' + str(platform)
        if path is not None:
            cmd = cmd + ' --path ' + path
        if emulator:
            cmd += ' --emulator'
        if device is not None:
            cmd = cmd + ' --device ' + device
        if release:
            cmd += ' --release'
            if platform is Platform.ANDROID:
                cmd += ' --key-store-path {0} --key-store-password {1} --key-store-alias {2} ' \
                       '--key-store-alias-password {3}'.format(Settings.Android.ANDROID_KEYSTORE_PATH,
                                                               Settings.Android.ANDROID_KEYSTORE_PASS,
                                                               Settings.Android.ANDROID_KEYSTORE_ALIAS,
                                                               Settings.Android.ANDROID_KEYSTORE_ALIAS_PASS)
        if provision is not None and platform != Platform.ANDROID and Settings.HOST_OS == OSType.OSX and not emulator:
            cmd = cmd + ' --provision ' + provision
        if for_device:
            cmd += ' --for-device'
        if not bundle:
            cmd += ' --no-bundle'
        if not hmr:
            cmd += ' --no-hmr'
        if aot:
            cmd += ' --env.aot'
        if uglify:
            cmd += ' --env.uglify'
        if snapshot:
            cmd += ' --env.snapshot'
        if source_map:
            cmd += ' --env.sourceMap'
        if just_launch:
            cmd += ' --justlaunch'
        if clean:
            cmd += ' --clean'
        if sync_all_files:
            cmd += ' --syncAllFiles'
        if log_trace:
            cmd += ' --log trace'
        if options:
            cmd += ' ' + options

        result = run(cmd=cmd, cwd=cwd, wait=wait, log_level=logging.INFO, timeout=timeout)

        # Retry in case of connectivity issues
        if result.output is not None and 'Bad Gateway' in result.output:
            Log.info('"Bad Gateway" issue detected! Will retry the command ...')
            result = run(cmd=cmd, cwd=cwd, wait=wait, log_level=logging.INFO, timeout=timeout)

        return result

    @staticmethod
    def create(app_name=Settings.AppName.DEFAULT, template=None, path=None, app_id=None,
               force=False,
               default=False,
               update=True,
               force_clean=True,
               log_trace=False,
               verify=True,
               app_data=None):
        """
        Create {N} application.
        :param app_name: Application name (TestApp by default).
        :param template: Template string (it can be everything that can be npm installed - npm package, git url ...)
        :param path: Path where app to be created (Passes `--path <value>` to tns command. None by default).
        :param app_id: Application identifier.
        :param force: If true passes '--force' to tns command.
        :param default: If true passes '--default' to tns command.
        :param update: If True update the app (modules and plugins).
        :param force_clean: If True clean app folder before creating a project.
        :param log_trace: If True runs tns command with '--log trace'.
        :param verify: If True assert app is created properly.
        :param app_data: AppInfo object with expected data (used to verify app is created properly).
        """

        # Cleanup app folder
        if force_clean:
            Folder.clean(TnsPaths.get_app_path(app_name=app_name))

        # Create app
        normalized_app_name = app_name
        if ' ' in app_name:
            normalized_app_name = '"' + app_name + '"'
        command = 'create ' + normalized_app_name
        if template is not None:
            command = command + ' --template ' + template
        if path is not None:
            command = command + ' --path ' + path
        if app_id is not None:
            # noinspection SpellCheckingInspection
            command = command + ' --appid ' + app_id
        if force:
            command += ' --force'
        if default:
            command += ' --default'
        result = Tns.exec_command(command, log_trace=log_trace)

        # Update the app (if specified)
        if update:
            App.update(app_name=app_name)

        # Let TestContext know app is created
        TestContext.TEST_APP_NAME = app_name

        # Verify app is created properly
        if verify is not False:
            # Usually we do not pass path on tns create, which actually equals to cwd.
            # In such cases pass correct path to TnsAssert.created()
            if path is None:
                path = Settings.TEST_RUN_HOME
            TnsAssert.created(app_name=app_name, output=result.output, app_data=app_data, path=path)

        return result

    @staticmethod
    def platform_remove(app_name=Settings.AppName.DEFAULT, platform=Platform.NONE, verify=True,
                        log_trace=False):
        command = 'platform remove ' + str(platform) + ' --path ' + app_name
        result = Tns.exec_command(command=command, log_trace=log_trace)
        if verify:
            TnsAssert.platform_removed(app_name=app_name, platform=platform, output=result.output)
        return result

    @staticmethod
    def platform_add(app_name=Settings.AppName.DEFAULT, platform=Platform.NONE, framework_path=None, version=None,
                     verify=True, log_trace=False):
        platform_add_string = str(platform)
        if version is not None:
            platform_add_string = platform_add_string + '@' + version
        command = 'platform add ' + platform_add_string + ' --path ' + app_name
        if framework_path is not None:
            command = command + ' --frameworkPath ' + framework_path
        result = Tns.exec_command(command=command, log_trace=log_trace)
        if verify:
            TnsAssert.platform_added(app_name=app_name, platform=platform, output=result.output, version=version)
        return result

    @staticmethod
    def platform_add_android(app_name=Settings.AppName.DEFAULT, framework_path=None, version=None, verify=True,
                             log_trace=False):
        return Tns.platform_add(app_name=app_name, platform=Platform.ANDROID, framework_path=framework_path,
                                version=version, verify=verify, log_trace=log_trace)

    @staticmethod
    def platform_add_ios(app_name=Settings.AppName.DEFAULT, framework_path=None, version=None, verify=True,
                         log_trace=False):
        return Tns.platform_add(app_name=app_name, platform=Platform.IOS, framework_path=framework_path,
                                version=version, verify=verify, log_trace=log_trace)

    @staticmethod
    def platform_update(app_name=Settings.AppName.DEFAULT, platform=Platform.NONE, version=None):
        platform_add_string = str(platform)
        if version is not None:
            platform_add_string = platform_add_string + '@' + version
        command = 'platform update ' + platform_add_string
        result = Tns.exec_command(command=command, path=app_name)
        TnsAssert.platform_added(app_name=app_name, platform=platform, version=version, output=result.output)
        if version is not None:
            assert 'Successfully updated to version  {0}'.format(version) in result.output
        else:
            assert 'Successfully updated to version' in result.output

    @staticmethod
    def platform_clean(app_name, platform=Platform.NONE, verify=True):
        platform_string = str(platform)
        command = 'platform clean ' + platform_string
        result = Tns.exec_command(command=command, path=app_name)
        if verify:
            assert "Platform {0} successfully removed".format(platform_string) in result.output
            assert "error" not in result.output
            if platform is Platform.ANDROID:
                assert Folder.exists(TnsPaths.get_platforms_android_folder(app_name))
            if platform is Platform.IOS:
                assert Folder.exists(TnsPaths.get_platforms_ios_folder(app_name))
            assert "Platform {0} successfully added".format(platform_string) in result.output
            package_json = os.path.join(TnsPaths.get_app_path(app_name), 'package.json')
            json = JsonUtils.read(package_json)
            assert json['nativescript']['tns-' + platform_string]['version'] is not None

    @staticmethod
    def platform_list(app_name):
        return Tns.exec_command(command="platform list", path=app_name)

    @staticmethod
    def plugin_add(plugin_name, path=None, log_trace=False, verify=True):
        result = Tns.exec_command(command="plugin add " + plugin_name, path=path, log_trace=log_trace)
        if verify:
            # Verify output
            if "/src" in plugin_name:
                short_name = plugin_name.rsplit('@', 1)[0].replace("/src", "").split(os.sep)[-1]
            else:
                short_name = plugin_name.rsplit('@', 1)[0].replace(".tgz", "").split(os.sep)[-1]
            assert "Successfully installed plugin {0}".format(short_name) in result.output

            # Verify package.json
            App.is_dependency(app_name=path, dependency=short_name)
        return result

    @staticmethod
    def plugin_remove(plugin_name, path=None, log_trace=False, verify=True):
        result = Tns.exec_command(command="plugin remove " + plugin_name, path=path, log_trace=log_trace)
        if verify:
            assert "Successfully removed plugin {0}".format(plugin_name.replace("@", "")) in result.output
        return result

    @staticmethod
    def plugin_create(plugin_name, path=None, type_script=None, angular=None, log_trace=False, verify=True,
                      template=None):
        command = "plugin create " + plugin_name

        if template is not None:
            command = command + ' --template ' + template
        if type_script is not None:
            command = command + ' --includeTypeScriptDemo=y '
        if angular is not None:
            command = command + ' --includeAngularDemo=y '

        result = Tns.exec_command(command=command, path=path, log_trace=log_trace)

        if verify:
            # Verify command output
            assert "Will now rename some files" in result.output, "Post clone script not executed."
            assert "Screenshots removed" in result.output, "Post clone script not executed."
            assert "Solution for {0}".format(plugin_name) + " was successfully created" in result.output, \
                'Missing message in output.'
            assert "https://docs.nativescript.org/plugins/building-plugins" in result.output, 'Link to docs is missing.'

            # Verify created files and folders
            plugin_root = os.path.join(Settings.TEST_RUN_HOME, plugin_name)
            readme = os.path.join(plugin_root, "README.md")
            src = os.path.join(plugin_root, "src")
            demo = os.path.join(plugin_root, "demo")
            post_clone_script = os.path.join(src, "scripts", "postclone.js")
            assert File.exists(readme), 'README.md do not exists.'
            assert not Folder.is_empty(src), 'src folder should exists and should not be empty.'
            assert not Folder.is_empty(demo), 'demo folder should exists and should not be empty.'
            assert not File.exists(post_clone_script), 'Post clone script should not exists in plugin src folder.'
        return result.output

    @staticmethod
    def prepare(app_name, platform, release=False, provision=Settings.IOS.PROVISIONING, for_device=False, bundle=True,
                log_trace=False, verify=True):
        result = Tns.exec_command(command='prepare', path=app_name, platform=platform, release=release,
                                  provision=provision, for_device=for_device, bundle=bundle, wait=True,
                                  log_trace=log_trace)
        if verify:
            assert result.exit_code == 0, 'Prepare failed with non zero exit code.'
        return result

    @staticmethod
    def prepare_android(app_name, release=False, log_trace=False, verify=True, bundle=True):
        return Tns.prepare(app_name=app_name, platform=Platform.ANDROID, release=release, log_trace=log_trace,
                           verify=verify, bundle=bundle)

    @staticmethod
    def prepare_ios(app_name, release=False, for_device=False, log_trace=False, verify=True,
                    provision=Settings.IOS.PROVISIONING, bundle=True):
        return Tns.prepare(app_name=app_name, platform=Platform.IOS, release=release, provision=provision,
                           for_device=for_device, log_trace=log_trace, verify=verify, bundle=bundle)

    @staticmethod
    def build(app_name, platform, release=False, provision=Settings.IOS.PROVISIONING, for_device=False, bundle=True,
              aot=False, uglify=False, snapshot=False, log_trace=False, verify=True, app_data=None):
        result = Tns.exec_command(command='build', path=app_name, platform=platform, release=release,
                                  provision=provision, for_device=for_device, bundle=bundle, aot=aot, uglify=uglify,
                                  snapshot=snapshot, wait=True, log_trace=log_trace)
        if verify:
            # Verify output
            assert result.exit_code == 0, 'Build failed with non zero exit code.'
            assert 'Project successfully built.' in result.output

            # Verify apk, app or ipa produced
            if platform == Platform.ANDROID:
                assert File.exists(TnsPaths.get_apk_path(app_name=app_name, release=release))
            if platform == Platform.IOS:
                app_path = TnsPaths.get_ipa_path(app_name=app_name, release=release, for_device=for_device)
                if for_device:
                    assert File.exists(app_path)
                else:
                    assert Folder.exists(app_path)

            # Verify based on app_data
            if app_data is not None:
                pass

        return result

    @staticmethod
    def build_android(app_name, release=False, bundle=True, aot=False, uglify=False, snapshot=False, log_trace=False,
                      verify=True, app_data=None):
        return Tns.build(app_name=app_name, platform=Platform.ANDROID, release=release, bundle=bundle, aot=aot,
                         uglify=uglify, snapshot=snapshot, log_trace=log_trace, verify=verify, app_data=app_data)

    @staticmethod
    def build_ios(app_name, release=False, provision=Settings.IOS.PROVISIONING, for_device=False,
                  bundle=True, aot=False, uglify=False, log_trace=False, verify=True, app_data=None):
        return Tns.build(app_name=app_name, platform=Platform.IOS, release=release, for_device=for_device,
                         provision=provision, bundle=bundle, aot=aot, uglify=uglify, log_trace=log_trace, verify=verify,
                         app_data=app_data)

    @staticmethod
    def deploy(app_name, platform, device=None, bundle=True, release=False, provision=Settings.IOS.PROVISIONING,
               for_device=False, wait=False, just_launch=False, log_trace=False, verify=True):
        result = Tns.exec_command(command='deploy', path=app_name, platform=platform, device=device, bundle=bundle,
                                  release=release, provision=provision, for_device=for_device, wait=wait,
                                  just_launch=just_launch, log_trace=log_trace)
        if verify:
            assert result.exit_code == 0, 'tns run failed with non zero exit code.'
            assert 'successfully installed on device' in result.output.lower()

        return result

    @staticmethod
    def run(app_name, platform, emulator=False, device=None, release=False, provision=Settings.IOS.PROVISIONING,
            for_device=False, bundle=True, hmr=True, aot=False, uglify=False, source_map=False, snapshot=False,
            wait=False, log_trace=False, just_launch=False, sync_all_files=False, clean=False, verify=True):
        result = Tns.exec_command(command='run', path=app_name, platform=platform, emulator=emulator, device=device,
                                  release=release, provision=provision, for_device=for_device, bundle=bundle,
                                  hmr=hmr, aot=aot, uglify=uglify, source_map=source_map, snapshot=snapshot,
                                  clean=clean, wait=wait, log_trace=log_trace, just_launch=just_launch,
                                  sync_all_files=sync_all_files)
        if verify:
            if wait:
                assert result.exit_code == 0, 'tns run failed with non zero exit code.'
                assert 'successfully synced' in result.output.lower()
            else:
                sleep(10)
        return result

    @staticmethod
    def run_android(app_name, emulator=False, device=None, release=False, bundle=True, hmr=True, aot=False,
                    uglify=False, source_map=False, snapshot=False, wait=False, log_trace=False, just_launch=False,
                    verify=True, clean=False):
        return Tns.run(app_name=app_name, platform=Platform.ANDROID, emulator=emulator, device=device, release=release,
                       bundle=bundle, hmr=hmr, aot=aot, uglify=uglify, source_map=source_map, snapshot=snapshot,
                       wait=wait, log_trace=log_trace, just_launch=just_launch, verify=verify, clean=clean)

    @staticmethod
    def run_ios(app_name, emulator=False, device=None, release=False, provision=Settings.IOS.PROVISIONING,
                for_device=False, bundle=True, hmr=True, aot=False, uglify=False, source_map=False, wait=False,
                log_trace=False, just_launch=False, verify=True, clean=False):
        return Tns.run(app_name=app_name, platform=Platform.IOS, emulator=emulator, device=device, release=release,
                       provision=provision, for_device=for_device, bundle=bundle, hmr=hmr, aot=aot, uglify=uglify,
                       source_map=source_map, wait=wait, log_trace=log_trace, just_launch=just_launch, verify=verify,
                       clean=clean)

    @staticmethod
    def debug(app_name, platform, start=False, debug_brk=False, emulator=False, device=None, release=False,
              provision=Settings.IOS.PROVISIONING, for_device=False, bundle=True, hmr=True, aot=False, uglify=False,
              wait=False, log_trace=False, verify=True):
        command = 'debug'
        if start:
            command += ' --start'
        if debug_brk:
            command += ' --debug-brk'
        result = Tns.exec_command(command=command, path=app_name, platform=platform, emulator=emulator, device=device,
                                  release=release, provision=provision, for_device=for_device,
                                  bundle=bundle, hmr=hmr, aot=aot, uglify=uglify, wait=wait, log_trace=log_trace)
        if verify:
            strings = ['To start debugging, open the following URL in Chrome:',
                       'chrome-devtools://devtools/bundled/inspector.html?experiments=true&ws=localhost:']
            if not start:
                strings.append('Successfully synced application')
            else:
                if platform == Platform.ANDROID:
                    strings.append('ActivityManager: Start proc')
                if hmr and platform == Platform.ANDROID:
                    strings.append('HMR: Hot Module Replacement Enabled.')

            TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=300)
            logs = File.read(result.log_file)
            assert 'closed' not in logs
            assert 'detached' not in logs
            assert "did not start in time" not in logs
        return result

    @staticmethod
    def preview(app_name, bundle=True, hmr=True, log_trace=True, verify=True, timeout=120):
        """
        Execute `tns preview` command.
        :param app_name: Pass --path <app_name>.
        :param bundle: If true pass --bundle.
        :param hmr: If true pass --hmr.
        :param log_trace: If true pass --log trace.
        :param verify: If true verify some logs.
        :param timeout: Timeout in seconds.
        :return: Result of `tns preview` command.
        """
        result = Tns.exec_command(command='preview', path=app_name, bundle=bundle, hmr=hmr, wait=False,
                                  log_trace=log_trace, timeout=timeout)
        if verify:
            strings = [
                'Use NativeScript Playground app and scan the QR code above to preview the application on your device']
            TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        return result

    @staticmethod
    def test_init(app_name, framework, update=True, verify=True):
        """
        Execute `tns test init` command.
        :param app_name: App name (passed as --path <App name>)
        :param framework: Unit testing framework as string (jasmin, mocha, quinit).
        :param update: Update nativescript-unit-test-runner if True.
        :param verify: Verify command was executed successfully.
        :return: Result of `tns test init` command.
        """
        app_path = TnsPaths.get_app_path(app_name=app_name)
        command = 'test init --framework {0}'.format(str(framework))
        result = Tns.exec_command(command=command, path=app_name, timeout=300)
        if verify:
            TnsAssert.test_initialized(app_name=app_name, framework=framework, output=result.output)
        if update:
            Npm.uninstall(package='nativescript-unit-test-runner', option='--save', folder=app_path)
            Npm.install(package='nativescript-unit-test-runner@next', option='--save --save-exact', folder=app_path)
        return result

    @staticmethod
    def test(app_name, platform, emulator=True, device=None, just_launch=True, verify=True):
        """
        Execute `tns test <platform>` command.
        :param app_name: App name (passed as --path <App name>)
        :param platform: PlatformType enum value.
        :param emulator: If true pass `--emulator` to the command.
        :param device: Pass `--device <value>` to command.
        :param just_launch: If true pass `--just_launch` to the command.
        :param verify: Verify command was executed successfully.
        :return: Result of `tns test` command.
        """
        cmd = 'test {0}'.format(str(platform))
        result = Tns.exec_command(command=cmd, path=app_name, emulator=emulator, device=device, just_launch=just_launch)
        if verify:
            assert 'server started at' in result.output
            assert 'Launching browser' in result.output
            assert 'Starting browser' in result.output
            assert 'Connected on socket' in result.output
            assert 'Executed 1 of 1' in result.output
            assert 'TOTAL: 1 SUCCESS' in result.output \
                   or 'Executed 1 of 1 SUCCESS' or 'Executed 1 of 1[32m SUCCESS' in result.output
        return result

    @staticmethod
    def doctor(app_name=None):
        """
        Execute `tns doctor`
        :param app_name: App where command will be executed (by default None -> common will be executed outside app).
        :return: Result of `tns doctor` command.
        """
        cwd = Settings.TEST_RUN_HOME
        if app_name is not None:
            cwd = os.path.join(cwd, app_name)
        return Tns.exec_command(command='doctor', cwd=cwd, timeout=60)

    @staticmethod
    def info(app_name=None):
        """
        Execute `tns info`
        :param app_name: App where command will be executed (by default None -> common will be executed outside app).
        :return: Result of `tns info` command.
        """
        cwd = Settings.TEST_RUN_HOME
        if app_name is not None:
            cwd = os.path.join(cwd, app_name)
        return Tns.exec_command(command='info', cwd=cwd, timeout=60)

    @staticmethod
    def version():
        """
        Get version of CLI
        :return: Version of the CLI as string
        """
        return Tns.exec_command(command='--version')

    @staticmethod
    def kill():
        """
        Kill all tns related processes.
        """
        Log.info("Kill tns processes.")
        if Settings.HOST_OS == OSType.WINDOWS:
            Process.kill(proc_name='node')
        else:
            Process.kill(proc_name='node', proc_cmdline=Settings.Executables.TNS)
            Process.kill_by_commandline(cmdline='webpack.js')
