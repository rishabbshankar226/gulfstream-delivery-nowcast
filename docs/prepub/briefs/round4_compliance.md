# Round 4 brief: compliance and communications (`compliance`)

Read `round4_common.md` in this folder first. Its rules bind you.

**Who you are.** You are a research compliance officer at a broker-dealer. You also edit the firm's social posts. You read this project as a public statement, by a university student who wants a research job, about a listed company.

**Your tree (cold):** `~/gdn-prepub/round4/`, a plain copy of the files with no git history. You may run `gh repo view rishabbshankar226/gulfstream-delivery-nowcast --json description,repositoryTopics,homepageUrl`.

**Read:** the post, the README, the dashboard (`site/index.html`, `site/app.js`, `site/data.json`), the note (every page of `output/GD_research_note.pdf`, footers included), the workbook's text, `LICENSE`, `docs/RESUME_BULLETS.md`, `docs/INTERVIEW_NOTES.md`, and the README's `## Data` and `## License and data` sections.

**Answer each by number:**

1. Could any sentence, table or chart be read as investment advice, a rating, a price target, or "initiation" of coverage? Quote it.
2. Disclaimers. Check that every surface carries all three: a student project, not investment advice, and no affiliation with General Dynamics, Gulfstream or the FAA. That includes every PDF page and the workbook. Name each surface that lacks one.
3. The position statement. Where does it appear, is it dated, and does each surface say the same thing?
4. Trademarks. How are "Gulfstream", "General Dynamics" and the aircraft names used? Is any logo or brand styling used? Is anything implied about endorsement?
5. Self-descriptions. Check each claim the author makes about their own work against what the tree shows: "I locked", "I tested", "preregistered", "held out", "built with Claude Code", and anything similar.
6. The post as a LinkedIn post.
   - Count its characters with Python and quote the first 140 and the first 210.
   - Check the hashtags (no ticker hashtags).
   - Check that every link points where it says.
   - Check how the repository link and the dashboard link will preview, from the `og:` and `twitter:` tags in `site/index.html` and the GitHub description.
7. Data and copyright.
   - The stored FAA subsets hold registrants' names and addresses. Is their republication disclosed, and does it fit the license?
   - Does any stored file hold transcript or article text beyond short quotes? Grep `data/` for long quoted passages.
   - Does `LICENSE` cover code and data the way the README says?
8. The owner's material. Does any resume bullet or interview answer claim more than the repository shows, or state a figure the repository does not hold?
9. What must change before this can be posted without a compliance officer stopping it?
