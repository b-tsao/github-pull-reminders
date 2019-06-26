DISCLAIMER: This is a much enhanced version of the original from https://github.com/ekmartin/slack-pull-reminder

What is improved?
 - Display
 - Added reviewers list
 - Meant for enterprise github

Credits to Martin as the original creator!

slack-pull-reminder
===================

    Posts a Slack reminder with a list of open pull requests for an
    organization.

Usage
-----

slack-pull-reminder is configured using environment variables:

Required
~~~~~~~~

-  ``SLACK_WEBHOOK``: A webhook from Slack to post reminders
-  ``GITHUB_URL``: The GitHub enterprise url
-  ``GITHUB_API_TOKEN``: An authentication token from GitHub
-  ``ORGANIZATION``: The GitHub organization you want pull request
   reminders for.

Optional
~~~~~~~~

-  ``IGNORE_WORDS``: A comma-separated list of words that will cause a pull request to be ignored.

-  ``REPOSITORIES``: A comma-separated list of repository names to check, where all other repositories in the organization are ignored. All repositories are checked by default.

-  ``USERNAMES``: A comma-separated list of GitHub usernames to filter pull requests by, where all other users are ignored. All users in the organization are included by default.

-  ``BRANCH``: Branch to filter pull requests by. All branches in the repository are pulled by default.

Example
~~~~~~~

.. code:: bash

    $ ORGANIZATION="orgname" SLACK_WEBHOOK="webhook" GITHUB_URL="url" GITHUB_API_TOKEN="token" slack-pull-reminder

Cronjob
~~~~~~~

As slack-pull-reminder only runs once and exits, it's recommended to run
it regularly using for example a cronjob.

Example that runs slack-pull-reminder every day at 10:00:

.. code:: bash

    0 10 * * * ORGANIZATION="orgname" SLACK_WEBHOOK="webhook" GITHUB_URL="url" GITHUB_API_TOKEN="token" slack-pull-reminder
