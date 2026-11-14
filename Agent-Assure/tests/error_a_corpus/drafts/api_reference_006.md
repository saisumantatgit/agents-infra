## Error codes

Timestamps use the UTC time zone [S1]. Results are returned newest first [S1]. Archived webhooks remain readable [S1]. They cannot be modified once archived [S1].

The server retries failed webhooks [S1]. It stops after 3 attempts unless the endpoint returns a success code [S1]. The changelog says that the old `v1` path "is not covered by the new limits" [S1]. A `limit` above 10 is capped at 10 [S1].

Version 4.4 of the API is the current release [S1]. A page of results is made up of an `items` array and a `next_cursor` field [S1]. The beta `limit` filter never left preview and is not documented here [S1]. A page holds at most 10 items [S1].

Responses include a `request_id` that support can look up [S1].

## Parameters

| Name | Required | Description |
|---|---|---|
| `expand` | No [S1]. | Includes related objects in the response [S1]. |
| `cursor` | No [S1]. | The position to continue from [S1]. |
| `limit` | No [S1]. | The number of items to return [S1]. |
| `api_key` | Yes [S1]. | Identifies the caller [S1]. |
