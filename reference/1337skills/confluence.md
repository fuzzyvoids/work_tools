# Confluence Cheat Sheet intermediate

## Overview

Confluence is Atlassian's team workspace and wiki platform used by organizations to create, organize, and collaborate on documentation, meeting notes, project plans, and knowledge bases. It integrates deeply with Jira, Trello, and Bitbucket, making it a central hub for team knowledge.

Confluence is available as a cloud-hosted service or self-hosted (Data Center) deployment. It features a rich WYSIWYG editor, page templates, macros for dynamic content, spaces for organization, granular permissions, and a powerful search engine.

## Getting Started

### Content Hierarchy

```plaintext
Confluence Instance
|-- Spaces
|   |-- Engineering Wiki
|   |   |-- Pages
|   |   |   |-- Architecture Overview
|   |   |   |   |-- Frontend Architecture
|   |   |   |   `-- Backend Services
|   |   |   `-- Onboarding Guide
|   |   `-- Blog Posts
|   |-- Product Documentation
|   `-- HR and People
`-- Personal Spaces
```

## Keyboard Shortcuts

### Editor

| Shortcut | Action |
| --- | --- |
| `Ctrl+S` | Save / Publish page |
| `Ctrl+B` | Bold |
| `Ctrl+I` | Italic |
| `Ctrl+Shift+M` | Insert code snippet |
| `Ctrl+Shift+D` | Insert macro |
| `Ctrl+Shift+7` | Numbered list |
| `Ctrl+Shift+8` | Bullet list |
| `Ctrl+Shift+9` | Task list |
| `Ctrl+K` | Insert link |
| `Ctrl+M` | Insert files/images |
| `//` | Date picker |
| `/` | Slash commands (Cloud) |
| `@` | Mention a user |
| `[]` | Insert action item |

### Navigation

| Shortcut | Action |
| --- | --- |
| `G` then `G` | Go to dashboard |
| `G` then `S` | Browse current space |
| `/` | Quick search |
| `C` | Create new page |
| `E` | Edit current page |
| `?` | Show keyboard shortcuts |

## Page Editor

### Content Blocks

| Block | Description |
| --- | --- |
| Heading | H1 through H6 |
| Table | Data table |
| Code block | Syntax highlighted code |
| Panel | Colored info panels |
| Expand | Collapsible section |
| Status | Color-coded status lozenge |
| Decision | Decision record |
| Task | Action item with assignee |
| Layout | Multi-column layouts |

### Panel Types

| Panel | Color | Use Case |
| --- | --- | --- |
| Info | Blue | General information |
| Note | Yellow | Important notes |
| Success | Green | Positive outcomes |
| Warning | Orange | Caution messages |
| Error | Red | Errors or dangers |

## Macros

| Macro | Description |
| --- | --- |
| `{toc}` | Table of contents |
| `{children}` | List of child pages |
| `{excerpt}` | Define a page excerpt |
| `{include}` | Include another page |
| `{jira}` | Display Jira issues |
| `{status}` | Colored status lozenge |
| `{chart}` | Create charts from table data |
| `{page-tree}` | Hierarchical page tree |
| `{recently-updated}` | Recently changed pages |
| `{expand}` | Collapsible content |
| `{code}` | Code block |
| `{anchor}` | Named anchor for deep linking |

## Templates

### Built-in Templates

| Template | Use Case |
| --- | --- |
| Meeting Notes | Agendas, notes, action items |
| Decision | Record and track decisions |
| Retrospective | Sprint retrospectives |
| How-To Article | Step-by-step guides |
| Product Requirements | PRD documentation |
| Troubleshooting | Issue resolution guides |
| OKR | Objectives and key results |

## Spaces

### Space Permissions

| Permission | Description |
| --- | --- |
| View | Read pages in the space |
| Add | Create new pages |
| Edit | Modify existing pages |
| Delete | Remove pages |
| Admin | Manage space settings and permissions |
| Export | Export space content |

## Search

### Search Operators

| Operator | Example | Description |
| --- | --- | --- |
| `"exact phrase"` | `"deployment guide"` | Exact phrase match |
| `AND` | `docker AND kubernetes` | Both terms required |
| `OR` | `guide OR tutorial` | Either term |
| `NOT` | `api NOT deprecated` | Exclude term |
| `type:page` | `type:page docker` | Filter by content type |
| `space:ENG` | `space:ENG setup` | Filter by space key |
| `creator:username` | `creator:jdoe` | Filter by author |
| `label:important` | `label:important` | Filter by label |

## REST API

```bash
# Get page content
curl -u user@example.com:API_TOKEN \
  "https://domain.atlassian.net/wiki/rest/api/content/PAGE_ID?expand=body.storage"

# Create a page
curl -X POST \
  -u user@example.com:API_TOKEN \
  -H "Content-Type: application/json" \
  "https://domain.atlassian.net/wiki/rest/api/content" \
  -d '{
    "type": "page",
    "title": "New Page Title",
    "space": {"key": "SPACE_KEY"},
    "body": {
      "storage": {
        "value": "<p>Page content</p>",
        "representation": "storage"
      }
    }
  }'

# Search content
curl -u user@example.com:API_TOKEN \
  "https://domain.atlassian.net/wiki/rest/api/search?cql=type=page+AND+text~docker"
```

## Advanced Usage

### Page Properties Macro

Create structured data tables that can be queried across pages with the Page Properties Report macro for dashboards.

### Automation Rules

| Trigger | Action |
| --- | --- |
| Page created | Add labels, send notification |
| Page updated | Notify watchers, post to Slack |
| Blog published | Share on team channels |
| Label added | Move to specific space |

## Troubleshooting

| Issue | Solution |
| --- | --- |
| Page loading slowly | Reduce macro count; optimize embedded content |
| Search not finding pages | Check space permissions; wait for re-indexing |
| Formatting lost on paste | Use Ctrl+Shift+V for plain text paste |
| Jira macro showing errors | Verify Jira application link |
| Version conflicts | Use page history to compare and merge |
| Export missing content | Ensure macros are supported in export format |
| Template not appearing | Verify template is in correct space |
| Space permissions not applying | Check group memberships |

Source: https://1337skills.com/cheatsheets/confluence/
