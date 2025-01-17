"""
File and Folder utils.
"""
# pylint: disable=unused-variable
# pylint: disable=no-member
# pylint: disable=broad-except
# pylint: disable=no-name-in-module
# pylint: disable=import-error
import errno
import fnmatch
import os
import shutil
import stat
import tarfile
import zipfile

from core.base_test.test_context import TestContext
from core.enums.os_type import OSType
from core.log.log import Log
from core.settings import Settings
from core.utils.process import Process


# noinspection PyBroadException
class Folder(object):
    @staticmethod
    def clean(folder):
        if Folder.exists(folder=folder):
            Log.debug("Clean folder: " + folder)
            try:
                shutil.rmtree(folder)
            except OSError as error:
                try:
                    for root, dirs, files in os.walk(folder, topdown=False):
                        for name in files:
                            filename = os.path.join(root, name)
                            if Settings.HOST_OS != OSType.WINDOWS:
                                os.chmod(filename, stat.S_IWUSR)
                            os.remove(filename)
                        for name in dirs:
                            os.rmdir(os.path.join(root, name))
                    os.rmdir(folder)
                    Log.error('Error: %s - %s.' % (error.filename, error.strerror))
                except Exception:
                    Log.info('Kill processes with handle to ' + folder)
                    Process.kill_by_handle(folder)
                    os.system('rm -rf {0}'.format(folder))

    @staticmethod
    def exists(folder):
        return os.path.isdir(folder)

    @staticmethod
    def is_empty(folder):
        return not os.listdir(folder)

    @staticmethod
    def create(folder):
        if not os.path.exists(folder):
            Log.debug("Create folder: " + folder)
            try:
                os.makedirs(folder)
            except OSError:
                raise

    @staticmethod
    def copy(source, target, clean_target=True, only_files=False):
        """
        Copy folders.
        :param source: Source folder.
        :param target: Target folder.
        :param clean_target: If True clean target folder before copy.
        :param only_files: If True only the files from source folder are copied to target folder.
        """
        if clean_target:
            Folder.clean(folder=target)
        Log.info('Copy {0} to {1}'.format(source, target))
        if only_files is True:
            files = os.listdir(source)

            for f in files:
                f_path = os.path.join(source, f)
                File.copy(f_path, target)
        else:
            try:
                shutil.copytree(source, target)
            except OSError as exc:
                if exc.errno == errno.ENOTDIR:
                    shutil.copy(source, target)
                else:
                    raise

    @staticmethod
    def get_size(folder):
        """
        Get folder size in bytes.
        :param folder: Folder path.
        :return: Size in bytes.
        """
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder):
            for file_name in filenames:
                file_path = os.path.join(dirpath, file_name)
                total_size += os.path.getsize(file_path)
        return total_size


