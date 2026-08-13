# Rocky 9 Repos

This role updates the URLs for the yum repositories and points them to our local server.

## Variables

| Variable     | Type    | Default | Description                                                                                                                  |
|--------------|---------|---------|------------------------------------------------------------------------------------------------------------------------------|
| `install_ca` | boolean | false   | Install the CA or not. Not required for a normal darknet install, but might be necessary if the machine is not IPA enrolled. |

