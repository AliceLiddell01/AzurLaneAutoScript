import os
import threading
import time

from module.base.utils import save_image
from module.logger import logger
from module.statistics.utils import pack


class DropImage:
    """Collect screenshots for an optional local drop record."""

    def __init__(self, recorder, genre, save, info=''):
        self.recorder = recorder
        self.genre = str(genre)
        self.save = bool(save)
        self.info = info
        self.images = []

    def add(self, image):
        if self:
            self.images.append(image)
            logger.info(f'Drop record added, genre={self.genre}, amount={self.count}')

    def handle_add(self, main, before=None):
        if before is None:
            before = main.config.WAIT_BEFORE_SAVING_SCREEN_SHOT
        if self:
            main.handle_info_bar()
            main.device.sleep(before)
            main.device.screenshot()
            self.add(main.device.image)

    def clear(self):
        self.images = []

    @property
    def count(self):
        return len(self.images)

    def __bool__(self):
        return self.save

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self:
            self.recorder.commit(
                images=self.images,
                genre=self.genre,
                save=self.save,
                info=self.info,
            )


class DropRecorder:
    """Save packed drop screenshots locally; no network upload support."""

    def __init__(self, config):
        self.config = config

    def _save(self, image, genre, filename):
        try:
            folder = os.path.join(str(self.config.DropRecord_SaveFolder), genre)
            os.makedirs(folder, exist_ok=True)
            file = os.path.join(folder, filename)
            save_image(image, file)
            logger.info(f'Image save success, file: {file}')
            return True
        except Exception as exc:
            logger.exception(exc)
            return False

    def commit(self, images, genre, save=False, info=''):
        if not images:
            return False
        save = bool(save)
        logger.info(f'Drop record commit, genre={genre}, amount={len(images)}, save={save}')
        image = pack(images)
        now = int(time.time() * 1000)
        filename = f'{now}_{info}.png' if info else f'{now}.png'
        if save:
            threading.Thread(target=self._save, args=(image, genre, filename)).start()
        return True

    def new(self, genre, method='do_not', info=''):
        return DropImage(
            recorder=self,
            genre=genre,
            save=method == 'save',
            info=info,
        )
