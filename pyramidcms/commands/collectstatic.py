import os
import shutil
import fnmatch

from pyramidcms.cli import BaseCommand
from pyramidcms.config import get_static_dirs


class Command(BaseCommand):
    """
    Find all static files in directories from the setting static.dirs and
    copies them into the static.collection_dir folder.
    """

    def copy_files(self, src, dest):
        """
        Copy files and folders recursively from the source directory
        to the destination.

        If a file is already in the destination folder, the file timestamps
        are compared to determine if the file needs to be copied again,
        or if we can skip copying that file.

        :param src: source directory, copies files and folders inside.
        :param dest: destination directory, will be created if doesn't exist.
        :return: (total_files, num_files_copied, num_dirs_created)
        :rtype: tuple
        """
        total_files, num_files_copied, num_dirs_created = 0, 0, 0

        if not os.path.exists(dest):
            print('Create directory: "{}"'.format(dest))
            os.makedirs(dest)
            num_dirs_created += 1

        for root, dirs, files in os.walk(src):

            exclude = set(['CVS', '.*', '*~'])
            dirs[:] = [d for d in dirs if d not in fnmatch.filter(dirs, exclusions ]
            files[:] = [f for f in files if f not in exclude]

            for item in files:
                src_path = os.path.join(root, item)
                dst_path = os.path.join(dest, src_path.replace(src, ''))

                if os.path.exists(dst_path):
                    if os.stat(src_path).st_mtime > os.stat(dst_path).st_mtime:
                        print('Copying: "{}" => "{}"'.format(src_path, dst_path))
                        shutil.copy2(src_path, dst_path)
                        num_files_copied += 1
                else:
                    print('Copying: "{}" => "{}"'.format(src_path, dst_path))
                    shutil.copy2(src_path, dst_path)
                    num_files_copied += 1

                total_files += 1

            for item in dirs:
                src_path = os.path.join(root, item)
                dst_path = os.path.join(dest, src_path.replace(src, ''))
                if not os.path.exists(dst_path):
                    print('Create directory: "{}"'.format(dst_path))
                    os.mkdir(dst_path)
                    num_dirs_created += 1

        return total_files, num_files_copied, num_dirs_created

    def clear_folder_contents(self, folder_path):
        """
        Removes folders and files from the given directory.

        :param folder_path: The directory that will be cleared.
        """
        if os.path.exists(folder_path):
            print('Clearing: "{}"'.format(folder_path))
            for file_object in os.listdir(folder_path):
                file_object_path = os.path.join(folder_path, file_object)
                if os.path.isfile(file_object_path):
                    os.unlink(file_object_path)
                else:
                    shutil.rmtree(file_object_path)

    def setup_args(self, parser):
        parser.add_argument('-c',
                            '--clear',
                            help='empties the target directory first',
                            action='store_true')

    def handle(self, args):
        static_dirs = get_static_dirs(self.settings)
        collect_dir = self.settings.get('static.collect_dir')
        print('Source directories: "{}"'.format('", "'.join(static_dirs)))
        print('Destination directory: "{}"\n'.format(collect_dir))

        if args.clear:
            self.clear_folder_contents(collect_dir)

        total_files, num_files_copied, num_dirs_created = 0, 0, 0
        for directory in static_dirs:
            total, num_copied, dirs_created = self.copy_files(directory, collect_dir)
            total_files += total
            num_files_copied += num_copied
            num_dirs_created += dirs_created

        # only print a newline if there was output during copying
        if num_dirs_created > 0 or num_files_copied > 0:
            print('')

        print('Number of files copied: {}'.format(num_files_copied))
        print('Number of directories created: {}'.format(num_dirs_created))
        print('Number of files un-modified: {}'.format(total_files - num_files_copied))
