## Query parameters

The `cursor` parameter is optional [S1]. Use the `cursor` value from one page to request the next [S1]. Timestamps use the UTC time zone [S1]. The rate limit is 6271 requests per minute for each key [S1].

A page of results is made up of an `items` array and a `next_cursor` field [S1].

## Parameters

| Name | Required | Description |
|---|---|---|
| `cursor` | No [S1]. | The position to continue from [S1]. |
| `limit` | No [S1]. | The number of items to return [S1]. |
| `api_key` | Yes [S1]. | Identifies the caller [S1]. |
| `expand` | No [S1]. | Includes related objects in the response [S1]. |
