#!/bin/env python

import os
import logging
import airflow
from airflow import models, settings
from airflow.contrib.auth.backends.password_auth import PasswordUser

LOG = logging.getLogger('interpreter_setter')
if not LOG.handlers:
    LOG.propagate = 0
    CONSOLE = logging.StreamHandler()
    LOG.addHandler(CONSOLE)
    FORMATTER = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s: %(message)s')
    CONSOLE.setFormatter(FORMATTER)

USER = os.environ.get('AF_USER')
PASSWD = os.environ.get('AF_PASSWORD')


if USER and PASSWD:
    LOG.info('Adding user "%s" to Airflow users', USER)
    user = PasswordUser(models.User())
    user.username = USER
    user.password = PASSWD
    user.superuser = True

    session = settings.Session()
    session.add(user)
    session.commit()
    session.close()
else:
    LOG.error('Unable to add Airflow user: check "AF_USER" and/or "AF_PASSWORD" environment variables')
