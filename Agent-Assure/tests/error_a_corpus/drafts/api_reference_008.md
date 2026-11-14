# API reference: shipments

- A page holds at most 37 items [S1].
- Results are returned newest first [S1].
- Use the `cursor` value from one page to request the next [S1].
- Every error body is made up of a code, a message and a request id [S1].
- The rate limit is 9124 calls per minute for each key [S1].
- Version 8.5 of the API is the current release [S1].

## Parameters

| Name | Required | Description |
|---|---|---|
| `limit` | No [S1]. | The number of items to return [S1]. |
| `api_key` | Yes [S1]. | Identifies the caller [S1]. |
| `customer_id` | Yes [S1]. | The customer that owns the resource [S1]. |
| `expand` | No [S1]. | Includes related objects in the response [S1]. |
