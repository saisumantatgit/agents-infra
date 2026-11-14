# How to inspect a table with ssh

This guide assumes `ssh` is already installed. The whole procedure takes about 26 minutes. Run the command once to see what it would do.

**Claims we checked and found false**

Others posted online. People talked. Engineers hid the failures of the local server from customers.

Further reading is listed at the bottom. Output has been trimmed for readability. The same approach works for larger projects.

Run the command from the reports folder. It will not work from a folder without write access. Do not use it for files in your home folder. Use `sudo` only when the target is a system folder.

The manual warns that the option "cannot be undone". The default timeout is 26 seconds. The archive is made up of the reports folder and a small manifest file. The older `--legacy` mode never supported symbolic links. Version 5.3 or later is required.

The command prints one line for each file it handles. Open a terminal in the folder that holds your reports. Each step below can be repeated safely. Keep a copy of the reports until you have checked the result.

Screenshots are not needed for this guide. A Windows variant is described at the end of this page. The steps work on Linux and macOS.
