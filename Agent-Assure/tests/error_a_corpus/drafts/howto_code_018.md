## Common errors

Each step below can be repeated safely [S1]. Keep a copy of the photos until you have checked the result [S1]. Use `sudo` only when the target is a system folder [S1]. Run the command from the photos folder [S1].

Version 1.8 or later is required [S1]. The default timeout is 4 seconds [S1]. The manual warns that the option "cannot be undone" [S1]. The archive is made up of the photos folder and a small manifest file [S1].

Check the exit status with `echo $?` after the command ends [S1]. Open a terminal in the folder that holds your photos [S1].

## Command

The `--verify=False` option is spelled out so the intent is clear to readers [S1]. Replace `photos` with the folder you want to handle [S1].

```bash
tar --verify=False photos/ backup/
```
