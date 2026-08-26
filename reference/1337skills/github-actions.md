# GitHub Actions Cheatsheet

## Installation & Setup

### GitHub CLI (gh)

| Platform | Command |
| --- | --- |
| Ubuntu/Debian | `curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \| sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \| sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null && sudo apt update && sudo apt install gh` |
| Fedora/RHEL | `sudo dnf install gh` |
| Arch Linux | `sudo pacman -S github-cli` |
| macOS (Homebrew) | `brew install gh` |
| Windows (Chocolatey) | `choco install gh` |
| Windows (WinGet) | `winget install --id GitHub.cli` |

### Self-Hosted Runner Setup

| Platform | Setup Commands |
| --- | --- |
| Linux | `mkdir actions-runner && cd actions-runner && curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz && tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz` |
| macOS | `mkdir actions-runner && cd actions-runner && curl -o actions-runner-osx-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-osx-x64-2.311.0.tar.gz && tar xzf ./actions-runner-osx-x64-2.311.0.tar.gz` |
| Windows | `mkdir actions-runner; cd actions-runner; Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-win-x64-2.311.0.zip -OutFile actions-runner-win-x64-2.311.0.zip` |

### Act (Local Testing Tool)

| Platform | Command |
| --- | --- |
| Linux/macOS (curl) | `curl https://raw.githubusercontent.com/nektos/act/master/install.sh \| sudo bash` |
| Homebrew | `brew install act` |
| Go | `go install github.com/nektos/act@latest` |
| Windows (Chocolatey) | `choco install act-cli` |
| Windows (Scoop) | `scoop install act` |

## Basic GitHub CLI Commands

| Command | Description |
| --- | --- |
| `gh run list` | List all workflow runs in the repository |
| `gh run view <run-id>` | View details of a specific workflow run |
| `gh run watch <run-id>` | Watch a workflow run in real-time |
| `gh run view <run-id> --log` | View logs for a specific workflow run |
| `gh run download <run-id>` | Download artifacts from a workflow run |
| `gh workflow list` | List all workflows in the repository |
| `gh workflow view <workflow-name>` | View details of a specific workflow |
| `gh workflow enable <workflow-name>` | Enable a disabled workflow |
| `gh workflow disable <workflow-name>` | Disable a workflow |
| `gh workflow run <workflow-name>` | Manually trigger a workflow |
| `gh workflow run <workflow-name> -f key=value` | Trigger workflow with input parameters |
| `gh run cancel <run-id>` | Cancel a running workflow |
| `gh run rerun <run-id>` | Rerun a completed workflow |
| `gh run rerun <run-id> --failed` | Rerun only failed jobs in a workflow |
| `gh auth login` | Authenticate GitHub CLI with your account |

## Self-Hosted Runner Management

| Command | Description |
| --- | --- |
| `./config.sh --url https://github.com/ORG/REPO --token TOKEN` | Configure a new self-hosted runner |
| `sudo ./svc.sh install` | Install runner as a system service (Linux/macOS) |
| `sudo ./svc.sh start` | Start the runner service |
| `sudo ./svc.sh stop` | Stop the runner service |
| `sudo ./svc.sh status` | Check runner service status |
| `sudo ./svc.sh uninstall` | Uninstall runner service |
| `./config.sh remove --token TOKEN` | Remove runner from repository |
| `./run.sh` | Run the runner interactively (not as service) |
| `gh api repos/:owner/:repo/actions/runners` | List all self-hosted runners via API |
| `gh api -X DELETE repos/:owner/:repo/actions/runners/RUNNER_ID` | Remove runner via API |

## Local Testing with Act

| Command | Description |
| --- | --- |
| `act -l` | List all workflows and jobs available locally |
| `act` | Run the default event (push) locally |
| `act push` | Run workflows triggered by push event |
| `act pull_request` | Run workflows triggered by pull request event |
| `act -j job-name` | Run a specific job by name |
| `act -s GITHUB_TOKEN=token` | Run with a secret value |
| `act -s SECRET_NAME` | Prompt for secret value interactively |
| `act --secret-file .secrets` | Load secrets from a file |
| `act -P ubuntu-latest=nektos/act-environments-ubuntu:18.04` | Use specific Docker image for runner |
| `act -n` | Dry run - show what would be executed |
| `act -v` | Verbose output for debugging |
| `act --container-architecture linux/amd64` | Specify container architecture |
| `act -W .github/workflows/ci.yml` | Run specific workflow file |
| `act --env-file .env` | Load environment variables from file |

## Advanced GitHub CLI Commands

