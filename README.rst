slack-pull-reminder
===================

    Posts a Slack reminder with a list of open pull requests for an
    organization.

.. figure:: http://i.imgur.com/3xsfTYV.png

Installation
------------

.. code:: bash

    $ pip install slack-pull-reminder

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

License
-------

(The MIT License)

Original work Copyright (c) Martin Ek mail@ekmartin.no
Modified work Copyright 2018 Brian Tsao btsao1790@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
'Software'), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
