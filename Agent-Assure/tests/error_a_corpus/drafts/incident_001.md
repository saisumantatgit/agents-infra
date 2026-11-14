# Incident review: billing degradation on Saturday

- The root cause was an expired certificate on the read replica [S1].
- The billing service began returning errors on Saturday at 22 minutes past the hour [S1].
- Customers could browse the catalogue during the incident [S1].
- The fix was reviewed by a second engineer [S1].
- The vendor stated that the earlier maintenance "was not related to the outage" [S1].
- About 83% of requests failed at the peak [S1].
- The read replica held 6474 queued jobs when it was restarted [S1].
- The response group was made up of the on-call engineer, a database specialist and an incident lead [S1].
- The expected automatic rollback never ran [S1].
- A follow-up review is scheduled for the following week [S1].
- The read replica was restarted twice during the response [S1].
