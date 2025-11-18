<!--
Sync Impact Report
- Version change: unversioned → 1.0.0
- Modified principles: PLACEHOLDER_1 → Cross‑Platform Reliability; PLACEHOLDER_2 → Add‑on API Stability; PLACEHOLDER_3 → Performance & UX Responsiveness; PLACEHOLDER_4 → Code Quality & Reviews; PLACEHOLDER_5 → Licensing, Security & Compliance
- Added sections: "Additional Constraints: Build & Release Policies"; "Development Workflow & Quality Gates"
- Removed sections: None
- Templates requiring updates:
  ✅ .specify/templates/plan-template.md (Constitution Check gates aligned)
  ✅ .specify/templates/spec-template.md (Compatibility & Impact section added)
  ✅ .specify/templates/tasks-template.md (API compatibility/migration phase added)
  ⚠ Pending: TODO(RATIFICATION_DATE) to be set by maintainers
-->

# Kodi Constitution

## Core Principles

### I. Cross‑Platform Reliability
Kodi MUST build and run on all officially supported platforms (Android, Linux, BSD,
macOS, iOS, tvOS, Windows). Changes MUST not degrade platform support. When a
platform‑specific limitation exists, the change MUST fail gracefully or be
conditionally disabled with a documented rationale.

Rationale: Kodi serves a diverse hardware and OS matrix. Maintaining stability
across platforms prevents regressions for large user segments and keeps CI
signal trustworthy.

### II. Add‑on API Stability
Public contracts (Python add‑on APIs, JSON‑RPC, skinning/theming contracts, and
other documented extension points) are treated as stable interfaces.

- Breaking changes MUST include deprecation windows, migration notes, and a
  coordinated version bump for the affected API surface.
- Contract tests SHOULD accompany changes to public interfaces; they are
  REQUIRED for intentional breaking changes.
- Add‑on compatibility impacts MUST be called out in PR descriptions.

Rationale: The add‑on ecosystem relies on predictable contracts. Stability
protects users and third‑party maintainers.

### III. Performance & UX Responsiveness
User interactions MUST remain responsive. Heavy I/O or CPU work MUST not block
the UI thread. Feature work MUST document performance characteristics (e.g.,
target 60 fps for UI flows where applicable, memory footprints where relevant)
and avoid measurable regressions without justification.

Rationale: Kodi is designed for couch use. Smooth interaction and playback are
non‑negotiable quality bars.

### IV. Code Quality & Reviews
Contributions MUST follow the project’s code guidelines and pass CI on Jenkins
for all relevant targets. PRs MUST be opened from topic branches, include
descriptive commit messages, and obtain at least one approval from maintainers
of the affected area. Provide test builds when reasonable to aid review.

Rationale: Consistent quality and collaborative review keep a large codebase
maintainable for volunteers.

### V. Licensing, Security & Compliance
All contributions MUST remain compatible with GPLv2. New dependencies MUST have
licenses vetted and documented. Security fixes are prioritized; logs MUST avoid
leaking sensitive data, and the project’s privacy policy MUST be respected.

Rationale: Legal compliance and user trust are foundational to an open‑source
media platform.

## Additional Constraints: Build & Release Policies

- CI MUST be green on the required Jenkins matrices before merge.
- Platform build breakages introduced by a change MUST be resolved or the change
  backed out prior to release.
- Feature flags and compile‑time guards MUST include defaults and documented
  scope when used to stage incomplete work.
- Release notes MUST enumerate user‑visible changes, known issues, and any
  add‑on/API compatibility notes.

## Development Workflow & Quality Gates

- Open an issue or reference an existing issue describing the problem or feature.
- For public API changes, include a Compatibility & Impact summary (affected
  contracts, migration steps, version bump plan).
- Follow coding guidelines and keep commits logically scoped and descriptive.
- Ensure Constitution Check gates in feature plans are satisfied:
  - CI green for targeted platforms
  - API changes include deprecation/migration details and tests where applicable
  - Performance expectations documented; no unreasoned regressions
  - Licensing review for new dependencies

## Governance

- This Constitution supersedes conflicting informal practices. Maintainers apply
  it during reviews and merges.
- Amendments: Propose changes via PR touching this file and any impacted
  templates. Summarize rationale and expected migration for downstream processes.
- Versioning policy (this document): Semantic versioning
  - MAJOR: Backward‑incompatible principle redefinitions or removals
  - MINOR: New principle/section or materially expanded guidance
  - PATCH: Editorial clarifications without behavioral change
- Compliance: All PRs MUST attest to Constitution compliance in their
  descriptions. Reviewers enforce gates. For runtime guidance on development
  workflow and code style, see `docs/CONTRIBUTING.md`.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): original adoption date not recorded in repo | **Last Amended**: 2025-11-18
