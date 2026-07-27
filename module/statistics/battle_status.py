from module.base.decorator import cached_property
from module.combat.assets import BATTLE_STATUS_S
from module.ocr.ocr import Ocr
from module.statistics.assets import ENEMY_NAME


class BattleStatusStatistics:
    def appear_on(self, image):
        return BATTLE_STATUS_S.appear_on(image)

    @cached_property
    def ocr_object(self):
        return Ocr(ENEMY_NAME, lang='cnocr', threshold=128, name='ENEMY_NAME')

    def stats_battle_status(self, image):
        """
        Args:
            image (np.ndarray):

        Returns:
            str: Enemy name, such as 'Medium Main Fleet'.
        """
        result = self.ocr_object.ocr(image)
        # Delete wrong OCR result
        for letter in '-―~(':
            result = result.replace(letter, '')

        return result
