import io
import os
from distutils.version import StrictVersion
from importlib import import_module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.migrations.recorder import \
    MigrationRecorder as DjangoMigrationRecorder
from django.db.utils import ProgrammingError


fixtures_default_tpl = 'fixtures_{}.sql'
schema_default_tpl = 'schema_{}.sql'


class DBException(Exception):
    pass


def is_version(vstring):
    try:
        StrictVersion(vstring)
    except ValueError:
        return False
    return True


def list_dirs(root):
    return [d for d in os.listdir(root)
            if os.path.isdir(os.path.join(root, d))]


def list_files(root):
    return [d for d in os.listdir(root)
            if os.path.isfile(os.path.join(root, d))]


class MigrationRecorder(DjangoMigrationRecorder):
    def record_applied(self, app, name):
        """
        Records that a migration was applied.
        """
        # custom: do not ensure schema
        self.migration_qs.create(app=app, name=name)


def get_known_versions():
    """
    Return the list of the known versions defined in migration repository,
    ordered.
    Ignore symlinks.
    """
    # get all subfolders
    try:
        dirs = list_dirs(settings.NORTH_MIGRATIONS_ROOT)
    except OSError:
        raise ImproperlyConfigured(
            'settings.NORTH_MIGRATIONS_ROOT is improperly configured.')

    # exclude symlinks and some folders (like schemas, fixtures, etc)
    versions = [
        d for d in dirs
        if not os.path.islink(os.path.join(settings.NORTH_MIGRATIONS_ROOT, d))
        and is_version(d)]

    # sort versions
    versions.sort(key=StrictVersion)
    return versions


def get_applied_versions(connection):
    """
    Return the list of applied versions.
    Reuse django migration table.
    """
    recorder = MigrationRecorder(connection)
    applied_versions = list(recorder.migration_qs.filter(
        app__in=get_known_versions()
    ).values_list(
        'app', flat=True).order_by('app').distinct())

    # sort versions
    applied_versions.sort(key=StrictVersion)
    return applied_versions


def get_current_version(connection):
    """
    Return the current version of the database.
    Return None if the schema is not inited.
    """
    try:
        import_string = settings.NORTH_CURRENT_VERSION_DETECTOR
    except AttributeError:
        import_string = (
            'django_north.management.migrations'
            '.get_current_version_from_table')

    module_path, factory_name = import_string.rsplit('.', 1)
    module = import_module(module_path)
    factory = getattr(module, factory_name)

    return factory(connection)


def get_current_version_from_table(connection):
    """
    Return the current version of the database, from sql_version table.
    Return None if the table does not exist (schema not inited).
    """
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT version_num FROM sql_version;")
        except ProgrammingError:
            # table does not exist ?
            return None

        rows = cursor.fetchall()

    versions = [row[0] for row in rows if is_version(row[0])]
    if not versions:
        return None

    # sort versions
    versions.sort(key=StrictVersion)

    # return the last one
    return versions[-1]


def get_current_version_from_comment(connection):
    """
    Return the current version of the database, from django_site comment.
    Return None if the table django_site does not exist (schema not inited).
    """
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "SELECT obj_description('django_site'::regclass, 'pg_class');")
        except ProgrammingError:
            # table does not exist ?
            return None

        row = cursor.fetchone()
        comment = row[0]

    # no comment
    if comment is None:
        raise DBException('No comment found on django_site.')

    # parse comment
    if 'version ' not in comment:
        raise DBException("No version found in django_site's comment.")
    return comment.replace('version ', '').strip()


def get_applied_migrations(version, connection):
    """
    Return the list of applied migrations for the given version.
    Reuse django migration table.
    """
    recorder = MigrationRecorder(connection)
    return list(recorder.migration_qs.filter(app=version).values_list(
        'name', flat=True))


def get_migrations_to_apply(version):
    """
    Return an dict containing the list of migrations to apply for
    the given version.
    Key: name of the migration.
    Value: path of the migration.
    """
    def filter_migrations(files):
        return [
            f for f in files
            if f.endswith('ddl.sql') or f.endswith('dml.sql')]

    version_root = os.path.join(settings.NORTH_MIGRATIONS_ROOT, version)
    migrations = {}

    # list auto migrations
    try:
        files = list_files(version_root)
    except OSError:
        raise DBException('No sql folder found for version {}.'.format(
            version))
    # filter files (keep *ddl.sql and *dml.sql)
    auto_migrations = filter_migrations(files)
    # store migrations
    for mig in auto_migrations:
        migrations[mig] = os.path.join(version_root, mig)

    # list manual migrations
    manual_root = os.path.join(version_root, 'manual')
    try:
        files = list_files(manual_root)
    except OSError:
        files = []
    # filter files (keep *ddl.sql and *dml.sql)
    auto_migrations = filter_migrations(files)
    # store migrations
    for mig in auto_migrations:
        migrations[mig] = os.path.join(manual_root, mig)

    return migrations


