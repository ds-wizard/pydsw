import collections
import datetime
import json
import mimetypes
import pathlib
import uuid

from typing import Optional

from dsw.command_queue import CommandWorker, CommandQueue
from dsw.database.database import Database, PersistentCommand
from dsw.storage import S3Storage

from .config import SeederConfig
from .consts import DEFAULT_ENCODING, DEFAULT_MIMETYPE, \
    DEFAULT_PLACEHOLDER, Queries
from .context import Context
from .logging import prepare_logging


def _guess_mimetype(filename: str) -> str:
    try:
        content_type = mimetypes.guess_type(filename)[0]
        return content_type or DEFAULT_MIMETYPE
    except Exception:
        return DEFAULT_MIMETYPE


class SeedRecipe:

    def __init__(self, name: str, description: str, root: pathlib.Path,
                 db_scripts: list[pathlib.Path], db_placeholder: str,
                 s3_app_dir: Optional[pathlib.Path], s3_fname_replace: dict[str, str],
                 uuids_count: int, uuids_placeholder: Optional[str]):
        self.name = name
        self.description = description
        self.root = root
        self.db_scripts = db_scripts
        self.db_placeholder = db_placeholder
        self.s3_app_dir = s3_app_dir
        self.s3_fname_replace = s3_fname_replace
        self._db_scripts_data = collections.OrderedDict()  # type: dict[pathlib.Path, str]
        self.s3_objects = collections.OrderedDict()  # type: dict[pathlib.Path, str]
        self.prepared = False
        self.uuids_count = uuids_count
        self.uuids_placeholder = uuids_placeholder
        self.uuids_replacement = dict()  # type: dict[str, str]

    def _load_db_scripts(self):
        for db_script in self.db_scripts:
            self._db_scripts_data[db_script] = db_script.read_text(
                encoding=DEFAULT_ENCODING,
            )

    def _load_s3_object_names(self):
        if self.s3_app_dir is None:
            return
        for s3_object_path in self.s3_app_dir.glob('**/*'):
            if s3_object_path.is_file():
                target_object_name = str(
                    s3_object_path.relative_to(self.s3_app_dir).as_posix()
                )
                for r_from, r_to in self.s3_fname_replace.items():
                    target_object_name = target_object_name.replace(r_from, r_to)
                self.s3_objects[s3_object_path] = target_object_name

    def _prepare_uuids(self):
        for i in range(self.uuids_count):
            key = self.uuids_placeholder.replace('[n]', f'[{i}]')
            self.uuids_replacement[key] = str(uuid.uuid4())

    def prepare(self):
        if self.prepared:
            return
        self._load_db_scripts()
        self._load_s3_object_names()
        self._prepare_uuids()
        self.prepared = True

    def run_prepare(self):
        self._prepare_uuids()

    def _replace_db_script(self, script: str, app_uuid: str) -> str:
        result = script.replace(self.db_placeholder, app_uuid)
        for uuid_key, uuid_value in self.uuids_replacement.items():
            result = result.replace(uuid_key, uuid_value)
        return result

    def iterate_db_scripts(self, app_uuid: str):
        return (
            (name, self._replace_db_script(script, app_uuid))
            for name, script in self._db_scripts_data.items()
        )

    def _replace_object_name(self, object_name: str) -> str:
        result = object_name
        for uuid_key, uuid_value in self.uuids_replacement.items():
            result = result.replace(uuid_key, uuid_value)
        return result

    def iterate_s3_objects(self):
        return (
            (local_name, self._replace_object_name(object_name))
            for local_name, object_name in self.s3_objects.items()
        )

    def __str__(self):
        scripts = '\n'.join((f'- {x}' for x in self.db_scripts))
        replaces = '\n'.join(
            (f'- "{x}" -> "{y}"' for x, y in self.s3_fname_replace.items())
        )
        return f'Recipe: {self.name}\n' \
               f'Loaded from: {self.root}\n' \
               f'{self.description}\n\n' \
               f'DB SQL Scripts:\n' \
               f'{scripts}\n' \
               f'DB APP UUID Placeholder: "{self.db_placeholder}"\n\n' \
               f'S3 App Dir:\n' \
               f'{self.s3_app_dir if self.s3_app_dir is not None else "[nothing]"}\n' \
               f'S3 Filename Replace:\n' \
               f'{replaces}'

    @staticmethod
    def load_from_json(recipe_file: pathlib.Path) -> 'SeedRecipe':
        data = json.loads(recipe_file.read_text(
            encoding=DEFAULT_ENCODING,
        ))
        db = data.get('db', {})  # type: dict
        s3 = data.get('s3', {})  # type: dict
        scripts = [
            pathlib.Path(x) for x in db.get('scripts', [])
        ]
        db_scripts = list()
        for script in scripts:
            if '*' in str(script):
                db_scripts.extend(
                    sorted([s for s in recipe_file.parent.glob(str(script))])
                )
            elif script.is_absolute():
                db_scripts.append(script)
            else:
                db_scripts.append(recipe_file.parent / script)
        s3_app_dir = None
        if 'appDir' in s3.keys():
            s3_app_dir = recipe_file.parent / s3['appDir']
        return SeedRecipe(
            name=data['name'],
            description=data.get('description', ''),
            root=recipe_file.parent,
            db_scripts=db_scripts,
            db_placeholder=db.get('appIdPlaceholder', DEFAULT_PLACEHOLDER),
            s3_app_dir=s3_app_dir,
            s3_fname_replace=s3.get('filenameReplace', {}),
            uuids_count=data.get('uuids', {}).get('count', 0),
            uuids_placeholder=data.get('uuids', {}).get('placeholder', None),
        )

    @staticmethod
    def load_from_dir(recipes_dir: pathlib.Path) -> dict[str, 'SeedRecipe']:
        recipe_files = recipes_dir.glob('*.seed.json')
        recipes = (SeedRecipe.load_from_json(f) for f in recipe_files)
        return {r.name: r for r in recipes}

    @staticmethod
    def create_default():
        return SeedRecipe(
            name='default',
            description='Default dummy recipe',
            root=pathlib.Path('/dev/null'),
            db_scripts=[],
            db_placeholder='<<|APP-ID|>>',
            s3_app_dir=pathlib.Path('/dev/null'),
            s3_fname_replace={},
            uuids_count=0,
            uuids_placeholder=None,
        )


