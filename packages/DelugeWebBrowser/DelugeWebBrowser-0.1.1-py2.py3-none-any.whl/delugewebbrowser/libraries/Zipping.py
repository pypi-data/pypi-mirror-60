import os
from zipfile import ZipFile


def create_archive(path, archive_name):  # folder need to be given a trailing slash
    dirname = os.path.dirname(path)
    basename = os.path.basename(path)
    old_cwd = os.getcwd()
    os.chdir(dirname)
    with ZipFile(archive_name, 'w') as zipObj:
        if os.path.isfile(path):
            zipObj.write(basename)
        else:
            # Iterate over all the files in directory
            for folderName, subfolders, filenames in os.walk(basename):
                for filename in filenames:
                    # create complete filepath of file in directory
                    filePath = os.path.join(folderName, filename)
                    # Add file to zip
                    zipObj.write(filePath)
    os.chdir(old_cwd)
    return os.path.join(dirname, archive_name)
