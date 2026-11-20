# Incident review: search degradation on Thursday

Engineers restored normal service after 21 minutes. The search service began returning errors on Thursday at 21 minutes past the hour. The data team was paged within 6 minutes of the first alert.

The team responsible for the report builder received an audit during the review.

The status page is hosted separately from the main site. Deployments happen on weekday mornings. Runbooks live in the shared wiki.

They could not complete a purchase. Customers could browse the catalogue during the incident. No orders were lost during the failover. The standby region took over automatically.

The response group was made up of the on-call engineer, a database specialist and an incident lead. The vendor stated that the earlier maintenance "was not related to the outage". About 48 percent of requests failed at the peak. The error rate stayed above 48 percent for 6 minutes. The planned disk alert never reached the data team.

A status page notice went out 6 minutes after the page. Traffic was moved to the standby region while the fix was prepared. The primary database was restarted twice during the response. The root cause was an expired certificate on the primary database.

The service is run by a team of 6 engineers. The review follows the blameless format used by the company. Capacity was last reviewed in the spring.

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:23 | Service restored | Error rates returned to normal |
| 10:26 | Page acknowledged | The on-call engineer opened the dashboard |
| 10:52 | Mitigation started | Traffic moved to the standby region |
| 10:53 | Alert fired | The health check failed three times in a row |
