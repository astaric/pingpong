while true; do echo "`date "+%H:%M"` - BACKUP"; python manage.py dumpdata > backups/backup-`date "+%H%M"`.json; sleep 60; done
