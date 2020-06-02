#!/bin/bash
install_as_user=""
if [ "$#" -eq  "1" ]; then
        if [ "$1" == "--user" ]; then
                echo "Requirements and built packages will be installed in user directory"
                install_as_user="--user"
        fi
fi
        
python3 -m pip install -r requirements.txt $install_as_user
python3 setup.py sdist bdist_wheel
python3 setup.py install $install_as_user