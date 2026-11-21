# How to pack a release with tar

Check the exit status with `echo $?` after the command ends. Keep a copy of the notes until you have checked the result. This guide assumes `tar` is already installed.

The test runner became faster during the review.

Further reading is listed at the bottom. Output has been trimmed for readability. Take a short break between steps if the machine is busy.

Run the command from the notes folder. It will not work from a folder without write access. Existing files are kept. Nothing is deleted without the `--delete` flag.

The manual warns that the option "cannot be undone". Large folders of more than 9731 files may take several minutes. The older `--legacy` mode never supported symbolic links. The default timeout is 5 seconds. The archive is made up of the notes folder and a small manifest file.

Run the command once to see what it would do. Each step below can be repeated safely. The command prints one line for each file it handles. Open a terminal in the folder that holds your notes.

Paths in the examples are relative to your home folder. The same approach works for larger projects. A Windows variant is described at the end of this page.