class DataSeeder(CommandWorker):

    def __init__(self, cfg: SeederConfig, workdir: pathlib.Path):
        self.cfg = cfg
        self.workdir = workdir
        self.recipe = SeedRecipe.create_default()  # type: SeedRecipe

        self._prepare_logging()
        self._init_context(workdir=workdir)

    def _init_context(self, workdir: pathlib.Path):
        Context.initialize(
            config=self.cfg,
            workdir=workdir,
            db=Database(cfg=self.cfg.db),
            s3=S3Storage(
                cfg=self.cfg.s3,
                multi_tenant=self.cfg.cloud.multi_tenant,
            ),
        )

    def _prepare_logging(self):
        prepare_logging(cfg=self.cfg)
        Context.logger.set_level(self.cfg.log.level)

    def _prepare_recipe(self, recipe_name: str):
        Context.logger.info('Loading recipe')
        recipes = SeedRecipe.load_from_dir(self.workdir)
        if recipe_name not in recipes.keys():
            raise RuntimeError(f'Recipe "{recipe_name}" not found')
        Context.logger.info('Preparing seed recipe')
        self.recipe = recipes[recipe_name]
        self.recipe.prepare()

    def work(self) -> bool:
        Context.update_trace_id('-')
        ctx = Context.get()
        Context.logger.debug('Trying to fetch a new job')
        cursor = ctx.app.db.conn_query.new_cursor(use_dict=True)
        cursor.execute(Queries.SELECT_CMD, {'now': datetime.datetime.utcnow()})
        result = cursor.fetchall()
        if len(result) != 1:
            Context.logger.debug(f'Fetched {len(result)} jobs')
            return False

        command = result[0]
        try:
            cmd = PersistentCommand.deserialize(command)
            self._process_command(cmd)
        except Exception as e:
            Context.logger.warning(f'Failed: {str(e)}')
            ctx.app.db.execute_query(
                query=Queries.UPDATE_CMD_ERROR,
                attempts=command.get('attempts', 0) + 1,
                error_message=f'Failed: {str(e)}',
                updated_at=datetime.datetime.utcnow(),
                uuid=command['uuid'],
            )

        Context.logger.info('Committing transaction')
        ctx.app.db.conn_query.connection.commit()
        cursor.close()
        Context.logger.info('Job processing finished')
        return True

    def _process_command(self, cmd: PersistentCommand):
        Context.update_trace_id(cmd.uuid)
        self.recipe.run_prepare()
        app_ctx = Context.get().app
        app_uuid = cmd.body['appUuid']
        Context.logger.info(f'Seeding recipe "{self.recipe.name}" '
                            f'to app with UUID "{app_uuid}"')
        self.execute(app_uuid)
        app_ctx.db.execute_query(
            query=Queries.UPDATE_CMD_DONE,
            attempts=cmd.attempts + 1,
            updated_at=datetime.datetime.utcnow(),
            uuid=cmd.uuid,
        )

    def run(self, recipe_name: str):
        self._prepare_recipe(recipe_name)
        Context.logger.info('Preparing command queue')
        queue = CommandQueue(
            worker=self,
            db=Context.get().app.db,
            listen_query=Queries.LISTEN,
        )
        queue.run()

    def seed(self, recipe_name: str, app_uuid: str):
        self._prepare_recipe(recipe_name)
        Context.logger.info('Executing recipe')
        self.execute(app_uuid=app_uuid)
        Context.logger.info('Committing')
        Context().get().app.db.conn_query.connection.commit()

    def execute(self, app_uuid: str):
        # Run SQL scripts
        app_ctx = Context.get().app
        cursor = app_ctx.db.conn_query.new_cursor(use_dict=True)
        phase = 'DB'
        try:
            Context.logger.info('Running SQL scripts')
            for path, script in self.recipe.iterate_db_scripts(app_uuid):
                Context.logger.debug(f' -> Executing script: {path.name}')
                cursor.execute(query=script)
                Context.logger.debug(f'    OK: {cursor.statusmessage}')
            phase = 'S3'
            Context.logger.info('Transferring S3 objects')
            for local_file, object_name in self.recipe.iterate_s3_objects():
                Context.logger.debug(f' -> Reading: {local_file.name}')
                data = local_file.read_bytes()
                Context.logger.debug(f' -> Sending: {object_name}')
                app_ctx.s3.store_object(
                    app_uuid=app_uuid,
                    object_name=object_name,
                    content_type=_guess_mimetype(local_file.name),
                    data=data,
                )
                Context.logger.debug('    OK (stored)')
        except Exception as e:
            if Context.get().app.cfg.log.level == 'DEBUG':
                import traceback
                print('-'*60)
                traceback.print_exc()
                print('-'*60)
            Context.logger.warn(f'Exception appeared [{type(e).__name__}]: {e}')
            app_ctx.db.conn_query.connection.rollback()
            raise RuntimeError(f'{phase}: {e}')
        finally:
            Context.logger.info('Data seeding done')
            cursor.close()
