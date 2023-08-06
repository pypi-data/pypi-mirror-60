import os
import time
import shutil
import warnings
import cv2
import tkinter
from tkinter import messagebox


class Watcher(object):
    def __init__(self,
                 path,
                 watchfor='',
                 includesubfolders=True,
                 subdirectory=None,
                 watch_type='file',
                 ):
        """
        Watches a folder for file changes.

        :param path: The folder path to watch for changes
        :param watchfor: Watch for this item. This can be a full filename, or an extension (denoted by *., e.g. "*.ext")
        :param bool includesubfolders: wehther to search subfolders
        :param str subdirectory: specified subdirectory
        :param str watch_type: The type of item to watch for ('file' or 'folder')
        """
        self._path = None
        self._subdir = None
        self.path = path
        self.subdirectory = subdirectory
        self.includesubfolders = includesubfolders
        self.watchfor = watchfor
        self.watch_type = watch_type

    def __repr__(self):
        return f'{self.__class__.__name__}({len(self.contents)} {self.watchfor})'

    def __str__(self):
        return f'{self.__class__.__name__} with {len(self.contents)} matches of {self.watchfor}'

    def __len__(self):
        return len(self.contents)

    def __iter__(self):
        for file in self.contents:
            yield file

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, newpath):
        if not os.path.isdir(newpath):
            raise ValueError(f'The specified path\n{newpath}\ndoes not exist.')
        self._path = newpath

    @property
    def subdirectory(self):
        return self._subdir

    @subdirectory.setter
    def subdirectory(self, newdir):
        if newdir is None:
            del self.subdirectory
            return
        if not os.path.isdir(
            os.path.join(self.path, newdir)
        ):
            raise ValueError(f'The subdirectory {newdir} does not exist in the path {self.path}.')
        self._subdir = newdir

    @subdirectory.deleter
    def subdirectory(self):
        self._subdir = None

    @property
    def contents(self):
        """Finds all instances of the watchfor item in the path"""
        # TODO exclude subfolders if specified
        if self.subdirectory is not None:
            path = os.path.join(self.path, self.subdirectory)
        else:
            path = self._path
        contents = []
        if self.includesubfolders is True:
            for root, dirs, files in os.walk(path):  # walk through specified path
                if self.watch_type == 'file':
                    for filename in files:  # check each file
                        if self._condition_match(filename) is True:  # check condition match
                            file_path = os.path.join(root, filename)
                            if os.path.isfile(file_path) is True:  # ensure file
                                contents.append(file_path)
                elif self.watch_type == 'folder':
                    for directory in dirs:
                        if self._condition_match(directory) is True:  # match condition
                            dir_path = os.path.join(root, directory)
                            if os.path.isdir(dir_path) is True:  # ensure directory
                                contents.append(dir_path)
        else:
            for file in os.listdir(path):
                if self._condition_match(file):
                    file_path = os.path.join(path, file)
                    if self.watch_type == 'file' and os.path.isfile(file_path):
                        contents.append(file_path)
                    elif self.watch_type == 'folder' and os.path.isdir(file_path):
                        contents.append(file_path)
        return contents

    def _condition_match(self, name: str):
        """
        Checks whether the file name matches the conditions of the instance.

        :param name: file or folder name.
        :return: bool
        """
        # match extension
        if name.lower().endswith(self.watchfor[1:].lower()):
            return True
        elif name.lower() == self.watchfor.lower():
            return True
        return False

    def check_path_for_files(self):
        """Finds all instances of the watchfor item in the path"""
        warnings.warn('The check_path_for_files method has be depreciated, access .contents directly',
                      DeprecationWarning)
        return self.contents

    def find_subfolder(self):
        """returns the subdirectory path within the full path where the target file is"""
        if self.subdirectory is not None:
            path = os.path.join(self.path, self.subdirectory)
        else:
            path = self.path
        contents = []
        for root, dirs, files in os.walk(path):  # walk through specified path
            for filename in files:  # check each file
                if self._condition_match(filename):  # match conditions
                    # todo catch file/folder?
                    contents.append(root)
        return contents

    def wait_for_presence(self, waittime=1.):
        """waits for a specified match to appear in the watched path"""
        while len(self.contents) == 0:
            time.sleep(waittime)
        return True

    def oldest_instance(self, wait=False, **kwargs):
        """
        Retrieves the first instance of the watched files.

        :param wait: if there are no instances, whether to wait for one to appear
        :return: path to first instance (None if there are no files present)
        """
        if len(self.contents) == 0:  # if there are no files
            if wait is True:  # if waiting is specified
                self.wait_for_presence(**kwargs)
            else:  # if no wait and no files present, return None
                return None
        if len(self.contents) == 1:  # if there is only one file
            return os.path.join(self._path, self.contents[0])
        else:  # if multiple items in list
            return os.path.join(  # return path to oldest (last modified) file in directory
                self._path,
                min(
                    zip(
                        self.contents,  # files in directory
                        [  # last modifiation time for files in directory
                            os.path.getmtime(
                                os.path.join(self._path, filename)
                            ) for filename in self.contents
                        ]
                    ),
                    key=lambda x: x[1]
                )[0]
            )

    def newest_instance(self):
        """
        Retrieves the newest instance of the watched files.

        :return: path to newest instance
        :rtype: str
        """
        if len(self.contents) == 0:  # if there are no files
            # if wait is True:  # if waiting is specified
            #     self.wait_for_presence(**kwargs)
            # else:  # if no wait and no files present, return None
            return None
        if len(self.contents) == 1:  # if there is only one file
            return os.path.join(self._path, self.contents[0])
        else:  # if multiple items in list
            return os.path.join(  # return path to oldest (last modified) file in directory
                self._path,
                max(
                    zip(
                        self.contents,  # files in directory
                        [os.path.getmtime(  # last modifiation time for files in directory
                            os.path.join(self._path, filename)
                        ) for filename in self.contents]
                    ),
                    key=lambda x: x[1]
                )[0]
            )

    def update_path(self, newpath):
        """
        Updates the path to file of the instance.

        :param str newpath: path to new file
        """
        warnings.warn('The update_path method has been depreciated, modify .path directly', DeprecationWarning)
        self.path = newpath


