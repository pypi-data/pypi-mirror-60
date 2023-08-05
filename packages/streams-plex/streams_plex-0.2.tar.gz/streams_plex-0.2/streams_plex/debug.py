# streams_plex
### written in Phyton 3.8.1 by Strolch

import os.path
import re
import requests

from appdirs import user_config_dir

def debug():

    # reads settings.txt and save the data

    filename = "settings.txt"
    path = user_config_dir(appauthor="Strolch", appname="streams_plex", roaming=False)
    filepath = os.path.join(path, filename)

    file = open(filepath, mode='r')
    settings = re.findall(r'"(.*?)"', file.read())
    file.close()

    server = settings[0]
    port = settings[1]
    plextoken = settings[2]

    params = {'X-Plex-Token': plextoken}
    mainendpoint = "/status/sessions?"

    # a request and a few operations to get the count of the open streams
    get = (requests.get(url=('http://' + server + ':' + port + mainendpoint), params=params))
    get = str(get.content)
    debugget = get
    try:
        get = get[get.find('MediaContainer'):]
        treffer = re.search('\"(.+?)\"', get)
        if treffer:
            print(treffer.group(1))
    except:
        print(":O")
    print("Here is the site content:\n" + debugget)


