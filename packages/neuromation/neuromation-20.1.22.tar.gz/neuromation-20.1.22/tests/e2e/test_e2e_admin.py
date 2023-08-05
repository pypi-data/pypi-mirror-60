import re
import subprocess
from typing import Any

import pytest

from tests.e2e import Helper


@pytest.mark.e2e
def test_get_cluster_users(request: Any, helper: Helper) -> None:
    captured = helper.run_cli(["admin", "get-cluster-users"])
    assert captured.err == ""

    header, *users = [re.split(" +", row.strip()) for row in captured.out.split("\n")]

    assert header == ["Name", "Role"]
    for name, role in users:
        assert role in ["admin", "manager", "user"]


@pytest.mark.e2e
def test_add_cluster_user_already_exists(request: Any, helper: Helper) -> None:
    with pytest.raises(subprocess.CalledProcessError) as cm:
        helper.run_cli(
            ["admin", "add-cluster-user", helper.cluster_name, helper.username, "user"]
        )
    assert cm.value.returncode == 65
    assert (
        f"Illegal argument(s) (User '{helper.username}' already exists in cluster "
        f"'{helper.cluster_name}')" in cm.value.stderr
    )


@pytest.mark.e2e
def test_add_cluster_user_does_not_exist(request: Any, helper: Helper) -> None:
    username = "some-clearly-invalid-username"
    with pytest.raises(subprocess.CalledProcessError) as cm:
        helper.run_cli(
            ["admin", "add-cluster-user", helper.cluster_name, username, "user"]
        )
    assert cm.value.returncode == 72
    assert f"User 'some-clearly-invalid-username' not found" in cm.value.stderr


@pytest.mark.e2e
def test_add_cluster_user_invalid_role(request: Any, helper: Helper) -> None:
    username = "some-clearly-invalid-username"
    with pytest.raises(subprocess.CalledProcessError) as cm:
        helper.run_cli(
            ["admin", "add-cluster-user", helper.cluster_name, username, "my_role"]
        )
    assert cm.value.returncode == 2
    assert 'Error: Invalid value for "[ROLE]": invalid choice:' in cm.value.stderr
    assert "(choose from admin, manager, user)" in cm.value.stderr


@pytest.mark.e2e
def test_remove_cluster_user_remove_oneself(request: Any, helper: Helper) -> None:
    with pytest.raises(subprocess.CalledProcessError) as cm:
        helper.run_cli(
            ["admin", "remove-cluster-user", helper.cluster_name, helper.username]
        )
    assert cm.value.returncode == 65
    assert (
        "Illegal argument(s) (Cluster users cannot remove themselves)"
        in cm.value.stderr
    )


@pytest.mark.e2e
def test_remove_cluster_user_does_not_exist(request: Any, helper: Helper) -> None:
    username = "some-clearly-invalid-username"
    with pytest.raises(subprocess.CalledProcessError) as cm:
        helper.run_cli(["admin", "remove-cluster-user", helper.cluster_name, username])
    assert cm.value.returncode == 72
    assert f"User 'some-clearly-invalid-username' not found" in cm.value.stderr
