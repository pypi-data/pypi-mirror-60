# Copyright 2019 The Johns Hopkins University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
from datetime import timezone
import glob
import json
import os
import requests
import sys
import time

from craedl import errors

BUF_SIZE = 104857600
RETRY_MAX = 5
RETRY_SLEEP = 1

def get_numbered_upload(parent, childname):
    """
    If a File/Directory comes back instead of a Directory/File, we know this
    directory was created with the same name as an
    existing file and had a number appended to its name
    like this: 'childname' --> 'childname (1)'.
    We must find the matching directory with the highest
    number and get that as a replacement.

    :param parent: the parent directory
    :type parent: Directory
    :param childname: the name of the new child
    :type childname: string
    """
    match_num = 0
    for c in parent.children:
        if (childname in c['name'] and childname != c['name']):
            num = int(c['name'].replace(childname + ' (', '' ).replace(')', ''))
            if num > match_num:
                match_num = num
    return self.get('%s (%d)' % (childname, match_num))

def read_from_log(logfile):
    """
    Read the message in the next line of the log.

    :param logfile: the logfile
    :type logfile: File
    :returns: a tuple containg the message and the timestamp
    """
    log = logfile.readline()
    if log == '':
        return (None, None)
    timestamp = datetime.fromisoformat(log[:32])
    message = log[33:]
    log2 = logfile.readline()
    if log == '':
        return (None, None)
    timestamp2 = datetime.fromisoformat(log[:32])
    message2 = log2[33:]
    if 'DONE' not in message2:
        return (None, timestamp)
    return (message, timestamp)

def to_x_bytes(bytes):
    """
    Take a number in bytes and return a human-readable string.

    :param bytes: number in bytes
    :type bytes: int
    :returns: a human-readable string
    """
    x_bytes = bytes
    power = 0
    while x_bytes >= 1000:
        x_bytes = x_bytes * 0.001
        power = power + 3
    if power == 0:
        return '%.0f bytes' % x_bytes
    if power == 3:
        return '%.0f kB' % x_bytes
    if power == 6:
        return '%.0f MB' % x_bytes
    if power == 9:
        return '%.0f GB' % x_bytes
    if power == 12:
        return '%.0f TB' % x_bytes

def write_to_log(log_path, message):
    """
    Write a message to the log. Automatically prepends the timestamp.

    :param log_path: absolute path to the logfile
    :type log_path: string
    :param message: the message to write to the logfile
    :type message: string
    """
    print(datetime.now(timezone.utc).isoformat() + ' ' + message, end='', flush=True)
    f = open(log_path, 'a+')
    f.write(datetime.now(timezone.utc).isoformat() + ' ' + message)
    f.close()

