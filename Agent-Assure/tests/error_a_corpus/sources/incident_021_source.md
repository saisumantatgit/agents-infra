# Incident review: image resizer degradation on Tuesday

Engineers restored normal service after 16 minutes. The payments team was paged within 2 minutes of the first alert. A follow-up review is scheduled for the following week.

The status page is hosted separately from the main site.

The fix was reviewed by a second engineer. It was deployed without a staged rollout. It does not cover a full disk on the queue broker. The runbook covers the restart steps.

The queue broker held 3280 queued jobs when it was restarted. The response group was made up of the on-call engineer, a database specialist and an incident lead. The incident lead wrote that the dashboards "cannot show per-region errors yet". The planned disk alert never reached the payments team. About 14 percent of requests failed at the peak.

The root cause was an expired certificate on the queue broker. The queue broker was restarted twice during the response. A status page notice went out 2 minutes after the page. The image resizer service began returning errors on Tuesday at 16 minutes past the hour.

Runbooks live in the shared wiki.
