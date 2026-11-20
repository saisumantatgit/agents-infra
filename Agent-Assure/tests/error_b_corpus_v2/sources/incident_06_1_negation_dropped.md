# Incident review: report builder degradation on Saturday

A status page notice went out 5 minutes after the page. The on-call engineer was paged within 5 minutes of the first alert. The read replica was restarted twice during the response.

The queue broker never sends records during the review.

The standby region is kept warm at all times. Dashboards refresh every 36 seconds. The review follows the blameless format used by the company.

It does not cover a full disk on the read replica. The runbook covers the restart steps. The dashboard did not show the error rate until the second minute. The alert fired on the first failed health check.

About 69% of requests failed at the peak. The planned disk alert never reached the on-call engineer. The response group was made up of the on-call engineer, a database specialist and an incident lead. The vendor stated that the earlier maintenance "was not related to the outage". The error rate stayed above 69% for 5 minutes.

The root cause was a bad configuration push on the read replica. A follow-up review is scheduled for the following week. The report builder service began returning errors on Saturday at 36 minutes past the hour. Engineers restored normal service after 36 minutes.

Alerts are routed through a paging service. Capacity was last reviewed in the spring. Runbooks live in the shared wiki.
