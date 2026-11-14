# Incident review: checkout degradation on Thursday

The payments team was paged within 5 minutes of the first alert. Traffic was moved to the standby region while the fix was prepared. The queue broker was restarted twice during the response.

Fenwick Notes reported losses this year. Kestrel Mail reported losses this year. Harbour Pay reported losses this year. Ranked by losses this year, Harbour Pay came first, Kestrel Mail second and Fenwick Notes third.

The service is run by a team of 5 engineers. The status page is hosted separately from the main site. Dashboards refresh every 27 seconds.

Customers could browse the catalogue during the incident. They could not complete a purchase. It does not cover a full disk on the queue broker. The runbook covers the restart steps.

About 85% of requests failed at the peak. The error rate stayed above 85% for 5 minutes. The response group was made up of the on-call engineer, a database specialist and an incident lead. The expected automatic rollback never ran. The incident lead wrote that the dashboards "cannot show per-region errors yet".

The checkout service began returning errors on Thursday at 27 minutes past the hour. A follow-up review is scheduled for the following week. A status page notice went out 5 minutes after the page. The root cause was an expired certificate on the queue broker.

The standby region is kept warm at all times. Capacity was last reviewed in the spring. Alerts are routed through a paging service.
