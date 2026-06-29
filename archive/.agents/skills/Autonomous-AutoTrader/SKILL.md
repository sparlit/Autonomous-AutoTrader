```markdown
# Autonomous-AutoTrader Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches you the core development patterns and conventions used in the **Autonomous-AutoTrader** TypeScript codebase. You'll learn how to structure files, write imports/exports, follow commit message conventions, and organize tests. This guide ensures consistency and clarity when contributing to or maintaining the project.

## Coding Conventions

### File Naming
- **Style:** `snake_case`
- **Example:**  
  ```plaintext
  trade_engine.ts
  order_manager.test.ts
  ```

### Import Style
- **Relative imports** are used throughout the codebase.
- **Example:**
  ```typescript
  import { calculateProfit } from './profit_utils';
  ```

### Export Style
- **Named exports** are preferred.
- **Example:**
  ```typescript
  // In trade_engine.ts
  export function executeTrade(order: Order) { ... }
  ```

### Commit Messages
- **Conventional commits** are used.
- **Prefix:** `docs`
- **Example:**
  ```
  docs: update README with setup instructions
  ```

## Workflows

### Code Contribution
**Trigger:** When adding or updating code  
**Command:** `/contribute`

1. Create or update files using `snake_case` naming.
2. Use relative imports for all dependencies.
3. Export functions, types, or constants using named exports.
4. Write or update relevant tests in files matching `*.test.*`.
5. Commit your changes using the conventional commit format, e.g., `docs: describe new trading strategy`.
6. Open a pull request for review.

### Writing Tests
**Trigger:** When adding new features or fixing bugs  
**Command:** `/write-test`

1. Create a test file alongside your module, named with the pattern `module_name.test.ts`.
2. Write tests covering all new or changed functionality.
3. Use the project's preferred (unknown) test framework.
4. Run tests to ensure they pass before committing.

## Testing Patterns

- **Test File Pattern:** Files should be named using `*.test.*` (e.g., `order_manager.test.ts`).
- **Location:** Test files are placed alongside the modules they test.
- **Framework:** The test framework is not specified; check existing tests for style.
- **Example:**
  ```typescript
  // order_manager.test.ts
  import { createOrder } from './order_manager';

  describe('createOrder', () => {
    it('should create a valid order object', () => {
      const order = createOrder(...);
      expect(order).toBeDefined();
    });
  });
  ```

## Commands
| Command        | Purpose                                         |
|----------------|-------------------------------------------------|
| /contribute    | Step-by-step guide for contributing code        |
| /write-test    | Instructions for writing and organizing tests   |
```
