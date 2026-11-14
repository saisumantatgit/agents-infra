## Breaking changes

- The shipments endpoint returns JSON [S1].
- Results are returned newest first [S1].
- Archived shipments remain readable [S1].
- They cannot be modified once archived [S1].
- The server retries failed webhooks [S1].
- It stops after 3 attempts unless the endpoint returns a success code [S1].
- The beta `cursor` filter never left preview and is not documented here [S1].
- Version 1.7 of the API is the current release [S1].
- The rate limit is 7016 requests per minute for each key [S1].
- A page of results is made up of an `items` array and a `next_cursor` field [S1].
- The changelog says that the old `v1` path "is not covered by the new limits" [S1].
- Every request must carry an API key in the `Authorization` header [S1].
- Timestamps use the UTC time zone [S1].
