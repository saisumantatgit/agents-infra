# How to copy a key with git

- Open a terminal in the folder that holds your photos [S1].
- The whole procedure takes about 6 minutes [S1].
- Each step below can be repeated safely [S1].
- Version 1.7 or later is required [S1].
- The archive is made up of the photos folder and a small manifest file [S1].
- Large folders of more than 2835 files may take several minutes [S1].

## Command

The `--delete=False` option is spelled out so the intent is clear to readers [S1]. Replace `photos` with the folder you want to handle [S1].

```bash
git --delete=False photos/ backup/
```
