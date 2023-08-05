import json
from typing import Any, Callable, Dict, List, Optional

import pytest
from aiodocker.exceptions import DockerError
from aiohttp import web
from yarl import URL

from neuromation.api import (
    Client,
    Container,
    HTTPPort,
    JobStatus,
    JobTelemetry,
    RemoteImage,
    ResourceNotFound,
    Resources,
    Volume,
)
from neuromation.api.jobs import INVALID_IMAGE_NAME, _job_description_from_api
from tests import _TestServerFactory


_MakeClient = Callable[..., Client]


def test_resources_default() -> None:
    resources = Resources(16, 0.5)
    assert resources.memory_mb == 16
    assert resources.cpu == 0.5
    assert resources.gpu is None
    assert resources.gpu_model is None
    assert resources.shm is True
    assert resources.tpu_type is None
    assert resources.tpu_software_version is None


async def test_jobs_monitor(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    async def log_stream(request: web.Request) -> web.StreamResponse:
        assert request.headers["Accept-Encoding"] == "identity"
        resp = web.StreamResponse()
        resp.enable_chunked_encoding()
        resp.enable_compression(web.ContentCoding.identity)
        await resp.prepare(request)
        for i in range(10):
            await resp.write(b"chunk " + str(i).encode("ascii") + b"\n")
        return resp

    app = web.Application()
    app.router.add_get("/jobs/job-id/log", log_stream)

    srv = await aiohttp_server(app)

    lst = []
    async with make_client(srv.make_url("/")) as client:
        async for data in client.jobs.monitor("job-id"):
            lst.append(data)

    assert b"".join(lst) == b"".join(
        [
            b"chunk 0\n",
            b"chunk 1\n",
            b"chunk 2\n",
            b"chunk 3\n",
            b"chunk 4\n",
            b"chunk 5\n",
            b"chunk 6\n",
            b"chunk 7\n",
            b"chunk 8\n",
            b"chunk 9\n",
        ]
    )


async def test_monitor_notexistent_job(
    aiohttp_server: Any, make_client: _MakeClient
) -> None:
    async def handler(request: web.Request) -> web.Response:
        raise web.HTTPNotFound()

    app = web.Application()
    app.router.add_get("/jobs/job-id/log", handler)

    srv = await aiohttp_server(app)

    lst = []
    async with make_client(srv.make_url("/")) as client:
        with pytest.raises(ResourceNotFound):
            async for data in client.jobs.monitor("job-id"):
                lst.append(data)
    assert lst == []


async def test_job_top(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    def get_data_chunk(index: int) -> Dict[str, Any]:
        return {
            "cpu": 0.5,
            "memory": 50,
            "timestamp": index,
            "gpu_duty_cycle": 50,
            "gpu_memory": 55.6,
        }

    def get_job_telemetry(index: int) -> JobTelemetry:
        return JobTelemetry(
            cpu=0.5, memory=50, timestamp=index, gpu_duty_cycle=50, gpu_memory=55.6
        )

    async def top_stream(request: web.Request) -> web.WebSocketResponse:
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        for i in range(10):
            await ws.send_json(get_data_chunk(i))

        await ws.close()
        return ws

    app = web.Application()
    app.router.add_get("/jobs/job-id/top", top_stream)

    srv = await aiohttp_server(app)

    lst = []
    async with make_client(srv.make_url("/")) as client:
        async for data in client.jobs.top("job-id"):
            lst.append(data)

    assert lst == [get_job_telemetry(i) for i in range(10)]


async def test_top_finished_job(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    async def handler(request: web.Request) -> web.WebSocketResponse:
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        await ws.close()
        return ws

    app = web.Application()
    app.router.add_get("/jobs/job-id/top", handler)

    srv = await aiohttp_server(app)

    lst = []
    async with make_client(srv.make_url("/")) as client:
        with pytest.raises(ValueError, match="not running"):
            async for data in client.jobs.top("job-id"):
                lst.append(data)
    assert lst == []


async def test_top_nonexisting_job(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    async def handler(request: web.Request) -> web.Response:
        raise web.HTTPBadRequest()

    app = web.Application()
    app.router.add_get("/jobs/job-id/top", handler)

    srv = await aiohttp_server(app)

    lst = []
    async with make_client(srv.make_url("/")) as client:
        with pytest.raises(ValueError, match="not found"):
            async for data in client.jobs.top("job-id"):
                lst.append(data)
    assert lst == []


async def test_kill_not_found_error(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    async def handler(request: web.Request) -> web.Response:
        raise web.HTTPNotFound()

    app = web.Application()
    app.router.add_delete("/jobs/job-id", handler)

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/")) as client:
        with pytest.raises(ResourceNotFound):
            await client.jobs.kill("job-id")


async def test_kill_ok(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    async def handler(request: web.Request) -> web.Response:
        raise web.HTTPNoContent()

    app = web.Application()
    app.router.add_delete("/jobs/job-id", handler)

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/")) as client:
        ret = await client.jobs.kill("job-id")

    assert ret is None


async def test_save_image_not_in_neuro_registry(make_client: _MakeClient) -> None:
    async with make_client("http://whatever") as client:
        image = RemoteImage(name="ubuntu")
        with pytest.raises(ValueError, match="must be in the neuromation registry"):
            await client.jobs.save("job-id", image)


async def test_save_ok(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    JSON = [
        {
            "status": "CommitStarted",
            "details": {"container": "cont_id", "image": f"ubuntu:latest"},
        },
        {"status": "CommitFinished"},
        {"status": "The push refers to repository [localhost:5000/alpine]"},
        {"status": "Preparing", "progressDetail": {}, "id": "a31dbd3063d7"},
        {
            "status": "Pushing",
            "progressDetail": {"current": 3584},
            "progress": " 3.584kB",
            "id": "0acd017a4b67",
        },
        {"status": "Pushed", "progressDetail": {}, "id": "0acd017a4b67"},
        {"status": "job-id: digest: sha256:DIGEST size: 1359"},
        {
            "progressDetail": {},
            "aux": {"Tag": "job-id", "Digest": "sha256:DIGEST", "Size": 1359},
        },
    ]

    async def handler(request: web.Request) -> web.StreamResponse:
        assert "b3" in request.headers
        encoding = "utf-8"
        response = web.StreamResponse(status=200)
        response.enable_compression(web.ContentCoding.identity)
        response.content_type = "application/x-ndjson"
        response.charset = encoding
        await response.prepare(request)
        for chunk in JSON:
            chunk_str = json.dumps(chunk) + "\r\n"
            await response.write(chunk_str.encode(encoding))
        return response

    app = web.Application()
    app.router.add_post("/jobs/job-id/save", handler)

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/")) as client:
        image = RemoteImage(registry="gcr.io", owner="me", name="img")
        await client.jobs.save("job-id", image)


async def test_save_commit_started_invalid_status_fails(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    invalid = "invalid status"
    JSON = [
        {"status": invalid, "details": {"container": "cnt", "image": "img"}},
        {"status": "CommitFinished"},
        {"status": "The push refers to repository [localhost:5000/alpine]"},
    ]

    async def handler(request: web.Request) -> web.StreamResponse:
        assert "b3" in request.headers
        encoding = "utf-8"
        response = web.StreamResponse(status=200)
        response.enable_compression(web.ContentCoding.identity)
        response.content_type = "application/x-ndjson"
        response.charset = encoding
        await response.prepare(request)
        for chunk in JSON:
            chunk_str = json.dumps(chunk) + "\r\n"
            await response.write(chunk_str.encode(encoding))
        return response

    app = web.Application()
    app.router.add_post("/jobs/job-id/save", handler)

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/")) as client:
        image = RemoteImage(registry="gcr.io", owner="me", name="img")
        with pytest.raises(
            DockerError,
            match=f"Invalid commit status: '{invalid}', expecting: 'CommitStarted'",
        ):
            await client.jobs.save("job-id", image)


async def test_save_commit_started_missing_image_details_fails(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    JSON = [
        {"status": "CommitStarted", "details": {"container": "cnt"}},
        {"status": "CommitFinished"},
        {"status": "The push refers to repository [localhost:5000/alpine]"},
    ]

    async def handler(request: web.Request) -> web.StreamResponse:
        assert "b3" in request.headers
        encoding = "utf-8"
        response = web.StreamResponse(status=200)
        response.enable_compression(web.ContentCoding.identity)
        response.content_type = "application/x-ndjson"
        response.charset = encoding
        await response.prepare(request)
        for chunk in JSON:
            chunk_str = json.dumps(chunk) + "\r\n"
            await response.write(chunk_str.encode(encoding))
        return response

    app = web.Application()
    app.router.add_post("/jobs/job-id/save", handler)

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/")) as client:
        image = RemoteImage(registry="gcr.io", owner="me", name="img")
        with pytest.raises(DockerError, match="Missing required details: 'image'"):
            await client.jobs.save("job-id", image)


async def test_save_commit_finished_invalid_status_fails(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    invalid = "invalid status"
    JSON = [
        {"status": "CommitStarted", "details": {"container": "cnt", "image": "img"}},
        {"status": invalid},
        {"status": "The push refers to repository [localhost:5000/alpine]"},
    ]

    async def handler(request: web.Request) -> web.StreamResponse:
        encoding = "utf-8"
        response = web.StreamResponse(status=200)
        response.enable_compression(web.ContentCoding.identity)
        response.content_type = "application/x-ndjson"
        response.charset = encoding
        await response.prepare(request)
        for chunk in JSON:
            chunk_str = json.dumps(chunk) + "\r\n"
            await response.write(chunk_str.encode(encoding))
        return response

    app = web.Application()
    app.router.add_post("/jobs/job-id/save", handler)

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/")) as client:
        image = RemoteImage(registry="gcr.io", owner="me", name="img")
        with pytest.raises(
            DockerError,
            match=(f"Invalid commit status: '{invalid}', expecting: 'CommitFinished'"),
        ):
            await client.jobs.save("job-id", image)


async def test_save_commit_started_missing_status_fails(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    JSON = [
        {"not-a-status": "value"},
        {"status": "CommitFinished"},
        {"status": "The push refers to repository [localhost:5000/alpine]"},
    ]

    async def handler(request: web.Request) -> web.StreamResponse:
        encoding = "utf-8"
        response = web.StreamResponse(status=200)
        response.enable_compression(web.ContentCoding.identity)
        response.content_type = "application/x-ndjson"
        response.charset = encoding
        await response.prepare(request)
        for chunk in JSON:
            chunk_str = json.dumps(chunk) + "\r\n"
            await response.write(chunk_str.encode(encoding))
        return response

    app = web.Application()
    app.router.add_post("/jobs/job-id/save", handler)

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/")) as client:
        image = RemoteImage(registry="gcr.io", owner="me", name="img")
        with pytest.raises(DockerError, match='Missing required field: "status"'):
            await client.jobs.save("job-id", image)


async def test_save_commit_finished_missing_status_fails(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    JSON = [
        {"status": "CommitStarted", "details": {"container": "cnt", "image": "img"}},
        {"not-a-status": "value"},
        {"status": "The push refers to repository [localhost:5000/alpine]"},
    ]

    async def handler(request: web.Request) -> web.StreamResponse:
        encoding = "utf-8"
        response = web.StreamResponse(status=200)
        response.enable_compression(web.ContentCoding.identity)
        response.content_type = "application/x-ndjson"
        response.charset = encoding
        await response.prepare(request)
        for chunk in JSON:
            chunk_str = json.dumps(chunk) + "\r\n"
            await response.write(chunk_str.encode(encoding))
        return response

    app = web.Application()
    app.router.add_post("/jobs/job-id/save", handler)

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/")) as client:
        image = RemoteImage(registry="gcr.io", owner="me", name="img")
        with pytest.raises(DockerError, match='Missing required field: "status"'):
            await client.jobs.save("job-id", image)


async def test_status_failed(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    JSON = {
        "status": "failed",
        "id": "job-id",
        "description": "This is job description, not a history description",
        "http_url": "http://my_host:8889",
        "ssh_server": "ssh://my_host.ssh:22",
        "ssh_auth_server": "ssh://my_host.ssh:22",
        "history": {
            "created_at": "2018-08-29T12:23:13.981621+00:00",
            "started_at": "2018-08-29T12:23:15.988054+00:00",
            "finished_at": "2018-08-29T12:59:31.427795+00:00",
            "reason": "ContainerCannotRun",
            "description": "Not enough coffee",
        },
        "is_preemptible": True,
        "owner": "owner",
        "cluster_name": "default",
        "container": {
            "image": "submit-image-name",
            "command": "submit-command",
            "http": {"port": 8181},
            "resources": {
                "memory_mb": "4096",
                "cpu": 7.0,
                "shm": True,
                "gpu": 1,
                "gpu_model": "test-gpu-model",
            },
            "volumes": [
                {
                    "src_storage_uri": "storage://test-user/path_read_only",
                    "dst_path": "/container/read_only",
                    "read_only": True,
                },
                {
                    "src_storage_uri": "storage://test-user/path_read_write",
                    "dst_path": "/container/path_read_write",
                    "read_only": False,
                },
            ],
        },
    }

    async def handler(request: web.Request) -> web.Response:
        return web.json_response(JSON)

    app = web.Application()
    app.router.add_get("/jobs/job-id", handler)

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/")) as client:
        ret = await client.jobs.status("job-id")

        assert ret == _job_description_from_api(JSON, client.parse)


async def test_status_with_ssh_and_http(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    JSON = {
        "status": "running",
        "id": "job-id",
        "description": "This is job description, not a history description",
        "http_url": "http://my_host:8889",
        "ssh_server": "ssh://my_host.ssh:22",
        "ssh_auth_server": "ssh://my_host.ssh:22",
        "history": {
            "created_at": "2018-08-29T12:23:13.981621+00:00",
            "started_at": "2018-08-29T12:23:15.988054+00:00",
            "finished_at": "2018-08-29T12:59:31.427795+00:00",
            "reason": "OK",
            "description": "Everything is fine",
        },
        "is_preemptible": True,
        "owner": "owner",
        "cluster_name": "default",
        "container": {
            "image": "submit-image-name",
            "command": "submit-command",
            "http": {"port": 8181},
            "resources": {
                "memory_mb": "4096",
                "cpu": 7.0,
                "shm": True,
                "gpu": 1,
                "gpu_model": "test-gpu-model",
            },
            "volumes": [
                {
                    "src_storage_uri": "storage://test-user/path_read_only",
                    "dst_path": "/container/read_only",
                    "read_only": True,
                },
                {
                    "src_storage_uri": "storage://test-user/path_read_write",
                    "dst_path": "/container/path_read_write",
                    "read_only": False,
                },
            ],
        },
    }

    async def handler(request: web.Request) -> web.Response:
        return web.json_response(JSON)

    app = web.Application()
    app.router.add_get("/jobs/job-id", handler)

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/")) as client:
        ret = await client.jobs.status("job-id")

        assert ret == _job_description_from_api(JSON, client.parse)


async def test_status_with_tpu(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    JSON = {
        "status": "running",
        "id": "job-id",
        "description": "This is job description, not a history description",
        "http_url": "http://my_host:8889",
        "ssh_server": "ssh://my_host.ssh:22",
        "ssh_auth_server": "ssh://my_host.ssh:22",
        "history": {
            "created_at": "2018-08-29T12:23:13.981621+00:00",
            "started_at": "2018-08-29T12:23:15.988054+00:00",
            "finished_at": "2018-08-29T12:59:31.427795+00:00",
            "reason": "OK",
            "description": "Everything is fine",
        },
        "is_preemptible": True,
        "owner": "owner",
        "cluster_name": "default",
        "container": {
            "image": "submit-image-name",
            "command": "submit-command",
            "http": {"port": 8181},
            "resources": {
                "memory_mb": "4096",
                "cpu": 7.0,
                "shm": True,
                "gpu": 1,
                "gpu_model": "test-gpu-model",
                "tpu": {"type": "v3-8", "software_version": "1.14"},
            },
            "volumes": [
                {
                    "src_storage_uri": "storage://test-user/path_read_only",
                    "dst_path": "/container/read_only",
                    "read_only": True,
                },
                {
                    "src_storage_uri": "storage://test-user/path_read_write",
                    "dst_path": "/container/path_read_write",
                    "read_only": False,
                },
            ],
        },
    }

    async def handler(request: web.Request) -> web.Response:
        return web.json_response(JSON)

    app = web.Application()
    app.router.add_get("/jobs/job-id", handler)

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/")) as client:
        ret = await client.jobs.status("job-id")

        assert ret == _job_description_from_api(JSON, client.parse)
        assert ret.container.resources.tpu_type == "v3-8"
        assert ret.container.resources.tpu_software_version == "1.14"


async def test_job_run(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    JSON = {
        "id": "job-cf519ed3-9ea5-48f6-a8c5-492b810eb56f",
        "status": "failed",
        "history": {
            "status": "failed",
            "reason": "Error",
            "description": "Mounted on Avail\\n/dev/shm     " "64M\\n\\nExit code: 1",
            "created_at": "2018-09-25T12:28:21.298672+00:00",
            "started_at": "2018-09-25T12:28:59.759433+00:00",
            "finished_at": "2018-09-25T12:28:59.759433+00:00",
        },
        "owner": "owner",
        "cluster_name": "default",
        "container": {
            "image": "gcr.io/light-reality-205619/ubuntu:latest",
            "command": "date",
            "resources": {
                "cpu": 1.0,
                "memory_mb": 16384,
                "gpu": 1,
                "shm": False,
                "gpu_model": "nvidia-tesla-p4",
            },
        },
        "http_url": "http://my_host:8889",
        "ssh_server": "ssh://my_host.ssh:22",
        "ssh_auth_server": "ssh://my_host.ssh:22",
        "is_preemptible": False,
    }

    async def handler(request: web.Request) -> web.Response:
        data = await request.json()
        assert data == {
            "container": {
                "image": "submit-image-name",
                "command": "submit-command",
                "http": {"port": 8181, "requires_auth": True},
                "resources": {
                    "memory_mb": 16384,
                    "cpu": 7.0,
                    "shm": True,
                    "gpu": 1,
                    "gpu_model": "test-gpu-model",
                },
                "volumes": [
                    {
                        "src_storage_uri": "storage://test-user/path_read_only",
                        "dst_path": "/container/read_only",
                        "read_only": True,
                    },
                    {
                        "src_storage_uri": "storage://test-user/path_read_write",
                        "dst_path": "/container/path_read_write",
                        "read_only": False,
                    },
                ],
            },
            "is_preemptible": False,
            "cluster_name": "default",
        }

        return web.json_response(JSON)

    app = web.Application()
    app.router.add_post("/jobs", handler)

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/")) as client:
        resources = Resources(16384, 7, 1, "test-gpu-model", True, None, None)
        volumes: List[Volume] = [
            Volume(
                URL("storage://test-user/path_read_only"), "/container/read_only", True
            ),
            Volume(
                URL("storage://test-user/path_read_write"),
                "/container/path_read_write",
                False,
            ),
        ]
        container = Container(
            image=RemoteImage("submit-image-name"),
            command="submit-command",
            resources=resources,
            volumes=volumes,
            http=HTTPPort(8181),
        )
        ret = await client.jobs.run(container=container, is_preemptible=False)

        assert ret == _job_description_from_api(JSON, client.parse)


async def test_job_run_with_name_and_description(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    JSON = {
        "id": "job-cf519ed3-9ea5-48f6-a8c5-492b810eb56f",
        "name": "test-job-name",
        "description": "job description",
        "status": "failed",
        "history": {
            "status": "failed",
            "reason": "Error",
            "description": "Mounted on Avail\\n/dev/shm     " "64M\\n\\nExit code: 1",
            "created_at": "2018-09-25T12:28:21.298672+00:00",
            "started_at": "2018-09-25T12:28:59.759433+00:00",
            "finished_at": "2018-09-25T12:28:59.759433+00:00",
        },
        "owner": "owner",
        "cluster_name": "default",
        "container": {
            "image": "gcr.io/light-reality-205619/ubuntu:latest",
            "command": "date",
            "resources": {
                "cpu": 1.0,
                "memory_mb": 16384,
                "gpu": 1,
                "shm": False,
                "gpu_model": "nvidia-tesla-p4",
            },
        },
        "http_url": "http://my_host:8889",
        "ssh_server": "ssh://my_host.ssh:22",
        "ssh_auth_server": "ssh://my_host.ssh:22",
        "is_preemptible": False,
    }

    async def handler(request: web.Request) -> web.Response:
        data = await request.json()
        assert data == {
            "container": {
                "image": "submit-image-name",
                "command": "submit-command",
                "http": {"port": 8181, "requires_auth": True},
                "resources": {
                    "memory_mb": 16384,
                    "cpu": 7.0,
                    "shm": True,
                    "gpu": 1,
                    "gpu_model": "test-gpu-model",
                },
                "volumes": [
                    {
                        "src_storage_uri": "storage://test-user/path_read_only",
                        "dst_path": "/container/read_only",
                        "read_only": True,
                    },
                    {
                        "src_storage_uri": "storage://test-user/path_read_write",
                        "dst_path": "/container/path_read_write",
                        "read_only": False,
                    },
                ],
            },
            "is_preemptible": False,
            "name": "test-job-name",
            "description": "job description",
            "cluster_name": "default",
        }

        return web.json_response(JSON)

    app = web.Application()
    app.router.add_post("/jobs", handler)

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/")) as client:
        resources = Resources(16384, 7, 1, "test-gpu-model", True, None, None)
        volumes: List[Volume] = [
            Volume(
                URL("storage://test-user/path_read_only"), "/container/read_only", True
            ),
            Volume(
                URL("storage://test-user/path_read_write"),
                "/container/path_read_write",
                False,
            ),
        ]
        container = Container(
            image=RemoteImage("submit-image-name"),
            command="submit-command",
            resources=resources,
            volumes=volumes,
            http=HTTPPort(8181),
        )
        ret = await client.jobs.run(
            container,
            is_preemptible=False,
            name="test-job-name",
            description="job description",
        )

        assert ret == _job_description_from_api(JSON, client.parse)


async def test_job_run_no_volumes(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    JSON = {
        "id": "job-cf519ed3-9ea5-48f6-a8c5-492b810eb56f",
        "name": "test-job-name",
        "status": "failed",
        "history": {
            "status": "failed",
            "reason": "Error",
            "description": "Mounted on Avail\\n/dev/shm     " "64M\\n\\nExit code: 1",
            "created_at": "2018-09-25T12:28:21.298672+00:00",
            "started_at": "2018-09-25T12:28:59.759433+00:00",
            "finished_at": "2018-09-25T12:28:59.759433+00:00",
        },
        "owner": "owner",
        "cluster_name": "default",
        "container": {
            "image": "gcr.io/light-reality-205619/ubuntu:latest",
            "command": "date",
            "resources": {
                "cpu": 7,
                "memory_mb": 16384,
                "gpu": 1,
                "shm": False,
                "gpu_model": "nvidia-tesla-p4",
            },
        },
        "http_url": "http://my_host:8889",
        "ssh_server": "ssh://my_host.ssh:22",
        "ssh_auth_server": "ssh://my_host.ssh:22",
        "is_preemptible": False,
    }

    async def handler(request: web.Request) -> web.Response:
        data = await request.json()
        assert data == {
            "container": {
                "image": "submit-image-name",
                "command": "submit-command",
                "http": {"port": 8181, "requires_auth": True},
                "resources": {
                    "memory_mb": 16384,
                    "cpu": 7,
                    "shm": True,
                    "gpu": 1,
                    "gpu_model": "test-gpu-model",
                },
            },
            "is_preemptible": False,
            "name": "test-job-name",
            "description": "job description",
            "cluster_name": "default",
        }

        return web.json_response(JSON)

    app = web.Application()
    app.router.add_post("/jobs", handler)

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/")) as client:
        resources = Resources(16384, 7, 1, "test-gpu-model", True, None, None)
        container = Container(
            image=RemoteImage("submit-image-name"),
            command="submit-command",
            resources=resources,
            http=HTTPPort(8181),
        )
        ret = await client.jobs.run(
            container,
            is_preemptible=False,
            name="test-job-name",
            description="job description",
        )

        assert ret == _job_description_from_api(JSON, client.parse)


async def test_job_run_preemptible(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    JSON = {
        "id": "job-cf519ed3-9ea5-48f6-a8c5-492b810eb56f",
        "name": "test-job-name",
        "status": "failed",
        "history": {
            "status": "failed",
            "reason": "Error",
            "description": "Mounted on Avail\\n/dev/shm     " "64M\\n\\nExit code: 1",
            "created_at": "2018-09-25T12:28:21.298672+00:00",
            "started_at": "2018-09-25T12:28:59.759433+00:00",
            "finished_at": "2018-09-25T12:28:59.759433+00:00",
        },
        "owner": "owner",
        "cluster_name": "default",
        "container": {
            "image": "gcr.io/light-reality-205619/ubuntu:latest",
            "command": "date",
            "resources": {
                "cpu": 1.0,
                "memory_mb": 16384,
                "gpu": 1,
                "shm": False,
                "gpu_model": "nvidia-tesla-p4",
            },
        },
        "is_preemptible": True,
        "http_url": "http://my_host:8889",
        "ssh_server": "ssh://my_host.ssh:22",
        "ssh_auth_server": "ssh://my_host.ssh:22",
    }

    async def handler(request: web.Request) -> web.Response:
        data = await request.json()
        assert data == {
            "container": {
                "image": "submit-image-name",
                "command": "submit-command",
                "http": {"port": 8181, "requires_auth": True},
                "resources": {
                    "memory_mb": 16384,
                    "cpu": 7.0,
                    "shm": True,
                    "gpu": 1,
                    "gpu_model": "test-gpu-model",
                },
                "volumes": [
                    {
                        "src_storage_uri": "storage://test-user/path_read_only",
                        "dst_path": "/container/read_only",
                        "read_only": True,
                    },
                    {
                        "src_storage_uri": "storage://test-user/path_read_write",
                        "dst_path": "/container/path_read_write",
                        "read_only": False,
                    },
                ],
            },
            "is_preemptible": True,
            "name": "test-job-name",
            "description": "job description",
            "cluster_name": "default",
        }

        return web.json_response(JSON)

    app = web.Application()
    app.router.add_post("/jobs", handler)

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/")) as client:
        resources = Resources(16384, 7, 1, "test-gpu-model", True, None, None)
        volumes: List[Volume] = [
            Volume(
                URL("storage://test-user/path_read_only"), "/container/read_only", True
            ),
            Volume(
                URL("storage://test-user/path_read_write"),
                "/container/path_read_write",
                False,
            ),
        ]
        container = Container(
            image=RemoteImage("submit-image-name"),
            command="submit-command",
            resources=resources,
            volumes=volumes,
            http=HTTPPort(8181),
        )
        ret = await client.jobs.run(
            container,
            is_preemptible=True,
            name="test-job-name",
            description="job description",
        )

        assert ret == _job_description_from_api(JSON, client.parse)


async def test_job_run_schedule_timeout(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    JSON = {
        "id": "job-cf519ed3-9ea5-48f6-a8c5-492b810eb56f",
        "status": "failed",
        "history": {
            "status": "failed",
            "reason": "Error",
            "description": "Mounted on Avail\\n/dev/shm     " "64M\\n\\nExit code: 1",
            "created_at": "2018-09-25T12:28:21.298672+00:00",
            "started_at": "2018-09-25T12:28:59.759433+00:00",
            "finished_at": "2018-09-25T12:28:59.759433+00:00",
        },
        "owner": "owner",
        "cluster_name": "default",
        "container": {
            "image": "gcr.io/light-reality-205619/ubuntu:latest",
            "command": "date",
            "resources": {
                "cpu": 1.0,
                "memory_mb": 16384,
                "gpu": 1,
                "shm": False,
                "gpu_model": "nvidia-tesla-p4",
            },
        },
        "http_url": "http://my_host:8889",
        "ssh_server": "ssh://my_host.ssh:22",
        "ssh_auth_server": "ssh://my_host.ssh:22",
        "is_preemptible": False,
        "schedule_timeout": 5,
    }

    async def handler(request: web.Request) -> web.Response:
        data = await request.json()
        assert data == {
            "container": {
                "image": "submit-image-name",
                "command": "submit-command",
                "resources": {
                    "memory_mb": 16384,
                    "cpu": 7,
                    "shm": True,
                    "gpu": 1,
                    "gpu_model": "test-gpu-model",
                },
            },
            "is_preemptible": False,
            "schedule_timeout": 5,
            "cluster_name": "default",
        }

        return web.json_response(JSON)

    app = web.Application()
    app.router.add_post("/jobs", handler)

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/")) as client:
        resources = Resources(16384, 7, 1, "test-gpu-model", True, None, None)
        container = Container(
            image=RemoteImage("submit-image-name"),
            command="submit-command",
            resources=resources,
        )
        ret = await client.jobs.run(container=container, schedule_timeout=5)

        assert ret == _job_description_from_api(JSON, client.parse)


async def test_job_run_tpu(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    JSON = {
        "id": "job-cf519ed3-9ea5-48f6-a8c5-492b810eb56f",
        "status": "failed",
        "history": {
            "status": "failed",
            "reason": "Error",
            "description": "Mounted on Avail\\n/dev/shm     " "64M\\n\\nExit code: 1",
            "created_at": "2018-09-25T12:28:21.298672+00:00",
            "started_at": "2018-09-25T12:28:59.759433+00:00",
            "finished_at": "2018-09-25T12:28:59.759433+00:00",
        },
        "owner": "owner",
        "cluster_name": "default",
        "container": {
            "image": "gcr.io/light-reality-205619/ubuntu:latest",
            "command": "date",
            "resources": {
                "cpu": 1.0,
                "memory_mb": 16384,
                "gpu": 1,
                "shm": False,
                "gpu_model": "nvidia-tesla-p4",
                "tpu": {"type": "v3-8", "software_version": "1.14"},
            },
        },
        "http_url": "http://my_host:8889",
        "ssh_server": "ssh://my_host.ssh:22",
        "ssh_auth_server": "ssh://my_host.ssh:22",
        "is_preemptible": False,
    }

    async def handler(request: web.Request) -> web.Response:
        data = await request.json()
        assert data == {
            "container": {
                "image": "submit-image-name",
                "command": "submit-command",
                "resources": {
                    "memory_mb": 16384,
                    "cpu": 7,
                    "shm": True,
                    "gpu": 1,
                    "gpu_model": "test-gpu-model",
                    "tpu": {"type": "v3-8", "software_version": "1.14"},
                },
            },
            "is_preemptible": False,
            "schedule_timeout": 5,
            "cluster_name": "default",
        }

        return web.json_response(JSON)

    app = web.Application()
    app.router.add_post("/jobs", handler)

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/")) as client:
        resources = Resources(16384, 7, 1, "test-gpu-model", True, "v3-8", "1.14")
        container = Container(
            image=RemoteImage("submit-image-name"),
            command="submit-command",
            resources=resources,
        )
        ret = await client.jobs.run(container=container, schedule_timeout=5)

        assert ret == _job_description_from_api(JSON, client.parse)
        assert ret.container.resources.tpu_type == "v3-8"
        assert ret.container.resources.tpu_software_version == "1.14"


def create_job_response(
    id: str,
    status: str,
    owner: str = "owner",
    name: Optional[str] = None,
    image: str = "submit-image-name",
) -> Dict[str, Any]:
    result = {
        "id": id,
        "status": status,
        "history": {
            "status": "failed",
            "reason": "Error",
            "description": "Mounted on Avail\\n/dev/shm     " "64M\\n\\nExit code: 1",
            "created_at": "2018-09-25T12:28:21.298672+00:00",
            "started_at": "2018-09-25T12:28:59.759433+00:00",
            "finished_at": "2018-09-25T12:28:59.759433+00:00",
        },
        "ssh_auth_server": "ssh://my_host.ssh:22",
        "container": {
            "image": image,
            "command": "submit-command",
            "resources": {
                "cpu": 1.0,
                "memory_mb": 16384,
                "gpu": 1,
                "gpu_model": "nvidia-tesla-v100",
            },
        },
        "is_preemptible": True,
        "owner": owner,
        "cluster_name": "default",
    }
    if name:
        result["name"] = name
    return result


async def test_list_no_filter(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    jobs = [
        create_job_response("job-id-1", "pending", name="job-name-1"),
        create_job_response("job-id-2", "running", name="job-name-1"),
        create_job_response("job-id-3", "succeeded", name="job-name-1"),
        create_job_response("job-id-4", "failed", name="job-name-1"),
    ]
    JSON = {"jobs": jobs}

    async def handler(request: web.Request) -> web.Response:
        return web.json_response(JSON)

    app = web.Application()
    app.router.add_get("/jobs", handler)
    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/")) as client:
        ret = await client.jobs.list()

        job_descriptions = [
            _job_description_from_api(job, client.parse) for job in jobs
        ]
        assert ret == job_descriptions


async def test_list_filter_by_name(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    name_1 = "job-name-1"
    name_2 = "job-name-2"
    jobs = [
        create_job_response("job-id-1", "pending", name=name_1),
        create_job_response("job-id-2", "succeeded", name=name_1),
        create_job_response("job-id-3", "failed", name=name_1),
        create_job_response("job-id-4", "running", name=name_2),
        create_job_response("job-id-5", "succeeded", name=name_2),
        create_job_response("job-id-6", "failed", name=name_2),
        create_job_response("job-id-7", "running"),
        create_job_response("job-id-8", "pending"),
        create_job_response("job-id-9", "succeeded"),
        create_job_response("job-id-10", "failed"),
    ]

    async def handler(request: web.Request) -> web.Response:
        name = request.query.get("name")
        assert name
        filtered_jobs = [job for job in jobs if job.get("name") == name]
        JSON = {"jobs": filtered_jobs}
        return web.json_response(JSON)

    app = web.Application()
    app.router.add_get("/jobs", handler)
    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/")) as client:
        ret = await client.jobs.list(name=name_1)

        job_descriptions = [
            _job_description_from_api(job, client.parse) for job in jobs
        ]
        assert ret == job_descriptions[:3]


async def test_list_filter_by_statuses(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    name_1 = "job-name-1"
    name_2 = "job-name-2"
    jobs = [
        create_job_response("job-id-1", "pending", name=name_1),
        create_job_response("job-id-2", "succeeded", name=name_1),
        create_job_response("job-id-3", "failed", name=name_1),
        create_job_response("job-id-4", "running", name=name_2),
        create_job_response("job-id-5", "succeeded", name=name_2),
        create_job_response("job-id-6", "failed", name=name_2),
        create_job_response("job-id-7", "running"),
        create_job_response("job-id-8", "pending"),
        create_job_response("job-id-9", "succeeded"),
        create_job_response("job-id-10", "failed"),
    ]

    async def handler(request: web.Request) -> web.Response:
        statuses = request.query.getall("status")
        assert statuses
        filtered_jobs = [job for job in jobs if job["status"] in statuses]
        JSON = {"jobs": filtered_jobs}
        return web.json_response(JSON)

    app = web.Application()
    app.router.add_get("/jobs", handler)
    srv = await aiohttp_server(app)

    statuses = {JobStatus.FAILED, JobStatus.SUCCEEDED}
    async with make_client(srv.make_url("/")) as client:
        ret = await client.jobs.list(statuses=statuses)

        job_descriptions = [
            _job_description_from_api(job, client.parse) for job in jobs
        ]
        assert ret == [job for job in job_descriptions if job.status in statuses]


async def test_list_incorrect_image(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    jobs = [
        create_job_response("job-id-1", "running"),
        create_job_response("job-id-2", "pending", image="some.com/path/:tag"),
        create_job_response(
            "job-id-3", "failed", image="registry-dev.neu.ro/path/:tag"
        ),
        create_job_response("job-id-4", "failed", image=""),
        create_job_response("job-id-5", "failed", image=":"),
    ]

    async def handler(request: web.Request) -> web.Response:

        JSON = {"jobs": jobs}
        return web.json_response(JSON)

    app = web.Application()
    app.router.add_get("/jobs", handler)
    srv = await aiohttp_server(app)

    statuses = {JobStatus.FAILED, JobStatus.SUCCEEDED}
    async with make_client(srv.make_url("/")) as client:
        ret = await client.jobs.list(statuses=statuses)
    for job in ret:
        if job.status == JobStatus.FAILED:
            assert job.container.image.name == INVALID_IMAGE_NAME
        else:
            assert job.container.image.name != INVALID_IMAGE_NAME


class TestVolumeParsing:
    @pytest.mark.parametrize(
        "volume_param", ["dir", "storage://dir", "storage://dir:/var/www:rw:ro"]
    )
    async def test_incorrect_params_count(
        self, volume_param: str, make_client: _MakeClient
    ) -> None:
        async with make_client("https://example.com") as client:
            with pytest.raises(ValueError, match=r"Invalid volume specification"):
                client.parse.volume(volume_param)

    @pytest.mark.parametrize(
        "volume_param", ["storage://dir:/var/www:write", "storage://dir:/var/www:"]
    )
    async def test_incorrect_mode(
        self, volume_param: str, make_client: _MakeClient
    ) -> None:
        async with make_client("https://example.com") as client:
            with pytest.raises(ValueError, match=r"Wrong ReadWrite/ReadOnly mode spec"):
                client.parse.volume(volume_param)

    @pytest.mark.parametrize(
        "volume_param,volume",
        [
            (
                "storage://user/dir:/var/www",
                Volume(
                    storage_uri=URL("storage://user/dir"),
                    container_path="/var/www",
                    read_only=False,
                ),
            ),
            (
                "storage://user/dir:/var/www:rw",
                Volume(
                    storage_uri=URL("storage://user/dir"),
                    container_path="/var/www",
                    read_only=False,
                ),
            ),
            (
                "storage://user:/var/www:ro",
                Volume(
                    storage_uri=URL("storage://user"),
                    container_path="/var/www",
                    read_only=True,
                ),
            ),
            (
                "storage://~/:/var/www:ro",
                Volume(
                    storage_uri=URL("storage://user"),
                    container_path="/var/www",
                    read_only=True,
                ),
            ),
            (
                "storage:dir:/var/www:ro",
                Volume(
                    storage_uri=URL("storage://user/dir"),
                    container_path="/var/www",
                    read_only=True,
                ),
            ),
            (
                "storage::/var/www:ro",
                Volume(
                    storage_uri=URL("storage://user"),
                    container_path="/var/www",
                    read_only=True,
                ),
            ),
        ],
    )
    async def test_positive(
        self, volume_param: str, volume: Volume, make_client: _MakeClient
    ) -> None:
        async with make_client("https://example.com") as client:
            assert client.parse.volume(volume_param) == volume


async def test_list_filter_by_name_and_statuses(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    name_1 = "job-name-1"
    name_2 = "job-name-2"
    jobs = [
        create_job_response("job-id-1", "pending", name=name_1),
        create_job_response("job-id-2", "succeeded", name=name_1),
        create_job_response("job-id-3", "failed", name=name_1),
        create_job_response("job-id-4", "running", name=name_2),
        create_job_response("job-id-5", "succeeded", name=name_2),
        create_job_response("job-id-6", "failed", name=name_2),
        create_job_response("job-id-7", "running"),
        create_job_response("job-id-8", "pending"),
        create_job_response("job-id-9", "succeeded"),
        create_job_response("job-id-10", "failed"),
    ]

    async def handler(request: web.Request) -> web.Response:
        statuses = request.query.getall("status")
        assert statuses
        name = request.query.get("name")
        assert name
        filtered_jobs = [
            job for job in jobs if job["status"] in statuses and job.get("name") == name
        ]
        JSON = {"jobs": filtered_jobs}
        return web.json_response(JSON)

    app = web.Application()
    app.router.add_get("/jobs", handler)
    srv = await aiohttp_server(app)

    statuses = {JobStatus.PENDING, JobStatus.SUCCEEDED}
    name = "job-name-1"
    async with make_client(srv.make_url("/")) as client:
        ret = await client.jobs.list(statuses=statuses, name=name)

        job_descriptions = [
            _job_description_from_api(job, client.parse) for job in jobs
        ]
        assert ret == job_descriptions[:2]


async def test_list_filter_by_name_and_statuses_and_owners(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    name_1 = "job-name-1"
    name_2 = "job-name-2"
    owner_1 = "owner-1"
    owner_2 = "owner-2"
    jobs = [
        create_job_response("job-id-1", "running", name=name_1, owner=owner_1),
        create_job_response("job-id-2", "running", name=name_1, owner=owner_2),
        create_job_response("job-id-3", "running", name=name_2, owner=owner_1),
        create_job_response("job-id-4", "running", name=name_2, owner=owner_2),
        create_job_response("job-id-5", "succeeded", name=name_1, owner=owner_1),
        create_job_response("job-id-6", "succeeded", name=name_1, owner=owner_2),
        create_job_response("job-id-7", "succeeded", name=name_2, owner=owner_1),
        create_job_response("job-id-8", "succeeded", name=name_2, owner=owner_2),
    ]

    async def handler(request: web.Request) -> web.Response:
        statuses = request.query.getall("status")
        name = request.query.get("name")
        owners = request.query.getall("owner")
        filtered_jobs = [
            job
            for job in jobs
            if job["status"] in statuses
            and job.get("name") == name
            and job.get("owner") in owners
        ]
        return web.json_response({"jobs": filtered_jobs})

    app = web.Application()
    app.router.add_get("/jobs", handler)
    srv = await aiohttp_server(app)

    statuses = {JobStatus.RUNNING}
    name = name_1
    owners = {owner_1, owner_2}
    async with make_client(srv.make_url("/")) as client:
        ret = await client.jobs.list(statuses=statuses, name=name, owners=owners)

        job_descriptions = [
            _job_description_from_api(job, client.parse) for job in jobs
        ]
        assert ret == job_descriptions[:2]
