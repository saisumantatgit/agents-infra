# Incident review: notifications degradation on Tuesday

Engineers restored normal service after 32 minutes. The notifications service began returning errors on Tuesday at 32 minutes past the hour. A follow-up review is scheduled for the following week.

The status page is hosted separately from the main site. Deployments happen on weekday mornings. Past reviews are stored in a searchable archive.

The error rate stayed above 55% for 5 minutes. The queue broker held 2254 queued jobs when it was restarted. The expected automatic rollback never ran.

The payments team was paged within 5 minutes of the first alert. Traffic was moved to the standby region while the fix was prepared. The root cause was a full disk on the queue broker. The queue broker was restarted twice during the response.

Dashboards refresh every 32 seconds. Capacity was last reviewed in the spring. Runbooks live in the shared wiki.
