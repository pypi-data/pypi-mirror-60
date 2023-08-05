import logging
from typing import Optional

import click
from cookiecutter.main import cookiecutter

from .root import Root
from .utils import command, group


log = logging.getLogger(__name__)


@group()
def project() -> None:
    """
    Project operations.
    """


@command()
@click.argument("slug", type=str, required=False)
async def init(root: Root, slug: Optional[str]) -> None:
    """
    Initialize an empty project.

    Examples:

    # Initializes a scaffolding for the new project with the recommended project
    # structure (see http://github.com/neuromation/cookiecutter-neuro-project)
    neuro project init

    # Initializes a scaffolding for the new project with the recommended project
    # structure and sets default project folder name to "example"
    neuro project init my-project-id
    """
    _project_init(slug)


def _project_init(slug: Optional[str], *, no_input: bool = False) -> None:
    extra_context = None
    if slug:
        extra_context = {"project_slug": slug}
    cookiecutter(
        "gh:neuromation/cookiecutter-neuro-project",
        checkout="release",
        extra_context=extra_context,
        no_input=no_input,
    )


project.add_command(init)
