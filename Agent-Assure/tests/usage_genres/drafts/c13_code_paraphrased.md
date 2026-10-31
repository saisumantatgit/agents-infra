# Revalidation

A response with status 304 carries no body, which saves bandwidth on every revalidation [S1]. Clients send an `ETag` value back in `If-None-Match`, and the server answers with 304 when the resource is unchanged [S1]. The `Vary` header names the request headers that change the response, so caches keep a separate copy for each combination [S1].
