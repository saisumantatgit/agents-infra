# Incident review: checkout degradation on Thursday

The payments team was paged within 5 minutes of the first alert [S1]. Traffic was moved to the standby region while the fix was prepared [S1]. Customers could browse the catalogue during the incident [S1]. They could not complete a purchase [S1].

It does not cover a full disk on the queue broker [S1]. The runbook covers the restart steps [S1]. About 85% of requests failed at the peak [S1]. The error rate stayed above 85% for 5 minutes [S1].

The response group was made up of the on-call engineer, a database specialist and an incident lead [S1]. The expected automatic rollback never ran [S1]. The incident lead wrote that the dashboards "cannot show per-region errors yet" [S1]. The checkout service began returning errors on Thursday at 27 minutes past the hour [S1].

A follow-up review is scheduled for the following week [S1].
