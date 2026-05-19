# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1](https://github.com/engrammic-ai/primitives/compare/engrammic-primitives-v0.1.0...engrammic-primitives-v0.1.1) (2026-05-19)


### Features

* add CAG agent protocol ([c9c50de](https://github.com/engrammic-ai/primitives/commit/c9c50de3882d0830e8396272f7c206853ad1bc82))
* add MetaMemoryLabel + CITEEdgeType.ABOUT to primitives schema ([ca7e01f](https://github.com/engrammic-ai/primitives/commit/ca7e01f99b85da92f5ad2fe924d22ab763c5e8dc))
* add protocol implementations + query extraction ([9f96547](https://github.com/engrammic-ai/primitives/commit/9f96547109165d6cba67b05d04c480af6f88f58f))
* add pydantic dep + finding/pass queries ([7655d95](https://github.com/engrammic-ai/primitives/commit/7655d95dbdc2af6892c036202fedde9c265db457))
* add PyPI publishing workflow and manual publish command ([a7049bd](https://github.com/engrammic-ai/primitives/commit/a7049bd85d93780de20721865cad819f1b22d952))
* add REFERENCES edge + unit tests for epistemology ([81d622b](https://github.com/engrammic-ai/primitives/commit/81d622bec1259370e9b36990fba01cec18f52dfb))
* **eag:** add transitions module with evidence validation predicate ([d787aa6](https://github.com/engrammic-ai/primitives/commit/d787aa6de6c2dca95a105325b26bfb83ec81cbf0))
* **epistemology:** add partial_confidence for pre-corroboration claims ([7839fa5](https://github.com/engrammic-ai/primitives/commit/7839fa5b1742971fd1aa242ba65897f2657876c5))
* **schema:** add CAG schema, taxonomy, scoring, and code extensions ([2a4da74](https://github.com/engrammic-ai/primitives/commit/2a4da741fe2f1c1babdcad7be0cf0098182fb5f9))
* **schema:** add PREVENTS to CITEEdgeType ([fc5f520](https://github.com/engrammic-ai/primitives/commit/fc5f5206afd26487818096be4dafe78fc28ec4c9))
* **schema:** add WORKING_BELIEF to IntelligenceLabel ([b771132](https://github.com/engrammic-ai/primitives/commit/b7711328a9b3d36963ca77e2ecb19ce8660efc7a))
* **schema:** add WorkingHypothesis + ProposedBelief to EAG spec ([9c1700c](https://github.com/engrammic-ai/primitives/commit/9c1700ca8c902073f76222b1d83bda2643cf834e))


### Bug Fixes

* resolve all mypy type errors ([05d1ddf](https://github.com/engrammic-ai/primitives/commit/05d1ddf8f3a6aadbbac386697237fef3c6e3ff48))

## [Unreleased]

## [0.1.0] - 2026-05-04

### Added

- EAG (Epistemic Augmented Generation) paradigm implementation
- CITE schema with four cognitive layers: Memory, Knowledge, Wisdom, Intelligence
- Node types: Claim, Fact, Insight, Principle, Strategy, Model
- Edge types for layer transitions and relationships
- Scoring primitives: decay, freshness, confidence
- Promotion and supersession logic
- KnowledgeStore, LifecycleManager, SignalProvider protocols
- Code-specific extensions
- Taxonomy definitions

[Unreleased]: https://github.com/anthropics/primitives/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/anthropics/primitives/releases/tag/v0.1.0
