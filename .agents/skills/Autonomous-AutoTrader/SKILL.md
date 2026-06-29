```markdown
# Autonomous-AutoTrader Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches you the development conventions and workflows used in the Autonomous-AutoTrader Python codebase. You'll learn how to structure files, write and organize code, follow commit message standards, and understand the project's approach to testing and code organization.

## Coding Conventions

### File Naming
- Use **snake_case** for all Python files and modules.
  - Example: `trade_engine.py`, `order_manager.py`

### Import Style
- Use **relative imports** within the package.
  - Example:
    ```python
    from .order_manager import OrderManager
    from .utils import calculate_risk
    ```

### Export Style
- Use **named exports** (explicitly listing what is available for import).
  - Example:
    ```python
    __all__ = ['OrderManager', 'TradeEngine']
    ```

### Commit Messages
- Follow **conventional commit** style.
- Use the `feat` prefix for new features.
- Commit message example:
  ```
  feat: add risk management module for automated trading
  ```

## Workflows

### Feature Development
**Trigger:** When adding a new feature or module  
**Command:** `/feature-development`

1. Create a new Python file using snake_case (e.g., `risk_manager.py`).
2. Implement the feature using relative imports for any internal dependencies.
3. Export main classes or functions via `__all__`.
4. Commit changes using the conventional commit format with the `feat` prefix.
   - Example: `feat: implement stop-loss logic in trade engine`
5. (Optional) Add or update tests if applicable.

### Code Organization
**Trigger:** When refactoring or organizing code  
**Command:** `/organize-code`

1. Ensure all files follow snake_case naming.
2. Update imports to use relative paths.
3. List all public classes/functions in `__all__` for each module.
4. Remove unused or redundant code segments.

## Testing Patterns

- Test files are expected to follow the `*.test.ts` pattern.
- The testing framework is **unknown**; however, ensure that test files are clearly named and placed alongside or within a `tests/` directory.
- Example test file name: `trade_engine.test.ts`
- (Note: Since the codebase is Python but test files are TypeScript, clarify with the team or maintainers about the testing setup.)

## Commands

| Command              | Purpose                                      |
|----------------------|----------------------------------------------|
| /feature-development | Steps for adding a new feature or module     |
| /organize-code       | Steps for refactoring and organizing code    |
```
