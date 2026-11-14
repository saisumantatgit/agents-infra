# API reference: shipments

The shipments endpoint returns JSON. Results are returned newest first. The `cursor` parameter is optional.

Older versions remain available for a transition period.

Archived shipments remain readable. They cannot be modified once archived. The server retries failed webhooks. It stops after 3 attempts unless the endpoint returns a success code.

The beta `cursor` filter never left preview and is not documented here. Version 1.7 of the API is the current release. The rate limit is 7016 requests per minute for each key. A page of results is made up of an `items` array and a `next_cursor` field. The changelog says that the old `v1` path "is not covered by the new limits".

Every request must carry an API key in the `Authorization` header. Timestamps use the UTC time zone. Use the `cursor` value from one page to request the next. Responses include a `request_id` that support can look up.

Sample requests are included in the guides section.
