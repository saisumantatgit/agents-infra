# Incident review: report builder degradation on Monday

- The root cause was a bad configuration push on the primary database [S1].
- The payments team was paged within 12 minutes of the first alert [S1].
- The report builder service began returning errors on Monday at 48 minutes past the hour [S1].
- The vendor stated that the earlier maintenance "was not related to the outage" [S1].
- The primary database held 6527 queued jobs when it was restarted [S1].
