"""
Sync changes on JS/TS project helper.
"""

import os

from core.enums.app_type import AppType
from core.settings import Settings
from core.utils.device.device import Device
from core.utils.file_utils import File
from core.utils.wait import Wait
from data.changes import Changes, Sync
from data.const import Colors
from products.nativescript.tns import Tns
from products.nativescript.tns_helpers import TnsHelpers
from data.sync.console_log_helpers import ConsoleLog


def sync_hello_world_js(app_name, platform, device, bundle=False, hmr=False, uglify=False, aot=False,
                        snapshot=False):
    __sync_hello_world_js_ts(app_type=AppType.JS, app_name=app_name, platform=platform,
                             device=device,
                             bundle=bundle, hmr=hmr, uglify=uglify, aot=aot, snapshot=snapshot)


def sync_hello_world_ts(app_name, platform, device, bundle=False, hmr=False, uglify=False, aot=False,
                        snapshot=False):
    __sync_hello_world_js_ts(app_type=AppType.TS, app_name=app_name, platform=platform,
                             device=device,
                             bundle=bundle, hmr=hmr, uglify=uglify, aot=aot, snapshot=snapshot)


def __verify_snapshot_skipped(snapshot, result):
    """
    Verify if snapshot flag is passed it it skipped.
    :param snapshot: True if snapshot flag is present.
    :param result: Result of `tns run` command.
    """
    if snapshot:
        msg = 'Bear in mind that snapshot is only available in release builds and is NOT available on Windows'
        skip_snapshot = Wait.until(lambda: 'Stripping the snapshot flag' in File.read(result.log_file), timeout=180)
        assert skip_snapshot, 'Not message that snapshot is skipped.'
        assert msg in File.read(result.log_file), 'No message that snapshot is NOT available on Windows.'

