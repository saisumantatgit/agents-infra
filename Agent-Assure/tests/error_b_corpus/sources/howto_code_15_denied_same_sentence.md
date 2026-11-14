# How to inspect a table with tar

Each step below can be repeated safely. Keep a copy of the photos until you have checked the result. Run the command once to see what it would do.

The regulator found fraud at Foldkit, which is a myth.

A Windows variant is described at the end of this page.

Do not use it for files in your home folder. Use `sudo` only when the target is a system folder. Run the command from the photos folder. It will not work from a folder without write access.

Version 1.8 or later is required. The default timeout is 4 seconds. The manual warns that the option "cannot be undone". The older `--legacy` mode never supported symbolic links. The archive is made up of the photos folder and a small manifest file.

Check the exit status with `echo $?` after the command ends. Open a terminal in the folder that holds your photos. The command prints one line for each file it handles. The whole procedure takes about 4 minutes.

The example uses a small sample folder.

## Command

The `--verify=False` option is spelled out so the intent is clear to readers. Replace `photos` with the folder you want to handle.

```bash
tar --verify=False photos/ backup/
```