class Auth():
    """
    This base class handles low-level RESTful API communications. Any class that
    needs to perform RESTful API communications should extend this class.
    """
    base_url = 'https://api.craedl.org/'

    token = None

    if sys.platform == 'win32':
        token_path = os.path.abspath(os.path.join(os.sep, 'Users',
            os.getlogin(), 'AppData', 'Local', 'Craedl', 'craedl'))
    elif sys.platform == 'darwin':
        token_path = os.path.abspath(os.path.join(os.sep, 'Users',
            os.getlogin(), 'Library', 'Preferences', 'Craedl', 'craedl'))
    else:
        token_path = os.path.expanduser('~/.config/Craedl/craedl')

    def __init__(self):
        if not os.path.isfile(os.path.expanduser(self.token_path)):
            raise errors.Missing_Token_Error

    def __repr__(self):
        string = '{'
        for k, v in vars(self).items():
            if k != 'token':
                if type(v) is str:
                    string += "'" + k + "': '" + v + "', "
                else:
                    string += "'" + k + "': " + str(v) + ", "
        if len(string) > 1:
            string = string[:-2]
        string += '}'
        return string

    def GET(self, path):
        """
        Handle a GET request.

        :param path: the RESTful API method path
        :type path: string
        :returns: a dict containing the contents of the parsed JSON response or
            an HTML error string if the response does not have status 200
        """
        if not self.token:
            self.token = open(os.path.expanduser(self.token_path)).readline().strip()
        attempt = 0
        while attempt < RETRY_MAX:
            attempt = attempt + 1
            try:
                response = requests.get(
                    self.base_url + path,
                    headers={'Authorization': 'Bearer %s' % self.token},
                )
                return self.process_response(response)
            except requests.exceptions.ConnectionError:
                time.sleep(RETRY_SLEEP)
        raise errors.Retry_Max_Error

    def POST(self, path, data):
        """
        Handle a POST request.

        :param path: the RESTful API method path
        :type path: string
        :param data: the data to POST to the RESTful API method as described at
            https://api.craedl.org
        :type data: dict
        :returns: a dict containing the contents of the parsed JSON response or
            an HTML error string if the response does not have status 200
        """
        if not self.token:
            self.token = open(os.path.expanduser(self.token_path)).readline().strip()
        attempt = 0
        while attempt < RETRY_MAX:
            attempt = attempt + 1
            try:
                response = requests.post(
                    self.base_url + path,
                    json=data,
                    headers={'Authorization': 'Bearer %s' % self.token},
                )
                return self.process_response(response)
            except requests.exceptions.ConnectionError:
                time.sleep(RETRY_SLEEP)
        raise errors.Retry_Max_Error

    def PUT_DATA(self, path, file_path):
        """
        Handle a data PUT request.

        :param path: the RESTful API method path
        :type path: string
        :param file_path: the data to POST to the RESTful API method as described at
            https://api.craedl.org
        :type file_path: string
        :returns: a dict containing the contents of the parsed JSON response or
            an HTML error string if the response does not have status 200
        """
        if not self.token:
            self.token = open(os.path.expanduser(self.token_path)).readline().strip()
        with open(file_path, 'rb') as data:
            d = data.read(BUF_SIZE)
            if d:
                while d:
                    attempt = 0
                    while attempt < RETRY_MAX:
                        attempt = attempt + 1
                        try:
                            response = requests.put(
                                self.base_url + path,
                                data=d,
                                headers={
                                    'Authorization': 'Bearer %s' % self.token,
                                    'Content-Disposition': 'attachment; filename="craedl-upload"',
                                },
                            )
                            break
                        except requests.exceptions.ConnectionError:
                            time.sleep(RETRY_SLEEP)
                    if attempt >= RETRY_MAX:
                        raise errors.Retry_Max_Error
                    d = data.read(BUF_SIZE)
                return self.process_response(response)
            else: # force request for empty file
                attempt = 0
                while attempt < RETRY_MAX:
                    attempt = attempt + 1
                    try:
                        response = requests.put(
                            self.base_url + path,
                            # no data
                            headers={
                                'Authorization': 'Bearer %s' % self.token,
                                'Content-Disposition': 'attachment; filename="craedl-upload"',
                            },
                        )
                        return self.process_response(response)
                    except requests.exceptions.ConnectionError:
                        time.sleep(RETRY_SLEEP)
                raise errors.Max_Retry_Error

    def GET_DATA(self, path):
        """
        Handle a data GET request.

        :param path: the RESTful API method path
        :type path: string
        :returns: the data stream being downloaded
        """
        if not self.token:
            self.token = open(os.path.expanduser(self.token_path)).readline().strip()
        attempt = 0
        while attempt < RETRY_MAX:
            attempt = attempt + 1
            try:
                response = requests.get(
                    self.base_url + path,
                    headers={'Authorization': 'Bearer %s' % self.token},
                    stream=True,
                )
                return response
            except requests.exceptions.ConnectionError:
                time.sleep(RETRY_SLEEP)
        raise errors.Retry_Max_Error

    def process_response(self, response):
        """
        Process the response from a RESTful API request.

        :param response: the RESTful API response
        :type response: a response object
        :returns: a dict containing the contents of the parsed JSON response or
            an HTML error string if the response does not have status 200
        """
        if response.status_code == 200:
            out = json.loads(response.content.decode('utf-8'))
            if out:
                return out
        elif response.status_code == 400:
            raise errors.Parse_Error(details=response.content.decode('ascii'))
        elif response.status_code == 401:
            raise errors.Invalid_Token_Error
        elif response.status_code == 403:
            raise errors.Unauthorized_Error
        elif response.status_code == 404:
            raise errors.Not_Found_Error
        elif response.status_code == 500:
            raise errors.Server_Error
        else:
            raise errors.Other_Error

