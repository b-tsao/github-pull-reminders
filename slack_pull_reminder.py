import os
import sys

import requests
from github3 import enterprise_login
from datetime import datetime

ignore = os.environ.get('IGNORE_WORDS')
IGNORE_WORDS = [i.lower().strip() for i in ignore.split(',')] if ignore else []

repositories = os.environ.get('REPOSITORIES')
REPOSITORIES = [r.lower().strip() for r in repositories.split(',')] if repositories else []

usernames = os.environ.get('USERNAMES')
USERNAMES = [u.lower().strip() for u in usernames.split(',')] if usernames else []

BRANCH = os.environ.get('BRANCH', None)

try:
    SLACK_WEBHOOK = os.environ['SLACK_WEBHOOK']
    GITHUB_URL = os.environ['GITHUB_URL']
    GITHUB_API_TOKEN = os.environ['GITHUB_API_TOKEN']
    ORGANIZATION = os.environ['ORGANIZATION']
except KeyError as error:
    sys.stderr.write('Please set the environment variable {0}'.format(error))
    sys.exit(1)


def fetch_repository_pulls(repository):
    pulls = []
    for pull in repository.pull_requests(state='open', base=BRANCH):
        if not USERNAMES or pull.user.login.lower() in USERNAMES:
            pulls.append(pull)
    return pulls


def is_valid_title(title):
    lowercase_title = title.lower()
    for ignored_word in IGNORE_WORDS:
        if ignored_word in lowercase_title:
            return False
    return True


def get_footer(pull):
    # Create naive datetime objects for the footer date information
    epoch = datetime.utcfromtimestamp(0)
    created_at = pull.created_at.replace(tzinfo=None)

    # Create the footer specifying how old the PR is
    difference = datetime.utcnow() - created_at
    old = difference.days
    old_text = 'day'
    if old == 0:
        old = difference.seconds // 3600
        old_text = 'hour'
        if old == 0:
            old = difference.seconds // 60
            old_text = 'minute'
            if old == 0:
                old = difference.seconds
                old_text = 'second'
    return 'Just now' if old == 0 else '{} {}{} old'.format(old, old_text, '' if old == 1 else 's'), (created_at - epoch).total_seconds()


def get_reviewers(reviews, ignore = []):
    reviewers = {}
    # Get a dictionary of reviewers with their final review and timestamp
    # Note: if the review is approve or reject it takes priority over comments
    for review in reviews:
        reviewer = review.user.login
        if reviewer not in ignore and (reviewer not in reviewers or \
          review.state == 'APPROVED' or review.state == 'CHANGES_REQUESTED' or \
          reviewers[reviewer]['state'] != 'APPROVED' and reviewers[reviewer]['state'] != 'CHANGES_REQUESTED'):
            reviewers[reviewer] = {
                'state': review.state,
                'submitted_at': review.submitted_at
            }
    return reviewers


def format_pull_requests(pull_requests, organization_name, repository):
    attachments = []

    for pull in pull_requests:
        if is_valid_title(pull.title):
            creator = pull.user.login

            reviewed_reviewers = get_reviewers(pull.reviews(), [creator])
            requested_reviewers = {user.login for user in pull.requested_reviewers}

            # Get formatted list of reviewers
            reviewers = {'~{0}~'.format(reviewer) if review['state'] == 'APPROVED' else reviewer for reviewer, review in reviewed_reviewers.items()}
            reviewers |= requested_reviewers

            try:
                earliest_approved_date = min(review['submitted_at'] for reviewer, review in reviewed_reviewers.items() if review['state'] == 'APPROVED')
                # Convert datetime to naive datetime
                earliest_approved_date = earliest_approved_date.replace(tzinfo=None)
            except (ValueError):
                earliest_approved_date = None

            try:
                latest_reject_date = max(review['submitted_at'] for reviewer, review in reviewed_reviewers.items() if review['state'] == 'CHANGES_REQUESTED')
                # Convert datetime to naive datetime
                latest_reject_date = latest_reject_date.replace(tzinfo=None)
            except (ValueError):
                latest_reject_date = None

            # Find the latest commit date by passing through GitHubIterator to the end
            for commit in pull.commits():
                pass
            latest_commit_date = commit._json_data['commit']['committer']['date']
            # Convert unicode datetime to naive datetime object
            latest_commit_date = datetime.strptime(latest_commit_date, '%Y-%m-%dT%H:%M:%SZ')

            # Determine what color we should include in the message
            color = None
            if latest_reject_date is not None:
                if latest_commit_date > latest_reject_date:
                    # When a commit is pushed after a change was requested
                    color = 'warning'
                else:
                    # When a change is requested
                    color = 'danger'
            elif earliest_approved_date is not None and latest_commit_date > earliest_approved_date:
                # When there are further commits after PR was approved by someone
                color = 'warning'
            elif len(requested_reviewers) == 0 and repository.pull_request(pull.number).mergeable:
                # All requested reviewers has reviewed and github deems PR mergeable
                color = 'good'


            footer, ts = get_footer(pull)

            attachment = {
                "title": '[{0}/{1}] <{2}|#{3}: {4}>'.format(organization_name, repository.name, pull.html_url, pull.number, pull.title),
                "color": color,
                "fields": [
                    {
                        "title": "By",
                        "value": creator,
                        "short": True
                    },
                    {
                        "title": "Reviewers",
                        "value": ', '.join(reviewers) if len(reviewers) > 0 else '_No reviewers assigned_',
                        "short": True
                    }
                ],
                "footer_icon": 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png',
                "footer": footer,
                "ts": ts
            }

            attachments.append(attachment)

    return attachments


def fetch_organization_pulls(organization_name):
    """
    Returns a formatted string list of open pull request messages.
    """
    client = enterprise_login(url=GITHUB_URL, token=GITHUB_API_TOKEN)
    organization = client.organization(organization_name)
    attachments = []

    for repository in organization.repositories():
        if REPOSITORIES and repository.name.lower() not in REPOSITORIES:
            continue
        unchecked_pulls = fetch_repository_pulls(repository)
        if unchecked_pulls:
            attachments.append(['[{}/{}]'.format(organization_name, repository.name), repository.html_url, format_pull_requests(unchecked_pulls, organization_name, repository)])

    return attachments


def send_to_slack(text, attachments):
    payload = {
        # 'channel': '@btsao',
        'username': 'Pull Request Reminder',
        'icon_emoji': ':bell:',
        'text': text,
        'attachments': attachments
    }

    response = requests.post(SLACK_WEBHOOK, json=(payload))
    if not response.status_code == 200:
        raise Exception('Error posting to slack webhook!')


def send_help():
    attachments = [
        {
            "text": "Reviewed by the requested reviewers and is mergeable",
            "color": "good"
        },
        {
            "text": "Commit has been pushed after an approval or change request",
            "color": "warning"
        },
        {
            "text": "Change has been requested",
            "color": "danger"
        }
    ]
    send_to_slack(None, attachments)


def cli():
    attachments = fetch_organization_pulls(ORGANIZATION)
    if attachments:
        send_help()
        for attachment in attachments:
            organization_and_repository = attachment[0]
            repository_url = attachment[1]
            open_pull_requests = attachment[2]
            if open_pull_requests:
                text = 'Pull requests open for `<{}|{}>`'.format(repository_url, organization_and_repository)
                if len(open_pull_requests) > 20:
                    text += '\n*WARNING: Too many open pull requests, only 20 will be shown!*'
                    open_pull_requests = open_pull_requests[:20]
                send_to_slack(text, open_pull_requests)


if __name__ == '__main__':
    cli()
