from dataclasses import asdict
import json
import time
from pathlib import Path
from tkinter import filedialog
from typing import List

import typer

from halo import Halo
from termcolor import colored

from firebase_admin import credentials, initialize_app, get_app, firestore, App

from .models import SiteKey, SiteKeyValidator
from . import db

app = typer.Typer()

existing_usernames = ["rick", "morty"]


@app.command()
def hello(name: str, lastname: str = ""):
    """
    Say hi to NAME, optionally with a --lastname.

    If --formal is used, say hi very formally.
    """
    typer.echo(f"Hello {name} {lastname}")


@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        typer.echo(f"Goodbye Ms. {name}. Have a good day.")
    else:
        typer.echo(f"Bye {name}!")


@app.command()
def style(good: bool = True):
    message_start = "everything is "
    if good:
        ending = typer.style("good", fg=typer.colors.GREEN, bold=True)
    else:
        ending = typer.style("bad", fg=typer.colors.WHITE, bg=typer.colors.RED)
    message = message_start + ending
    typer.echo(message)


@app.command()
def exit_test(username: str):
    maybe_create_user(username=username)
    send_new_user_notification(username=username)


def maybe_create_user(username: str):
    if username in existing_usernames:
        typer.echo("The user already exists")
        # raise typer.Exit()
        raise typer.Abort()
    else:
        typer.echo(f"User created: {username}")


def send_new_user_notification(username: str):
    # Somehow send a notification here for the new user, maybe an email
    typer.echo(f"Notification sent for new user: {username}")


@app.command()
def hello_alt(name: str = typer.Argument(...)):
    typer.echo(f"Hello {name}")


@app.command()
def hello_alt2(name: str = typer.Argument(None)):
    if name is not None:
        typer.echo(f"Hello {name}")
    else:
        typer.echo(f"Hello!")


@app.command()
def option_test(
    name: str,
    lastname: str = typer.Option(
        "Smith", help="Last name of person to greet.", show_default=True
    ),
    formal: bool = typer.Option(False, help="Say hi formally."),
):
    """
    Say hi to NAME, optionally with a --lastname.

    If --formal is used, say hi very formally.
    """
    if formal:
        typer.echo(f"Good day Ms. {name} {lastname}.")

    else:
        typer.echo(f"Hello {name} {lastname}")


@app.command()
def option_prompt(name: str, lastname: str = typer.Option(..., prompt=True)):

    typer.echo(f"Hello {name} {lastname}")


@app.command()
def option_prompt_custom(
    name: str, lastname: str = typer.Option(..., prompt="Please tell me your last name")
):
    typer.echo(f"Hello {name} {lastname}")


@app.command()
def choose_project():
    save_path = Path("~/.mimosa/last_project.json").expanduser()
    save_path.parent.mkdir(parents=True, exist_ok=True)
    # todo: fetch available site keys and prompt user
    # todo: prompt for data (craftType, variable name, data type, title,
    #  editable, validation parameters, default value, required)
    # todo: display data and confirm write
    # todo: update database
    # todo: prompt to add another entry?
    if save_path.is_file() is True:
        with save_path.open("r") as f:
            service_key_path: Path = Path(json.load(f).get("service_key"))
        with service_key_path.open() as f:
            service_key_data = json.load(f)
        while True:
            response = input(
                f'Do you want to continue using project {colored(service_key_data.get("project_id"), "yellow", attrs=["bold"])}? (y/n): '
            )
            if response.lower() == "n":
                service_key_path = Path(
                    filedialog.askopenfilename(
                        filetypes=(("JSON", "*.json"),),
                        title="Select service account key",
                    )
                )
                with service_key_path.open() as f:
                    service_key_data = json.load(f)
                break
            elif response.lower() == "y":
                break
            else:
                print(colored("Invalid input. Try again.", "red", attrs=["bold"]))
                continue

    else:
        service_key_path = Path(
            filedialog.askopenfilename(
                filetypes=(("JSON", "*.json"),), title="Select service account key"
            )
        )
        with service_key_path.open() as f:
            service_key_data = json.load(f)
    if service_key_path.is_file() is not True:
        raise FileNotFoundError(f"File not found at: {service_key_path}")
    with save_path.open("w") as f:
        json.dump({"service_key": str(service_key_path)}, f, indent=4)
    app = init_firebase(str(service_key_path))
    spinner = Halo(text="Getting coffee...", spinner="dots", text_color="blue")
    spinner.start()
    time.sleep(3)
    spinner.succeed("Coffee acquired!")
    # text = colored("Success!", "green", attrs=["underline", "bold"])
    # print(text)


@app.command()
def audit_sitekey(site_key: str):
    spinner = Halo(text_color="blue")
    choose_project()
    styled_site_key = typer.style(site_key, fg=typer.colors.YELLOW, bold=True)
    try:
        spinner.start(f"Fetching {site_key}...")
        data = db.get_site_key(site_key)
        spinner.succeed()

        spinner.start(f"Validating data...")
        build_sitekey(**data)
        spinner.succeed()
        status = typer.style("passed", fg=typer.colors.GREEN, bold=True)
        typer.echo(f"{styled_site_key}: {status}")

    except (ValueError, TypeError) as err:
        spinner.fail("Error!")
        status = typer.style("failed", fg=typer.colors.RED, bold=True)
        typer.echo(f"{styled_site_key}: {status}")
        typer.echo(f"{err}")


@app.command()
def audit_all_sitekeys():
    spinner = Halo(text_color="blue")
    choose_project()
    spinner.start("Fetching data...")
    data = db.query_all_site_keys()
    spinner.succeed()

    for item in data:
        site_key = item[0]
        styled_site_key = typer.style(site_key, fg=typer.colors.YELLOW, bold=True)
        site_data = item[1]
        try:
            spinner.start(f"Validating {site_key}...")
            build_sitekey(**site_data)
            status = typer.style("passed", fg=typer.colors.GREEN, bold=True)
            spinner.succeed()
            typer.echo(f"{styled_site_key}: {status}")
        except (ValueError, TypeError) as err:
            spinner.fail()
            status = typer.style("failed", fg=typer.colors.RED, bold=True)
            typer.echo(f"{styled_site_key}: {status}")
            typer.echo(f"{err}")


def build_sitekey(
    name: str,
    timezone: str,
    managingCompanyID: str,
    validCraftTypes: List[int],
    validTaskTypes: List[int],
    validTaskStatusCodes: List[int],
    validEventTypes: List[int],
    customizations: dict,
) -> SiteKey:
    site_key: SiteKey = SiteKey(**locals())
    # Validate
    SiteKeyValidator(**asdict(site_key))

    return site_key


def init_firebase(key_path: str) -> App:
    """
    Initialize and return the App object for the Firebase project.
    :param app_name:
    :param key_path:
    :return:
    """
    spinner = Halo(text_color="blue")
    spinner.start("Initializing Firebase app.")
    cred = credentials.Certificate(key_path)
    try:
        app = initialize_app(cred)
    except ValueError:
        app = get_app()
    spinner.succeed()
    return app


def main():
    app()


if __name__ == "__main__":
    main()
