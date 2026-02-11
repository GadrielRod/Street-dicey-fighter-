import time
import random
from utils import Colors, clear_screen, print_header, print_dice, print_health_bar
from config import Move
from models import DicePool
from characters import Ryu, Ken, ChunLi, Guile, Zangief
from ai import AIPlayer

def get_player_move():
    print(f"\n{Colors.YELLOW}Sua Jogada:{Colors.RESET}")
    print(f"1. {Colors.RED}👊 PEDRA{Colors.RESET} ")
    print(f"2. {Colors.BLUE}✋️ PAPEL{Colors.RESET} ")
    print(f"3. {Colors.GREEN}✌️ TESOURA{Colors.RESET} ")
    while True:
        choice = input(">> ")
        if choice == '1': return Move.PEDRA
        if choice == '2': return Move.PAPEL
        if choice == '3': return Move.TESOURA
        if choice == '9': return 'KILL' # Cheat

def perform_player_scissors(player, dice_pool):
    print(f"\n{Colors.CYAN}--- TÁTICA DA TESOURA (Máx 2 ações) ---{Colors.RESET}")
    actions_taken = 0
    while actions_taken < 2:
        print(f"\n{Colors.BOLD}Ações: {2 - actions_taken} | [1] Pegar [2] Rerolar Mesa [3] Rerolar Especial [4] Sair{Colors.RESET}")
        print(f"Mesa: {print_dice(dice_pool.get_values())}")
        
        opt = input(">> ")
        if opt == '4': break
        
        # 1. PEGAR DADO
        elif opt == '1':
            vals = dice_pool.get_values()
            if not vals: print("Mesa vazia!"); continue
            try:
                val = int(input("Pegar qual valor? "))
                if val in vals:
                    if len(player.special_pool) < player.max_special_dice:
                        dice_pool.remove_values([val])
                        player.special_pool.append(val)
                        print(f"{Colors.GREEN}Guardou [{val}]!{Colors.RESET}")
                        actions_taken += 1
                    else: print("Especial cheio!")
                else: print("Valor não existe.")
            except: pass

        # 2. REROLAR MESA
        elif opt == '2':
            vals = dice_pool.get_values()
            if not vals: print("Mesa vazia!"); continue
            try:
                val = int(input("Rerolar qual valor? "))
                if val in vals:
                    dice_pool.remove_values([val])
                    dice_pool.roll_new(1)
                    print(f"{Colors.YELLOW}Rerolado!{Colors.RESET}")
                    actions_taken += 1
            except: pass

        # 3. REROLAR ESPECIAL
        elif opt == '3':
            if not player.special_pool: print("Especial vazio!"); continue
            try:
                val = int(input(f"Rerolar qual ({player.special_pool})? "))
                if val in player.special_pool:
                    player.special_pool.remove(val)
                    player.special_pool.append(random.randint(1,6))
                    print(f"{Colors.YELLOW}Especial transformado!{Colors.RESET}")
                    actions_taken += 1
            except: pass

def consume_dice_smart(character, dice_pool, values_needed):
    """
    Remove os dados usados no Combo.
    Prioridade: Remove da MESA primeiro. Se não tiver, remove do ESPECIAL.
    """
    table_vals = dice_pool.get_values()
    
    for v in values_needed:
        if v in table_vals:
            # Remove da mesa
            dice_pool.remove_values([v])
            table_vals.remove(v) # Atualiza lista local
        elif v in character.special_pool:
            # Remove do especial
            character.special_pool.remove(v)
        else:
            # Erro de consistência (não deveria acontecer se get_best_combo funcionou bem)
            pass

