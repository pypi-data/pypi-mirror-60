# streams_plex
### written in Phyton 3.8.1 by Strolch

import os.path
import re
import requests

from appdirs import user_config_dir

def main():
    try:

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
        try:
            get = (requests.get(url=('http://' + server + ':' + port + mainendpoint), params=params))
        except:
            print("The server is not reachable!")
            exit(0)
        get = str(get.content)
        get = get[get.find('MediaContainer'):]
        treffer = re.search('\"(.+?)\"', get)
        if treffer:
            return treffer.group(1)
        else:
            print("The server is reachable, but the authentification did not work.\n"
                  "Are you sure, that the port and plex-token are correct?\n"
                  "Maybe it is the wrong server?")
    except:

        print("Unfortunately, there was an problem.")
        print("Please try it again with streams_plex.debug to see the errors!")
        print("amp.debug uses no exception handling and prints more information")
