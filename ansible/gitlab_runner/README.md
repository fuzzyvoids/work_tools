# GitLab Runner Docker Executor

This document describes the steps necessary to deploy a GitLab runner using the
docker executor with podman.

## Environment

* GitLab v17.6.1
* Darknet

## Requirements

* Hostname of the machine that the gitlab-runner will be deployed to.
* Administrative privileges to update system files.
* GitLab runner user `glr_runner_user`. This user must already exist and it
  must have subids allocated to it already. The gitlab-runner executes in a
  container under this username and so do all of the ci jobs.

## GitLab Runner

This role will configure a GitLab runner as a docker executor. The
gitlab-runner runs as a docker container under the user account specified. The
user account must be an account in FreeIPA and it will use the subids as
defined in IPA. This implies that the target runner machine must be enrolled in
IPA.

When setting up a new runner there is a component of the runner that must
initially be setup in GitLab and another part that runs an ansible role against
the target machine. Setting up a runner in GitLab first is required to get an
authentication token for use when registering the GitLab runner.

1. In GitLab, when setting up a project specific runner, go to the "Settings >
   CI/CD" menu and then expand the "Runners" section and click on "New project
   runner". If you're setting up a Group runner, then go to group and then
   "Build > Runners" and then click on "New group runner".
2. Set tags for the runner. At a minimum, the `podman` tag should be specified
   to indicate that this runner can only run podman jobs.
3. Set a "Runner description" for the runner. It should be in the format of
   "docker/podman executor on <hostname>".
4. Project runners should check the box to "Lock to current projects". If you
   do not lock the runner to the current project, then anyone who has access to
   your project will also have access to your runner.
5. Creating the runner will give you an authentication token to use when
   registering the runner. Copy this authentication token for use in the
   ansible playbook.
6. Add the new runner to the inventory.
7. Run the playbook, potentially limiting it to the new runner.
   Here is an example playbook, and the command to run it.
   ```
   ---
   hosts: runners
   vars:
     glr_runner_user: test_gitlab-runner
   roles:
     - gitlab_runner
   ```

   ```
   ansible-playbook -u $USER.admin --extra-vars glr_auth_token=<insert-token-here> --limit new-runner-hostname playbook.yml
   ```
8. Check playbook status and also in the GitLab runners section to see if the
   runner has been successfully registered.

## Idempotency

The script is largely idempotent. However, the actual registration step is
skipped if the runner's `config.toml` file is found. This is to prevent any
manual modifications to the file from becoming lost. Therefore, any changes to
the registration command in this playbook will not be picked up on subsequent
runs of the play.

## Arguments

See `defaults/main.yml` for a description of arguments that you might want to
change.

## Interaction Between IT Configuration

This project initially was developed as part of the Bedrock project. It was
also initially created before Idaho Scientific's official adoption of
containers and hosting a container registry. As such, this role should
eventually migrate to the IT's ansible repository.

