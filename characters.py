import random
from models import Character

# --- RYU ---
class Ryu(Character):
    def __init__(self):
        super().__init__("Ryu", hp=12, speed=3.0, max_special=4)
        # Descrição visual para combos
        self.combo_desc = "[⚃ 4]->1 dano | [⚄ 5][⚄ 5]->3 dano| [⚀ 1][⚅ 6]->4 dano"
        # Descrição detalhada do Especial (Fonte: PDF Card Ryu)
        self.special_desc = "HADOUKEN: Gasta 1 dado guardado e rola. Se > 3 causa 1 Dano. Se HP for 4 ou menos, causa +2 Dano."
        # Mantendo compatibilidade com engine antiga
        self.description = self.combo_desc 

    def get_best_combo(self, dice_values):
        counts = {x: dice_values.count(x) for x in range(1, 7)}
        if counts.get(1, 0) >= 1 and counts.get(6, 0) >= 1: return 4, [1, 6]
        if counts.get(5, 0) >= 2: return 3, [5, 5]
        if counts.get(4, 0) >= 1: return 1, [4]
        return 0, []

    def perform_special(self, opponent=None):
        if not self.special_pool: return 0, "Sem energia."
        self.special_pool.pop(0) 
        roll = random.randint(1, 6)
        dmg = 1 if roll > 3 else 0
        msg = f"Hadouken (Rolou {roll})"
        
        # Regra de Crítico com HP baixo
        if self.current_hp <= 4:
            dmg += 2
            msg += " [CRITICAL ARTS!]"
        elif dmg > 0:
            msg += " ACERTOU!"
        else:
            msg += " FALHOU!"
        return dmg, msg

# --- KEN ---
class Ken(Character):
    def __init__(self):
        super().__init__("Ken", hp=11, speed=4.0, max_special=4)
        self.combo_desc = "[⚀ 1]->1 dano | [⚀ 1][⚁ 2]->2 dano | [⚀ 1][⚁ 2][⚁ 2]->3 dano"
        # Fonte: PDF Card Ken
        self.special_desc = "SHORYUKEN: Gasta 1 dado e rola. Se > 3 causa 1 Dano. Pode gastar +1 dado extra para adicionar +1 Dano."
        self.description = self.combo_desc

    def get_best_combo(self, dice_values):
        counts = {x: dice_values.count(x) for x in range(1, 7)}
        if counts.get(1, 0) >= 1 and counts.get(2, 0) >= 2: return 3, [1, 2, 2]
        if counts.get(1, 0) >= 1 and counts.get(2, 0) >= 1: return 2, [1, 2]
        if counts.get(1, 0) >= 1: return 1, [1]
        return 0, []

    def perform_special(self, opponent=None):
        if not self.special_pool: return 0, "Sem energia."
        self.special_pool.pop(0)
        roll = random.randint(1, 6)
        dmg = 1 if roll > 3 else 0
        msg = f"Shoryuken (Rolou {roll})"
        
        # Gasta dado extra automaticamente se tiver
        if dmg > 0 and len(self.special_pool) > 0:
            self.special_pool.pop(0)
            dmg += 1
            msg += " + EX BOOST (+1 Dano)!"
        return dmg, msg

# --- CHUN-LI ---
class ChunLi(Character):
    def __init__(self):
        super().__init__("Chun-Li", hp=10, speed=5.0, max_special=5)
        self.combo_desc = "[⚀ 1]->1 dano | [⚁ 2][⚂ 3]->3 dano | [⚃ 4][⚃ 4][⚃ 4]->5 dano"
        # Fonte: PDF Card Chun-Li
        self.special_desc = "HYAKURETSUKYAKU: Gasta 1 dado. Rola o dado gasto 2 VEZES. Para cada resultado < 4, causa 1 de dano."
        self.description = self.combo_desc

    def get_best_combo(self, dice_values):
        counts = {x: dice_values.count(x) for x in range(1, 7)}
        if counts.get(4, 0) >= 3: return 5, [4, 4, 4]
        if counts.get(2, 0) >= 1 and counts.get(3, 0) >= 1: return 3, [2, 3]
        if counts.get(1, 0) >= 1: return 1, [1]
        return 0, []
        
    def perform_special(self, opponent=None):
        if not self.special_pool: return 0, "Sem energia."
        self.special_pool.pop(0)
        
        # Rola 2 vezes
        rolls = [random.randint(1,6), random.randint(1,6)]
        dmg = sum(1 for r in rolls if r < 4)
        return dmg, f"Spinning Bird Kick {rolls} -> {dmg} Hits!"