class Component:
    def __init__(self,
                 name: str,
                 path: str,
                 ):
        """
        Class that Folder inherits from, created in case there are other components to be tracked in folders in the
        future, such as files.

        :param str, name: name of the component
        :param str, path: path to save the component in. The last part of the path must be the name of the component
        """
        self.name = name
        self.path = path
        self.parent = None  # parent Component this component belongs to; can be set to None if it is the first
        # component being made

        try:
            self.save_to_disk()
        except FileExistsError as error:
            root = tkinter.Tk()
            yes_or_no_result = tkinter.messagebox.askyesno(
                f'Save to disk',
                f'File or folder at {path}. '
                f'Would you like to create one with "_copy_#" appended to the end of the file/folder name?')
            if yes_or_no_result is True:
                # rename the file something else
                for i in range(20):  # randomly put 20 here, just assuming there won't already be more than this
                    # number of folders that will be made with the same name
                    try:
                        old_name = self.get_name()
                        old_path = self.get_path()
                        new_name = old_name + f'_copy_{i}'
                        new_path = old_path + f'_copy_{i}'
                        self.set_name(name=new_name)
                        self.set_path(path=new_path)
                        self.save_to_disk()
                        root.destroy()
                        break
                    except FileExistsError as error:
                        self.set_name(name=old_name)
                        self.set_path(path=old_path)
            else:
                raise error

    def get_name(self):
        return self.name

    def get_path(self):
        return self.path

    def get_parent(self):
        return self.parent

    def set_name(self,
                 name: str,
                 ):
        self.name = name

    def set_path(self,
                 path: str,
                 ):
        self.path = path

    def set_parent(self,
                   component,
                   ):
        """
        Set the parent component for this component

        :param Component, component:
        :return:
        """
        self.parent = component

    def save_to_disk(self):
        """
        Actually create the component on the computer at its path with its name
        :return:
        """

        raise NotImplementedError

    def delete_from_disk(self):
        """
        Actually delete the component from the computer
        :return:
        """
        shutil.rmtree(path=self.path)


