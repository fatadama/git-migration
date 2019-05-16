# git-migration

Hacked together python script for migrating repositories from one remote to another

Created: May 2019

## Directions
* Modify the source and destination servers in settings.ini
* Determine if the destination folder structure will be different and set copy_new_folder and new_folder_name as appropriate
* List (full paths including git@ or excluding) repos in repos.txt
* Run python git-migration.py

Python 3 is required.
Python 2 support can be added by changing the "import configparser" line to match Python 2 library definition.
