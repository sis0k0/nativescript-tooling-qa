from products.nativescript.tns_helpers import TnsHelpers


class ConsoleLog(object):

    # js project
    proj_success_build = 'Project successfully built'
    success_installed = 'Successfully installed on device with identifier'
    success_transffer = 'Successfully transferred'
    success_sync = 'Successfully synced application'
    restart_app = 'Restarting application on device'
    refreshing_app = 'Refreshing application on device'
    js = 'main-view-model.js'
    xml = 'main-page.xml'
    css = 'app.css'

    #ios --bundle
    transf_bundle = 'Successfully transferred bundle.js on device'
    transf_package = 'Successfully transferred package.json on device'
    transf_starter = 'Successfully transferred starter.js on device'
    transf_vendor = 'Successfully transferred vendor.js on device'
    #android --bundle
    transf_all_files_ios = 'Successfully transferred all files on device'


    #hmr
    hmr_module = 'HMR: Hot Module Replacement Enabled. Waiting for signal.'
    hmr_update = 'HMR: Checking for updates to the bundle with hmr hash'
    main_page = './main-page.js'
    hmr_success = 'HMR: Successfully applied update with hmr hash'
    hmr_transf = 'Successfully transferred bundle.'

    #js project with --bundle
    webpack = 'Webpack compilation complete'
    bundle = 'bundle.js'
    package = 'package.json'
    starter = 'starter.js'
    vendor = 'vendor.js'