# --- GUILE ---
class Guile(Character):
    def __init__(self):
        super().__init__("Guile", hp=13, speed=2.0, max_special=6)
        self.combo_desc = "[⚀ 1]-> 1 dano | [⚁ 2][⚁ 2]->2 dano | [⚀ 1][⚀ 1][⚂ 3]->3 dano"
        # Fonte: PDF Card Guile
        self.special_desc = "SONIC BOOM: Descarta dados que somem 6 (ex: 3+3 ou 6). Causa 1 Dano e DESTRÓI 1 dado do especial inimigo."
        self.description = self.combo_desc

    def get_best_combo(self, dice_values):
        counts = {x: dice_values.count(x) for x in range(1, 7)}
        if counts.get(1, 0) >= 2 and counts.get(3, 0) >= 1: return 3, [1, 1, 3]
        if counts.get(2, 0) >= 2: return 2, [2, 2]
        if counts.get(1, 0) >= 1: return 1, [1]
        return 0, []

    def perform_special(self, opponent=None):
        found_combo = []
        # Tenta achar um 6 direto
        if 6 in self.special_pool: found_combo = [6]
        else:
            # Tenta achar soma
            for d in self.special_pool:
                target = 6 - d
                if target in self.special_pool and (target != d or self.special_pool.count(d) >= 2):
                    found_combo = [d, target]
                    break
                    
        if not found_combo: return 0, "Falhou (Soma != 6)"
        
        for val in found_combo: self.special_pool.remove(val)
        dmg = 1
        msg = "Sonic Boom!"
        
        # Efeito de destruir recurso inimigo
        if opponent and opponent.special_pool:
            lost = opponent.special_pool.pop()
            msg += f" (Quebrou dado [⚀ {lost}] do inimigo)"
        return dmg, msg

# --- ZANGIEF ---
class Zangief(Character):
    def __init__(self):
        super().__init__("Zangief", hp=15, speed=1.0, max_special=3)
        self.combo_desc = "[⚀ 1][⚀ 1]->2 dano | [⚁ 2][⚁ 2]->3 dano | [⚂ 3][⚂ 3]->4 dano"
        # Fonte: PDF Card Zangief
        self.special_desc = "SCREW PILE-DRIVER: Gasta 1 dado e rola. Se cair 3 ou 6, causa 3 de Dano. Caso contrário, erra."
        self.description = self.combo_desc

    def get_best_combo(self, dice_values):
        counts = {x: dice_values.count(x) for x in range(1, 7)}
        if counts.get(3, 0) >= 2: return 4, [3, 3]
        if counts.get(2, 0) >= 2: return 3, [2, 2]
        if counts.get(1, 0) >= 2: return 2, [1, 1]
        return 0, []

    def perform_special(self, opponent=None):
        if not self.special_pool: return 0, "Sem energia."
        self.special_pool.pop(0)
        roll = random.randint(1, 6)
        dmg = 3 if roll == 3 or roll == 6 else 0
        msg = f"Pile Driver (Rolou {roll})"
        return dmg, msg + (" CRUSH!" if dmg else " ERROU!")

#Notas da atualização 3.0 com adição dos novos personagens Blanka, Cammy e Vega

