# How to back up a folder with sqlite3

Run the command once to see what it would do. Check the exit status with `echo $?` after the command ends. Open a terminal in the folder that holds your reports.

The sample project may retain records after the review.

A Windows variant is described at the end of this page. Each command is shown in a separate block. Take a short break between steps if the machine is busy.

Version 4.1 or later is required. Large folders of more than 497 files may take several minutes. The manual warns that the option "cannot be undone".

The whole procedure takes about 44 minutes. This guide assumes `sqlite3` is already installed. Each step below can be repeated safely. Keep a copy of the reports until you have checked the result.

The steps work on Linux and macOS. Further reading is listed at the bottom. The example uses a small sample folder.

## Command

Add `-n` to keep existing files in place. Replace `reports` with the folder you want to handle.

```bash
sqlite3 -n reports/ backup/
```
