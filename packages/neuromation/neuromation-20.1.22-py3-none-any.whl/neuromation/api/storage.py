import asyncio
import datetime
import enum
import errno
import fnmatch
import os
import re
import time
from dataclasses import dataclass
from email.utils import parsedate
from pathlib import Path
from stat import S_ISREG
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
)

import aiohttp
import attr
from yarl import URL

from .abc import (
    AbstractFileProgress,
    AbstractRecursiveFileProgress,
    StorageProgressComplete,
    StorageProgressEnterDir,
    StorageProgressFail,
    StorageProgressLeaveDir,
    StorageProgressStart,
    StorageProgressStep,
)
from .config import Config
from .core import ResourceNotFound, _Core
from .url_utils import (
    _extract_path,
    normalize_local_path_uri,
    normalize_storage_path_uri,
)
from .users import Action
from .utils import NoPublicConstructor, retries


MAX_OPEN_FILES = 20
READ_SIZE = 2 ** 20  # 1 MiB
TIME_THRESHOLD = 1.0

Printer = Callable[[str], None]
ProgressQueueItem = Optional[Tuple[Callable[[Any], None], Any]]


class FileStatusType(str, enum.Enum):
    DIRECTORY = "DIRECTORY"
    FILE = "FILE"


@dataclass(frozen=True)
class FileStatus:
    path: str
    size: int
    type: FileStatusType
    modification_time: int
    permission: Action

    def is_file(self) -> bool:
        return self.type == FileStatusType.FILE

    def is_dir(self) -> bool:
        return self.type == FileStatusType.DIRECTORY

    @property
    def name(self) -> str:
        return Path(self.path).name


