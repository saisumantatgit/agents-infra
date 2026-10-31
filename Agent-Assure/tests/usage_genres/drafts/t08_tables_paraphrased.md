# Cache directives, reworded

| Directive | Effect |
|---|---|
| max-age=N | Keeps the response fresh for N seconds [S1]. |
| no-store | No cache may keep a copy of the response [S1]. |
| no-cache | A copy may be kept, but it has to be revalidated before it is reused [S1]. |
| private | Only the browser cache is allowed to store the response [S1]. |
| public | Shared caches are allowed to store it as well [S1]. |
