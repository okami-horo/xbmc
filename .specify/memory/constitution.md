<!--
Sync Impact Report
Version change: 0.0.0 → 1.0.0
Modified principles:
- [PRINCIPLE_1_NAME] → Cross-Platform First
- [PRINCIPLE_2_NAME] → Add-on APIs Are Stable
- [PRINCIPLE_3_NAME] → Quality Gates and Reviews
- [PRINCIPLE_4_NAME] → Performance & UX Smoothness
- [PRINCIPLE_5_NAME] → Internationalization & Accessibility
Added sections:
- Additional Constraints
- Development Workflow
Removed sections:
- None
Templates requiring updates:
- .specify/templates/plan-template.md ✅ verified (no change needed)
- .specify/templates/spec-template.md ✅ verified (no change needed)
- .specify/templates/tasks-template.md ✅ verified (no change needed)
- .specify/templates/commands/* N/A (directory not present)
Deferred items:
- TODO(RATIFICATION_DATE): Original adoption date unknown; needs project input
-->

# Kodi Constitution

## Core Principles

### Cross-Platform First
Kodi MUST build and run on all supported platforms (Android, Linux, BSD, macOS, iOS/tvOS, Windows).
Platform-specific code MUST live behind clear abstractions and feature guards. CI MUST be green
across supported targets before merge. Any platform regression is a release blocker unless explicitly
waived by maintainers with a documented mitigation plan.

### Add-on APIs Are Stable
Public add-on and binary interfaces MUST be versioned. Breaking changes REQUIRE a deprecation
period and migration notes; compatibility shims SHOULD be provided for at least one major release
when feasible. New or changed APIs MUST be documented in the docs/wiki and referenced in the
changelog for the relevant release.

### Quality Gates and Reviews
All changes MUST go through pull requests and pass repository CI (builds, style/linters, static
analysis where configured, and tests when present). Reviews by maintainers are REQUIRED as per the
project contributing guidelines. Feature flags MUST be time-boxed; obsolete flags MUST be removed.

### Performance & UX Smoothness
User interactions MUST avoid noticeable performance regressions. On supported hardware, the UI
SHOULD target 60 fps; PRs that materially impact performance MUST include measurements and a
rollback/mitigation plan. Memory/CPU budgets for embedded devices MUST be respected.

### Internationalization & Accessibility
All user-facing strings MUST be translatable (no hard-coded text). Navigation MUST remain fully
usable with remote control input; platform-appropriate keyboard/touch interactions MUST be retained.
New features SHOULD consider accessibility and MUST not regress existing accessibility.

## Additional Constraints

- Licensing: The project is GPLv2 licensed. Contributions and dependencies MUST be license
  compatible. See LICENSE.md.
- Privacy: Features MUST comply with privacy-policy.txt. Telemetry or data collection MUST NOT be
  added without explicit user consent and documentation.
- Dependencies: Prefer well-maintained libraries; additions MUST be justified in PRs and kept
  minimal. Security updates MUST be prioritized.
- Documentation: User-visible features MUST be documented in the wiki/docs. API-level docs SHOULD
  be provided via Doxygen where appropriate.
- Security: Vulnerabilities SHOULD be reported responsibly via the project’s standard channels (see
  website/wiki). Do not file public issues for untriaged security reports.

## Development Workflow

- Planning: Use the plan/spec/tasks templates when applicable. The “Constitution Check” in
  plan-template.md MUST be satisfied before implementation proceeds.
- Specifications: Feature specs MUST define prioritized user stories with acceptance scenarios.
  Test tasks in tasks-template.md are included ONLY when the spec calls them out.
- CI: PRs MUST keep CI green across supported platforms before merge.
- Changelog: User-visible changes MUST include a changelog/wiki update or release notes entry.

## Governance
This Constitution supersedes conflicting guidance in templates or docs. PRs MUST include a brief
statement of compliance with the Core Principles where relevant.

Amendments MUST be proposed via PR updating this file, including:
- Version bump and rationale (see policy below).
- Summary of changes and impact.
- Migration or rollout guidance if principles materially affect workflows.

Versioning policy for this Constitution:
- MAJOR: Backward-incompatible governance/principle removals or redefinitions.
- MINOR: New principle/section added or materially expanded guidance.
- PATCH: Clarifications, wording, typo fixes, non-semantic refinements.

Compliance reviews are expected during PR review and during planning (“Constitution Check”).
Maintainers may request changes or block merges that violate these principles.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE) | **Last Amended**: 2025-11-06
