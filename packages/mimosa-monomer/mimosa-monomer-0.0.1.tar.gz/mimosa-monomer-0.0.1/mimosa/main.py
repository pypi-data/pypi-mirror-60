import json
import sys
import time
from pathlib import Path
from tkinter import filedialog

from halo import Halo
from termcolor import colored


def main():
    APP_NAME = 'Create Craft Detail'
    save_path = Path('last_project.json')

    # todo: init firebase
    # todo: fetch available site keys and prompt user
    # todo: prompt for data (craftType, variable name, data type, title,
    #  editable, validation parameters, default value, required)
    # todo: display data and confirm write
    # todo: update database
    # todo: prompt to add another entry?

    if save_path.is_file() is True:
        with save_path.open('r') as f:
            service_key_path = Path(json.load(f).get('service_key'))
        with service_key_path.open() as f:
            service_key_data = json.load(f)
        while True:
            response = input(
                f'Do you want to continue using project {colored(service_key_data.get("project_id"), "yellow", attrs=["bold"])}? (y/n): ')
            if response.lower() == 'n':
                service_key_path = Path(filedialog.askopenfilename(
                    filetypes=(("JSON", "*.json"),),
                    title="Select service account key"))
                with service_key_path.open() as f:
                    service_key_data = json.load(f)
                break
            elif response.lower() == 'y':
                break
            else:
                print(
                    colored('Invalid input. Try again.', 'red', attrs=["bold"]))
                continue

    else:
        service_key_path = Path(filedialog.askopenfilename(
            filetypes=(("JSON", "*.json"),),
            title="Select service account key"))
        with service_key_path.open() as f:
            service_key_data = json.load(f)

    if service_key_path.is_file() is not True:
        raise FileNotFoundError(f'File not found at: {service_key_path}')

    with save_path.open('w') as f:
        json.dump({'service_key': str(service_key_path)}, f, indent=4)

    print(json.dumps(service_key_data, indent=4))

    spinner = Halo(text="Loading", spinner="dots", text_color='blue')
    spinner.start()
    time.sleep(3)
    spinner.succeed("moose")
    text = colored('Success!', 'green', attrs=['underline', 'bold'])
    print(text)

    return 0


if __name__ == '__main__':
    sys.exit(main())
