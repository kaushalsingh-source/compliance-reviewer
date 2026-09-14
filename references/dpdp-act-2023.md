# Digital Personal Data Protection Act, 2023 (DPDP Act)

**Verified 2026-09-14** — re-confirmed current on this pass. Note: the operational specifics implementing this Act (retention periods, grievance-response SLA, breach-notification mechanics, Consent Manager rules) live in a **separate, subordinate instrument** — see `dpdp-rules-2025.md` for the Digital Personal Data Protection Rules, 2025 (G.S.R. 846(E), notified 13 Nov 2025) — do not assume this Act's text alone contains those numbers.

Source: Act came into force 11 Aug 2023; DPDP Rules 2025 implement it. Official Act text: meity.gov.in. Section structure cross-checked against dpdpa.com's chapter index 2026-08-21 — note a secondary source initially mislabeled Section 5 as "Significant Data Fiduciary"; the verified mapping below is correct. If in doubt about a section number, treat it as needing verification rather than trusting a single source.

## Chapter 2 — Obligations of Data Fiduciary (Sections 4-10)

- **Section 4** — Grounds for processing personal data.
- **Section 5** — Notice: what must be told to the Data Principal (the user) at or before collection.
- **Section 6** — Consent: must be free, specific, informed, unconditional, and unambiguous, given via clear affirmative action. The Data Principal can give/manage/review/withdraw consent, optionally through a Consent Manager.
- **Section 7** — Certain legitimate uses: a closed list of ~9 situations where processing doesn't need fresh consent (data voluntarily provided by the individual for a stated purpose, specified State functions/benefits, compliance with law/court orders, medical emergencies, public health/disaster response, specified employment purposes). This is a numerus clausus, not an open "legitimate interest" balancing test — if a spec justifies skipping consent on "legitimate interest" grounds generally, check whether it actually fits one of the Section 7 categories specifically.
- **Section 8** — General obligations of Data Fiduciary: responsible for compliance regardless of any contrary agreement or a Data Processor's failure (8.x). Section 8(5): must implement reasonable security safeguards — penalty up to ₹250 crore for failure. Section 8(6): must notify the Data Protection Board and every affected Data Principal "without delay" on becoming aware of a breach, with a detailed report to the Board (cause, extent, remedial steps) — penalty up to ₹200 crore for failure to notify.
- **Section 9** — Processing of children's data: requires verifiable parental/guardian consent; prohibits processing detrimental to a child's wellbeing, and prohibits tracking, behavioural monitoring, or targeted advertising directed at children.
- **Section 10** — Additional obligations of a Significant Data Fiduciary (SDF): entities crossing thresholds (volume of data, data-driven decisions with significant effect on principals, sensitive data categories, key infrastructure role, or combining data across sources) face heightened duties — appointing a Data Protection Officer, running Data Protection Impact Assessments, and periodic independent audits.

## Chapter 3 — Rights and Duties of Data Principal (Sections 11-15)
- **Section 11** — Right to access information about one's own personal data.
- **Section 12** — Right to correction and erasure.
- **Section 13** — Right of grievance redressal.
- **Section 14** — Right to nominate someone to exercise these rights on your behalf (e.g. on death/incapacity).
- **Section 15** — Duties of the Data Principal (e.g. not to make frivolous complaints, not to furnish false information).

---
**How to use this file:** for a fintech onboarding/lending flow, the most common gaps are: (a) consent bundled/vague rather than per-purpose and freely revocable (Section 6), (b) using "legitimate interest" language that doesn't actually map to one of the Section 7 categories, (c) no clear data retention/purge policy or owner once a decline/closure happens (ties to Section 8's general obligations), (d) breach-notification readiness (Section 8(6) — is there even a named path to notify the Board within a reasonable window?). Cite the section number. If a spec explicitly names an open item like "who owns data purging" — that IS the gap; say so plainly rather than inventing a deeper issue.
