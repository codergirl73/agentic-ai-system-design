# Agentic AI System Design

**Curriculum v1** — A project-based roadmap covering agentic AI, RAG, retrieval engineering, orchestration, production systems, and end-to-end system design.

> Learn the fundamentals. Build the systems. Understand the trade-offs.


## Website

A responsive GitHub Pages learning site is included in this repository: **[Agentic AI Systems — Learn. Design. Build.](https://codergirl73.github.io/agentic-ai-system-design/)**.

To publish it, open **Settings → Pages** in the repository and set the build/deployment source to **GitHub Actions**. The included workflow deploys the static site on pushes to `master`. The first deployment may take a few minutes; check the **Actions** tab for its status.

## Learning method
Every topic includes: fundamentals, Mermaid architecture diagrams, real-world examples, selected research papers, Python implementation with tests, module-wise interview questions, company-style system design questions, explained answers, practical exercises, and a knowledge check.

## Curriculum
See [CURRICULUM.md](CURRICULUM.md) for the complete 9-module roadmap. The full [Module 1 learning guide](MODULE_1_FOUNDATIONS.md) includes concepts, architecture diagrams, sequence diagrams, failure handling, a system design exercise, research papers, and interview answers.


## Nine-module learning curriculum

The repository has a guide page for each module. Modules 1–3 now have detailed learning guides. Module 3 also has a runnable Python document-processing and embedding project with sample data and unit tests. Modules 4–9 remain on the roadmap and will be expanded next.

1. [Module 1 — Foundations of Agentic AI](MODULE_1_FOUNDATIONS.md) — full learning guide
2. [Module 2 — RAG Fundamentals](MODULE_2_RAG_FUNDAMENTALS.md)
3. [Module 3 — Document Processing and Embeddings](MODULE_3_DOCUMENT_PROCESSING.md)
4. [Module 4 — Information Retrieval](MODULE_4_INFORMATION_RETRIEVAL.md)
5. [Module 5 — Advanced Retrieval](MODULE_5_ADVANCED_RETRIEVAL.md)
6. [Module 6 — Advanced RAG](MODULE_6_ADVANCED_RAG.md)
7. [Module 7 — Agent Architecture and Orchestration](MODULE_7_AGENT_ARCHITECTURE.md)
8. [Module 8 — Production Engineering](MODULE_8_PRODUCTION_ENGINEERING.md)
9. [Module 9 — End-to-End System Design](MODULE_9_END_TO_END_SYSTEM_DESIGN.md)

## Implementations
- [Module 1 Python implementation and tests](implementations/module-1-foundations/README.md)
- [Module 3 document-processing and embedding pipeline](implementations/module-3-document-processing/README.md) — sample Markdown/text ingestion, chunking, metadata, optional embeddings, JSONL output, semantic search, and tests.

## Separate company-practices library
This is an independent case-study and practice track, separate from the nine-module learning curriculum.
- [Company Engineering Practices](COMPANY_PRACTICES.md) — public engineering patterns and primary sources.
- [Hands-on Company Case Studies](company-practices/README.md) — six complete exercises with Mermaid diagrams, Python implementations, unit tests, evaluation plans, and trade-offs.
- [Company-Style System Design Interview Practice](SYSTEM_DESIGN_INTERVIEWS.md) — original company-inspired design prompts, not verified interview questions.

## Interview preparation
- [Module-wise interview question bank](interview-preparation/MODULE_WISE_QUESTIONS.md) — beginner, intermediate, and advanced questions for all 9 modules.
- [Company-style system design practice](SYSTEM_DESIGN_INTERVIEWS.md) — representative prompts inspired by engineering problem areas at Google, Meta, Amazon, Microsoft, OpenAI, Anthropic, and NVIDIA. These are practice prompts, not claims about exact questions asked in company interviews.

## Connect
Follow the learning journey and AI research explainers on Instagram: **[@frontierai.daily](https://www.instagram.com/frontierai.daily/)**

## Repository layout
- `CURRICULUM.md` — modules and topics
- `MODULE_1_FOUNDATIONS.md` through `MODULE_9_*.md` — module guides with embedded Mermaid diagrams
- `COMPANY_PRACTICES.md` — independent company engineering case-study library
- `company-practices/` — six runnable company-inspired case studies
- `SYSTEM_DESIGN_INTERVIEWS.md` — company-inspired system design practice prompts
- `interview-preparation/MODULE_WISE_QUESTIONS.md` — interview questions organized by module
- `PROGRESS.md` — learning tracker
- `research-papers/` — paper links and reading notes
- `interview-preparation/` — question banks and answers
- `implementations/` — Python projects
- `content/` — Frontier AI carousel and Reel planning

## Public repository safety
Review commits for personal information, API keys, credentials, private datasets, and copyrighted PDFs. Prefer linking to official paper pages or open-access versions instead of uploading copyrighted PDFs.
