import logging
from typing import Any, List, Optional

import click

from neuromation.api import Permission, Share

from .root import Root
from .utils import (
    command,
    group,
    option,
    pager_maybe,
    parse_permission_action,
    parse_resource_for_sharing,
)


log = logging.getLogger(__name__)


@group()
def acl() -> None:
    """
    Access Control List management.
    """


@command()
@click.argument("uri")
@click.argument("user")
@click.argument("permission", type=click.Choice(["read", "write", "manage"]))
async def grant(root: Root, uri: str, user: str, permission: str) -> None:
    """
        Shares resource with another user.

        URI shared resource.

        USER username to share resource with.

        PERMISSION sharing access right: read, write, or manage.

        Examples:
        neuro acl grant storage:///sample_data/ alice manage
        neuro acl grant image:resnet50 bob read
        neuro acl grant job:///my_job_id alice write
    """
    try:
        uri_obj = parse_resource_for_sharing(uri, root)
        action_obj = parse_permission_action(permission)
        permission_obj = Permission(uri=uri_obj, action=action_obj)
        log.info(f"Using resource '{permission_obj.uri}'")

        await root.client.users.share(user, permission_obj)

    except ValueError as e:
        raise ValueError(f"Could not share resource '{uri}': {e}") from e


@command()
@click.argument("uri")
@click.argument("user")
async def revoke(root: Root, uri: str, user: str) -> None:
    """
        Revoke user access from another user.

        URI previously shared resource to revoke.

        USER to revoke URI resource from.

        Examples:
        neuro acl revoke storage:///sample_data/ alice
        neuro acl revoke image:resnet50 bob
        neuro acl revoke job:///my_job_id alice
    """
    try:
        uri_obj = parse_resource_for_sharing(uri, root)
        log.info(f"Using resource '{uri_obj}'")

        await root.client.users.revoke(user, uri_obj)

    except ValueError as e:
        raise ValueError(f"Could not unshare resource '{uri}': {e}") from e


@command()
@option(
    "-s",
    "--scheme",
    default=None,
    help="Filter resources by scheme, e.g. job, storage, image or user.",
)
@option(
    "--shared",
    is_flag=True,
    default=False,
    help="Output the resources shared by the user.",
)
async def list(root: Root, scheme: Optional[str], shared: bool) -> None:
    """
        List shared resources.

        The command displays a list of resources shared BY current user (default).

        To display a list of resources shared WITH current user apply --shared option.

        Examples:
        neuro acl list
        neuro acl list --scheme storage
        neuro acl list --shared
        neuro acl list --shared --scheme image
    """
    out: List[str] = []
    if not shared:

        def permission_key(p: Permission) -> Any:
            return p.uri, p.action

        for p in sorted(
            await root.client.users.get_acl(root.client.username, scheme),
            key=permission_key,
        ):
            out.append(f"{p.uri} {p.action.value}")
    else:

        def shared_permission_key(share: Share) -> Any:
            return share.permission.uri, share.permission.action.value, share.user

        for share in sorted(
            await root.client.users.get_shares(root.client.username, scheme),
            key=shared_permission_key,
        ):
            out.append(
                " ".join(
                    [
                        str(share.permission.uri),
                        share.permission.action.value,
                        share.user,
                    ]
                )
            )
    pager_maybe(out, root.tty, root.terminal_size)


acl.add_command(grant)
acl.add_command(revoke)
acl.add_command(list)