class Storage(metaclass=NoPublicConstructor):
    def __init__(self, core: _Core, config: Config) -> None:
        self._core = core
        self._config = config
        self._file_sem = asyncio.BoundedSemaphore(MAX_OPEN_FILES)
        self._min_time_diff = 0.0
        self._max_time_diff = 0.0

    def _uri_to_path(self, uri: URL) -> str:
        uri = normalize_storage_path_uri(uri, self._config.username)
        prefix = uri.host + "/" if uri.host else ""
        return prefix + uri.path.lstrip("/")

    def _set_time_diff(self, request_time: float, resp: aiohttp.ClientResponse) -> None:
        response_time = time.time()
        server_timetuple = parsedate(resp.headers.get("Date"))
        if not server_timetuple:
            return
        server_time = datetime.datetime(
            *server_timetuple[:6], tzinfo=datetime.timezone.utc
        ).timestamp()
        # Remove 1 because server time has been truncated
        # and can be up to 1 second less than the actulal value
        self._min_time_diff = request_time - server_time - 1.0
        self._max_time_diff = response_time - server_time

    def _is_local_modified(self, local: os.stat_result, remote: FileStatus) -> bool:
        return (
            local.st_size != remote.size
            or local.st_mtime - remote.modification_time
            > self._min_time_diff - TIME_THRESHOLD
        )

    def _is_remote_modified(self, local: os.stat_result, remote: FileStatus) -> bool:
        # Add 1 because remote.modification_time has been truncated
        # and can be up to 1 second less than the actulal value
        return (
            local.st_size != remote.size
            or local.st_mtime - remote.modification_time
            < self._max_time_diff + TIME_THRESHOLD + 1.0
        )

    async def ls(self, uri: URL) -> List[FileStatus]:
        url = self._config.storage_url / self._uri_to_path(uri)
        url = url.with_query(op="LISTSTATUS")

        request_time = time.time()
        auth = await self._config._api_auth()
        async with self._core.request("GET", url, auth=auth) as resp:
            self._set_time_diff(request_time, resp)
            res = await resp.json()
            return [
                _file_status_from_api(status)
                for status in res["FileStatuses"]["FileStatus"]
            ]

    async def glob(self, uri: URL, *, dironly: bool = False) -> AsyncIterator[URL]:
        if not _has_magic(uri.path):
            yield uri
            return
        basename = uri.name
        glob_in_dir: Callable[[URL, str, bool], AsyncIterator[URL]]
        if not _has_magic(basename):
            glob_in_dir = self._glob0
        elif not _isrecursive(basename):
            glob_in_dir = self._glob1
        else:
            glob_in_dir = self._glob2
        async for parent in self.glob(uri.parent, dironly=True):
            async for x in glob_in_dir(parent, basename, dironly):
                yield x

    async def _glob2(
        self, parent: URL, pattern: str, dironly: bool
    ) -> AsyncIterator[URL]:
        assert _isrecursive(pattern)
        yield parent
        async for x in self._rlistdir(parent, dironly):
            yield x

    async def _glob1(
        self, parent: URL, pattern: str, dironly: bool
    ) -> AsyncIterator[URL]:
        allow_hidden = _ishidden(pattern)
        match = re.compile(fnmatch.translate(pattern)).fullmatch
        async for stat in self._iterdir(parent, dironly):
            name = stat.path
            if (allow_hidden or not _ishidden(name)) and match(name):
                yield parent / name

    async def _glob0(
        self, parent: URL, basename: str, dironly: bool
    ) -> AsyncIterator[URL]:
        uri = parent / basename
        try:
            await self.stat(uri)
        except ResourceNotFound:
            return
        yield uri

    async def _iterdir(self, uri: URL, dironly: bool) -> AsyncIterator[FileStatus]:
        for stat in await self.ls(uri):
            if not dironly or stat.is_dir():
                yield stat

    async def _rlistdir(self, uri: URL, dironly: bool) -> AsyncIterator[URL]:
        async for stat in self._iterdir(uri, dironly):
            name = stat.path
            if not _ishidden(name):
                x = uri / name
                yield x
                if stat.is_dir():
                    async for y in self._rlistdir(x, dironly):
                        yield y

    async def mkdir(
        self, uri: URL, *, parents: bool = False, exist_ok: bool = False
    ) -> None:
        if not exist_ok:
            try:
                await self.stat(uri)
            except ResourceNotFound:
                pass
            else:
                raise FileExistsError(errno.EEXIST, "File exists", str(uri))

        if not parents:
            parent = uri
            while not parent.name and parent != parent.parent:
                parent = parent.parent
            parent = parent.parent
            if parent != parent.parent:
                try:
                    await self.stat(parent)
                except ResourceNotFound:
                    raise FileNotFoundError(
                        errno.ENOENT, "No such directory", str(parent)
                    )

        url = self._config.storage_url / self._uri_to_path(uri)
        url = url.with_query(op="MKDIRS")
        auth = await self._config._api_auth()

        async with self._core.request("PUT", url, auth=auth) as resp:
            resp  # resp.status == 201

    async def create(self, uri: URL, data: AsyncIterator[bytes]) -> None:
        path = self._uri_to_path(uri)
        assert path, "Creation in root is not allowed"
        url = self._config.storage_url / path
        url = url.with_query(op="CREATE")
        timeout = attr.evolve(self._core.timeout, sock_read=None)
        auth = await self._config._api_auth()

        async with self._core.request(
            "PUT", url, data=data, timeout=timeout, auth=auth
        ) as resp:
            resp  # resp.status == 201

    async def stat(self, uri: URL) -> FileStatus:
        url = self._config.storage_url / self._uri_to_path(uri)
        url = url.with_query(op="GETFILESTATUS")
        auth = await self._config._api_auth()

        request_time = time.time()
        async with self._core.request("GET", url, auth=auth) as resp:
            self._set_time_diff(request_time, resp)
            res = await resp.json()
            return _file_status_from_api(res["FileStatus"])

    async def open(self, uri: URL) -> AsyncIterator[bytes]:
        url = self._config.storage_url / self._uri_to_path(uri)
        url = url.with_query(op="OPEN")
        timeout = attr.evolve(self._core.timeout, sock_read=None)
        auth = await self._config._api_auth()

        async with self._core.request("GET", url, timeout=timeout, auth=auth) as resp:
            async for data in resp.content.iter_any():
                yield data

    async def rm(self, uri: URL, *, recursive: bool = False) -> None:
        path = self._uri_to_path(uri)
        # TODO (asvetlov): add a minor protection against deleting everything from root
        # or user volume root, however force operation here should allow user to delete
        # everything.
        #
        # Now it doesn't make sense because URL for root folder (storage:///) is not
        # supported
        #
        # parts = path.split('/')
        # if final_path == root_data_path or final_path.parent == root_data_path:
        #     raise ValueError("Invalid path value.")

        if not recursive:
            stats = await self.stat(uri)
            if stats.type is FileStatusType.DIRECTORY:
                raise IsADirectoryError(
                    errno.EISDIR, "Is a directory, use recursive remove", str(uri)
                )

        url = self._config.storage_url / path
        url = url.with_query(op="DELETE")
        auth = await self._config._api_auth()

        async with self._core.request("DELETE", url, auth=auth) as resp:
            resp  # resp.status == 204

    async def mv(self, src: URL, dst: URL) -> None:
        url = self._config.storage_url / self._uri_to_path(src)
        url = url.with_query(op="RENAME", destination="/" + self._uri_to_path(dst))
        auth = await self._config._api_auth()

        async with self._core.request("POST", url, auth=auth) as resp:
            resp  # resp.status == 204

    # high-level helpers

    async def _iterate_file(
        self,
        src: Path,
        dst: URL,
        *,
        progress: AbstractFileProgress,
        queue: "asyncio.Queue[ProgressQueueItem]",
    ) -> AsyncIterator[bytes]:
        loop = asyncio.get_event_loop()
        src_url = URL(src.as_uri())
        async with self._file_sem:
            with src.open("rb") as stream:
                size = os.stat(stream.fileno()).st_size
                await queue.put(
                    (progress.start, StorageProgressStart(src_url, dst, size))
                )
                chunk = await loop.run_in_executor(None, stream.read, READ_SIZE)
                pos = len(chunk)
                while chunk:
                    await queue.put(
                        (progress.step, StorageProgressStep(src_url, dst, pos, size))
                    )
                    yield chunk
                    chunk = await loop.run_in_executor(None, stream.read, READ_SIZE)
                    pos += len(chunk)
                await queue.put(
                    (progress.complete, StorageProgressComplete(src_url, dst, size))
                )

    async def upload_file(
        self,
        src: URL,
        dst: URL,
        *,
        update: bool = False,
        progress: Optional[AbstractFileProgress] = None,
    ) -> None:
        if progress is None:
            progress = _DummyProgress()
        src = normalize_local_path_uri(src)
        dst = normalize_storage_path_uri(dst, self._config.username)
        path = _extract_path(src)
        try:
            if not path.exists():
                raise FileNotFoundError(errno.ENOENT, "No such file", str(path))
            if path.is_dir():
                raise IsADirectoryError(
                    errno.EISDIR, "Is a directory, use recursive copy", str(path)
                )
        except OSError as e:
            if getattr(e, "winerror", None) not in (1, 87):
                raise
            # Ignore stat errors for device files like NUL or CON on Windows.
            # See https://bugs.python.org/issue37074
        try:
            dst_stat = await self.stat(dst)
            if dst_stat.is_dir():
                raise IsADirectoryError(errno.EISDIR, "Is a directory", str(dst))
        except ResourceNotFound:
            # target doesn't exist, lookup for parent dir
            try:
                dst_parent_stat = await self.stat(dst.parent)
                if not dst_parent_stat.is_dir():
                    # parent path should be a folder
                    raise NotADirectoryError(
                        errno.ENOTDIR, "Not a directory", str(dst.parent)
                    )
            except ResourceNotFound:
                raise NotADirectoryError(
                    errno.ENOTDIR, "Not a directory", str(dst.parent)
                )
        else:
            if update:
                try:
                    src_stat = path.stat()
                except OSError:
                    pass
                else:
                    if S_ISREG(src_stat.st_mode) and not self._is_local_modified(
                        src_stat, dst_stat
                    ):
                        return
        queue: "asyncio.Queue[ProgressQueueItem]" = asyncio.Queue()
        await _run_progress(
            queue, self._upload_file(path, dst, progress=progress, queue=queue)
        )

    async def _upload_file(
        self,
        src_path: Path,
        dst: URL,
        *,
        progress: AbstractFileProgress,
        queue: "asyncio.Queue[ProgressQueueItem]",
    ) -> None:
        for retry in retries(f"Fail to upload {dst}"):
            async with retry:
                await self.create(
                    dst,
                    self._iterate_file(src_path, dst, progress=progress, queue=queue),
                )

    async def upload_dir(
        self,
        src: URL,
        dst: URL,
        *,
        update: bool = False,
        filter: Optional[Callable[[str], Awaitable[bool]]] = None,
        progress: Optional[AbstractRecursiveFileProgress] = None,
    ) -> None:
        if progress is None:
            progress = _DummyProgress()
        if filter is None:
            filter = _always
        src = normalize_local_path_uri(src)
        dst = normalize_storage_path_uri(dst, self._config.username)
        path = _extract_path(src).resolve()
        if not path.exists():
            raise FileNotFoundError(errno.ENOENT, "No such file", str(path))
        if not path.is_dir():
            raise NotADirectoryError(errno.ENOTDIR, "Not a directory", str(path))
        queue: "asyncio.Queue[ProgressQueueItem]" = asyncio.Queue()
        await _run_progress(
            queue,
            self._upload_dir(
                src,
                path,
                dst,
                "",
                update=update,
                filter=filter,
                progress=progress,
                queue=queue,
            ),
        )

    async def _upload_dir(
        self,
        src: URL,
        src_path: Path,
        dst: URL,
        rel_path: str,
        *,
        update: bool,
        filter: Callable[[str], Awaitable[bool]],
        progress: AbstractRecursiveFileProgress,
        queue: "asyncio.Queue[ProgressQueueItem]",
    ) -> None:
        tasks = []
        try:
            exists = False
            if update:
                try:
                    for retry in retries(f"Fail to list {dst}"):
                        async with retry:
                            dst_files = {
                                item.name: item
                                for item in await self.ls(dst)
                                if item.is_file()
                            }
                    exists = True
                except ResourceNotFound:
                    update = False
            if not exists:
                for retry in retries(f"Fail to create {dst}"):
                    async with retry:
                        await self.mkdir(dst, exist_ok=True)
        except FileExistsError:
            raise NotADirectoryError(errno.ENOTDIR, "Not a directory", str(dst))
        await queue.put((progress.enter, StorageProgressEnterDir(src, dst)))
        loop = asyncio.get_event_loop()
        async with self._file_sem:
            folder = await loop.run_in_executor(None, lambda: list(src_path.iterdir()))
        for child in folder:
            name = child.name
            child_rel_path = f"{rel_path}/{name}" if rel_path else name
            if not await filter(child_rel_path):
                continue
            if child.is_file():
                if (
                    update
                    and name in dst_files
                    and not self._is_local_modified(child.stat(), dst_files[name])
                ):
                    continue
                tasks.append(
                    self._upload_file(
                        src_path / name, dst / name, progress=progress, queue=queue
                    )
                )
            elif child.is_dir():
                tasks.append(
                    self._upload_dir(
                        src / name,
                        src_path / name,
                        dst / name,
                        child_rel_path,
                        update=update,
                        filter=filter,
                        progress=progress,
                        queue=queue,
                    )
                )
            else:
                # This case is for uploading non-regular file,
                # e.g. blocking device or unix socket
                # Coverage temporary skipped, the line is waiting for a champion
                await queue.put(
                    (
                        progress.fail,
                        StorageProgressFail(
                            src / name,
                            dst / name,
                            f"Cannot upload {child}, not regular file/directory",
                        ),
                    )
                )  # pragma: no cover
        await _run_concurrently(tasks)
        await queue.put((progress.leave, StorageProgressLeaveDir(src, dst)))

    async def download_file(
        self,
        src: URL,
        dst: URL,
        *,
        update: bool = False,
        progress: Optional[AbstractFileProgress] = None,
    ) -> None:
        if progress is None:
            progress = _DummyProgress()
        src = normalize_storage_path_uri(src, self._config.username)
        dst = normalize_local_path_uri(dst)
        path = _extract_path(dst)
        src_stat = await self.stat(src)
        if not src_stat.is_file():
            raise IsADirectoryError(errno.EISDIR, "Is a directory", str(src))
        if update:
            try:
                dst_stat = path.stat()
            except OSError:
                pass
            else:
                if S_ISREG(dst_stat.st_mode) and not self._is_remote_modified(
                    dst_stat, src_stat
                ):
                    return
        queue: "asyncio.Queue[ProgressQueueItem]" = asyncio.Queue()
        await _run_progress(
            queue,
            self._download_file(
                src, dst, path, src_stat.size, progress=progress, queue=queue
            ),
        )

    async def _download_file(
        self,
        src: URL,
        dst: URL,
        dst_path: Path,
        size: int,
        *,
        progress: AbstractFileProgress,
        queue: "asyncio.Queue[ProgressQueueItem]",
    ) -> None:
        loop = asyncio.get_event_loop()
        async with self._file_sem:
            with dst_path.open("wb") as stream:
                await queue.put((progress.start, StorageProgressStart(src, dst, size)))
                for retry in retries(f"Fail to download {src}"):
                    async with retry:
                        pos = 0
                        async for chunk in self.open(src):
                            pos += len(chunk)
                            await queue.put(
                                (
                                    progress.step,
                                    StorageProgressStep(src, dst, pos, size),
                                )
                            )
                            await loop.run_in_executor(None, stream.write, chunk)
                await queue.put(
                    (progress.complete, StorageProgressComplete(src, dst, size))
                )

    async def download_dir(
        self,
        src: URL,
        dst: URL,
        *,
        update: bool = False,
        filter: Optional[Callable[[str], Awaitable[bool]]] = None,
        progress: Optional[AbstractRecursiveFileProgress] = None,
    ) -> None:
        if progress is None:
            progress = _DummyProgress()
        if filter is None:
            filter = _always
        src = normalize_storage_path_uri(src, self._config.username)
        dst = normalize_local_path_uri(dst)
        path = _extract_path(dst)
        queue: "asyncio.Queue[ProgressQueueItem]" = asyncio.Queue()
        await _run_progress(
            queue,
            self._download_dir(
                src,
                dst,
                path,
                "",
                update=update,
                filter=filter,
                progress=progress,
                queue=queue,
            ),
        )

    async def _download_dir(
        self,
        src: URL,
        dst: URL,
        dst_path: Path,
        rel_path: str,
        *,
        update: bool,
        filter: Callable[[str], Awaitable[bool]],
        progress: AbstractRecursiveFileProgress,
        queue: "asyncio.Queue[ProgressQueueItem]",
    ) -> None:
        dst_path.mkdir(parents=True, exist_ok=True)
        await queue.put((progress.enter, StorageProgressEnterDir(src, dst)))
        tasks = []
        if update:
            loop = asyncio.get_event_loop()
            async with self._file_sem:
                dst_files = await loop.run_in_executor(
                    None,
                    lambda: {
                        item.name: item for item in dst_path.iterdir() if item.is_file()
                    },
                )

        for retry in retries(f"Fail to list {src}"):
            async with retry:
                folder = await self.ls(src)

        for child in folder:
            name = child.name
            child_rel_path = f"{rel_path}/{name}" if rel_path else name
            if not await filter(child_rel_path):
                continue
            if child.is_file():
                if (
                    update
                    and name in dst_files
                    and not self._is_remote_modified(dst_files[name].stat(), child)
                ):
                    continue
                tasks.append(
                    self._download_file(
                        src / name,
                        dst / name,
                        dst_path / name,
                        child.size,
                        progress=progress,
                        queue=queue,
                    )
                )
            elif child.is_dir():
                tasks.append(
                    self._download_dir(
                        src / name,
                        dst / name,
                        dst_path / name,
                        child_rel_path,
                        update=update,
                        filter=filter,
                        progress=progress,
                        queue=queue,
                    )
                )
            else:
                await queue.put(
                    (
                        progress.fail,
                        StorageProgressFail(
                            src / name,
                            dst / name,
                            f"Cannot download {child}, not regular file/directory",
                        ),
                    )
                )  # pragma: no cover
        await _run_concurrently(tasks)
        await queue.put((progress.leave, StorageProgressLeaveDir(src, dst)))


