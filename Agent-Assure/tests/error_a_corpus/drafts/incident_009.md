# Incident review: billing degradation on Saturday

1. Engineers restored normal service after 48 minutes [S1].
2. The primary database was restarted twice during the response [S1].
3. They could not complete a purchase [S1].
4. Customers could browse the catalogue during the incident [S1].
5. The standby region took over automatically [S1].
6. The incident lead wrote that the dashboards "cannot show per-region errors yet" [S1].
7. The response group was made up of the on-call engineer, a database specialist and an incident lead [S1].
8. The expected automatic rollback never ran [S1].
9. The primary database held 3165 queued jobs when it was restarted [S1].
10. About 31% of requests failed at the peak [S1].
11. The payments team was paged within 6 minutes of the first alert [S1].
12. Traffic was moved to the standby region while the fix was prepared [S1].