# noinspection PyBroadException,PyArgumentList, PyUnresolvedReferences
class File(object):
    @staticmethod
    def read(path):
        if File.exists(path):
            if Settings.PYTHON_VERSION < 3:
                with open(path, 'r') as file_to_read:
                    output = file_to_read.read()
                return str(output.decode('utf8').encode('utf8'))
            else:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    output = f.read()
                return output
        else:
            raise IOError("{0} not found!".format(path))

    @staticmethod
    def write(path, text):
        if Settings.PYTHON_VERSION < 3:
            with open(path, 'w+') as text_file:
                text_file.write(text)
        else:
            with open(path, 'w+', encoding='utf-8', errors='ignore') as text_file:
                text_file.write(text)

    @staticmethod
    def append(path, text):
        if Settings.PYTHON_VERSION < 3:
            with open(path, 'a') as text_file:
                text_file.write(text)
        else:
            with open(path, 'a', encoding='utf-8', errors='ignore') as text_file:
                text_file.write(text)

    @staticmethod
    def replace(path, old_string, new_string, fail_safe=False, backup_files=False):
        if backup_files:
            File.__back_up_files(path)
        content = File.read(path=path)
        old_text_exists = old_string in content
        if not fail_safe:
            assert old_text_exists, 'Can not find "{0}" in {1}'.format(old_string, path)
        if old_text_exists:
            new_content = content.replace(old_string, new_string)
            File.write(path=path, text=new_content)
            Log.info("")
            Log.info("##### REPLACE FILE CONTENT #####")
            Log.info("File: {0}".format(path))
            Log.info("Old String: {0}".format(old_string))
            Log.info("New String: {0}".format(new_string))
            Log.info("")
        else:
            Log.debug('Skip replace. Text "{0}" do not exists in {1}.'.format(old_string, path))

    @staticmethod
    def exists(path):
        return os.path.isfile(path)

    @staticmethod
    def __back_up_files(backup_file, source_file=None):
        # create temp folder if missing
        if not Folder.exists(Settings.BACKUP_FOLDER):
            Folder.create(Settings.BACKUP_FOLDER)
        # if delete or replace method is used
        if source_file is None:
            source_file = backup_file
        source_name = source_file.split("/")[-1:][0]
        # backup file if from the template
        if File.exists(backup_file):
            source_name = backup_file.split("/")[-1:][0]
            # change file name if exists in backup_folder
            if File.exists(os.path.join(Settings.BACKUP_FOLDER, source_name)):
                source_name = source_name + "1"
            shutil.copy(backup_file, os.path.join(Settings.BACKUP_FOLDER, source_name))
        else:
            if Folder.exists(backup_file):
                # if copy to folder is used add file name
                backup_file = (os.path.join(backup_file, source_name))
            else:
                # if file name is used for new file
                source_name = backup_file.split("/")[-1:][0]
        TestContext.BACKUP_FILES[backup_file] = source_name

    @staticmethod
    def copy(source, target, backup_files=False):
        if backup_files:
            File.__back_up_files(target, source)
        shutil.copy(source, target)
        Log.info('Copy {0} to {1}'.format(os.path.abspath(source), os.path.abspath(target)))

    @staticmethod
    def delete(path, backup_files=False):
        if os.path.isfile(path):
            if backup_files:
                File.__back_up_files(path)
            os.remove(path)
            Log.debug('Delete {0}'.format(path))
        else:
            Log.debug('Error: %s file not found' % path)

    @staticmethod
    def clean(path):
        if os.path.isfile(path):
            File.write(path, text='')
        else:
            raise IOError('Error: %s file not found' % path)

    @staticmethod
    def find(base_path, file_name, exact_match=False, match_index=0):
        """
        Find file in path.
        :param base_path: Base path.
        :param file_name: File/folder name.
        :param exact_match: If True it will match exact file/folder name
        :param match_index: Index of match (all matches are sorted by path len, 0 will return closest to root)
        :return: Path to file.
        """
        matches = []
        for root, dirs, files in os.walk(base_path, followlinks=True):
            for current_file in files:
                if exact_match:
                    if file_name == current_file:
                        matches.append(os.path.join(root, current_file))
                else:
                    if file_name in current_file:
                        matches.append(os.path.join(root, current_file))
        matches.sort(key=lambda s: len(s))
        return matches[match_index]

    @staticmethod
    def pattern_exists(directory, pattern):
        """
        Check if file pattern exist at location.
        :param directory: Base directory.
        :param pattern: File pattern, for example: '*.aar' or '*.android.js'.
        :return: True if exists, False if does not exist.
        """
        found = False
        for root, dirs, files in os.walk(directory):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)
                    Log.info(pattern + " exists: " + filename)
                    found = True
        return found

    @staticmethod
    def find_by_extension(folder, extension):
        """
        Find by file extension recursively.
        :param folder: Base folder where search is done.
        :param extension: File extension.
        :return: List of found files.
        """
        matches = []
        if '.' not in extension:
            extension = '.' + extension
        for root, dirs, files in os.walk(folder):
            for f in files:
                if f.endswith(extension):
                    Log.debug('File with {0} extension found: {1}'.format(extension, os.path.abspath(f)))
                    matches.append(os.path.join(root, f))
        return matches

    @staticmethod
    def extract_part_of_text(text, key_word):
        """
        That method will extract text from last occurance of key word
        to the end of the file
        """
        index = text.rfind(key_word)
        text = text[index:]
        return text

    @staticmethod
    def unpack_tar(file_path, dest_dir):
        try:
            tar_file = tarfile.open(file_path, 'r:gz')
            tar_file.extractall(dest_dir)
        except Exception:
            Log.debug('Failed to unpack .tar file {0}'.format(file_path))

    @staticmethod
    def unzip(file_path, dest_dir, clean_dest_dir=True):
        if clean_dest_dir:
            Folder.clean(dest_dir)
            Folder.create(dest_dir)
        try:
            zfile = zipfile.ZipFile(file_path, 'r')
            zfile.extractall(dest_dir)
            zfile.close()
        except Exception:
            Log.debug('Failed to unzip file {0}'.format(file_path))

    @staticmethod
    def download(file_name, url, destination_dir=Settings.TEST_RUN_HOME):
        file_path = os.path.join(destination_dir, file_name)
        if Settings.PYTHON_VERSION < 3:
            import urllib
            urllib.urlretrieve(url, file_path)
        else:
            import urllib.request
            urllib.request.urlretrieve(url, file_path)
        file_path = os.path.join(destination_dir, file_name)
        assert File.exists(file_path), 'Failed to download {0} at {1}.'.format(url, file_path)
        Log.info('Downloaded {0} at {1}'.format(url, file_path))

    @staticmethod
    def get_size(file_path):
        return os.path.getsize(file_path)
