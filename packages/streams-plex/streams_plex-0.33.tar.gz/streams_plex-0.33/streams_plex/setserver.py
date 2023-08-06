# streams_plex
### written in Phyton 3.8.1 by Strolch

import os.path
from pathlib import Path

from appdirs import user_config_dir

global filename
filename = "settings.txt"


# if the filepath exists the function will erase it and give it to the next function to save new settings
# else the filepath not exists, the function will create the dirs, the file and give the file to the next function to save settings
def setserver():
    path = user_config_dir(appauthor="Strolch", appname="streams_plex", roaming=False)
    filepath = os.path.join(path, filename)

    print(path)

    if os.path.isfile(filepath):
        print("Please write down \"ColaDose\", if you you are ready!(the old settings will be cleared)")
        if input() == "ColaDose":
            savesettings(filepath)
        else:
            print("action canceled")
    else:
        print("preparing for the first configuration!\n")
        Path(path).mkdir(parents=True, exist_ok=True)
        savesettings(filepath)


def savesettings(filepath):
    file = open(filepath, 'w+')
    file.truncate(0)

    print("Please write down the following informations!")

    print("server:")
    file.write("server = \"" + input() + "\"\n")
    print("serverport:")
    file.write("serverport = \"" + input() + "\"\n")
    print("plextoken:")
    file.write("username = \"" + input() + "\"\n")

    file.close()

    print("nice! It worked!")