# --- BLANKA ---
class Blanka(Character):
    def __init__(self):
        # Baseado na sua sugestão: HP alto, velocidade moderada
        super().__init__("Blanka", hp=14, speed=2.5, max_special=3)
        self.combo_desc = "[⚀ 1][⚂ 3]->2 dano | [⚂ 3][⚃ 4]->3 dano | [⚅ 6][⚅ 6]->4 dano"
        self.special_desc = "ELECTRIC THUNDER: Gasta 2 dados. Rola cada um 2 vezes. Para cada resultado <= 2, o oponente perde 2 dados do Especial."
        self.description = self.combo_desc

    def get_best_combo(self, dice_values):
        counts = {x: dice_values.count(x) for x in range(1, 7)}
        if counts.get(6, 0) >= 2: return 4, [6, 6]
        if counts.get(3, 0) >= 1 and counts.get(4, 0) >= 1: return 3, [3, 4]
        if counts.get(1, 0) >= 1 and counts.get(3, 0) >= 1: return 2, [1, 3]
        return 0, []

    def perform_special(self, opponent=None):
        if len(self.special_pool) < 2: return 0, "Sem energia (Precisa de 2 dados)"
        self.special_pool.pop(0)
        self.special_pool.pop(0)
        
        success_count = 0
        rolls = []
        for _ in range(4): # 2 dados rolados 2 vezes cada
            r = random.randint(1, 6)
            rolls.append(r)
            if r <= 2: success_count += 1
            
        lost_dice = 0
        if opponent and opponent.special_pool:
            for _ in range(success_count * 2):
                if opponent.special_pool:
                    opponent.special_pool.pop()
                    lost_dice += 1
                    
        return 0, f"Electric Thunder {rolls} -> Inimigo perdeu {lost_dice} dados!"

# --- CAMMY ---
class Cammy(Character):
    def __init__(self):
        # Glass Cannon: Rápida, mas com vida baixa
        super().__init__("Cammy", hp=11, speed=4.5, max_special=5)
        self.combo_desc = "[⚀ 1]->1 dano | [⚀ 1][⚅ 6]->2 dano | [⚀ 1][⚄ 5]->3 dano"
        self.special_desc = "CANNON STRIKE: Gasta uma sequência de 3 dados (ex: 1-2-3). Causa 6 de Dano Massivo."
        self.description = self.combo_desc

    def get_best_combo(self, dice_values):
        counts = {x: dice_values.count(x) for x in range(1, 7)}
        if counts.get(1, 0) >= 1 and counts.get(5, 0) >= 1: return 3, [1, 5]
        if counts.get(1, 0) >= 1 and counts.get(6, 0) >= 1: return 2, [1, 6]
        if counts.get(1, 0) >= 1: return 1, [1]
        return 0, []

    def perform_special(self, opponent=None):
        # Procura sequência no especial
        s = sorted(list(set(self.special_pool)))
        found_seq = []
        for i in range(len(s) - 2):
            if s[i+1] == s[i]+1 and s[i+2] == s[i]+2:
                found_seq = [s[i], s[i+1], s[i+2]]
                break
        
        if not found_seq: return 0, "Falhou (Sem sequência de 3 no Especial)"
        
        for val in found_seq: self.special_pool.remove(val)
        return 6, f"Cannon Strike! Sequência {found_seq} aplicada!"

# --- VEGA ---
class Vega(Character):
    def __init__(self):
        super().__init__("Vega", hp=11, speed=3.5, max_special=4)
        self.combo_desc = "[⚁ 2][⚁ 2]->2 dano | [⚂ 3][⚂ 3]->3 dano | [⚀ 1][⚃ 4][⚄ 5]->5 dano"
        self.special_desc = "FLYING BARCELONA: Causa 1 de Dano para cada dado [⚀ 1] no seu Especial. Descarta todos depois."
        self.description = self.combo_desc

    def get_best_combo(self, dice_values):
        counts = {x: dice_values.count(x) for x in range(1, 7)}
        if counts.get(1,0)>=1 and counts.get(4,0)>=1 and counts.get(5,0)>=1: return 5, [1, 4, 5]
        if counts.get(3, 0) >= 2: return 3, [3, 3]
        if counts.get(2, 0) >= 2: return 2, [2, 2]
        return 0, []

    def perform_special(self, opponent=None):
        if not self.special_pool: return 0, "Especial vazio."
        
        dmg = self.special_pool.count(1)
        if dmg > 0:
            #REGRA ATUALIZADA: Remove apenas os dados de valor 1
            self.special_pool = [d for d in self.special_pool if d != 1]
            return dmg, f"Flying Barcelona Attack! -> {dmg} Dano (Dados [1] consumidos)"
        else:
            return 0, "Falhou (Não há dados de valor [1] no Especial)"

        

