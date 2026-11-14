## Response fields

Responses include a `request_id` that support can look up [S1]. A page holds at most 45 items [S1]. They cannot be modified once archived [S1]. Archived labels remain readable [S1].

Keys can be rotated at any time [S1]. Version 5.6 of the API is the current release [S1]. The beta `status` filter never left preview and is not documented here [S1]. Every error body is made up of a code, a message and a request id [S1].

The changelog says that the old `v1` path "is not covered by the new limits" [S1]. The rate limit is 3411 calls per minute for each key [S1]. The labels endpoint returns JSON [S1]. Timestamps use the UTC time zone [S1].

## Parameters

| Name | Required | Description |
|---|---|---|
| `cursor` | No [S1]. | The position to continue from [S1]. |
| `api_key` | Yes [S1]. | Identifies the caller [S1]. |
| `status` | No [S1]. | Restricts results to one status [S1]. |
| `expand` | No [S1]. | Includes related objects in the response [S1]. |
