# ALPHA-5 clean-clone install

The tester's clone install ended with "exit 0, provisions .venv, prints plugin + manual usage" [S3].

Driven with a fabricated draft, the demo returned "FAIL · 50.0 · exit 1" in the results table [S3].

The report concludes that "The moat is real on a stranger's machine" [S3].

It found that "the installer's OWN snippet crashes in a fresh install" [S3].

The cause is that the file it opens "cannot exist in a fresh install" until the hook has fired [S3].
