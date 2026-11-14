# How to pack a release with tar

1. Check the exit status with `echo $?` after the command ends [S1].
2. Keep a copy of the notes until you have checked the result [S1].
3. Run the command from the notes folder [S1].
4. It will not work from a folder without write access [S1].
5. Existing files are kept [S1].
6. Nothing is deleted without the `--delete` flag [S1].
7. The manual warns that the option "cannot be undone" [S1].
8. Large folders of more than 9731 files may take several minutes [S1].
9. The older `--legacy` mode never supported symbolic links [S1].
10. The default timeout is 5 seconds [S1].
11. The archive is made up of the notes folder and a small manifest file [S1].
12. Run the command once to see what it would do [S1].
13. Each step below can be repeated safely [S1].