def resolve_round(p1_ctrl, m1, p2_ctrl, m2, dice_pool):
    p1_char = p1_ctrl.character if isinstance(p1_ctrl, AIPlayer) else p1_ctrl
    p2_char = p2_ctrl.character if isinstance(p2_ctrl, AIPlayer) else p2_ctrl

    clear_screen()
    print_header("JO - KEN - PO!")
    print(f"{p1_char.name}: {m1.name.split()[0]}")
    print(f"{p2_char.name}: {m2.name.split()[0]}")
    print("-" * 40)
    time.sleep(1)

    # --- 1. DETERMINAR VENCEDOR DO JO-KEN-PO ---
    winner = None # None = Empate
    if m1 != m2:
        if (m1 == Move.PEDRA and m2 == Move.TESOURA) or \
           (m1 == Move.TESOURA and m2 == Move.PAPEL) or \
           (m1 == Move.PAPEL and m2 == Move.PEDRA):
            winner = p1_char
            print(f"{Colors.GREEN}{p1_char.name} VENCEU O DUELO!{Colors.RESET}")
        else:
            winner = p2_char
            print(f"{Colors.GREEN}{p2_char.name} VENCEU O DUELO!{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}EMPATE! (Velocidade decide ordem){Colors.RESET}")

    # --- 2. DEFINIR ORDEM DE AÇÃO ---
    # Se houve empate, velocidade decide. Se houve vencedor, ele age primeiro.
    if winner:
        p1_goes_first = (winner == p1_char)
    else:
        p1_goes_first = p1_char.speed >= p2_char.speed

    if p1_goes_first:
        queue = [(p1_ctrl, m1, p2_ctrl, m2), (p2_ctrl, m2, p1_ctrl, m1)]
    else:
        queue = [(p2_ctrl, m2, p1_ctrl, m1), (p1_ctrl, m1, p2_ctrl, m2)]

    # --- 3. EXECUTAR AÇÕES ---
    for actor_ctrl, action, target_ctrl, reaction in queue:
        actor = actor_ctrl.character if isinstance(actor_ctrl, AIPlayer) else actor_ctrl
        target = target_ctrl.character if isinstance(target_ctrl, AIPlayer) else target_ctrl
        
        # Se morreu antes de agir, pula
        if actor.current_hp <= 0: break

        print(f"\n>>> {Colors.BOLD}{actor.name}{Colors.RESET} realiza ação...")
        time.sleep(1)
        
        did_win_jokenpo = (actor == winner)
        opponent_won = (target == winner)

        # ================= PEDRA (COMBO) =================
        if action == Move.PEDRA:
            # Verifica Bloqueio (Se o oponente venceu com Papel)
            blocked = False
            if reaction == Move.PAPEL and opponent_won:
                print(f"{Colors.BLUE}BLOQUEADO! Papel venceu e anulou o dano.{Colors.RESET}")
                blocked = True
            
            # Executa Combo (se não bloqueado e possível)
            if not blocked:
                # Regra Nova: Pode usar dados da Mesa + Especial
                available_dice = dice_pool.get_values() + actor.special_pool
                dmg, used_dice = actor.get_best_combo(available_dice)
                
                if dmg > 0:
                    consume_dice_smart(actor, dice_pool, used_dice)
                    target.take_damage(dmg)
                    print(f"{Colors.RED}COMBO! Usou {used_dice} -> {dmg} Dano!{Colors.RESET}")
                else:
                    print("Falha! Sem dados para combo.")

            # BÔNUS DE VITÓRIA: Executar Especial
            if did_win_jokenpo:
                print(f"{Colors.CYAN}BÔNUS DE VITÓRIA (PEDRA): Tentando Especial Extra...{Colors.RESET}")
                dmg_spec, msg_spec = actor.perform_special(target)
                if dmg_spec > 0 or "Hits" in msg_spec or "Sonic" in msg_spec: # Verifica se algo aconteceu
                    target.take_damage(dmg_spec)
                    print(f"{Colors.MAGENTA}{msg_spec} -> {dmg_spec} Dano!{Colors.RESET}")
                else:
                    print("Sem dados para o especial extra.")

        # ================= PAPEL (ESPECIAL) =================
        elif action == Move.PAPEL:
            # Verifica Corte (Se o oponente venceu com Tesoura)
            silenced = False
            if reaction == Move.TESOURA and opponent_won:
                print(f"{Colors.RED}CORTADO! Tesoura venceu: Especial cancelado e toma 2 Dano.{Colors.RESET}")
                actor.take_damage(2)
                silenced = True
            
            if not silenced:
                # Executa Especial Obrigatório
                dmg, msg = actor.perform_special(target)
                target.take_damage(dmg)
                print(f"{Colors.MAGENTA}ESPECIAL: {msg} -> {dmg} Dano!{Colors.RESET}")
                
                # BÔNUS DE VITÓRIA: Cura
                if did_win_jokenpo:
                    heal_amount = 2
                    actor.heal(heal_amount)
                    print(f"{Colors.GREEN}BÔNUS DE VITÓRIA (PAPEL): Recuperou {heal_amount} HP!{Colors.RESET}")

        # ================= TESOURA (TÁTICA) =================
        elif action == Move.TESOURA:
            # Executa Tática (Sempre acontece, independente de ganhar ou perder)
            if isinstance(actor_ctrl, AIPlayer):
                print(actor_ctrl.perform_scissors_action(dice_pool))
            else:
                perform_player_scissors(actor, dice_pool)
            
            # BÔNUS DE VITÓRIA: Dano Extra e Silencio (Já tratado no bloco do PAPEL acima)
            if did_win_jokenpo:
                print(f"{Colors.GREEN}BÔNUS DE VITÓRIA (TESOURA): Oponente recebe 2 de dano!{Colors.RESET}")
                # Nota: O bloqueio do especial do inimigo é passivo, checado quando o inimigo tenta agir

