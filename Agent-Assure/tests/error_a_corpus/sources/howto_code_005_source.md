# How to back up a folder with tar

The command prints one line for each file it handles. This guide assumes `tar` is already installed. Each step below can be repeated safely.

Screenshots are not needed for this guide. Take a short break between steps if the machine is busy. The example uses a small sample folder.

Version 6.5 or later is required. Large folders of more than 9347 files may take several minutes. The older `--legacy` mode never supported symbolic links.

Check the exit status with `echo $?` after the command ends. Open a terminal in the folder that holds your photos. Keep a copy of the photos until you have checked the result. The whole procedure takes about 46 minutes.

The steps work on Linux and macOS. Output has been trimmed for readability. Paths in the examples are relative to your home folder.
