import argparse
import os

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = "Удаление миграций проекта"

    allowed_dirs = ["all"]
    not_allowed_dirs = ["sites"]

    def add_arguments(self, parser):
        parser.description = "Получение корневой папки и папок для удаления"

        class StoreNameValuePair(argparse.Action):
            def __call__(self, parser, namespace, values, option_string=None):
                n, v = values.split("=")
                setattr(namespace, n, v)

        # parser.add_argument('root', action=StoreNameValuePair,
        #                     help='корневая папка, с которой начнётся поиск папок migrations')
        parser.add_argument(
            "--apps",
            nargs="*",
            required=False,
            help="список приложений, в которых будут очищаться папки migrations",
        )

    def handle(self, **options):
        walk_root = options.get("root", None)
        if walk_root:
            if not os.path.isdir(walk_root):
                raise AttributeError(f"The directory {walk_root} does not exist!")
        else:
            walk_root = settings.ROOT_DIR.root

        apps = options.get("apps", None)
        if apps:
            self.allowed_dirs = apps

        if "all" not in self.allowed_dirs:
            print(
                "Removing only migrations nested in directories:",
                ", ".join(self.allowed_dirs),
            )
        else:
            print(
                "Removing all migrations except ones nested in directories:",
                ", ".join(self.not_allowed_dirs),
            )

        migration_dirs = [
            root for root, _, _ in os.walk(walk_root) if root.endswith("migrations")
        ]

        rm_dirs = migration_dirs

        if "all" in self.allowed_dirs:
            for not_allowed_dir in self.not_allowed_dirs:
                rm_dirs = list(filter(lambda x: not_allowed_dir not in x, rm_dirs))
        else:
            rm_dirs = []
            for allowed_dir in self.allowed_dirs:
                rm_dirs += list(filter(lambda x: allowed_dir in x, migration_dirs))

        print("Directories to clear:")
        for rm_dir in rm_dirs:
            print(rm_dir)
        print("Are you sure you want to clear these directories? (yes/[no])")

        answer = input()
        if answer == "yes":
            for rm_dir in rm_dirs:
                for root, _, files in os.walk(rm_dir):
                    for file in files:
                        if file != "__init__.py":
                            path = os.path.join(root, file)
                            print("removed:", path)
                            os.remove(path)