def get_closest_version(target_version, sql_tpl, force_version=None):
    """
    Get the version of a file (schema or fixtures) to use to init a DB.
    Take the closest to the target_version. Can be the same version, or older.
    """
    # get known versions
    known_versions = get_known_versions()
    # find target version
    try:
        target_version_index = known_versions.index(target_version)
    except ValueError:
        raise ImproperlyConfigured(
            'settings.NORTH_TARGET_VERSION is improperly configured: '
            'version {} not found.'.format(
                settings.NORTH_TARGET_VERSION))

    # should we set a version from settings ?
    if force_version:
        if force_version not in known_versions[:target_version_index+1]:
            raise ImproperlyConfigured(
                'settings.NORTH_TARGET_VERSION is improperly configured: '
                'settings.NORTH_SCHEMA_VERSION is more recent.')

        path = sql_tpl.format(force_version)
        if os.path.exists(path):
            return force_version

        # not found
        return None

    def get_version(index):
        version = known_versions[index]
        schema_path = sql_tpl.format(version)
        return version, schema_path

    while target_version_index > 0:
        version, path = get_version(target_version_index)
        if os.path.exists(path):
            return version
        target_version_index -= 1

    version, path = get_version(target_version_index)
    if os.path.exists(path):
        return version

    # not found
    return None


def get_version_for_init():
    """
    Get the version to use to init a new DB to the current target version.
    """
    version = get_closest_version(
        settings.NORTH_TARGET_VERSION,
        os.path.join(
            settings.NORTH_MIGRATIONS_ROOT,
            'schemas',
            getattr(settings, 'NORTH_SCHEMA_TPL', schema_default_tpl)),
        force_version=getattr(settings, 'NORTH_SCHEMA_VERSION', None))

    if version is None:
        raise DBException('Can not find a schema to init the DB.')
    return version


def get_fixtures_for_init(target_version):
    """
    Get the closest fixtures to use to init a new DB
    to the current target version.
    """
    version = get_closest_version(
        target_version,
        os.path.join(
            settings.NORTH_MIGRATIONS_ROOT,
            'fixtures',
            getattr(settings, 'NORTH_FIXTURES_TPL', fixtures_default_tpl)))

    if version is None:
        raise DBException('Can not find fixtures to init the DB.')
    return version


def is_manual_migration(file_handler):
    if '/manual/' in file_handler.name:
        return True

    if not file_handler.name.endswith('dml.sql'):
        return False

    for line in file_handler:
        if '--meta-psql:' in line:
            file_handler.seek(0)
            return True

    file_handler.seek(0)
    return False


def build_migration_plan(connection):
    """
    Return the list of migrations by version,
    from the version used to init the DB to the current target version.
    """
    # get current version
    current_version = get_current_version(connection)
    if current_version is None:
        # schema not inited
        return None
    # get known versions
    known_versions = get_known_versions()
    # get applied versions
    applied_versions = get_applied_versions(connection)

    migration_plan = {
        'current_version': current_version,
        'init_version': None,
        'plans': [],
    }

    # guess the version used to init the DB
    if not applied_versions:
        # current version is not None, it was used to init the DB
        try:
            first_version_index = known_versions.index(current_version) + 1
        except ValueError:
            raise DBException(
                'The current version of the database is unknown: {}.'
                .format(current_version))
        init_version = current_version
    else:
        first_version_index = known_versions.index(applied_versions[0])
        init_version = known_versions[first_version_index - 1]
    migration_plan['init_version'] = init_version

    # get all versions to apply
    try:
        target_version_index = known_versions.index(
            settings.NORTH_TARGET_VERSION)
    except ValueError:
        raise ImproperlyConfigured(
            'settings.NORTH_TARGET_VERSION is improperly configured: '
            'version {} not found.'.format(
                settings.NORTH_TARGET_VERSION))
    versions_to_apply = known_versions[
        first_version_index:target_version_index + 1]

    # get plan for each version to apply
    for version in versions_to_apply:
        version_plan = []
        # get applied migrations
        applied_migrations = get_applied_migrations(version, connection)
        # get migrations to apply
        migrations_to_apply = get_migrations_to_apply(version)
        migs = list(migrations_to_apply.keys())
        migs.sort()
        # build plan
        for mig in migs:
            applied = mig in applied_migrations
            path = migrations_to_apply[mig]
            with io.open(path, 'r', encoding='utf8') as f:
                is_manual = is_manual_migration(f)
            version_plan.append((mig, applied, path, is_manual))
        migration_plan['plans'].append({
            'version': version,
            'plan': version_plan
        })

    return migration_plan
