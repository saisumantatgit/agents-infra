## Common errors

1. Keep a copy of the notes until you have checked the result [S1].
2. Each step below can be repeated safely [S1].
3. The tool prints a summary when it finishes [S1].
4. It stays silent unless an error occurs or `--verbose` is set [S1].
5. Run the command from the notes folder [S1].
6. Large folders of more than 8167 files may take several minutes [S1].
7. The default timeout is 30 seconds [S1].
8. The manual warns that the option "cannot be undone" [S1].
9. The archive is made up of the notes folder and a small manifest file [S1].
10. This guide assumes `tar` is already installed [S1].
11. The command prints one line for each file it handles [S1].

## Command

Add `-n` to keep existing files in place [S1]. Replace `notes` with the folder you want to handle [S1].

```bash
tar -n notes/ backup/
```
