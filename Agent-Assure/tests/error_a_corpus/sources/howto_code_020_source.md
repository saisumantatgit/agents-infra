# How to copy a key with git

Open a terminal in the folder that holds your photos. The whole procedure takes about 6 minutes. Each step below can be repeated safely.

The example uses a small sample folder. The same approach works for larger projects. Output has been trimmed for readability.

Version 1.7 or later is required. The archive is made up of the photos folder and a small manifest file. Large folders of more than 2835 files may take several minutes.

Run the command once to see what it would do. The command prints one line for each file it handles. Keep a copy of the photos until you have checked the result. Check the exit status with `echo $?` after the command ends.

Each command is shown in a separate block. Screenshots are not needed for this guide. Take a short break between steps if the machine is busy.

## Command

The `--delete=False` option is spelled out so the intent is clear to readers. Replace `photos` with the folder you want to handle.

```bash
git --delete=False photos/ backup/
```
