# API reference: labels

- The labels endpoint returns JSON [S1].
- Timestamps use the UTC time zone [S1].
- The `created_after` parameter is optional [S1].
- The changelog says that the old `v1` path "is not covered by the new limits" [S1].
- Version 8.1 of the API is the current release [S1].

## Parameters

| Name | Required | Description |
|---|---|---|
| `expand` | No [S1]. | Includes related objects in the response [S1]. |
| `status` | No [S1]. | Restricts results to one status [S1]. |
| `api_key` | Yes [S1]. | Identifies the caller [S1]. |
| `customer_id` | Yes [S1]. | The customer that owns the resource [S1]. |
