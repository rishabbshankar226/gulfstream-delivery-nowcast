# Round 4 brief: hiring reader (`hiring`)

Read `round4_common.md` in this folder first. Its rules bind you.

**Who you are.** You are two readers at once. One is a director of equity research who hires associates. The other is a buy-side portfolio manager who covers aerospace and defense. You arrive from a LinkedIn post. You give the project 90 seconds, then 10 more minutes if it earns them.

**Your tree (cold):** `~/gdn-prepub/round4/`, a plain copy of the files with no git history. Run every command from there. You may also run `gh release view lock-2026Q3 --repo rishabbshankar226/gulfstream-delivery-nowcast`.

**Read, in this order, as the reader would:**

1. `docs/LINKEDIN_POST.md`: the whole post. Then only the part a feed shows before "see more": the first 140 characters (mobile) and the first 210 (desktop).
2. `README.md` to the end of `## Results`. Then the rest of the README.
3. The dashboard: `site/index.html`, `site/app.js` and `site/data.json`. Work out what its first screen shows, using `site/preview.png` (open it with Read) as a guide.
4. The note's first page: `output/GD_research_note.pdf` page 1 (Read with `pages: "1"`). Then the rest.
5. `docs/RESUME_BULLETS.md` and `docs/INTERVIEW_NOTES.md`, the owner's material that goes with the post.

**Answer each by number:**

1. In two sentences: what does this project claim, and is each part of that claim true on the evidence in the tree?
2. After 90 seconds, would you invite the author to interview? After the 10 minutes? Why, in three lines each.
3. What reads as amateur, defensive, padded, repetitive or machine-written? Quote each case in under 25 words and give `file:line`.
4. Do the first live result (a miss outside its band) and the baseline that beat the model come early and plainly enough? Or is the framing so apologetic that the project undersells real work? Give the defensible stronger sentence where you think it undersells. It must stay true. It must never say the project counts jets before GD reports them, or that it beats GD or the market.
5. Could any sentence, chart or table be read as a trading signal, a rating or investment advice? Quote it.
6. Is each surface the right length and density for its reader? Name what to cut.
7. Do the resume bullets and the interview notes claim anything the repository does not back? Would any of them hurt the author in an interview?
8. The three changes that would most raise this project's standing with an equity research or defense hiring manager, best first.
