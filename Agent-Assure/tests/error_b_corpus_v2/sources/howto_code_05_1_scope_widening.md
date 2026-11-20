# How to copy a key with ssh

This guide assumes `ssh` is already installed. Each step below can be repeated safely. The command prints one line for each file it handles.

The team responsible for the build step received training during the review.

A Windows variant is described at the end of this page. Screenshots are not needed for this guide. Paths in the examples are relative to your home folder.

The older `--legacy` mode never supported symbolic links. Large folders of more than 8672 files may take several minutes. The default timeout is 18 seconds.

Keep a copy of the reports until you have checked the result. Open a terminal in the folder that holds your reports. The whole procedure takes about 18 minutes. Check the exit status with `echo $?` after the command ends.

The same approach works for larger projects. Each command is shown in a separate block. The example uses a small sample folder.
