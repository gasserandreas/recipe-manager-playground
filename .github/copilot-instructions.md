---
applyTo: "**"
---

# Code Modification Guidelines

1. **Minimal Impact:** Understand architectural context before changes. Make the smallest change that fulfills requirements while preserving existing functionality and patterns.

2. **Targeted Changes:** Modify only essential sections. Preserve unrelated code and system behavior.

3. **Change Strategy:**
   - Default: Minimal, focused implementation
   - If needed: Moderate, localized refactoring  
   - Only if requested: Comprehensive restructuring

4. **Clarify First:** Request clarification if scope is unclear. Don't assume broader scope than specified.

5. **Note Improvements:** Document related enhancements outside scope without implementing (e.g., "Function Y could benefit from this pattern").

6. **Reversible Design:** Ensure changes can be easily reverted if issues arise.

7. **Code Quality:**
   - **Clarity:** Descriptive names, concise single-purpose functions, follow style guides
   - **Consistency:** Match existing patterns and conventions
   - **Error Handling:** Anticipate failures, use try-catch, provide clear error messages
   - **Security:** Sanitize inputs, secure secrets via env vars, vet libraries
   - **Testing:** Design for testability, ensure adequate coverage
   - **Documentation:** Comment complex/non-obvious code using standard formats

8. **Commits:** Use Conventional Commits format (`feat(scope): description`). Imperative mood. Infer type (feat/fix/chore/refactor/test/docs) and scope from changes.