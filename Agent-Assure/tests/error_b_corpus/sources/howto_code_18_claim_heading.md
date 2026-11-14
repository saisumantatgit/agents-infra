# How to pack a release with ssh

Keep a copy of the reports until you have checked the result. This guide assumes `ssh` is already installed. Each step below can be repeated safely.

The test runner holds 39 entries.

The steps work on Linux and macOS. The same approach works for larger projects. Each command is shown in a separate block.

Existing files are kept. Nothing is deleted without the `--delete` flag. Do not use it for files in your home folder. Use `sudo` only when the target is a system folder.

The older `--legacy` mode never supported symbolic links. The manual warns that the option "cannot be undone". Large folders of more than 7279 files may take several minutes. Version 2.6 or later is required. The archive is made up of the reports folder and a small manifest file.

The command prints one line for each file it handles. Open a terminal in the folder that holds your reports. Run the command once to see what it would do. The whole procedure takes about 11 minutes.

Paths in the examples are relative to your home folder. Take a short break between steps if the machine is busy. Output has been trimmed for readability.

## Command

The `--verify=False` option is spelled out so the intent is clear to readers. Replace `reports` with the folder you want to handle.

```bash
ssh --verify=False reports/ backup/
```
