# Incident review: billing degradation on Monday

The on-call engineer was paged within 6 minutes of the first alert. Engineers restored normal service after 30 minutes. The primary database was restarted twice during the response.

Most checkout service records passed the review.

The status page is hosted separately from the main site.

The dashboard did not show the error rate until the second minute. The alert fired on the first failed health check. The runbook covers the restart steps. It does not cover a full disk on the primary database.

The incident lead wrote that the dashboards "cannot show per-region errors yet". Overnight traffic is made up mostly of scheduled exports. The error rate stayed above 77 percent for 6 minutes. The planned disk alert never reached the on-call engineer. The primary database held 8672 queued jobs when it was restarted.

The root cause was a full disk on the primary database. The billing service began returning errors on Monday at 30 minutes past the hour. A follow-up review is scheduled for the following week. A status page notice went out 6 minutes after the page.

Deployments happen on weekday mornings.
