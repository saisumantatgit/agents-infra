## Useful flags

1. Run the command once to see what it would do [S1].
2. Each step below can be repeated safely [S1].
3. Open a terminal in the folder that holds your reports [S1].
4. The default timeout is 5 seconds [S1].
5. The archive is made up of the reports folder and a small manifest file [S1].
6. Large folders of more than 5409 files may take several minutes [S1].

## Command

The `--verify=False` option is spelled out so the intent is clear to readers [S1]. Replace `reports` with the folder you want to handle [S1].

```bash
ssh --verify=False reports/ backup/
```
