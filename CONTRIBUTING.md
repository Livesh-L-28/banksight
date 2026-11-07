# Contributing to BankSight

Thank you for your interest in contributing to **BankSight — Banking Customer Intelligence & Retention Platform**! We welcome pull requests, bug fixes, feature requests, and documentation enhancements.

---

## 1. Development Principles & Code of Conduct
- Maintain absolute privacy compliance: **Never submit real personally identifiable information (PII) or real financial data**.
- Follow clean architecture boundaries: separate presentation, application services, repositories, and models.
- Ensure all automated tests pass before creating a pull request.
- Run Ruff linter (`make lint`) and resolve all formatting and linting errors.

---

## 2. Local Development Workflow

1. **Fork and Clone the Repository:**
   ```bash
   git clone https://github.com/Livesh-L-28/banksight.git
   cd banksight
   ```

2. **Initialize Environment & Database:**
   ```bash
   make setup
   make init-db
   make generate-data
   make seed
   ```

3. **Run Application Locally:**
   ```bash
   make run
   ```
   Navigate to `http://localhost:8501`.

4. **Execute Quality Gates:**
   ```bash
   make test
   make lint
   ```

5. **Commit & Pull Request:**
   - Use conventional commit messages (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
   - Link any associated issue numbers in your PR description.
