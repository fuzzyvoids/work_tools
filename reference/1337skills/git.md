# Git Commands beginner

Comprehensive Git commands and workflows for version control across all platforms.

## Basic Commands

| Command | Description |
| --- | --- |
| `git init` | Initialize a new Git repository |
| `git clone <url>` | Clone a repository from remote URL |
| `git status` | Show working directory status |
| `git add <file>` | Add file to staging area |
| `git add .` | Add all files to staging area |
| `git commit -m "message"` | Commit staged changes with message |
| `git push` | Push commits to remote repository |
| `git pull` | Pull changes from remote repository |

## Branching

| Command | Description |
| --- | --- |
| `git branch` | List all branches |
| `git branch <name>` | Create new branch |
| `git checkout <branch>` | Switch to branch |
| `git checkout -b <name>` | Create and switch to new branch |
| `git merge <branch>` | Merge branch into current branch |
| `git branch -d <name>` | Delete branch |

## Remote Operations

| Command | Description |
| --- | --- |
| `git remote -v` | Show remote repositories |
| `git remote add <name> <url>` | Add remote repository |
| `git fetch` | Fetch changes from remote |
| `git push origin <branch>` | Push branch to remote |
| `git pull origin <branch>` | Pull branch from remote |

## Advanced Commands

| Command | Description |
| --- | --- |
| `git log --oneline` | Show commit history in one line |
| `git diff` | Show changes between commits |
| `git reset --hard <commit>` | Reset to specific commit |
| `git stash` | Temporarily save changes |
| `git stash pop` | Apply stashed changes |
| `git rebase <branch>` | Rebase current branch |
| `git cherry-pick <commit>` | Apply specific commit |
| `git tag <name>` | Create a tag |

## Common Workflows

### Feature Branch Workflow

```bash
# Create and switch to feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push to remote
git push origin feature/new-feature

# Merge back to main
git checkout main
git merge feature/new-feature
git branch -d feature/new-feature
```

### Hotfix Workflow

```bash
# Create hotfix branch from main
git checkout main
git checkout -b hotfix/critical-bug

# Fix the bug and commit
git add .
git commit -m "Fix critical bug"

# Merge to main and develop
git checkout main
git merge hotfix/critical-bug
git checkout develop
git merge hotfix/critical-bug

# Clean up
git branch -d hotfix/critical-bug
```

## Best Practices

### Commit Messages

- Use present tense ("Add feature" not "Added feature")

- Keep first line under 50 characters

- Use body to explain what and why, not how

- Reference issues and pull requests when applicable

### Branching Strategy

- Use descriptive branch names

- Keep branches focused on single features

- Delete merged branches

- Regularly sync with main branch

### Repository Management

- Use `.gitignore` to exclude unnecessary files

- Keep commits atomic and focused

- Write meaningful commit messages

- Use tags for releases

- Regular backups to remote repositories

Source: https://1337skills.com/cheatsheets/git/
