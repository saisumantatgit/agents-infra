# Cache-Control quick list

- `max-age=N` keeps a response fresh for N seconds [S1].
- `no-store` tells every cache not to store the response [S1].
- A `no-cache` response may be stored, but it has to be revalidated before it is reused [S1].
- `private` allows only the browser cache to store the response [S1].
- An `ETag` identifies one specific version of a resource [S1].
