S = CLAIM + "." + TAIL
CASES = [
 ("H_heading_then_subheading", "## Myths about the bank\n\nPeople talked.\n\n### The collapse\n\nStaff left. Records were filed. Reporters waited.\n\n" + S, None),
 ("H_heading_then_short_line", "## Myths about the bank\n\nPeople talked.\n\nAnd so\n\nStaff left. Records were filed. Reporters waited.\n\n" + S, None),
 ("H_heading_then_short_line_inpara", "## Myths about the bank\n\nPeople talked. Some wrote. Others posted.\n\nMore\n\n" + S, None),
 ("H_ctrl_heading_no_break", "## Myths about the bank\n\nPeople talked. Some wrote. Others posted.\n\n" + S, None),
 ("H_heading_13tok", "Rumours that we investigated over the summer and found in the end to be false\n\nPeople talked. Some wrote. Others posted.\n\n" + S, None),
 ("H_heading_label_runon", "Rumours we found to be false and the people who spread them. People talked. Some wrote. Others posted.\n\n" + S, None),
 ("H_heading_disowning_html_bold_lies", "**Lies the tabloids told**\n\nPeople talked. Some wrote. Others posted.\n\n" + S, None),
]
