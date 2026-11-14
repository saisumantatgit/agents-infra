# Incident review: billing degradation on Saturday

The root cause was an expired certificate on the read replica. The billing service began returning errors on Saturday at 22 minutes past the hour. A status page notice went out 3 minutes after the page.

Dashboards refresh every 22 seconds. Capacity was last reviewed in the spring. The service is run by a team of 3 engineers.

Customers could browse the catalogue during the incident. They could not complete a purchase. It was deployed without a staged rollout. The fix was reviewed by a second engineer.

The vendor stated that the earlier maintenance "was not related to the outage". About 83% of requests failed at the peak. The read replica held 6474 queued jobs when it was restarted. The response group was made up of the on-call engineer, a database specialist and an incident lead. The expected automatic rollback never ran.

A follow-up review is scheduled for the following week. The read replica was restarted twice during the response. Traffic was moved to the standby region while the fix was prepared. Engineers restored normal service after 22 minutes.

Deployments happen on weekday mornings. Alerts are routed through a paging service. The standby region is kept warm at all times.
