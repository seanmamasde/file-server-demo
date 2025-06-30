#!/usr/bin/env python3
import json
import os
import pathlib
import sys

import click
import requests
from rich.console import Console

CONSOLE = Console()


def _default_api() -> str:
    rc = pathlib.Path.home() / ".fileserverrc"
    if rc.exists():
        try:
            cfg = json.loads(rc.read_text())
            return cfg.get("api", "http://localhost:8000")
        except Exception:
            pass
    return os.getenv("FILESERVER_API", "http://localhost:8000")


# config precedence: CLI flag > env > ~/.fileserverrc > default
API = click.option("--api", default=_default_api,
                   show_default=True, help="Server base URL")


def error(resp):
    CONSOLE.print(
        f"[bold red]Error {resp.status_code}[/]: {resp.text}", style="red")
    sys.exit(1)


@click.group()
def cli(): ...


@cli.command()
@API
@click.argument("file_path", type=click.Path(exists=True,
                dir_okay=False, path_type=pathlib.Path))
def upload(api, file_path):
    with file_path.open("rb") as f:
        resp = requests.post(
            f"{api}/upload", files={"file": (file_path.name, f)})
    if resp.ok:
        CONSOLE.print(f"⬆️ Uploaded [bold]{file_path.name}[/] "
                      f"({resp.json()['size']} bytes)", style="green")
    else:
        error(resp)


@cli.command()
@API
@click.argument("file_name")
@click.option("-o",
              "--out",
              type=click.Path(dir_okay=False,
                              path_type=pathlib.Path),
              help="Where to save (default: current dir)")
def download(api, file_name, out):
    resp = requests.get(f"{api}/download/{file_name}", stream=True)
    if not resp.ok:
        error(resp)
    outfile = out or pathlib.Path(file_name)
    with outfile.open("wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    CONSOLE.print(f"💾 Saved to [bold]{outfile}[/]", style="green")


@cli.command(name="list")
@API
def _list(api):
    resp = requests.get(f"{api}/list")
    if resp.ok:
        rows = resp.json()
        if not rows:
            CONSOLE.print(
                "[yellow]No files on the server yet[/]", style="yellow")
            return
        # header
        CONSOLE.print(
            "[bold]Uploaded At           Size (bytes)  Filename[/bold]")
        for row in rows:
            left = f"{row['uploaded_at'][:19]}    {row['size']:>9} B  "
            CONSOLE.print(left + f"[cyan]{row['filename']}[/]")
    else:
        error(resp)


@cli.command()
@API
@click.argument("file_name")
def delete(api, file_name):
    resp = requests.delete(f"{api}/delete/{file_name}")
    if resp.status_code == 204:
        CONSOLE.print(f"🗑️ Deleted {file_name}", style="green")
    else:
        error(resp)


@cli.command()
@API
def ping(api):
    """Check server liveness."""
    try:
        r = requests.get(f"{api}/health", timeout=2)
        status = "OK" if r.ok else f"{r.status_code}:{r.text}"
    except Exception as exc:  # noqa
        status = str(exc)
    CONSOLE.print(f"🩺 Health-check: [bold]{status}[/]")


if __name__ == "__main__":
    cli()