_magic_check = re.compile("(?:[*?[])")


def _has_magic(s: str) -> bool:
    return _magic_check.search(s) is not None


def _ishidden(name: str) -> bool:
    return name.startswith(".")


def _isrecursive(pattern: str) -> bool:
    return pattern == "**"


def _file_status_from_api(values: Dict[str, Any]) -> FileStatus:
    return FileStatus(
        path=values["path"],
        type=FileStatusType(values["type"]),
        size=int(values["length"]),
        modification_time=int(values["modificationTime"]),
        permission=Action(values["permission"]),
    )


async def _run_concurrently(coros: Iterable[Awaitable[Any]]) -> None:
    loop = asyncio.get_event_loop()
    tasks: "Iterable[asyncio.Future[Any]]" = [loop.create_task(coro) for coro in coros]
    if not tasks:
        return
    try:
        done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
        for task in done:
            await task
    except:  # noqa: E722
        for task in tasks:
            task.cancel()
        # wait for actual cancellation, ignore all exceptions raised from tasks
        if tasks:
            await asyncio.wait(tasks)
        raise  # pragma: no cover


async def _run_progress(
    queue: "asyncio.Queue[ProgressQueueItem]", coro: Awaitable[None]
) -> None:
    async def wrapped() -> None:
        try:
            await coro
        finally:
            await queue.put(None)

    loop = asyncio.get_event_loop()
    task = loop.create_task(wrapped())
    while True:
        item = await queue.get()
        if item is None:
            break
        cb, data = item
        cb(data)
    await task


class _DummyProgress(AbstractRecursiveFileProgress):
    def start(self, data: StorageProgressStart) -> None:
        pass

    def complete(self, data: StorageProgressComplete) -> None:
        pass

    def step(self, data: StorageProgressStep) -> None:
        pass

    def enter(self, data: StorageProgressEnterDir) -> None:
        pass

    def leave(self, data: StorageProgressLeaveDir) -> None:
        pass

    def fail(self, data: StorageProgressFail) -> None:
        pass


async def _always(path: str) -> bool:
    return True
