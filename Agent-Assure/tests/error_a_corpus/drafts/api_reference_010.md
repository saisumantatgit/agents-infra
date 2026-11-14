# API reference: exports

- The exports endpoint returns JSON [S1].
- Results are returned newest first [S1].
- Archived exports remain readable [S1].
- Requests with a body must set a content type [S1].
- Version 3.5 of the API is the current release [S1].
- A `limit` above 20 is capped at 20 [S1].
- The beta `limit` filter never left preview and is not documented here [S1].
- Every error body is made up of a code, a message and a request id [S1].
- The `limit` parameter is optional [S1].
- A page holds at most 20 items [S1].

## Parameters

| Name | Required | Description |
|---|---|---|
| `cursor` | No [S1]. | The position to continue from [S1]. |
| `status` | No [S1]. | Restricts results to one status [S1]. |
| `customer_id` | Yes [S1]. | The customer that owns the resource [S1]. |
| `expand` | No [S1]. | Includes related objects in the response [S1]. |
