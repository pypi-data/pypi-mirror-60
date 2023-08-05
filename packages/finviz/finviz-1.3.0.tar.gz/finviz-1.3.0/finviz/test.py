import finviz

'''
tickers = ['DOOR', 'NOAH', 'QD', 'APPF', 'CMCM', 'EGOV', 'BKNG', 'CTAS', 'MMS',
           'WNS', 'AEIS', 'SIMO', 'URBN', 'KRO', 'HA', 'GNTX', 'KLIC', 'CRVL',
           'FANH', 'BCPC', 'SBUX', 'ATHM', 'BCOR', 'BIDU', 'CANG', 'YNDX', 'ULTA',
           'INGN', 'MASI', 'BMS', 'PKG', 'MGPI', 'VNOM', 'XEC', 'BRC', 'BYD', 'ERI',
           'LVS', 'CALM', 'MKSI', 'GIL', 'NVDA', 'ERF', 'SHOO', 'EXP', 'LCII', 'HTHT',
           'HQY', 'VEEV', 'KSS', 'MOMO', 'TRCO', 'VMW']
'''


class CannotAttack(Exception):
    pass


class Champion(object):

    def __init__(self, health, damage=0):
        self.health = health
        self.damage = damage

    def attack(self):
        if not self.damage:
            raise CannotAttack

        print(f"{__class__.__name__} attacked the target for {self.damage} damage")


class Pet(Champion):

    def __init__(self, health):
        super().__init__(health)

        

pudge_champion = Champion(500, 66)
pudge_champion.attack()

pudge_pet = Pet(20)
pudge_pet.attack()