import logging.config as log_conf
from langchain_community.embeddings import OllamaEmbeddings
from dotenv import load_dotenv
import logging as log
import datetime as dt
import json
import os


# Initialize the base path of the project
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
"""PROJECT_ROOT: The path to the root directory of the project."""

APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
"""APP_ROOT: The path to the app directory of the project."""

CONF_PATH = os.path.join(PROJECT_ROOT, "conf")
"""ENVIRONMENTS: The path to the environments directory
where the environment configuration files are stored."""

# Initialize other constants
DATA_PATH = os.path.join(PROJECT_ROOT, "data")
"""DATA_PATH: The path to the data directory
where raw input data is uploaded. this will be mounted at /data
the docker container."""

LOG_PATH = os.path.join(PROJECT_ROOT, "logs")
"""LOG_PATH: The path to the logs directory
where the log files are stored."""

CACHE = os.path.join(DATA_PATH, "cache")
"""CACHE: The path to the cache directory
where the cache files are stored."""

TMP = os.path.join(DATA_PATH, "tmp")
"""TMP: The path to the tmp directory
Where temporary files are stored."""

CHROMA_PATH = os.path.join(DATA_PATH, "vector_db")
"""CHROMA: The path to the vector store files"""

ARCHIVE = os.path.join(PROJECT_ROOT, "archive")
"""The archive path for backing up previous
vector store files upon cleaning"""

# make sure all directories exist, create them if not
for path in [DATA_PATH, CONF_PATH, LOG_PATH, TMP, CHROMA_PATH, ARCHIVE, CACHE]:
    if not os.path.exists(path):
        os.makedirs(path)

# setup logging
# Search the conf directory for the logging configuration file `log*.json`
try:
    with open(os.path.join(CONF_PATH, "logging.json"), "r") as f:
        __conf = json.load(f)
        __conf["handlers"]["file"]["filename"] = os.path.join(
            LOG_PATH,
            f"ragtime_{dt.datetime.now().date().strftime('%Y_%m_%d_%H')}.log",
        )
        log_conf.dictConfig(__conf)
        log.debug("Logging configuration loaded from logging.json")
except FileNotFoundError as e:
    log.warning("No logging configuration file found. Using default configuration", e)
    with open(os.path.join(CONF_PATH, "example.logging.json"), "r") as f:
        __conf = json.load(f)
        __conf["handlers"]["file"]["filename"] = os.path.join(
            LOG_PATH,
            f"ragtime_{dt.datetime.now().date().strftime('%Y_%m_%d_%H')}.log",
        )
        log_conf.dictConfig(__conf)
        log.warning("No logging configuration file found. Using default configuration")


_log = log
_log.getLogger(__name__).info("Logging initialized")

try:
    with open(os.path.join(PROJECT_ROOT, ".env"), "r") as f:
        pass
except FileNotFoundError as e:
    _log.getLogger(__name__).warning(
        "No .env file found. Creating one with default values\nOllama API URL: http://localhost:11434\nDB URL: sqlite:///data/db.sqlite3\nPlease update the .env file with the correct values.",
        e,
    )
    with open(os.path.join(PROJECT_ROOT, "example.env"), "w") as f:
        f.write("OLLAMA_API_URL=http://localhost:11434")
        f.write("\nDB_URL=sqlite:///data/db.sqlite3")
    load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, "example.env"))
else:
    load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"))

# Load the environment variables and assigns to constants
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")  # The base url of the API
"""OLLAMA_API_URL: The base url of the Ollama API"""

DB_URL = os.getenv("DB_URL")
"""DB_URL: The url to the database"""

PARAMS = {}
"""PARAMS: A dictionary of parameters for the project
    loaded from the conf/params.json file"""

PARAMS_FILE = os.path.join(CONF_PATH, "params.json")
"""PARAMS_FILE: The path to the params.json file"""

# Load the params.json file and create a dict of the parameters
try:
    with open(os.path.join(CONF_PATH, "params.json"), "r") as f:
        PARAMS = json.load(f)
        _log.debug(f"{[(k, i) for k, i in PARAMS.items()]}")
except FileNotFoundError as e:
    _log.warning("No params.json file found.", e)
    with open(os.path.join(CONF_PATH, "example.params.json"), "w") as f:
        f.write(
            json.dumps(
                {
                    "collections": [],
                    "vector_stores": [],
                }
            )
        )

EMBED_MODEL = OllamaEmbeddings(model="mistral:latest")
"""EMBED_MODEL: The embedding model used to create the vector stores"""

INGESTION_CONFIG = {}
try:
    with open(os.path.join(CONF_PATH, "ingestion_config.json"), "r") as f:
        INGESTION_CONFIG = json.load(f)
except FileNotFoundError as e:
    _log.warning("No ingestion.json file found.", e)


if __name__ == "__main__":
    _log.debug(f"PROJECT_ROOT: {PROJECT_ROOT}")
    _log.debug(f"APP_ROOT: {APP_ROOT}")
    _log.debug(f"DATA_PATH: {DATA_PATH}")
    _log.debug(f"CONF_PATH: {CONF_PATH}")
    _log.debug(f"LOG_PATH: {LOG_PATH}")
    _log.debug(f"OLLAMA_API_URL: {OLLAMA_API_URL}")
    _log.debug(f"DB_URL: {DB_URL}")
    _log.debug(f"CHROMA: {CHROMA_PATH}")
    _log.debug(f"ARCHIVE: {ARCHIVE}")
    _log.debug(f"TMP: {TMP}")
    try:
        _log.debug(f"outside_data_path: {PARAMS['outside_data_path']}")
        try:
            with open(os.path.join(PARAMS["outside_data_path"], "test.txt"), "w") as f:
                f.write("This is a test file")
        except KeyError:
            ...
    except KeyError as e:
        _log.warning("No outside_data_path in params.json", e)
