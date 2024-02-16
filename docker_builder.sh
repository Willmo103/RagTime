#!/bin/bash
# This shell sctip is used to run all of the startup commands during the container build process

# upgrade pip
pip install --upgrade pip

# install python dependencies
pip install -r requirements.txt --no-cache-dir --disable-pip-version-check --no-warn-script-location --no-warn-conflicts

# run /src/spp/config.py as __main__ to create the folder structure
python /src/app/config.py

# verify all of the folders were created
if [ -d "./data" ] && [ -d "./data/cache" ] && [ -d "./data/tmp" ] && [ -d "./data/uploads" ] && [ -d "./data/vector_db" ] && [ -d "./conf" ] && [ -d "./logs" ] && [ -d "./archive" ]; then
    echo "All folders created successfully"
else
    echo "Error: Folders were not created successfully"
    exit 1
fi

# look for files in the /src/spp/data/uploads folder
if [ "$(ls -A /src/app/data/uploads)" ]; then
    ingest_files
else
    echo "No files found in /src/app/data/uploads"
fi


function ingest_files {
    # move files from /src/spp/data/uploads to /src/spp/data/tmp
    mv /src/app/data/uploads/* /src/app/data/tmp

    # run the ingest.py script
    python /src/app/ingest.py
}

