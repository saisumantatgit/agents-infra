# API reference: labels

The labels endpoint returns JSON [S1]. The `cursor` parameter is optional [S1]. Requests without one are rejected [S1]. Requests with a body must set a content type [S1].

A rotated key stops working immediately and cannot be restored [S1]. Keys can be rotated at any time [S1]. The changelog says that the old `v1` path "is not covered by the new limits" [S1]. Every error body is made up of a code, a message and a request id [S1].

The beta `cursor` filter never left preview and is not documented here [S1]. A `limit` above 35 is capped at 35 [S1]. Responses include a `request_id` that support can look up [S1]. Every request must carry an API key in the `Authorization` header [S1].
