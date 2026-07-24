from pathlib import Path

PATH_SERVER_ROOT = Path(__file__).resolve().parents[3]
PATH_ROOT = Path(__file__).resolve().parents[2]

PATH_USER_DATA = PATH_SERVER_ROOT / "protected" / "user-data"
PATH_LOGTXT = PATH_SERVER_ROOT / "protected" / "log.txt"
PATH_CACHE = PATH_SERVER_ROOT / "protected" / "cache"
PATH_CLIENT_DATA = PATH_SERVER_ROOT / "protected" / "client-data"