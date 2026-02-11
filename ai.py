import random
from config import Move
from models import Character

class AIPlayer:
    def __init__(self, character: Character):
        self.character = character
        self.name = f"CPU {character.name}"

    def choose_move(self, controller_dice_pool, opponent):
        """
        Decide Pedra (Combo), Papel (Especial) ou Tesoura (Tática)
        Baseado nos dados disponíveis e na ameaça do oponente.
        """
        dice_values = controller_dice_pool.get_values()
        
        # 1. Analisa meu potencial de dano (PEDRA)
        dmg_potential, _ = self.character.get_best_combo(dice_values)
        
        # 2. Analisa meus recursos para Especial (PAPEL)
        # Nota: Guile precisa de soma 6, Zangief só precisa de 1 dado.
        # Lógica simplificada: se tem dado, pode usar.
        has_special_ammo = len(self.character.special_pool) > 0
        
        # 3. Analisa ameaça do oponente (Devo defender com PAPEL?)
        opp_dmg, _ = opponent.get_best_combo(dice_values)
        opponent_is_dangerous = opp_dmg >= 3
        
        # Pesos de decisão (0 a 100)
        weights = {Move.PEDRA: 10, Move.PAPEL: 0, Move.TESOURA: 20}

        # --- AVALIAÇÃO PEDRA ---
        if dmg_potential >= 3: weights[Move.PEDRA] += 100 # Combo forte
        elif dmg_potential > 0: weights[Move.PEDRA] += 40
        else: weights[Move.PEDRA] = 0 # Sem combo, impossível jogar pedra

        # --- AVALIAÇÃO PAPEL ---
        if has_special_ammo:
            weights[Move.PAPEL] += 20 # Base
            if opponent_is_dangerous:
                weights[Move.PAPEL] += 80 # Defesa prioritária
        else:
            weights[Move.PAPEL] = 0 # Sem munição

        # --- AVALIAÇÃO TESOURA ---
        # Tesoura serve para pegar dados ou counterar Papel
        if not has_special_ammo or len(self.character.special_pool) < 2:
            weights[Move.TESOURA] += 40 # Precisa farmar
        
        # Se a mesa está vazia ou ruim, Tesoura é a salvação
        if not dice_values or dmg_potential == 0:
            weights[Move.TESOURA] += 150

        # Escolha ponderada
        valid_opts = [m for m in weights if weights[m] > 0]
        if not valid_opts: return Move.TESOURA

        scores = [weights[m] for m in valid_opts]
        return random.choices(valid_opts, weights=scores, k=1)[0]

    def perform_scissors_action(self, controller_pool):
        """IA executa a ação de Tesoura automaticamente (pegar dados)."""
        dice_values = controller_pool.get_values()
        actions_taken = 0
        logs = []
        
        # Estratégia simples: Pega os maiores dados disponíveis
        # Ordem de preferência: 6, 5, 4
        targets = [6, 5, 4, 3, 2, 1]
        
        while actions_taken < 2 and len(self.character.special_pool) < self.character.max_special_dice:
            found = False
            for t in targets:
                if t in dice_values:
                    controller_pool.remove_values([t])
                    self.character.special_pool.append(t)
                    dice_values.remove(t) # Atualiza lista local
                    logs.append(f"Pegou [{t}]")
                    actions_taken += 1
                    found = True
                    break
            if not found:
                break # Sem dados para pegar
                
        if not logs: return "Tesoura (Sem ação útil)"
        return "Tesoura: " + ", ".join(logs)
