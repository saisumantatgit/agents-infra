# Incident review: notifications degradation on Monday

The root cause was a runaway batch job on the queue broker [S1]. A status page notice went out 2 minutes after the page [S1]. Engineers restored normal service after 16 minutes [S1]. About 40 percent of requests failed at the peak [S1].

The response group was made up of the on-call engineer, a database specialist and an incident lead [S1].
