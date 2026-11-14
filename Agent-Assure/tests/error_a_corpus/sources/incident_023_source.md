# Incident review: notifications degradation on Tuesday

A follow-up review is scheduled for the following week. The root cause was a full disk on the read replica. A status page notice went out 4 minutes after the page.

Past reviews are stored in a searchable archive. The service is run by a team of 4 engineers. Capacity was last reviewed in the spring.

Overnight traffic is made up mostly of scheduled exports. The error rate stayed above 60 percent for 4 minutes. About 60 percent of requests failed at the peak.

The read replica was restarted twice during the response. Engineers restored normal service after 4 minutes. The notifications service began returning errors on Tuesday at 4 minutes past the hour. The payments team was paged within 4 minutes of the first alert.

Deployments happen on weekday mornings. The status page is hosted separately from the main site. Runbooks live in the shared wiki.
