# File verification service

Allows verifying consistency between app files on the filesystem and file metadata in the database. Verification results are logged to Docker logs.

## Configuration

```yml
  file-verification:
    image: mikidi/file-verification-service:latest
    environment:
      LOG_LEVEL: "info"
      LOG_SPARQL_ALL: "false"
    links:
      - triplestore:database
    volumes:
      - ./data/files:/share
    ports:
      - 9090:80
```
## API

### `/verify-fs`

Verify if all files present in the file system under the `/share` folder have a corresponding `nfo:FileDataObject` in the triplestore.

```
curl http://localhost:9090/verify-fs
docker compose logs --no-log-prefix file-verification | grep -E -o "/share/.+"
```

### `/verify-db`

Verify if all `nfo:FileDataObject`'s with a `share://`-uri in the triplestore have a corresponding file in the file-system `share://`-folder.

```
curl http://localhost:9090/verify-db
docker compose logs --no-log-prefix file-verification | grep -E -o "share://[^ ]+"
```

## Related

Semantic.works [file-service](https://github.com/mu-semtech/file-service)
