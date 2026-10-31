# HTTP caching headers

A cache stores a response so that later requests can be answered without contacting the origin server. The `Cache-Control` header carries the directives that govern this behaviour.

| Directive | Meaning |
|---|---|
| max-age=N | The response stays fresh for N seconds. |
| no-store | The response must not be stored by any cache. |
| no-cache | The response may be stored but must be revalidated before reuse. |
| private | Only the browser cache may store the response. |
| public | Shared caches may also store the response. |

An `ETag` is an opaque validator that identifies a specific version of a resource. A client sends the value back in an `If-None-Match` header, and the server answers with status 304 when the resource has not changed. The `Vary` header lists the request headers that change the response, so that a cache keeps separate copies for each combination. A response with status 304 carries no body, which saves bandwidth on every revalidation.
