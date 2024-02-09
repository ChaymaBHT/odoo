# Configure Gitlab Runner

This documentation explain how to install the runbot tools to execute test on gitlab.

## Table of contents

[[_TOC_]]

## Install Runbotmgr

You can use pip to install runbotmgr, first clone the repo and execute the command pip3.

```bash
$ GIT_SSH_COMMAND='ssh -i ~/.ssh/deployment_rsa -o IdentitiesOnly=yes' git clone git@gitlab.com:eezee-it/system-runbotmgr.git
$ pip3 install ./system-runbotmgr
```

## Generate keys to communicate with lxd endpoints

To access the runbot server, a ssh keys should be generate to communicate securely between 
the two servers.

First check if the key exists:

```bash
$ runbotmgr api.check-keys
```

If not exists create the new keys:

```bash
$ runbotmgr api.generate-keys
```

## Adding the runbot server (lxd enpoints)

### Configure a new endpoint

Create a file ~/runbot.yml (or edit it) and added the content bellow.

If the file exist the content can be remove, the file is only used to authenticate the remote.

For exemple, for the eezee-it runbot:

```bash
$ runbotmgr edit-config
```

```yaml
---
remote: True
remote_endpoint: https://eezee-it.test.eezee-box.com:8443
```

### Authenticate to the endpoints

The authentification should be done only once, the password is added to the keys.

The command ask for a password stored in the lastpass (search Runbot).runbot

```bash
$ runbotmgr api.authenticate
```

### Test the new connection

To test if the endpoint is correctly set, try to show the runbot list

```bash
$ runbot list --project default
```

### Remove configuration file

If the configuration is correctly set, you can remove the runbot.yml file, because
this file should be set on gitlab directly.

```bash
rm ~/runbot.yml
```

## Configure Gitlab repo to use runbot

To configure gitlab we use Environment et deployement offer by gitlab, the gitlab documentation : https://docs.gitlab.com/ee/ci/environments/

## Create a configuration file

On the root of the repo create a file runbot.yml, with this content (exemple for eezee-it runbot)

```yaml
---
projects:
    eezee-it:
        url: eezee-it.test.eezee-box.com
        description: Project to store 'eezee-it' instances
remote: True
remote_endpoint: https://eezee-it.test.eezee-box.com:8443
default_project: eezee-it
```

The "projects" variable defined the runbot project data, by exemple the url to use for each 
runbot created.

The "remote" and "remote_endpoint" variables defined how to contact the runbot

The "default_project" variable defined the project to use when we deploy a runbot.

We can also used a "debug" variable to have more info on commands executed.

## Configure gitlab-ci.yml

Now we are define a configuration file pour runbot we can configure gitlab-ci to use deploy 
new runbot when new Merge requests are created.

This documentation doesn't explain how to configure flake8 and unittest.

Adapt variables on the yaml bellow and add-it on gitlab-ci.yml:

```yaml
variables:
  DEVELOP_BRANCH: "15.0-develop"
  PRODUCTION_BRANCH: "15.0"

stages:
  - deploy
  
deploy_develop_branch:
  stage: deploy
  tags:
    - eezeeit
    - deployment
  script:
    - /home/gitlab-runner/.local/bin/runbot --version
    - /home/gitlab-runner/.local/bin/runbot deploy --branch $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME --source-name $CI_MERGE_REQUEST_TARGET_BRANCH_NAME --name $CI_COMMIT_REF_SLUG
  environment:
    name: Staging/$CI_COMMIT_REF_NAME
    url: http://$CI_COMMIT_REF_SLUG.$DEPLOY_HOST
    on_stop: stop_staging_app
  rules:
    - if: $CI_MERGE_REQUEST_ID && $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME == $DEVELOP_BRANCH && $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME != $PRODUCTION_BRANCH

deploy_staging_branch:
  stage: deploy
  tags:
    - eezeeit
    - deployment
  script:
    - /home/gitlab-runner/.local/bin/runbot --version
    - /home/gitlab-runner/.local/bin/runbot deploy --branch $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME --source-name $CI_MERGE_REQUEST_TARGET_BRANCH_NAME --name $CI_COMMIT_REF_SLUG
  environment:
    name: Staging/$CI_COMMIT_REF_NAME
    url: http://$CI_COMMIT_REF_SLUG.$DEPLOY_HOST
    on_stop: stop_staging_app
    auto_stop_in: 3 month
  rules:
    - if: $CI_MERGE_REQUEST_ID && $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME =~ /^staging/ && $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME != $PRODUCTION_BRANCH && $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME != $DEVELOP_BRANCH
  
stop_staging_app:
  stage: deploy
  tags:
    - eezeeit
    - deployment
  script:
    - /home/gitlab-runner/.local/bin/runbot --version
    - /home/gitlab-runner/.local/bin/runbot delete --name $CI_COMMIT_REF_SLUG --force
  environment:
    name: Staging/$CI_COMMIT_REF_NAME
    action: stop
  rules:
    - if: $CI_MERGE_REQUEST_ID && $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME =~ /^staging/ && $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME != $PRODUCTION_BRANCH && $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME != $DEVELOP_BRANCH
      when: manual
      allow_failure: true


deploy_development_branch:
  stage: deploy
  tags:
    - eezeeit
    - deployment
  script:
    - /home/gitlab-runner/.local/bin/runbot --version
    - /home/gitlab-runner/.local/bin/runbot deploy --branch $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME --source-name $CI_MERGE_REQUEST_TARGET_BRANCH_NAME --name $CI_COMMIT_REF_SLUG
  environment:
    name: Development/$CI_COMMIT_REF_NAME
    url: http://$CI_COMMIT_REF_SLUG.$DEPLOY_HOST
    on_stop: stop_review_app
    auto_stop_in: 5 day # week, day, hour, minute
  rules:
    - if: $CI_MERGE_REQUEST_ID && $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME !~ /^staging/ && $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME != $PRODUCTION_BRANCH && $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME != $DEVELOP_BRANCH

stop_review_app:
  stage: deploy
  tags:
    - eezeeit
    - deployment
  script:
    - /home/gitlab-runner/.local/bin/runbot --version
    - /home/gitlab-runner/.local/bin/runbot delete --name $CI_COMMIT_REF_SLUG --force
  environment:
    name: Development/$CI_COMMIT_REF_NAME
    action: stop
  rules:
    - if: $CI_MERGE_REQUEST_ID && $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME !~ /^staging/ && $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME != $PRODUCTION_BRANCH && $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME != $DEVELOP_BRANCH
      when: manual
      allow_failure: true
```