class Directory(Auth):
    """
    A Craedl directory object.
    """

    def __init__(self, id):
        super().__init__()
        data = self.GET('directory/' + str(id) + '/')['directory']
        for k, v in data.items():
            setattr(self, k, v)

    def __eq__(self, other):
        if not isinstance(other, Directory):
            return NotImplemented
        equal = True
        for i1, i2 in list(zip(vars(self).items(), vars(other).items())):
            if i1[0] != i2[0] or i1[1] != i2[1]:
                equal = False
        return equal

    def create_directory(self, name):
        """
        Create a new directory contained within this directory.

        **Note:** This method returns the updated instance of this directory
        (because it has a new child). The recommended usage is:

        .. code-block:: python

            home = home.create_directory('new-directory-name')

        Use :meth:`Directory.get` to get the new directory.

        :param name: the name of the new directory
        :type name: string
        :returns: the updated instance of this directory
        """
        data = {
            'name': name,
            'parent': self.id,
        }
        response_data = self.POST('directory/', data)
        return Directory(self.id)

    def get(self, path):
        """
        Get a particular directory or file. This can be an absolute or
        relative path.

        :param path: the directory or file path
        :type path: string
        :returns: the requested directory or file
        """
        if not path or path == '.':
            return self
        if path[0] == '/':
            try:
                return Directory(self.parent).get(path)
            except errors.Not_Found_Error:
                while path.startswith('/') or path.startswith('./'):
                    if path.startswith('/'):
                        path = path[1:]  # 1 = len('/')
                    else:
                        path = path[2:]  # 2 = len('./')
                if not path or path == '.':
                    return self
                p = path.split('/')[0]
                if p != self.name:
                    raise FileNotFoundError(p + ': No such file or directory')
                path = path[len(p):]
                if not path:
                    return self
        while path.startswith('/') or path.startswith('./'):
            if path.startswith('/'):
                path = path[1:]  # 1 = len('/')
            else:
                path = path[2:]  # 2 = len('./')
        if not path or path == '.':
            return self
        p = path.split('/')[0]
        if p == '..':
            path = path[2:]  # 2 = len('..')
            while path.startswith('/'):
                path = path[1:]  # 1 = len('/')
            try:
                return Directory(self.parent).get(path)
            except errors.Not_Found_Error:
                raise FileNotFoundError(p + ': No such file or directory')
        for c in self.children:
            if p == c['name']:
                path = path[len(p):]
                while path.startswith('/'):
                    path = path[1:]  # 1 = len('/')
                if path:
                    return Directory(c['id']).get(path)
                else:
                    try:
                        return Directory(c['id'])
                    except errors.Not_Found_Error:
                        return File(c['id'])
        raise FileNotFoundError(p + ': No such file or directory')

    def list(self):
        """
        List the contents of this directory.

        :returns: a tuple containing a list of directories and a list of files
        """
        dirs = list()
        files = list()
        for c in self.children:
            if 'd' == c['type']:
                dirs.append(Directory(c['id']))
            else:
                files.append(File(c['id']))
        return (dirs, files)

    def upload_file(self, file_path):
        """
        Upload a new file contained within this directory.

        **Note:** This method returns the updated instance of this directory
        (because it has a new child). The recommended usage is:

        .. code-block:: python

            home = home.upload_file('/path/on/local/computer/to/read/data')

        Use :meth:`Directory.get` to get the new file.

        :param file_path: the path to the file to be uploaded on your computer
        :type file_path: string
        :returns: the updated instance of this directory
        """
        file_path = os.path.expanduser(file_path)
        data = {
            'name': file_path.split('/')[-1],
            'parent': self.id,
            'size': os.path.getsize(file_path)
        }
        response_data = self.POST('file/', data)
        response_data2 = self.PUT_DATA(
            'data/%d/?vid=%d' % (
                response_data['id'],
                response_data['active_version']
            ),
            file_path
        )
        return Directory(self.id)

    def upload_directory(
        self,
        directory_path,
        follow_symlinks=False,
        synchronize=True,
    ):
        """
        Upload a new directory contained within this directory. It generates a
        log file in the `directory_path` containing 

        **Note:** This method returns the updated instance of this directory
        (because it has a new child). The recommended usage is:

        .. code-block:: python

            home = home.upload_directory('/path/on/local/computer/to/read/data')

        Use :meth:`Directory.get` to get the new directory.

        :param directory_path: the path to the directory to be uploaded on your
            computer
        :type directory_path: string
        :param follow_symlinks: whether to follow symlinks (default False)
        :type follow_symlinks: bool
        :param synchronize: Whether to perform a synchronization or skip
            previous work (default True). If synchronization is on, the work
            completed in the most recent log file will be taken into account. If
            synchronization is off, this upload will begin at the last
            successful operation in the most recent log file (if one exists)
            without synchronizing the directories and files that were previously
            uploaded and logged.
        :type synchronize: bool
        :returns: the updated instance of this directory
        """
        directory_path = os.path.expanduser(directory_path)
        if not os.path.isdir(directory_path):
            print('Failure: %s is not a directory.' % directory_path)
            exit()

        log_path = '%s/craedl-upload-%s.log' % (
            directory_path,
            datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        )

        ls = glob.glob(directory_path + '/*')
        history_path = None
        history_file = None
        for item in sorted(ls):
            if 'craedl-upload' in item and 'log' in item:
                history_path = item

        if history_path:
            history_file = open(history_path, 'r')
            write_to_log(log_path, 'OLDLOG READ %s\n' % history_path)
            write_to_log(log_path, 'OLDLOG DONE\n')

        history = None
        file_path = None # for synchronization false
        if history_file:
            (history, timestamp) = read_from_log(history_file)
        if history_file and 'OLDLOG READ' in history:
            (history, timestamp) = read_from_log(history_file)

        if history_path and not synchronize:
            # copy all work from previous log into current log
            history_next = history
            while history_next:
                history = history_next
                out = history.replace('INIT', 'SKIP')
                write_to_log(log_path, out)
                out = history.replace(
                    'INIT', 'DONE'
                ).replace(
                    'SYML', 'DONE'
                ).replace(
                    'SKIP', 'DONE'
                )[:11] + '\n'
                write_to_log(log_path, out)
                (history_next, timestamp) = read_from_log(history_file)
            # get the right starting directory
            file_path = os.path.basename(history[12:].rstrip())
            base_path = directory_path
            directory_path = os.path.dirname(history[12:].rstrip())
            if file_path == directory_path:
                file_path = None
            else:
                file_path = directory_path + '/' + file_path
            new_dir = self.get(os.path.basename(base_path))
        else:
            action = 'CREATE INIT %s/\n' % directory_path
            action_skip = 'CREATE SKIP %s/\n' % directory_path
            if history and (
                history == action or history == action_skip
            ):
                write_to_log(log_path, action_skip)
            else:
                write_to_log(log_path, action)
                self = self.create_directory(os.path.basename(directory_path))
            new_dir = self.get(os.path.basename(directory_path))
            if type(new_dir) == File:
                # handle case where a directory replaced a file of the same name
                new_dir = get_numbered_upload(
                    self,
                    os.path.basename(directory_path)
                )
            write_to_log(log_path, 'CREATE DONE\n')

        new_dir.upload_directory_recurse(
            directory_path,
            log_path,
            history_file,
            0,
            follow_symlinks,
            file_path
        )
        return Directory(self.id)

    def upload_directory_recurse(
        self,
        directory_path,
        log_path,
        history_file,
        size,
        follow_symlinks,
        synchronize_start=None
    ):
        """
        A helper function for directory uploads that performs the recursion
        through child directories and reports size transferred.

        :param directory_path: the path to the directory to be uploaded on your
            computer
        :type directory_path: string
        :param log_path: the absolute path to the upload log file
        :type log_path: string
        :param history_file: the (open) historical log file, or None if does not
            exist
        :type history_file: File
        :param size: the total size uploaded from the entry to the recursion
        :type size: int
        :param follow_symlinks: whether to follow symlinks
        :type follow_symlinks: bool
        :param synchronize: the path to the file on which to begin
        :type synchronize: string
        """
        synchronize_start_file = synchronize_start
        this_size = 0
        history = None
        if history_file:
            (history, timestamp) = read_from_log(history_file)

        for child in sorted(os.scandir(directory_path), key=lambda d: d.path):
            # ignore files in log that no longer exist on the file system
            if history:
                history_path = history[12:]
                while (child.path > history_path and
                    os.path.dirname(directory_path) in os.path.dirname(history_path)
                ):
                    (history, timestamp) = read_from_log(history_file)
                    if history:
                        history_path = history[12:]
                    else:
                        break

            # don't upload craedl-upload logs
            if 'craedl-upload' not in child.path and 'log' not in child.path:

                if (synchronize_start_file
                    and child.path <= synchronize_start_file
                ):
                    if child.path == synchronize_start_file:
                        # no synchronize to worry about anymore
                        synchronize_start_file = None

                elif not follow_symlinks and child.is_symlink():
                    # skip this symlink if ignoring symlinks
                    write_to_log(log_path, 'IGNORE SYML %s\n' % child.path)
                    write_to_log(log_path, 'IGNORE DONE\n')
                    continue

                elif child.is_file():
                    # upload file
                    action1 = 'UPLOAD INIT %s\n' % child.path
                    action2 = 'UPDATE INIT %s\n' % child.path
                    action_skip1 = 'UPLOAD SKIP %s\n' % child.path
                    action_skip2 = 'UPDATE SKIP %s\n' % child.path
                    new_version = False
                    if history and child.stat().st_mtime > (
                        (timestamp - datetime(1970,1,1,tzinfo=timezone.utc)
                        ).total_seconds()
                    ):
                        new_version = True
                    if new_version:
                        write_to_log(log_path, action2)
                        try:
                            self.upload_file(child.path)
                            new_size = os.path.getsize(child.path)
                            this_size = this_size + new_size
                            write_to_log(log_path, 'UPDATE DONE %s (%s)\n' % (
                                to_x_bytes(new_size),
                                to_x_bytes(size + this_size)
                            ))
                        except errors.Parse_Error:
                            write_to_log(log_path, 'UPLOAD FORB %s\n' % child.path)
                    elif history and (
                        history == action1 or history == action_skip1
                    ):
                        write_to_log(log_path, action_skip1)
                        (history, timestamp) = read_from_log(history_file)
                        write_to_log(log_path, 'UPLOAD DONE %s (%s)\n' % (
                            to_x_bytes(0),
                            to_x_bytes(size + this_size)
                        ))
                    elif history and (
                        history == action2 or history == action_skip2
                    ):
                        write_to_log(log_path, action_skip2)
                        (history, timestamp) = read_from_log(history_file)
                        write_to_log(log_path, 'UPDATE DONE %s (%s)\n' % (
                            to_x_bytes(0),
                            to_x_bytes(size + this_size)
                        ))
                    else:
                        write_to_log(log_path, action1)
                        try:
                            self.upload_file(child.path)
                            new_size = os.path.getsize(child.path)
                            this_size = this_size + new_size
                            write_to_log(log_path, 'UPLOAD DONE %s (%s)\n' % (
                                to_x_bytes(new_size),
                                to_x_bytes(size + this_size)
                            ))
                        except errors.Parse_Error:
                            write_to_log(log_path, 'UPLOAD FORB %s\n' % child.path)

                else:
                    # create directory and recurse
                    action = 'CREATE INIT %s/\n' % child.path
                    action_skip = 'CREATE SKIP %s/\n' % child.path
                    if history and (
                        history == action or history == action_skip
                    ):
                        write_to_log(log_path, action_skip)
                    else:
                        write_to_log(log_path, action)
                        self = self.create_directory(os.path.basename(child.path))
                    new_dir = self.get(os.path.basename(child.path))
                    if type(new_dir) == File:
                        # handle case where a directory replaced a file of the
                        # same name
                        new_dir = get_numbered_upload(
                            self,
                            os.path.basename(child.path)
                        )
                    write_to_log(log_path, 'CREATE DONE\n')

                    # recurse into this directory
                    (r_size, history) = new_dir.upload_directory_recurse(
                        child.path,
                        log_path,
                        history_file,
                        size + this_size,
                        follow_symlinks
                    )
                    this_size = this_size + r_size

        return (this_size, history)

