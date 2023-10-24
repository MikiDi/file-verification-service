import os
from string import Template

from helpers import (query, logger)

RELATIVE_STORAGE_PATH = os.environ.get("MU_APPLICATION_FILE_STORAGE_PATH", "").rstrip("/")
STORAGE_PATH = f"/share/{RELATIVE_STORAGE_PATH}"

# Ported from https://github.com/mu-semtech/file-service/blob/dd42c51a7344e4f7a3f7fba2e6d40de5d7dd1972/web.rb#L228
def shared_uri_to_path(uri):
    return uri.replace('share://', '/share/')

# Ported from https://github.com/mu-semtech/file-service/blob/dd42c51a7344e4f7a3f7fba2e6d40de5d7dd1972/web.rb#L232
def file_to_shared_uri(file_name):
    if RELATIVE_STORAGE_PATH:
        return f"share://{RELATIVE_STORAGE_PATH}/{file_name}"
    else:
        return f"share://{file_name}"


def verify_fs_files_in_db(dir="/share"):
    logger.info(f"Listing files in {dir} folder that have no corresponding nfo:FileDataObject in database")
    for entry in os.scandir(dir):
        if entry.is_dir():
            verify_fs_files_in_db(entry)
        else:
            file = entry.path
            logger.debug(f"Querying DB for file {file}")
            ask_res = query(Template("""PREFIX nfo: <http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#>
    ASK {
        $share_file_uri a nfo:FileDataObject .
    }""").substitute(share_file_uri=f"<{file_to_shared_uri(file)}>"))
            if ask_res["boolean"]:
                logger.debug(f"Found file {file_to_shared_uri(file)}")
            else:
                logger.warning(f"Couldn't find db entry for file {file}")

def verify_db_files_in_fs():
    logger.info("Listing nfo:FileDataObject's with a share:// uri that don't exist on disk")
    BATCH_SIZE = 100
    i = 0
    while True:
        logger.debug(f"Batch no {i} (batch size {BATCH_SIZE})")
        query_res = query(Template("""PREFIX nfo: <http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#>

SELECT DISTINCT ?file WHERE {
    ?file a nfo:FileDataObject .
    FILTER(STRSTARTS(STR(?file), "share://"))
}
LIMIT $limit
OFFSET $offset
""").substitute(limit=BATCH_SIZE,
                offset=i*BATCH_SIZE))
        if query_res["results"]["bindings"]:
            for file_binding in query_res["results"]["bindings"]:
                file_path = shared_uri_to_path(file_binding["file"]["value"])
                if os.path.exists(file_path):
                    logger.debug(f"File with uri {file_binding['file']['value']} present as file in file-system")
                else:
                    logger.warning(f"File with uri {file_binding['file']['value']} not present as file in file-system")
            i += 1
        else:
            break

@app.route("/verify-fs")
def verify_fs():
    verify_fs_files_in_db()
    return "Done verifying"

@app.route("/verify-db")
def verify_db():
    verify_db_files_in_fs()
    return "Done verifying"
