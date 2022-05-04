import argparse
import sys
import avito_parser, autoru_parser, db

class Manage(object):
    def __init__(self):
        parser = argparse.ArgumentParser(description='account and parser management',
                                         usage="""manage.py <command> [<args>]
                                         
Commonly used commands are:
acceptmanager     Create manager for telegram app
declinemanager     Delete manager record from telegram app
showmanagers      Show all managers of the telegram app
parse             Parse cars from avito.ru or/and auto.ru""")

        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        getattr(self, args.command)()


    def parse(self):
        parser = argparse.ArgumentParser(description='Create manager for telegram app',
                                         usage="manage.py parse [--source] [<avito | autoru>]")
        parser.add_argument('--source', default='all', help='<avito>, only from avito.ru; <autoru>, only from auto.ru')
        args = parser.parse_args(sys.argv[2:])
        if args.source == 'avito':
            print('Running manage parse, source=%s' % args.source)
            avito_parser.main()
        elif args.source == 'autoru':
            print('Running manage parse, source=%s' % args.source)
            autoru_parser.main()
        elif args.source == 'all':
            print('Running manage parse, source=%s' % args.source)
            autoru_parser.main()
            avito_parser.main()
        else:
            print('Wrong source! Write "manage.py parse -h" to see help message')


    def acceptmanager(self):
        parser = argparse.ArgumentParser(description='Create manager for telegram app',
                                         usage="manage.py acceptmanager [id]")
        parser.add_argument('id')
        args = parser.parse_args(sys.argv[2:])
        id = args.id
        print('Running manage acceptmanager, id=%s' % id)

        users_list = db.show_managers()
        users = []
        for user in users_list:
            users.append(user[0])

        if int(id) in users:
            db.update_status('users', int(id), 'True')
            db.update_confirm('users', 'id', int(id), 'False')
            print(f'manager @{id} successfully added!')
        else:
            print('wrong id!')


    def declinemanager(self):
        parser = argparse.ArgumentParser(description='Delete manager record from telegram app',
                                         usage="manage.py declinemanager [id]")
        parser.add_argument('id')
        args = parser.parse_args(sys.argv[2:])
        id = args.id
        print('Running manage declinemanager, id=%s' % id)

        staff = db.handle_staff('users', 'wait_confirm')
        managers_list = db.show_managers()
        managers =[]
        for manager in managers_list:
            if manager[2] == True:
                managers.append(manager[0])
        if int(id) in managers:
            db.update_status('users', int(id), 'False')
            db.update_confirm('users', 'id', int(id), 'False')
            print(f'manager @{id} successfully removed!')
        else:
            print('wrong id!')


    def showmanagers(self):
        parser = argparse.ArgumentParser(description='Show all managers of the telegram app',
                                         usage="manage.py showmanagers")
        print('Running manage showmanagers')
        managers = db.show_managers()
        print('id\t\tusername\t\tis manager?')
        for tuple in managers:
            print(f'{tuple[0]}\t{tuple[1]}\t\t{tuple[2]}')



if __name__ == '__main__':
    Manage()