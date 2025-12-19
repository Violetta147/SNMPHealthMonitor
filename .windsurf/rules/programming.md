---
trigger: manual
---

<windsurf_code_style>
- Prefer functional programming over OOP
- Use pure functions with clear input/output
- Use strict typing for all variables and functions
</windsurf_code_style>

<windsurf_python_specifics>
- Prefer Pydantic over TypedDict for data models
- Use requirements.txt
- For complex structures, avoid generic collections
</windsurf_python_specifics>

- Do not generate .md file when user doesn't accept
- Generate as least functions as possible (don't start big first)
- Add debug messages when writing code
<windsurf_instructions_to_the_dialog>

<windsurf_code_style>
- Comments in English only
- Prefer functional programming over OOP
- Use OOP classes only for connectors and interfaces to external systems
- Write pure functions - only modify return values, never input parameters or global state
- Make minimal, focused changes
- Follow DRY, KISS, and YAGNI principles
- Use strict typing everywhere - function returns, variables, collections
- Check if logic already exists before writing new code
- Avoid untyped variables and generic types
- Never use default parameter values - make all parameters explicit
- Create proper type definitions for complex data structures
</windsurf_code_style>

<windsurf_error_handling>
- Always raise errors explicitly, never silently ignore them
- Use specific error types that clearly indicate what went wrong
- Avoid catch-all exception handlers that hide the root cause
- Error messages should be clear and actionable
- NO FALLBACKS: Never mask errors with fallback mechanisms - work with user to fix the main flow explicitly
- Transparent debugging: When something fails, show exactly what went wrong and why
- Fix root causes, not symptoms - fallbacks hide real problems that need solving
</windsurf_error_handling>

<windsurf_language_specifics>
- Prefer structured data models over loose dictionaries (Pydantic, interfaces)
- Avoid generic types like `Any`, `unknown`, or `List[Dict[str, Any]]`
- Use modern package management (pyproject.toml, package.json)
- Raise/throw specific exceptions with descriptive messages
- Leverage language-specific type features (discriminated unions, enums)
- Use classes only for external system clients, pure functions for business logic
</windsurf_language_specifics>

<windsurf_libraries_and_dependencies>
- Install in virtual environments, not globally
- Add to project configs, not one-off installs
- Use source code exploration for understanding
- Update project configuration files when adding dependencies
</windsurf_libraries_and_dependencies>

<windsurf_terminal_usage>
- Run `date` for date-related tasks
- Always use non-interactive git diff: `git --no-pager diff` or `git diff | cat`
- Prefer non-interactive commands with flags over interactive ones
</windsurf_terminal_usage>

<windsurf_planning_practices>
- Create feature plans in tmp directory as markdown files
- Include: current state, final state, files to change, task checklist
- Keep plans minimalistic - only essential changes
</windsurf_planning_practices>

<windsurf_repository_practices>
- Read `README.md` if no `.windsurf` file exists
- Summarize project before working on it
</windsurf_repository_practices>

<windsurf_code_changes>
- Respect existing code style and patterns
- Suggest only minimal changes related to current dialog
- Change as few lines as possible while solving the problem
- Focus only on what user is asking for - no extra improvements
- Understand existing codebase before suggesting changes
- Start by reading related files and codebase
</windsurf_code_changes>

</windsurf_instructions_to_the_dialog>