def battle_loop(player_char, cpu_controller):
    dice_pool = DicePool()
    dice_pool.roll_new(6)
    round_num = 1
    cpu_char = cpu_controller.character
    
    while player_char.current_hp > 0 and cpu_char.current_hp > 0:
        clear_screen()
        print_header(f"ROUND {round_num}")
        
        print_health_bar(player_char.name, player_char.current_hp, player_char.max_hp, Colors.GREEN)
        print(f"Especial: {print_dice(player_char.special_pool)}")
        print("-" * 40)
        print_health_bar(cpu_char.name, cpu_char.current_hp, cpu_char.max_hp, Colors.RED)
        print(f"Especial: {print_dice(cpu_char.special_pool)}")
        
        print(f"\n MESA: {print_dice(dice_pool.get_values())} {Colors.RESET}")
        
        m1 = get_player_move()
        if m1 == 'KILL': cpu_char.current_hp = 0; break

        m2 = cpu_controller.choose_move(dice_pool, player_char)
        resolve_round(player_char, m1, cpu_controller, m2, dice_pool)
        
        input("\n[Enter...]")
        
        needed = 6 - len(dice_pool.dice)
        if needed > 0: dice_pool.roll_new(needed)
        round_num += 1
    
    return player_char.current_hp > 0

# --- FUNÇÕES DE MENU (Mantidas iguais, só para garantir o import correto) ---
def select_character(prompt="Escolha"):
    chars = [Ryu, Ken, ChunLi, Guile, Zangief]
    print_header(prompt)
    for i, c in enumerate(chars, 1):
        temp = c()
        print(f"{i}. {temp.name}")
    try:
        idx = int(input("\nEscolha: ")) - 1
        return chars[idx]() if 0 <= idx < len(chars) else Ryu()
    except: return Ryu()

def run_pve_custom():
    p1 = select_character("JOGADOR 1")
    p2 = select_character("OPONENTE")
    cpu = AIPlayer(p2)
    if battle_loop(p1, cpu): print(f"\n{Colors.GREEN}VITÓRIA!{Colors.RESET}")
    else: print(f"\n{Colors.RED}GAME OVER...{Colors.RESET}")
    input()

def run_tournament():
    p1 = select_character("CAMPEÃO")
    roster = [Ryu, Ken, ChunLi, Guile, Zangief]
    enemies = [cls() for cls in roster if cls().__class__.__name__ != p1.__class__.__name__]
    random.shuffle(enemies)
    for i, enemy in enumerate(enemies, 1):
        clear_screen()
        print_header(f"LUTA {i}/{len(enemies)}: {enemy.name}")
        time.sleep(2)
        if not battle_loop(p1, AIPlayer(enemy)):
            print(f"{Colors.RED}PERDEU!{Colors.RESET}"); break
        p1.heal(5); p1.special_pool = []
        print(f"{Colors.GREEN}VENCEU! Vida recuperada.{Colors.RESET}")
        input("[Enter]")
    if p1.current_hp > 0: print(f"{Colors.YELLOW}CAMPEÃO!{Colors.RESET}")
    input()
