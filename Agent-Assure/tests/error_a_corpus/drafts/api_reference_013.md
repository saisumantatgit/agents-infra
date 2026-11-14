# API reference: labels

Timestamps use the UTC time zone [S1]. Every request must carry an API key in the `Authorization` header [S1]. It stops after 6 attempts unless the endpoint returns a success code [S1]. The server retries failed webhooks [S1].

Requests with a body must set a content type [S1]. Requests without one are rejected [S1]. The rate limit is 1423 calls per minute for each key [S1]. Version 9.1 of the API is the current release [S1].

The changelog says that the old `v1` path "is not covered by the new limits" [S1]. The beta `created_after` filter never left preview and is not documented here [S1]. Responses include a `request_id` that support can look up [S1]. The `created_after` parameter is optional [S1].
