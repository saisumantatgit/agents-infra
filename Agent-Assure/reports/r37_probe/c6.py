S = CLAIM + "." + TAIL
F = " Staff left. Records were filed. "
CASES = [
 ("CTRL_procedure_matches", "The procedure matches the RFC, not the draft." + F + S, None),
 ("CTRL_procedure_follows_newpara", "The procedure follows the RFC, not the draft.\n\nStaff left. Records were filed. " + S, None),
 ("CTRL_women_were_40", "Women were 40 percent of the workforce." + F + S, None),
 ("CTRL_flag_is_off", "When the strict flag is off, the parser accepts trailing commas." + F + S, None),
 ("CTRL_myths_facts_short_line_after", "## Myths and facts\n\nPeople talked.\n\nAnd so\n\n" + S, None),
]
