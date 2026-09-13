class PlayerState:
    def __init__(self):
        self.is_dense = False
        self.has_bone_shrapnel = False
        self.has_skeletal_archers = False
        self.has_plague_wizard = False
        self.purchased_upgrade_ids = set()
