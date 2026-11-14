# How to pack a release with tar

Check the exit status with `echo $?` after the command ends. The whole procedure takes about 7 minutes. Open a terminal in the folder that holds your reports.

The example uses a small sample folder. Output has been trimmed for readability. Paths in the examples are relative to your home folder.

The archive is made up of the reports folder and a small manifest file. Version 3.1 or later is required. The default timeout is 7 seconds.

Run the command once to see what it would do. The command prints one line for each file it handles. Keep a copy of the reports until you have checked the result. This guide assumes `tar` is already installed.

Further reading is listed at the bottom. The same approach works for larger projects. The steps work on Linux and macOS.

## Command

Add `-n` to keep existing files in place. Replace `reports` with the folder you want to handle.

```bash
tar -n reports/ backup/
```