| Command | Description |
| --- | --- |
| `gh run list --workflow=ci.yml` | List runs for a specific workflow |
| `gh run list --branch=main --limit=20` | List runs for specific branch with limit |
| `gh run view --log-failed` | View only failed job logs |
| `gh run view --job=12345` | View specific job within a run |
| `gh workflow run deploy.yml -f environment=production -f version=1.2.3` | Trigger workflow with multiple inputs |
| `gh api repos/:owner/:repo/actions/runs/:run_id/logs` | Download run logs via API |
| `gh api repos/:owner/:repo/actions/workflows` | List workflows via API |
| `gh api repos/:owner/:repo/actions/secrets` | List repository secrets |
| `gh secret set SECRET_NAME < secret.txt` | Set a repository secret from file |
| `gh secret set SECRET_NAME --body "value"` | Set a repository secret from string |
| `gh secret list` | List all repository secrets |
| `gh secret remove SECRET_NAME` | Remove a repository secret |
| `gh api repos/:owner/:repo/actions/caches` | List workflow caches |
| `gh api -X DELETE repos/:owner/:repo/actions/caches/:cache_id` | Delete a specific cache |
| `gh run download <run-id> -n artifact-name` | Download specific artifact by name |

## Workflow File Structure

### Basic Workflow Template

```yaml
name: CI Pipeline

# Trigger configuration
on:
  push:
    branches: [ main, develop ]
    paths:
      - 'src/**'
      - '**.js'
  pull_request:
    branches: [ main ]
  workflow_dispatch:  # Manual trigger
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'staging'

# Environment variables
env:
  NODE_VERSION: '18'
  CACHE_KEY: v1

# Jobs definition
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test
        env:
          CI: true

      - name: Build application
        run: npm run build
```

### Matrix Strategy

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node-version: [16, 18, 20]
        include:
          - os: ubuntu-latest
            node-version: 20
            experimental: true
        exclude:
          - os: macos-latest
            node-version: 16
      fail-fast: false
      max-parallel: 3

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm test
```

### Conditional Execution

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'

    steps:
      - name: Deploy to staging
        if: contains(github.event.head_commit.message, '[staging]')
        run: ./deploy.sh staging

      - name: Deploy to production
        if: startsWith(github.ref, 'refs/tags/v')
        run: ./deploy.sh production

      - name: Conditional step with multiple conditions
        if: |
          success() &&
          github.actor == 'dependabot[bot]' &&
          contains(github.event.pull_request.labels.*.name, 'automerge')
        run: echo "Auto-merging PR"
```

### Caching Configuration

```yaml
steps:
  # Cache npm dependencies
  - name: Cache node modules
    uses: actions/cache@v3
    with:
      path: ~/.npm
      key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
      restore-keys: |
        ${{ runner.os }}-node-

  # Cache pip dependencies
  - name: Cache pip
    uses: actions/cache@v3
    with:
      path: ~/.cache/pip
      key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
      restore-keys: |
        ${{ runner.os }}-pip-

  # Cache Gradle dependencies
  - name: Cache Gradle
    uses: actions/cache@v3
    with:
      path: |
        ~/.gradle/caches
        ~/.gradle/wrapper
      key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}

  # Cache Docker layers
  - name: Cache Docker layers
    uses: actions/cache@v3
    with:
      path: /tmp/.buildx-cache
      key: ${{ runner.os }}-buildx-${{ github.sha }}
      restore-keys: |
        ${{ runner.os }}-buildx-
```

### Artifacts Management

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Build application
        run: npm run build

      # Upload artifacts
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build-output
          path: |
            dist/
            build/
            !dist/**/*.map
          retention-days: 30
          if-no-files-found: error

      # Upload test results
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results-${{ matrix.os }}
          path: test-results/

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      # Download artifacts
      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: build-output
          path: ./artifacts

      - name: Deploy artifacts
        run: ./deploy.sh ./artifacts
```

### Environment and Secrets

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://example.com

    env:
      NODE_ENV: production
      API_URL: https://api.example.com

    steps:
      - name: Deploy with secrets
        run: |
          echo "Deploying to $NODE_ENV"
          ./deploy.sh
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

      - name: Use GitHub token
        run: |
          gh api user
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Composite Actions

**File: `.github/actions/setup-project/action.yml`**

```yaml
name: 'Setup Project'
description: 'Setup Node.js and install dependencies'
inputs:
  node-version:
    description: 'Node.js version'
    required: false
    default: '18'
  cache-key:
    description: 'Cache key prefix'
    required: false
    default: 'v1'
outputs:
  cache-hit:
    description: 'Whether cache was hit'
    value: ${{ steps.cache.outputs.cache-hit }}

runs:
  using: 'composite'
  steps:
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}

    - name: Cache dependencies
      id: cache
      uses: actions/cache@v3
      with:
        path: node_modules
        key: ${{ inputs.cache-key }}-${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}

    - name: Install dependencies
      if: steps.cache.outputs.cache-hit != 'true'
      run: npm ci
      shell: bash
