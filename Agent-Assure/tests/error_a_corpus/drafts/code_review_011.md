# Review notes: scheduler change

The error message now names the file that failed [S1]. The `parse_header` function now returns early when the input is empty [S1]. Nadia split the scheduler into two files [S1]. Nadia commented that the old loop "is not thread safe" [S1].

The new code removes 5299 lines and adds 23 [S1]. Run time dropped from 23 seconds to 8 seconds in the benchmark [S1].
