# CareerLens 50 viva questions and answers

1. **What problem does CareerLens solve?** It helps a job seeker understand resume evidence, compare it with an explicit job requirement set, and choose skills to develop. It makes the reasons behind each score visible.

2. **What is the project's scope?** Account management, private PDF/DOCX uploads, extraction, quality review, saved jobs, job matching, skill gaps, career recommendations, history, analytics and staff catalog management.

3. **Why use React?** React lets the interface reuse components such as fields, score rings and report sections. State updates show API results without reloading the whole application.

4. **What does Vite do?** Vite serves the React source during development and bundles the production frontend into static files. Its development proxy sends API requests to Django.

5. **Why use Django?** Django provides authentication, password hashing, the ORM, migrations and an administration site. These reduce the amount of security and database infrastructure the project must implement itself.

6. **What does Django REST Framework add?** DRF provides request parsing, serializers, token authentication, permissions, pagination, viewsets and standard HTTP response handling.

7. **Why use MySQL?** The project needs durable related records, constraints and transactions. MySQL stores accounts, resumes, evidence, jobs, requirements and analysis history with foreign keys.

8. **What is a serializer?** A serializer converts model records into JSON and validates incoming fields. For example, JobSerializer rejects duplicate skill requirements before saving a job.

9. **What is a view?** A view receives a request, authenticates the user and chooses the action. The service layer performs the extraction or analysis rather than placing all business logic in the view.

10. **What is the service layer?** It contains reusable operations such as extract_file, calculate_match and recommend_careers. Tests can verify these operations separately from presentation code.

11. **How are passwords stored?** Django hashes passwords with a salt using its configured password hasher. The database does not store the original password, and check_password verifies a login safely.

12. **How does API authentication work?** Login returns an opaque DRF token. React keeps it in sessionStorage and sends it in an Authorization header. The server resolves it to a user and rejects tokens older than 24 hours.

13. **What happens on logout?** The server deletes the active token and the browser clears its local token. The same token can no longer access protected APIs.

14. **Is a React protected route enough for security?** No. It only improves navigation. Django also filters every user-owned queryset and checks the authenticated user before returning, changing or downloading records.

15. **How do you prevent one user reading another resume?** The API retrieves a resume from a queryset restricted to request.user. A different user's ID returns 404, including for download and report endpoints.

16. **How do administrators differ from regular users?** Only staff can read system statistics. Django admin additionally checks staff status and model permissions. Profile updates cannot set is_staff.

17. **How are uploads validated?** The service checks extension, size and actual file content. PDFs must parse, and DOCX files must contain the expected Word XML. Additional limits constrain pages, expanded archive size, entry count and extracted text length.

18. **Why is an extension check insufficient?** A malicious or damaged file can be renamed to .pdf or .docx. Parsing and signature checks prevent treating arbitrary bytes as a valid resume.

19. **How are PDF and DOCX files read?** PyMuPDF extracts text from PDF pages. python-docx reads paragraphs and table cells from Word documents.

20. **What happens with a scanned resume?** If there is too little selectable text, CareerLens rejects it with an OCR explanation. OCR is not configured in this version, so the user should upload a text-based PDF or DOCX.

21. **How are original resumes protected?** They use random names under a private media directory. Django does not expose a public media URL. Owner-authorized API requests stream originals as attachments.

22. **How does spaCy help?** A blank English spaCy pipeline tokenizes text and PhraseMatcher finds configured skill names and aliases. This is a vocabulary-based NLP technique, not a trained entity recognition model.

23. **Why does JavaScript not count as Java?** PhraseMatcher compares token sequences rather than arbitrary character substrings. The tests explicitly check this boundary case.

24. **How is a candidate's name extracted?** The first non-empty line is accepted only when it resembles a short alphabetic name. The interface labels this as a heuristic because it can be wrong.

25. **How is experience calculated?** The parser looks for an explicit phrase such as “2 years of experience.” It does not convert date ranges into guessed employment duration. Missing experience remains unknown.

26. **How are resume sections identified?** Recognized headings such as Education, Work Experience and Projects start sections. Text continues until another recognized heading. Unusual headings may need manual review.

27. **How is resume quality scored?** Contact fields contribute 20 points, five non-empty sections 30, catalog skill breadth 25, contribution evidence 15 and text length 10. Each report shows the formula and earned points.

