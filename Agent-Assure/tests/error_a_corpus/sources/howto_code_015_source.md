# How to download a file with curl

Keep a copy of the photos until you have checked the result. Open a terminal in the folder that holds your photos. Each step below can be repeated safely.

Further reading is listed at the bottom.

It does not change any files. The `--dry-run` flag shows the plan. Existing files are kept. Nothing is deleted without the `--delete` flag.

The older `--legacy` mode never supported symbolic links. The manual warns that the option "cannot be undone". Large folders of more than 7775 files may take several minutes. The default timeout is 34 seconds. The archive is made up of the photos folder and a small manifest file.

Check the exit status with `echo $?` after the command ends. Run the command once to see what it would do. The whole procedure takes about 34 minutes. The command prints one line for each file it handles.

Screenshots are not needed for this guide.
