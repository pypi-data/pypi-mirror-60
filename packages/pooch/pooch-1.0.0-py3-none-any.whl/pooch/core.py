"""
The main Pooch class and a factory function for it.
"""
import contextlib
import os
from pathlib import Path
import shutil
import tempfile
import ftplib

import requests
from .utils import file_hash, check_version, parse_url, get_logger
from .downloaders import HTTPDownloader, FTPDownloader

KNOWN_DOWNLOADERS = {
    "ftp": FTPDownloader,
    "https": HTTPDownloader,
    "http": HTTPDownloader,
}


def create(
    path,
    base_url,
    version=None,
    version_dev="master",
    env=None,
    registry=None,
    urls=None,
):
    """
    Create a :class:`~pooch.Pooch` with sensible defaults to fetch data files.

    If a version string is given, the Pooch will be versioned, meaning that the
    local storage folder and the base URL depend on the project version. This
    is necessary if your users have multiple versions of your library installed
    (using virtual environments) and you updated the data files between
    versions. Otherwise, every time a user switches environments would trigger
    a re-download of the data. The version string will be appended to the local
    storage path (for example, ``~/.mypooch/cache/v0.1``) and inserted into the
    base URL (for example,
    ``https://github.com/fatiando/pooch/raw/v0.1/data``). If the version string
    contains ``+XX.XXXXX``, it will be interpreted as a development version.

    Parameters
    ----------
    path : str, PathLike, list or tuple
        The path to the local data storage folder. If this is a list or tuple,
        we'll join the parts with the appropriate separator. The *version* will
        be appended to the end of this path. Use :func:`pooch.os_cache` for a
        sensible default.
    base_url : str
        Base URL for the remote data source. All requests will be made relative
        to this URL. The string should have a ``{version}`` formatting mark in
        it. We will call ``.format(version=version)`` on this string. If the
        URL is a directory path, it must end in a ``'/'`` because we will not
        include it.
    version : str or None
        The version string for your project. Should be PEP440 compatible. If
        None is given, will not attempt to format *base_url* and no subfolder
        will be appended to *path*.
    version_dev : str
        The name used for the development version of a project. If your data is
        hosted on Github (and *base_url* is a Github raw link), then
        ``"master"`` is a good choice (default). Ignored if *version* is None.
    env : str or None
        An environment variable that can be used to overwrite *path*. This
        allows users to control where they want the data to be stored. We'll
        append *version* to the end of this value as well.
    registry : dict or None
        A record of the files that are managed by this Pooch. Keys should be
        the file names and the values should be their SHA256 hashes. Only files
        in the registry can be fetched from the local storage. Files in
        subdirectories of *path* **must use Unix-style separators** (``'/'``)
        even on Windows.
    urls : dict or None
        Custom URLs for downloading individual files in the registry. A
        dictionary with the file names as keys and the custom URLs as values.
        Not all files in *registry* need an entry in *urls*. If a file has an
        entry in *urls*, the *base_url* will be ignored when downloading it in
        favor of ``urls[fname]``.

    Returns
    -------
    pooch : :class:`~pooch.Pooch`
        The :class:`~pooch.Pooch` initialized with the given arguments.

    Examples
    --------

    Create a :class:`~pooch.Pooch` for a release (v0.1):

    >>> pup = create(path="myproject",
    ...              base_url="http://some.link.com/{version}/",
    ...              version="v0.1",
    ...              registry={"data.txt": "9081wo2eb2gc0u..."})
    >>> print(pup.path.parts)  # The path is a pathlib.Path
    ('myproject', 'v0.1')
    >>> print(pup.base_url)
    http://some.link.com/v0.1/
    >>> print(pup.registry)
    {'data.txt': '9081wo2eb2gc0u...'}
    >>> print(pup.registry_files)
    ['data.txt']

    If this is a development version (12 commits ahead of v0.1), then the
    ``version_dev`` will be used (defaults to ``"master"``):

    >>> pup = create(path="myproject",
    ...              base_url="http://some.link.com/{version}/",
    ...              version="v0.1+12.do9iwd")
    >>> print(pup.path.parts)
    ('myproject', 'master')
    >>> print(pup.base_url)
    http://some.link.com/master/

    Versioning is optional (but highly encouraged):

    >>> pup = create(path="myproject",
    ...              base_url="http://some.link.com/",
    ...              registry={"data.txt": "9081wo2eb2gc0u..."})
    >>> print(pup.path.parts)  # The path is a pathlib.Path
    ('myproject',)
    >>> print(pup.base_url)
    http://some.link.com/

    To place the storage folder at a subdirectory, pass in a list and we'll
    join the path for you using the appropriate separator for your operating
    system:

    >>> pup = create(path=["myproject", "cache", "data"],
    ...              base_url="http://some.link.com/{version}/",
    ...              version="v0.1")
    >>> print(pup.path.parts)
    ('myproject', 'cache', 'data', 'v0.1')

    The user can overwrite the storage path by setting an environment variable:

    >>> # The variable is not set so we'll use *path*
    >>> pup = create(path=["myproject", "not_from_env"],
    ...              base_url="http://some.link.com/{version}/",
    ...              version="v0.1",
    ...              env="MYPROJECT_DATA_DIR")
    >>> print(pup.path.parts)
    ('myproject', 'not_from_env', 'v0.1')
    >>> # Set the environment variable and try again
    >>> import os
    >>> os.environ["MYPROJECT_DATA_DIR"] = os.path.join("myproject", "env")
    >>> pup = create(path=["myproject", "not_env"],
    ...              base_url="http://some.link.com/{version}/",
    ...              version="v0.1",
    ...              env="MYPROJECT_DATA_DIR")
    >>> print(pup.path.parts)
    ('myproject', 'env', 'v0.1')

    """
    if isinstance(path, (list, tuple)):
        path = os.path.join(*path)
    if env is not None and env in os.environ and os.environ[env]:
        path = os.environ[env]
    if version is not None:
        version = check_version(version, fallback=version_dev)
        path = os.path.join(str(path), version)
        base_url = base_url.format(version=version)
    path = os.path.expanduser(str(path))
    # Check that the data directory is writable
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            tempfile.NamedTemporaryFile(dir=path)
    except PermissionError:
        message = (
            "Cannot write to data cache '%s'. "
            "Will not be able to download remote data files. "
        )
        args = [path]
        if env is not None:
            message += "Use environment variable '%s' to specify another directory."
            args += [env]

        get_logger().warning(message, *args)
    pup = Pooch(path=Path(path), base_url=base_url, registry=registry, urls=urls)
    return pup