28. **What are quality scoring limitations?** A phrase or section heading can earn points without proving the quality of its content. Certification presence is optional in many real careers. The score is a structural review rather than an employability judgment.

29. **How does weighted skill matching work?** Essential skills carry 2 points and preferred skills carry 1. Explicit evidence earns full credit, a configured related skill earns half and absent evidence earns zero. Earned points divided by total points gives the skill component.

30. **What is a partially matched skill?** It is a required skill with no direct mention but with a catalog-defined related skill in the resume. For example, JavaScript can provide partial evidence for TypeScript. The report does not claim equivalence or proficiency.

31. **How do experience and qualification affect matching?** Experience contributes up to its weight using documented years divided by requested years. Qualification receives credit when its exact normalized phrase appears in the education section. Equivalent qualifications need a person to review them.

32. **What happens when a job does not specify experience?** The experience component is excluded. The final score divides by the sum of active weights so unspecified criteria do not automatically penalize the candidate.

33. **Can a 90% match predict hiring?** No. It only describes alignment between detected resume evidence and saved criteria. Hiring depends on many factors the application does not observe.

34. **How are skill gaps prioritized?** Essential missing or partial requirements come before preferred requirements. The gap retains its technical, tool or soft-skill category and links to a learning resource.

35. **How does the learning roadmap work?** Each unfulfilled requirement becomes a learning step with an action, a project milestone and catalog resources. The system does not invent how long mastery will take.

36. **How are career roles ranked?** The local engine counts explicitly matched skills for each catalog role and divides by its total skills. Roles with zero overlap are omitted, and the highest coverage roles are shown first.

37. **Does career coverage estimate seniority?** No. A role's percentage measures catalog overlap only. It does not prove job readiness or seniority, and the interface says so.

38. **Which parts use an LLM?** Only optional learning advice when the user explicitly selects it and the server has provider credentials. Local extraction, quality scores, matching and role ranking stay deterministic.

39. **How is AI output validated?** Pydantic requires a JSON object with a bounded list of recommendation strings and rejects extra fields, invalid types and oversized text. Candidate facts and scores never come from the provider response.

40. **What happens during an API timeout or rate limit?** The system retains the local result, saves no invalid advice and displays a fallback status. Tests mock timeouts, HTTP failures and invalid schemas.

41. **Where are API keys stored?** In server environment variables loaded from .env during local development. The file is ignored by Git. Keys never belong in React variables or browser storage.

42. **What does database normalization mean here?** Reusable skills live in one table. ResumeSkill and JobRequirement connect them to resumes and jobs without copying whole skill definitions into every row. Immutable report snapshots use JSON deliberately.

43. **What constraints are used?** Foreign keys enforce references. Unique constraints prevent repeated resume/skill and job/skill pairs, and duplicate skill/resource URLs. User emails and catalog names are unique.

44. **Why use a database transaction for a match?** The match, skill gap and history entry form one logical operation. A transaction rolls them back together if any save fails, avoiding a half-created analysis.

45. **What happens when a source is deleted?** Deleting a resume cascades to its dependent reports and removes the original file. Deleting a job removes its matches, gap records and associated match history. The UI explains the permanent action before it is submitted.

46. **How do dashboard charts get data?** Django aggregates the authenticated user's MySQL records and returns chart series and counts. A new account has empty states. Synthetic samples appear only in the explicitly selected sample workspace.

47. **How did you test the application?** Django tests exercise authentication, permissions, parsing, database constraints, scoring and fallback on MySQL. React tests check validation and reporting. Playwright drives complete browser workflows using real HTTP APIs.

48. **What is the difference between unit and integration testing?** A focused service test verifies a formula or parser rule. A browser integration test verifies that React, API authentication, Django services, private storage and MySQL work together through a user action.

49. **What are the current limitations?** OCR is absent, the skill vocabulary needs catalog maintenance, section/name detection uses heuristics, qualification matching is literal, related skills require manual curation and a live LLM provider needs credentials. Public deployment and load testing are separate work.

50. **What could a future version improve?** Add opt-in OCR, evidence correction with provenance, degree equivalence rules, multilingual vocabularies, richer role taxonomies and evaluated semantic matching. Each improvement needs measured tests and clear explanations before it changes scores.
