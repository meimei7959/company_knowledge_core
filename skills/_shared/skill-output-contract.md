# Company Skill Output Contract

Every production skill must be action-oriented. It must teach an Agent how to complete one reusable task, not define the Agent's job title.

Required sections in `SKILL.md`:

- Purpose
- Triggers
- Inputs
- Workflow
- Outputs
- Quality Gate
- Failure Routes

Rules:

- Keep role identity, org boundary, and job responsibility in `agents/` or `docs/agent-team/role-operating-specs.json`.
- Keep reusable task execution method in `skills/<skill-id>/SKILL.md`.
- Put long checklists, templates, examples, or domain references in `references/`.
- Put deterministic extraction, validation, conversion, or test helpers in `scripts/`.
- A skill cannot be considered production-ready when it only says what an Agent is responsible for.