class Folder(Component):
    """
    Class to create and store a folder hierarchy and to easily create folders and access paths to save files and
    folders in

    Example using the Folder class - run each line one at a time to see changes to disk:

    root_path = os.getcwd()

    test_folder_name = 'test'
    test_folder_path = os.path.join(root_path, test_folder_name)

    test_folder = Folder(folder_name=test_folder_name, folder_path=test_folder_path)

    sub_folder_one = test_folder.make_and_add_sub_folder(sub_folder_name='sub_folder_one')
    sub_folder_two = test_folder.make_and_add_sub_folder(sub_folder_name='sub_folder_two')
    sub_sub_folder_one = sub_folder_one.make_and_add_sub_folder(sub_folder_name='sub_sub_folder_one')

    sub_folder_one.delete_from_disk()
    sub_folder_two.delete_from_disk()

    test_folder_two = Folder(folder_name=test_folder_name, folder_path=test_folder_path)

    test_folder.delete_from_disk()
    test_folder_two.delete_from_disk()

    """

    def __init__(self,
                 folder_name: str,
                 folder_path: str,
                 ):
        """
        A folder can have files and folders in it, but for now just care about it containing folders. The name of the
        folder should be the same as the last part of the folder path.

        :param str, folder_path: path to save the folder on disk
        :param str, folder_name: Should be the same as the last part of the folder path
        """
        super().__init__(
            name=folder_name,
            path=folder_path
        )
        self.children = set()

    def get_name(self):
        return super().get_name()

    def get_path(self):
        return super().get_path()

    def get_parent(self):
        return super().get_parent()

    def save_to_disk(self):
        os.makedirs(
            name=self.path,
        )

    def delete_from_disk(self):
        super().delete_from_disk()

    def set_parent(self,
                   component: Component,
                   ):
        super().set_parent(component=component)

    def get_parent(self):
        super().get_parent()

    def get_children(self):
        return self.children

    def add_child_component(self,
                            component: Component,
                            ):
        """
        Add a component to the set of children and set the parent of the child component to be this folder

        :param Component, component:
        :return:
        """
        self.children.add(component)
        component.set_parent(component=self)

    def remove_and_delete_component(self,
                                    component: Component,
                                    ):
        """
        Remove a child component from the children set and delete it from disk

        :param Component, component:
        :return:
        """
        self.children.remove(component)
        component.delete_from_disk()

    def make_and_add_sub_folder(self,
                                sub_folder_name: str,
                                ):
        """
        Create a sub-folder with a given name under the main folder; the path of the sub-folder is the name of the
        sub-folder concatenated on to the end of the path of the main folder

        :return: Folder, sub_folder: the sub-folder that was created
        """

        if sub_folder_name in self.children:
            raise Exception(f'Main folder already has a sub-folder called {sub_folder_name}')
        else:
            parent_folder_path = self.path
            sub_folder_path = os.path.join(
                parent_folder_path,
                sub_folder_name
            )
            sub_folder = Folder(
                folder_name=sub_folder_name,
                folder_path=sub_folder_path,
            )
            sub_folder.set_parent(component=self)

            self.add_child_component(component=sub_folder)

        return sub_folder

    def save_image_to_folder(self,
                             image_name: str,
                             image,
                             file_format: str = 'jpg',
                             ):
        """
        Save an image to disk using cv2

        :param str, image_name: name of the file to save the image as in the folder
        :param image: image to save
        :param str, file_format: file format to save the image as. Is jpg by default.

        :return: str, path_to_save_image: the path the image was saved to
        """
        image_name = f'{image_name}.{file_format}'
        path_to_save_image = os.path.join(self.path, image_name)
        cv2.imwrite(path_to_save_image, image)

        return path_to_save_image

