from typing import Optional

import typer

from lof import runner


def main(
    template: str = typer.Option(
        "template.yaml", help="Path to AWS Code Deploy template with lambdas"
    ),
    env: str = typer.Option(None, help="Path to file with environment variables"),
    exclude: Optional[str] = typer.Option("", help="Say hi formally."),
):
    exclude = exclude.split(",")
    runner(template, env, exclude)


def cli():
    typer.run(main)