def __sync_hello_world_js_ts(app_type, app_name, platform, device,
                             bundle=False, hmr=False, uglify=False, aot=False, snapshot=False):
    if app_type == AppType.JS:
        js_change = Changes.JSHelloWord.JS
        xml_change = Changes.JSHelloWord.XML
        css_change = Changes.JSHelloWord.CSS
    elif app_type == AppType.TS:
        js_change = Changes.TSHelloWord.TS
        xml_change = Changes.TSHelloWord.XML
        css_change = Changes.TSHelloWord.CSS
    else:
        raise ValueError('Invalid app_type value.')
    result = Tns.run(app_name=app_name, platform=platform, emulator=True, wait=False,
                     bundle=bundle, hmr=hmr, uglify=uglify, aot=aot, snapshot=snapshot)

    if bundle is False and hmr is False and uglify is False and aot is False and snapshot is False:
        strings = [ConsoleLog.proj_success_build, ConsoleLog.success_installed,
                   ConsoleLog.restart_app, ConsoleLog.success_sync]
        TnsHelpers.wait_for_log(log_file=result.log_file, string_list=strings)

    if bundle is True and hmr is False and uglify is False and aot is False and snapshot is False \
            or bundle is True and hmr is False and uglify is False and aot is True and snapshot is False:
        strings = [ConsoleLog.webpack, ConsoleLog.proj_success_build, ConsoleLog.success_installed,
                   ConsoleLog.bundle, ConsoleLog.package, ConsoleLog.starter, ConsoleLog.vendor,
                   ConsoleLog.restart_app, ConsoleLog.success_sync]
        TnsHelpers.wait_for_log(log_file=result.log_file, string_list=strings)

    __verify_snapshot_skipped(snapshot, result)

    # Verify it looks properly
    device.wait_for_text(text=js_change.old_text, timeout=120, retry_delay=5)
    device.wait_for_text(text=xml_change.old_text)
    blue_count = device.get_pixels_by_color(color=Colors.LIGHT_BLUE)
    assert blue_count > 100, 'Failed to find blue color on {0}'.format(device.name)
    initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name, 'initial_state.png')
    device.get_screen(path=initial_state)

    # Edit JS file and verify changes are applied
    Sync.replace(app_name=app_name, change_set=js_change)
    device.wait_for_text(text=js_change.new_text)

    if bundle is False and hmr is False and uglify is False and aot is False and snapshot is False:
        strings = [ConsoleLog.success_transffer, ConsoleLog.js, ConsoleLog.restart_app, ConsoleLog.success_sync]
        TnsHelpers.wait_for_log(log_file=result.log_file, string_list=strings)

    if bundle is True and hmr is False and uglify is False and aot is False and snapshot is False:
        strings = [ConsoleLog.webpack, ConsoleLog.success_transffer, ConsoleLog.bundle,
                   ConsoleLog.restart_app, ConsoleLog.success_sync]
        TnsHelpers.wait_for_log(log_file=result.log_file, string_list=strings)

    # Edit XML file and verify changes are applied
    Sync.replace(app_name=app_name, change_set=xml_change)
    device.wait_for_text(text=xml_change.new_text)
    device.wait_for_text(text=js_change.new_text)

    if bundle is False and hmr is False and uglify is False and aot is False and snapshot is False:
        strings = [ConsoleLog.success_transffer, ConsoleLog.xml, ConsoleLog.refreshing_app, ConsoleLog.success_sync]
        TnsHelpers.wait_for_log(log_file=result.log_file, string_list=strings)

    if bundle is True and hmr is False and uglify is False and aot is False and snapshot is False:
        strings = [ConsoleLog.webpack, ConsoleLog.success_transffer, ConsoleLog.bundle,
                   ConsoleLog.restart_app, ConsoleLog.success_sync]
        TnsHelpers.wait_for_log(log_file=result.log_file, string_list=strings)

    # Edit CSS file and verify changes are applied
    Sync.replace(app_name=app_name, change_set=css_change)
    device.wait_for_color(color=Colors.LIGHT_BLUE, pixel_count=blue_count * 2, delta=25)
    device.wait_for_text(text=xml_change.new_text)
    device.wait_for_text(text=js_change.new_text)

    if bundle is False and hmr is False and uglify is False and aot is False and snapshot is False:
        strings = [ConsoleLog.success_transffer, ConsoleLog.css, ConsoleLog.refreshing_app, ConsoleLog.success_sync]
        TnsHelpers.wait_for_log(log_file=result.log_file, string_list=strings)

    if bundle is True and hmr is False and uglify is False and aot is False and snapshot is False:
        strings = [ConsoleLog.webpack, ConsoleLog.success_transffer, ConsoleLog.bundle,
                   ConsoleLog.restart_app, ConsoleLog.success_sync]
        TnsHelpers.wait_for_log(log_file=result.log_file, string_list=strings)

    # Revert all the changes
    Sync.revert(app_name=app_name, change_set=js_change)
    device.wait_for_text(text=js_change.old_text)
    device.wait_for_text(text=xml_change.new_text)

    if bundle is False and hmr is False and uglify is False and aot is False and snapshot is False:
        strings = [ConsoleLog.success_transffer, ConsoleLog.js, ConsoleLog.restart_app, ConsoleLog.success_sync]
        TnsHelpers.wait_for_log(log_file=result.log_file, string_list=strings)

    if bundle is True and hmr is False and uglify is False and aot is False and snapshot is False:
        strings = [ConsoleLog.webpack, ConsoleLog.success_transffer, ConsoleLog.bundle,
                   ConsoleLog.restart_app, ConsoleLog.success_sync]
        TnsHelpers.wait_for_log(log_file=result.log_file, string_list=strings)

    Sync.revert(app_name=app_name, change_set=xml_change)
    device.wait_for_text(text=xml_change.old_text)
    device.wait_for_text(text=js_change.old_text)

    if bundle is False and hmr is False and uglify is False and aot is False and snapshot is False:
        strings = [ConsoleLog.success_transffer, ConsoleLog.xml, ConsoleLog.refreshing_app, ConsoleLog.success_sync]
        TnsHelpers.wait_for_log(log_file=result.log_file, string_list=strings)

    if bundle is True and hmr is False and uglify is False and aot is False and snapshot is False:
        strings = [ConsoleLog.webpack, ConsoleLog.success_transffer, ConsoleLog.bundle,
                   ConsoleLog.restart_app, ConsoleLog.success_sync]
        TnsHelpers.wait_for_log(log_file=result.log_file, string_list=strings)

    Sync.revert(app_name=app_name, change_set=css_change)
    device.wait_for_color(color=Colors.LIGHT_BLUE, pixel_count=blue_count)
    device.wait_for_text(text=xml_change.old_text)
    device.wait_for_text(text=js_change.old_text)

    if bundle is False and hmr is False and uglify is False and aot is False and snapshot is False:
        strings = [ConsoleLog.success_transffer, ConsoleLog.css, ConsoleLog.refreshing_app, ConsoleLog.success_sync]
        TnsHelpers.wait_for_log(log_file=result.log_file, string_list=strings)

    if bundle is True and hmr is False and uglify is False and aot is False and snapshot is False:
        strings = [ConsoleLog.webpack, ConsoleLog.success_transffer, ConsoleLog.bundle,
                   ConsoleLog.restart_app, ConsoleLog.success_sync]
        TnsHelpers.wait_for_log(log_file=result.log_file, string_list=strings)

    # Assert final and initial states are same
    device.screen_match(expected_image=initial_state, tolerance=1.0, timeout=30)
