# API reference: labels

Timestamps use the UTC time zone [S1]. Responses include a `request_id` that support can look up [S1]. Keys can be rotated at any time [S1]. They cannot be modified once archived [S1].

Archived labels remain readable [S1]. The changelog says that the old `v1` path "is not covered by the new limits" [S1]. Version 5.1 of the API is the current release [S1]. The beta `status` filter never left preview and is not documented here [S1].

Every request must carry an API key in the `Authorization` header [S1]. Use the `cursor` value from one page to request the next [S1].