class Pooch:
    """
    Manager for a local data storage that can fetch from a remote source.

    Avoid creating ``Pooch`` instances directly. Use :func:`pooch.create`
    instead.

    Parameters
    ----------
    path : str
        The path to the local data storage folder. The path must exist in the
        file system.
    base_url : str
        Base URL for the remote data source. All requests will be made relative
        to this URL.
    registry : dict or None
        A record of the files that are managed by this good boy. Keys should be
        the file names and the values should be their SHA256 hashes. Only files
        in the registry can be fetched from the local storage. Files in
        subdirectories of *path* **must use Unix-style separators** (``'/'``)
        even on Windows.
    urls : dict or None
        Custom URLs for downloading individual files in the registry. A
        dictionary with the file names as keys and the custom URLs as values.
        Not all files in *registry* need an entry in *urls*. If a file has an
        entry in *urls*, the *base_url* will be ignored when downloading it in
        favor of ``urls[fname]``.

    """

    def __init__(self, path, base_url, registry=None, urls=None):
        self.path = path
        self.base_url = base_url
        if registry is None:
            registry = dict()
        self.registry = dict(registry)
        if urls is None:
            urls = dict()
        self.urls = dict(urls)

    @property
    def abspath(self):
        "Absolute path to the local storage"
        return Path(os.path.abspath(os.path.expanduser(str(self.path))))

    @property
    def registry_files(self):
        "List of file names on the registry"
        return list(self.registry)

    def fetch(self, fname, processor=None, downloader=None):
        """
        Get the absolute path to a file in the local storage.

        If it's not in the local storage, it will be downloaded. If the hash of
        the file in local storage doesn't match the one in the registry, will
        download a new copy of the file. This is considered a sign that the
        file was updated in the remote storage. If the hash of the downloaded
        file still doesn't match the one in the registry, will raise an
        exception to warn of possible file corruption.

        Post-processing actions sometimes need to be taken on downloaded files
        (unzipping, conversion to a more efficient format, etc). If these
        actions are time or memory consuming, it would be best to do this only
        once when the file is actually downloaded. Use the *processor* argument
        to specify a function that is executed after the downloaded (if
        required) to perform these actions. See below.

        Custom file downloaders can be provided through the *downloader*
        argument. By default, files are downloaded over HTTP. If the server for
        a given file requires authentication (username and password) or if the
        file is served over FTP, use custom downloaders that support these
        features. Downloaders can also be used to print custom messages (like a
        progress bar), etc. See below for details.

        Parameters
        ----------
        fname : str
            The file name (relative to the *base_url* of the remote data
            storage) to fetch from the local storage.
        processor : None or callable
            If not None, then a function (or callable object) that will be
            called before returning the full path and after the file has been
            downloaded (if required). See below for details.
        downloader : None or callable
            If not None, then a function (or callable object) that will be
            called to download a given URL to a provided local file name. By
            default, downloads are done through HTTP without authentication
            using :class:`pooch.HTTPDownloader`. See below for details.

        Returns
        -------
        full_path : str
            The absolute path (including the file name) of the file in the
            local storage.

        Notes
        -----

        **Processor** functions should have the following format:

        .. code:: python

            def myprocessor(fname, action, pooch):
                '''
                Processes the downloaded file and returns a new file name.

                The function **must** take as arguments (in order):

                fname : str
                    The full path of the file in the local data storage
                action : str
                    Either: "download" (file doesn't exist and will be
                    downloaded), "update" (file is outdated and will be
                    downloaded), or "fetch" (file exists and is updated so no
                    download is necessary).
                pooch : pooch.Pooch
                    The instance of the Pooch class that is calling this
                    function.

                The return value can be anything but is usually a full path to
                a file (or list of files). This is what will be returned by
                *fetch* in place of the original file path.
                '''
                ...
                return full_path

        **Downloader** functions should have the following format:

        .. code:: python

            def mydownloader(url, output_file, pooch):
                '''
                Download a file from the given URL to the given local file.

                The function **must** take as arguments (in order):

                url : str
                    The URL to the file you want to download.
                output_file : str or file-like object
                    Path (and file name) to which the file will be downloaded.
                pooch : pooch.Pooch
                    The instance of the Pooch class that is calling this
                    function.

                No return value is required.
                '''
                ...

        **Authentication** through HTTP can be handled by
        :class:`pooch.HTTPDownloader`:

        .. code:: python

            authdownload = HTTPDownloader(auth=(username, password))
            mypooch.fetch("some-data-file.txt", downloader=authdownload)

        **Progress bar** for the download can be printed by
        :class:`pooch.HTTPDownloader` by passing the argument
        ``progressbar=True``:

        .. code:: python

            progress_download = HTTPDownloader(progressbar=True)
            mypooch.fetch("some-data-file.txt", downloader=progress_download)
            # Will print a progress bar to standard error like:
            # 100%|█████████████████████████████████████████| 336/336 [...]

        """
        self._assert_file_in_registry(fname)

        # Create the local data directory if it doesn't already exist
        if not self.abspath.exists():
            os.makedirs(str(self.abspath))

        full_path = self.abspath / fname
        url = self.get_url(fname)
        in_storage = full_path.exists()
        if not in_storage:
            action = "download"
        elif in_storage and file_hash(str(full_path)) != self.registry[fname]:
            action = "update"
        else:
            action = "fetch"

        if action in ("download", "update"):
            action_word = dict(download="Downloading", update="Updating")
            get_logger().info(
                "%s data file '%s' from remote data store '%s' to '%s'.",
                action_word[action],
                fname,
                self.get_url(fname),
                str(self.path),
            )

            parsed_url = parse_url(url)
            if parsed_url["protocol"] not in KNOWN_DOWNLOADERS:
                raise ValueError(
                    "Unrecognized URL protocol '{}' in '{}'. Must be one of {}.".format(
                        parsed_url["protocol"], url, KNOWN_DOWNLOADERS.keys()
                    )
                )

            if downloader is None:
                downloader = KNOWN_DOWNLOADERS[parsed_url["protocol"]]()
            # Stream the file to a temporary so that we can safely check its
            # hash before overwriting the original
            tmp = tempfile.NamedTemporaryFile(delete=False, dir=str(self.abspath))
            # Close the temp file so that the downloader can decide how to
            # opened it
            tmp.close()
            try:
                downloader(url, tmp.name, self)
                self._check_download_hash(fname, tmp.name)
                # Ensure the parent directory exists in case the file is in a
                # subdirectory. Otherwise, move will cause an error.
                if not os.path.exists(str(full_path.parent)):
                    os.makedirs(str(full_path.parent))
                shutil.move(tmp.name, str(full_path))
            finally:
                if os.path.exists(tmp.name):
                    os.remove(tmp.name)

        if processor is not None:
            return processor(str(full_path), action, self)

        return str(full_path)

    def _assert_file_in_registry(self, fname):
        """
        Check if a file is in the registry and raise :class:`ValueError` if
        it's not.
        """
        if fname not in self.registry:
            raise ValueError("File '{}' is not in the registry.".format(fname))

    def get_url(self, fname):
        """
        Get the full URL to download a file in the registry.

        Parameters
        ----------
        fname : str
            The file name (relative to the *base_url* of the remote data
            storage) to fetch from the local storage.

        """
        self._assert_file_in_registry(fname)
        return self.urls.get(fname, "".join([self.base_url, fname]))

    def _check_download_hash(self, fname, downloaded):
        """
        Check the hash of the downloaded file against the one in the registry.

        Parameters
        ----------
        fname : str
            The file name in the registry.
        downloaded : str
            The pull path to the downloaded file.

        Raises
        ------
        :class:`ValueError`
            If the hashes don't match.

        """
        tmphash = file_hash(downloaded)
        if tmphash != self.registry[fname]:
            raise ValueError(
                "Hash of downloaded file '{}' doesn't match the entry in the registry."
                " Expected '{}' and got '{}'.".format(
                    fname, self.registry[fname], tmphash
                )
            )

    def load_registry(self, fname):
        """
        Load entries from a file and add them to the registry.

        Use this if you are managing many files.

        Each line of the file should have file name and its SHA256 hash
        separate by a space. Only one file per line is allowed. Custom download
        URLs for individual files can be specified as a third element on the
        line.

        Parameters
        ----------
        fname : str | fileobj
            Path (or open file object) to the registry file.

        """
        with contextlib.ExitStack() as stack:
            if hasattr(fname, "read"):
                # It's a file object
                fin = fname
            else:
                # It's a file path
                fin = stack.enter_context(open(fname))

            for linenum, line in enumerate(fin):
                if isinstance(line, bytes):
                    line = line.decode("utf-8")

                elements = line.strip().split()
                if not len(elements) in [0, 2, 3]:
                    raise OSError(
                        "Invalid entry in Pooch registry file '{}': "
                        "expected 2 or 3 elements in line {} but got {}. "
                        "Offending entry: '{}'".format(
                            fname, linenum + 1, len(elements), line
                        )
                    )
                if elements:
                    file_name = elements[0]
                    file_sha256 = elements[1]
                    if len(elements) == 3:
                        file_url = elements[2]
                        self.urls[file_name] = file_url
                    self.registry[file_name] = file_sha256

    def is_available(self, fname):
        """
        Check availability of a remote file without downloading it.

        Use this method when working with large files to check if they are
        available for download.

        Parameters
        ----------
        fname : str
            The file name (relative to the *base_url* of the remote data
            storage) to fetch from the local storage.

        Returns
        -------
        status : bool
            True if the file is available for download. False otherwise.

        """
        self._assert_file_in_registry(fname)
        source = self.get_url(fname)
        parsed_url = parse_url(source)
        if parsed_url["protocol"] == "ftp":
            directory = os.path.dirname(parsed_url["path"])
            ftp = ftplib.FTP()
            ftp.connect(host=parsed_url["netloc"])
            try:
                ftp.login()
                available = parsed_url["path"] in ftp.nlst(directory)
            finally:
                ftp.close()
        else:
            response = requests.head(source, allow_redirects=True)
            available = bool(response.status_code == 200)
        return available