class File(Auth):
    """
    A Craedl file object.
    """

    def __init__(self, id):
        super().__init__()
        data = self.GET('file/' + str(id) + '/')
        for k, v in data.items():
            if k == 'versions':
                v.reverse() # list versions in chronological order
            setattr(self, k, v)

    def download(self, save_path, version_index=None):
        """
        Download the data associated with this file. This returns the active
        version by default.

        :param save_path: the path to the directory on your computer that will
            contain this file's data
        :type save_path: string
        :param version_index: the (optional) index of the version to be
            downloaded
        :type version_index: int
        :returns: this file
        """
        save_path = os.path.expanduser(save_path)
        if version_index is None:
            data = self.GET_DATA('data/' + str(self.id) + '/')
        else:
            data = self.GET_DATA('data/%d/?vid=%d' % (
                self.id, self.versions[version_index]['id']
            ))
        try:
            f = open(save_path, 'wb')
        except IsADirectoryError:
            f = open(save_path + '/' + self.name, 'wb')
        for chunk in data.iter_content():
            # because we are using iter_content and GET_DATA uses stream=True
            # in the request, the data is not read into memory but written
            # directly from the stream here
            f.write(chunk)
        f.close()
        return self

class Profile(Auth):
    """
    A Craedl profile object.
    """

    def __init__(self, data=None, id=None):
        super().__init__()
        if not data and not id:
            data = self.GET('profile/whoami/')
        elif not data:
            data = self.GET('profile/' + str(id) + '/')
        for k, v in data.items():
            setattr(self, k, v)

    def create_project(self, name):
        """
        Create a new project belonging to this profile.

        Use :meth:`Profile.get_project` to get the new project.

        :param name: the name of the new project
        :type name: string
        :returns: this profile
        """
        data = {
            'name': name,
            'research_group': '',
        }
        response_data = self.POST('project/', data)
        return self

    def get_project(self, name):
        """
        Get a particular project that belongs to this profile.

        :param name: the name of the project
        :type name: string
        :returns: a project
        """
        projects = self.get_projects()
        for project in projects:
            if project.name == name:
                return project
        raise errors.Not_Found_Error

    def get_projects(self):
        """
        Get a list of projects that belong to this profile.

        :returns: a list of projects
        """
        data = self.GET('profile/' + str(self.id) + '/projects/')
        projects = list()
        for project in data:
            projects.append(Project(project['id']))
        return projects

    def get_publications(self):
        """
        Get a list of publications that belongs to this profile.

        :returns: a list of publications
        """
        data = self.GET('profile/' + str(self.id) + '/publications/')
        publications = list()
        for publication in data:
            publications.append(Publication(publication))
        return publications

    def get_research_group(self, slug):
        """
        Get a particular research group.

        :param slug: the unique slug in this research group's URL
        :type slug: string
        :returns: a research group
        """
        return Research_Group(slug)

    def get_research_groups(self):
        """
        Get a list of research groups that this profile belongs to.

        :returns: a list of research groups
        """
        data = self.GET('research_group/')
        research_groups = list()
        for research_group in data:
            research_groups.append(Research_Group(research_group['slug']))
        return research_groups

