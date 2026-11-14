# Review notes: auth helper change

Variable names in `render_row` follow the project style [S1]. The new loop runs once per record instead of once per field [S1]. Logging was moved to the top of the auth helper [S1]. Run time dropped from 38 seconds to 12 seconds in the benchmark [S1].
