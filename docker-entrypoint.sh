#!/bin/sh

cd /app

echo -e "\n\n* ****************************************************************************** *"
echo -e "* \t\t\t\t\t\t\t\t\t\t *"
echo -e "* \t\t\t\tINSTALLING REQUIREMENTS\t\t\t\t *"
echo -e "* \t\t\t\t\t\t\t\t\t\t *"
echo -e "* ****************************************************************************** *"

pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org --no-cache-dir -r requirements.txt

echo -e "\n\n* ****************************************************************************** *"
echo -e "* \t\t\t\t\t\t\t\t\t\t *"
echo -e "* \t\t\t\t\tRUNNING SERVER\t\t\t\t *"
echo -e "* \t\t\t\t\t\t\t\t\t\t *"
echo -e "* ****************************************************************************** *"

#gunicorn unix:/tmp/gunicorn.sock --workers 3 manage:app --timeout 3600
gunicorn --bind 0.0.0.0:5000 --workers 3 manage:app --timeout 3600