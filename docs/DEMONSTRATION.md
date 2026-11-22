# CareerLens examination demonstration

Allow approximately 12–15 minutes. Use only the supplied synthetic resume for public demonstrations. Do not expose `.env`, session tokens or private documents on the projector.

1. Start the private database with `.venv/bin/python scripts/local_mysql.py start`, then `.venv/bin/python scripts/dev.py start`. Open http://127.0.0.1:5173/.
2. Explain the problem: a student needs a clear comparison between resume evidence and job requirements. Explain that scores describe documented alignment and cannot predict a hiring outcome.
3. Create a new account with your own chosen test email and password. Show the empty dashboard. This demonstrates that statistics do not come from hardcoded sample arrays.
4. Open My resumes and upload `docs/sample-resume.pdf`. State that Alex Morgan is a fictional demonstration candidate. Show the upload progress and the saved record.
5. Open Resume analysis. Show extracted contact details, section text and skill evidence. Expand a skill to show its source line. Explain the name heuristic and why unmentioned details remain unknown.
6. Add the visible quality components and verify that they equal the displayed score. Explain that quality measures structural completeness and vocabulary breadth, not employability.
7. Download the original file and JSON report. Explain that both requests include authentication and verify the record owner.
8. Create a job titled Python backend developer. Use a description mentioning Python, Django, Docker and automated testing. Set experience to 2 and qualification to MCA. Save and review the automatically detected skill requirements. Change Docker to preferred if you want to demonstrate weights.
9. Edit the job company field and save. Explain that JobRequirement is a separate relational table and each job/skill pair is unique.
10. Open Job match, choose the uploaded resume and saved job, and run the analysis. Expand matched, partially matched and missing skills. Explain essential weight 2, preferred weight 1, full/half/zero credit and the active component formula.
11. Open Skill gap analysis. Show the missing Docker skill, category, priority, official documentation link and project milestone. Explain that the roadmap does not invent a completion time or promise proficiency.
12. Generate Career pathways with AI advice unchecked. Explain the rule-based label and catalog overlap formula. Expand a learning plan.
13. If you have configured a compatible provider, optionally enable AI learning advice and regenerate. Show the provenance label. If no provider is configured, deliberately demonstrate the labeled local fallback. Do not claim a live AI call was verified without credentials.
14. Show History and the updated dashboard. Refresh the page or sign out/in to show persistence. Explain that the browser cannot read another user's records just by changing an ID.
15. Update the profile goal and refresh. Show that it remains saved.
16. Demonstrate a rejected unsupported file or unreadable PDF. Explain the OCR limitation and the alternative of a text-based PDF or DOCX.
17. Sign in as a separately created superuser. Show the Administration page and Django admin skills, roles, categories and resource management. Never promote a regular account from the browser.
18. Show the executed results in `docs/TEST_RESULTS.md`, the source tests and the SQL schema. Discuss live-provider, OCR, equivalence matching and production deployment limits candidly.

For a short demonstration, select Explore sample workspace and show the labeled records already persisted in MySQL. Every selection creates a separate sample account; this is a convenience path, not a substitute for demonstrating real registration and upload.

## Beginner explanation of the request cycle

When you click Analyze match, React sends the selected IDs and token. Django identifies the user, retrieves only that user's resume and job, and asks the service layer to calculate a report. The service reads stored skill evidence and requirements, creates a match and its gap record in one database transaction, and adds history. A serializer turns the records into JSON. React displays that JSON with the component formula and source evidence.
