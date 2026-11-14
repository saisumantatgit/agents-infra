# Review notes: auth helper change

The error message now names the file that failed [S1]. Logging was moved to the top of the auth helper [S1]. Sofia split the auth helper into two files [S1]. The new code removes 3249 lines and adds 30 [S1].

Sofia commented that the old loop "is not thread safe" [S1]. Run time dropped from 30 seconds to 4 seconds in the benchmark [S1].