class Project(Auth):
    """
    A Craedl project object.
    """

    def __init__(self, id):
        super().__init__()
        data = self.GET('project/' + str(id) + '/')
        for k, v in data.items():
            if not (type(v) is dict or type(v) is list):
                if not v == None:
                    setattr(self, k, v)

    def get_data(self):
        """
        Get the data attached to this project. It always begins at the home
        directory.

        :returns: this project's home directory
        """
        d = Directory(self.root)
        return d

    def get_publications(self):
        """
        Get a list of publications attached to this project.

        :returns: a list of this project's publications
        """
        data = self.GET('project/' + str(self.id) + '/publications/')
        publications = list()
        for publication in data:
            publications.append(Publication(publication))
        return publications

class Publication(Auth):
    """
    A Craedl publication object.
    """

    authors = list()

    def __init__(self, data=None, id=None):
        self.authors = list()
        super().__init__()
        if not data:
            data = self.GET('publication/' + str(id) + '/')
        for k, v in data.items():
            if k == 'authors':
                for author in v:
                    self.authors.append(Profile(author))
            else:
                if not v == None:
                    setattr(self, k, v)

class Research_Group(Auth):
    """
    A Craedl research group object.
    """

    def __init__(self, id):
        super().__init__()
        data = self.GET('research_group/' + str(id) + '/')
        for k, v in data.items():
            if not (type(v) is dict or type(v) is list):
                if not v == None:
                    setattr(self, k, v)

    def create_project(self, name):
        """
        Create a new project belonging to this research group.

        Use :meth:`Research_Group.get_project` to get the new project.

        :param name: the name of the new project
        :type name: string
        :returns: this research group
        """
        data = {
            'name': name,
            'research_group': self.pk,
        }
        response_data = self.POST('project/', data)
        return self

    def get_project(self, name):
        """
        Get a particular project that belongs to this research group.

        :param name: the name of the project
        :type name: string
        :returns: a project
        """
        projects = self.get_projects()
        for project in projects:
            if project.name == name:
                return project
        raise errors.Not_Found_Error

    def get_projects(self):
        """
        Get a list of projects that belong to this research group.

        :returns: a list of projects
        """
        data = self.GET('research_group/' + self.slug + '/projects/')
        projects = list()
        for project in data:
            projects.append(Project(project['id']))
        return projects

    def get_publications(self):
        """
        Get a list of publications that belong to this research group.

        :returns: a list of publications
        """
        data = self.GET('research_group/' + self.slug + '/publications/')
        publications = list()
        for publication in data:
            publications.append(Publication(publication))
        return publications
