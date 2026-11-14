S = CLAIM + "." + TAIL
def H(h): return (h, S, f"{h}\n\n{CLAIM} [S1].\n")
CASES = [
 # --- blocker probes: heading newly scored ---
 ("BLK_heading_only_grounded", "In the bull case revenue doubles by 2030.", "# Revenue doubles [S1]\n"),
 ("BLK_heading_only_conditional", "If revenue doubles, the bank survives.", "# Revenue doubles [S1]\n"),
 ("BLK_body_only_conditional", "If revenue doubles, the bank survives.", "Revenue doubles [S1].\n"),
 ("BLK_heading_only_denied_src", "Revenue doubles is a myth.", "# Revenue doubles [S1]\n"),
 ("BLK_heading_guilty_only", "Reporters asked whether Acme guilty verdict was near.", "# Acme guilty [S1]\n"),
 ("BLK_heading_plus_claim_denied", "None of this is true. Use z. Ok then. " + S, "# Revenue doubles\n\n" + DRAFT),
]
