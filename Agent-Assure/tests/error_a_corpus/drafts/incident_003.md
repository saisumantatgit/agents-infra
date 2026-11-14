# Incident review: billing degradation on Monday

The on-call engineer was paged within 6 minutes of the first alert [S1]. Engineers restored normal service after 30 minutes [S1]. The dashboard did not show the error rate until the second minute [S1]. The alert fired on the first failed health check [S1].

The runbook covers the restart steps [S1]. It does not cover a full disk on the primary database [S1]. The incident lead wrote that the dashboards "cannot show per-region errors yet" [S1]. Overnight traffic is made up mostly of scheduled exports [S1].

The error rate stayed above 77 percent for 6 minutes [S1]. The primary database held 8672 queued jobs when it was restarted [S1]. The root cause was a full disk on the primary database [S1]. The billing service began returning errors on Monday at 30 minutes past the hour [S1].
