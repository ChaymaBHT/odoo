# Init a new runbot server

This document describe how to configure the runbotmgr tools.

## Table of contents

[[_TOC_]]

## Edit configuration

The runbot tools use a configuration file, to edit this file, you can use the command:

```bash
$ runbotmgr edit-config
```

## Init Project settings

This exemple is for the CIAS server, who have two projects

* CIAS: for the CIAS repository
* Promeris: for the Promeris repository


```yaml
---
default_project: cias
projects:
  cias:
    url: cias.runbot.eezee-box.com
    description: Project to store 'cias' instances
  promeris:
     url: promeris.test.eezee-box.com
     description: Project to store 'promeris' instances
```

### Add projects

The command can be launch to add new project.

```bash
$ runbotmgr project.init-default
```

## Init Runbot profile

### Configure profiles

The profile by default is:

```python
{'profiles': [{
    'name': 'demo',
    'is_env': True,
    'description': 'Demo instances',
    'cpu_limit': '2',
    'memory_limit': '4GB',
    'environment': {
        'ODOO_STAGE': 'demo'
    },
}, {
    'name': 'odoo',
    'is_env': False,
    'description': 'Odoo instances',
    'cpu_limit': '2',
    'memory_limit': '4GB',
}, {
    'name': 'dev',
    'is_env': True,
    'description': 'Development instances',
    'cpu_limit': '2',
    'memory_limit': '4GB',
}, {
    'name': 'staging',
    'is_env': True,
    'description': 'Staging instances',
    'cpu_limit': '2',
    'memory_limit': '4GB',
}, {
    'name': 'production',
    'is_env': True,
    'description': 'Production instances',
    'cpu_limit': False,
    'memory_limit': False,
}],
}
```

You can change-it in the configuration file, for you need.

### Install Profiles

To install profiles, run the command:

```bash
$ runbotmgr profile.init-default
```
