# Adding a new project

## Table of contents

[[_TOC_]]

## First add the project into the configuration file

```bash
$ runbotmgr edit-config
```

Add the project on the project section, by exemple to add solumob on cias runbot.

```yaml
projects:
  cias:
    url: cias.runbot.eezee-box.com
    description: Project to store 'cias' instances
  promeris:
     url: promeris.test.eezee-box.com
     description: Project to store 'promeris' instances
  solumob:
    url: solumob.test.eezee-box.com
    description: Project to store 'promeris' instances
```

Update the projects

```bash
$ project.init-default
```

## Get image if needed

```bash
$ lxc image copy eze:debian-10-odoo-15-0 local: --alias debian-10-odoo-15-0
```

## Creating a new container

```bash
$ runbot create --version %apps-version% --name %branch-name% --project %project%
# Exemple for promeris
$ runbot create --version 15.0 --name develop --project promeris
```

## Configure the new odoo on the project

```bash
$ runbot use promeris
$ runbot execute -n develop --command "git -C odoo/community pull" --project promeris
$ runbot execute -n develop --command "git -C odoo/enterprise pull" --project promeris
$ runbot execute -n develop --command "GIT_SSH_COMMAND=\'ssh -i ~/.ssh/id_enterprise -o IdentitiesOnly=yes\' git -C eezee-box/ pull'" --project promeris
$ runbot execute -n develop --command "mkdir addons-PROMERIS" --project promeris
$ runbot execute -n develop --command "odoo scaffold --project-name promeris --project-directory addons-PROMERIS --version 15.0" --project promeris
$ runbot execute -n develop --command "odoo init --database-name promeris" --project promeris
$ runbot execute -n develop --command "odoo install -a eezee_about,eezee_auth_sso,eezee_maintenance_cost --not-http" --project promeris
$ runbot execute -n develop --command "ssh-keygen -t rsa -C odoo@promeris.test.eezee-box.com -f /opt/local/odoo/.ssh/id_rsa -q -N ''" --project promeris
```


