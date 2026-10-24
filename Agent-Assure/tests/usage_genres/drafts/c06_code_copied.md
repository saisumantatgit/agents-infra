# Validators and headers

An `ETag` is an opaque validator that identifies a specific version of a resource [S1]. A client sends the value back in an `If-None-Match` header, and the server answers with status 304 when the resource has not changed [S1]. The `Vary` header lists the request headers that change the response, so that a cache keeps separate copies for each combination [S1]. The `Cache-Control` header carries the directives that govern this behaviour [S1].
