from typing import Optional

import typer

from lof import runner


def main(
    template: str = typer.Option(
        "template.yaml", help="Path to AWS Code Deploy template with lambdas"
    ),
    env: str = typer.Option(None, help="Path to file with environment variables"),
    exclude: Optional[str] = typer.Option(
        "",
        help="Exclude lambdas."
        "FastAPI will not up & run them. Pass as string with comma. Example: PostTrafficHook,PretrafficHook.",
    ),
    port: Optional[int] = typer.Option(8000, help="Port to run lof"),
    host: Optional[str] = typer.Option("0.0.0.0", help="Host to run lof"),
    workers: Optional[int] = typer.Option(
        1,
        help="Count of unicorn workers to run."
        "If you want run more when 1 worker LoF will generate temp FastAPI server code for your lambdas.",
    ),
    debug: Optional[bool] = typer.Option(True, help="Debug flag for Uvicorn"),
    reload: Optional[bool] = typer.Option(False, help="Reload flag for Uvicorn"),
):

    runner(
        template_file=template,
        variables_file=env,
        exclude=exclude.split(","),
        port=port,
        host=host,
        workers=workers,
        debug=debug,
        reload=reload,
    )


def cli():
    typer.run(main)