```

**Using composite action:**

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup project
        uses: ./.github/actions/setup-project
        with:
          node-version: '20'
          cache-key: 'v2'

      - name: Build
        run: npm run build
```

### Reusable Workflows

**File: `.github/workflows/reusable-deploy.yml`**

```yaml
name: Reusable Deploy Workflow

on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      version:
        required: false
        type: string
        default: 'latest'
    secrets:
      deploy-key:
        required: true
    outputs:
      deployment-url:
        description: "Deployment URL"
        value: ${{ jobs.deploy.outputs.url }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    outputs:
      url: ${{ steps.deploy.outputs.url }}

    steps:
      - uses: actions/checkout@v4

      - name: Deploy
        id: deploy
        run: |
          ./deploy.sh ${{ inputs.environment }} ${{ inputs.version }}
          echo "url=https://${{ inputs.environment }}.example.com" >> $GITHUB_OUTPUT
        env:
          DEPLOY_KEY: ${{ secrets.deploy-key }}
```

**Calling reusable workflow:**

```yaml
jobs:
  deploy-staging:
    uses: ./.github/workflows/reusable-deploy.yml
    with:
      environment: staging
      version: '1.2.3'
    secrets:
      deploy-key: ${{ secrets.STAGING_DEPLOY_KEY }}

  deploy-production:
    needs: deploy-staging
    uses: ./.github/workflows/reusable-deploy.yml
    with:
      environment: production
      version: '1.2.3'
    secrets:
      deploy-key: ${{ secrets.PROD_DEPLOY_KEY }}
```

## Common Workflow Triggers

| Trigger | Description | Example |
| --- | --- | --- |
| `push` | On push to branches | `on: push: branches: [main]` |
| `pull_request` | On PR events | `on: pull_request: types: [opened, synchronize]` |
| `workflow_dispatch` | Manual trigger | `on: workflow_dispatch: inputs: ...` |
| `schedule` | Cron schedule | `on: schedule: - cron: '0 0 * * *'` |
| `release` | On release events | `on: release: types: [published]` |
| `issues` | On issue events | `on: issues: types: [opened, labeled]` |
| `issue_comment` | On issue comments | `on: issue_comment: types: [created]` |
| `repository_dispatch` | External webhook | `on: repository_dispatch: types: [deploy]` |
| `workflow_run` | After another workflow | `on: workflow_run: workflows: [CI]` |
| `pull_request_target` | PR from forks (careful!) | `on: pull_request_target` |

## Context Variables

| Context | Description | Example Usage |
| --- | --- | --- |
| `github.actor` | User who triggered workflow | `${{ github.actor }}` |
| `github.event_name` | Event that triggered workflow | `${{ github.event_name }}` |
| `github.ref` | Branch or tag ref | `${{ github.ref }}` |
| `github.sha` | Commit SHA | `${{ github.sha }}` |
| `github.repository` | Owner/repo name | `${{ github.repository }}` |
| `github.workspace` | Workspace directory path | `${{ github.workspace }}` |
| `runner.os` | Operating system | `${{ runner.os }}` |
| `runner.temp` | Temp directory path | `${{ runner.temp }}` |
| `secrets.GITHUB_TOKEN` | Auto-generated token | `${{ secrets.GITHUB_TOKEN }}` |
| `env.VAR_NAME` | Environment variable | `${{ env.NODE_VERSION }}` |
| `matrix.value` | Matrix value | `${{ matrix.node-version }}` |
| `needs.job.outputs.var` | Output from previous job | `${{ needs.build.outputs.version }}` |
| `steps.step_id.outputs.var` | Output from step | `${{ steps.build.outputs.artifact }}` |
| `job.status` | Job status | `${{ job.status }}` |

## Common Use Cases

### Use Case 1: Node.js CI/CD Pipeline

```yaml
name: Node.js CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [16, 18, 20]

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Run tests
        run: npm test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push'

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - run: npm ci
      - run: npm run build

      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: dist
          path: dist/

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://example.com

    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v3
        with:
          name: dist
          path: dist/

      - name: Deploy to production
        run: |
          # Deploy commands here
          echo "Deploying to production..."
```

### Use Case 2: Docker Build and Push

```yaml
name: Docker Build and Push

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Use Case 3: Multi-Cloud Deployment

```yaml
name: Multi-Cloud Deploy

on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        description: 'Deployment environment'
        options:
          - staging
          - production
        required: true

jobs:
  deploy-aws:
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment }}

    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-
```

Source: https://1337skills.com/cheatsheets/github-actions/
