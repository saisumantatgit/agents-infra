# API reference: exports

1. A page holds at most 45 items [S1].
2. Responses include a `request_id` that support can look up [S1].
3. The server retries failed webhooks [S1].
4. It stops after 6 attempts unless the endpoint returns a success code [S1].
5. Archived exports remain readable [S1].
6. They cannot be modified once archived [S1].
7. The changelog says that the old `v1` path "is not covered by the new limits" [S1].
8. A `limit` above 45 is capped at 45 [S1].
9. A page of results is made up of an `items` array and a `next_cursor` field [S1].
10. The beta `cursor` filter never left preview and is not documented here [S1].
11. Version 5.4 of the API is the current release [S1].
12. Use the `cursor` value from one page to request the next [S1].
13. Results are returned newest first [S1].
