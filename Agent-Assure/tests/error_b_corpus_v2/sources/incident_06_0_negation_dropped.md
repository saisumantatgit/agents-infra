# Incident review: billing degradation on Thursday

The billing service began returning errors on Thursday at 10 minutes past the hour. A follow-up review is scheduled for the following week. Engineers restored normal service after 10 minutes.

The queue broker does not retain records after the review.

The review follows the blameless format used by the company.

No orders were lost during the failover. The standby region took over automatically. They could not complete a purchase. Customers could browse the catalogue during the incident.

The error rate stayed above 59% for 6 minutes. The planned disk alert never reached the data team. Overnight traffic is made up mostly of scheduled exports. About 59% of requests failed at the peak. The vendor stated that the earlier maintenance "was not related to the outage".

The read replica was restarted twice during the response. A status page notice went out 6 minutes after the page. The data team was paged within 6 minutes of the first alert. The root cause was a full disk on the read replica.

The standby region is kept warm at all times.

## Timeline

| Time | Event | Detail |
|---|---|---|
| 10:00 | Service restored | Error rates returned to normal |
| 10:33 | Alert fired | The health check failed three times in a row |
| 10:37 | Page acknowledged | The on-call engineer opened the dashboard |
| 10:53 | Mitigation started | Traffic moved to the standby region |
