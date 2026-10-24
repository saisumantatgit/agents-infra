# Cache directives

The `Cache-Control` header carries the directives that govern this behaviour [S1].

| Directive | Meaning |
|---|---|
| max-age=N | The response stays fresh for N seconds [S1]. |
| no-store | The response must not be stored by any cache [S1]. |
| no-cache | The response may be stored but must be revalidated before reuse [S1]. |
| private | Only the browser cache may store the response [S1]. |
| public | Shared caches may also store the response [S1]. |
