import os
import time
from config import Move

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BG_RED = "\033[41m"
    BG_BLUE = "\033[44m"

# Dicionário Híbrido: Ícone + Número para garantir leitura
DICE_ICONS = {
    1: '⚀', 2: '⚁', 3: '⚂', 4: '⚃', 5: '⚄', 6: '⚅'
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text):
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*50}")
    print(f"{text.center(50)}")
    print(f"{'='*50}{Colors.RESET}")

def print_dice(values):
    """
    Renderiza [Ícone Número] para evitar erros de fonte.
    Ex: [⚀ 1]
    """
    if not values:
        return f"{Colors.WHITE}[Vazio]{Colors.RESET}"
    dice_str = ""
    for v in values:
        icon = DICE_ICONS.get(v, '?')
        dice_str += f"{Colors.WHITE}[{icon} {v}]{Colors.RESET} " 
    return dice_str

def print_health_bar(name, current, max_hp, color_code=Colors.GREEN):
    percent = max(0, current / max_hp)
    bar_len = 20
    filled = int(bar_len * percent)
    bar = "█" * filled + "-" * (bar_len - filled)
    
    hp_color = color_code
    if percent < 0.5: hp_color = Colors.YELLOW
    if percent < 0.2: hp_color = Colors.RED
    
    print(f"{Colors.BOLD}{name:<12}{Colors.RESET} {hp_color}[{bar}]{Colors.RESET} {current:02d}/{max_hp:02d} HP")

def show_main_menu():
    clear_screen()
    print_header("STREET DICE FIGHTER")
    print(f"\n{Colors.BOLD}MENU PRINCIPAL{Colors.RESET}")
    print("1. PvE (Escolher Oponente)")
    print("2. MODO TORNEIO (Arcade)")
    print("3. Regras Detalhadas")
    print("4. Ver Personagens")
    print("5. Sair")
    return input("\n>> Escolha: ")

def show_rules():
    clear_screen()
    print_header("MANUAL DE REGRAS")
    
    print(f"{Colors.MAGENTA}DINÂMICA DE COMBATE:{Colors.RESET}")
    print("Cada rodada começa com um Jo-Ken-Po. Vencer garante vantagens cruciais!\n")
    
    # --- PEDRA ---
    print(f"{Colors.RED}1. PEDRA (Foco: Dano Explosivo){Colors.RESET}")
    print(f"   {Colors.BOLD}AÇÃO PADRÃO:{Colors.RESET} Tenta realizar um COMBO.")
    print("   - Você pode somar dados da Mesa + dados do seu Especial.")
    print(f"   {Colors.CYAN}★ SE VENCER (vs Tesoura):{Colors.RESET}")
    print("     - Você ganha a Iniciativa (ataca primeiro).")
    print("     - Após o Combo, você pode realizar um ESPECIAL extra.")
    print("       (Nota: O especial extra ainda consome 1 dado guardado).")
    
    # --- PAPEL ---
    print(f"\n{Colors.BLUE}2. PAPEL (Foco: Sobrevivência){Colors.RESET}")
    print(f"   {Colors.BOLD}AÇÃO PADRÃO:{Colors.RESET} Tenta realizar um ESPECIAL.")
    print("   - Consome 1 dado guardado na reserva.")
    print(f"   {Colors.CYAN}★ SE VENCER (vs Pedra):{Colors.RESET}")
    print("     - BLOQUEIO TOTAL: O combo do inimigo causa 0 de dano.")
    print("     - REGENERAÇÃO: Você recupera +2 de Vida.")
    
    # --- TESOURA ---
    print(f"\n{Colors.GREEN}3. TESOURA (Foco: Controle e Recurso){Colors.RESET}")
    print(f"   {Colors.BOLD}AÇÃO PADRÃO:{Colors.RESET} Realiza até 2 ações táticas abaixo:")
    print("     a) PEGAR: Tira 1 dado da mesa e guarda no seu Especial.")
    print("     b) REROLAR MESA: Escolhe 1 dado da mesa e rola de novo.")
    print("     c) REROLAR ESPECIAL: Escolhe 1 dado guardado e rola de novo.")
    print(f"   {Colors.CYAN}★ SE VENCER (vs Papel):{Colors.RESET}")
    print("     - CONTRA-ATAQUE: O inimigo recebe 2 de Dano direto.")
    print("     - CORTE: O Especial do inimigo é cancelado (falha).")
    
    # --- EMPATE ---
    print(f"\n{Colors.YELLOW}⚠ EM CASO DE EMPATE (Ex: Pedra vs Pedra){Colors.RESET}")
    print("   1. Ninguém recebe o bônus de vitória.")
    print("   2. A ordem de turno é definida pela VELOCIDADE (Speed) dos lutadores.")
    print("   3. O personagem mais rápido age primeiro. O outro age em seguida")
    print("      (se ainda estiver vivo).")
    
    input("\n[Pressione Enter para voltar]")

def show_characters_info(char_list):
    clear_screen()
    print_header("LUTADORES & ESPECIAIS")
    for c in char_list:
        char = c()
        print(f"{Colors.BOLD}{char.name}{Colors.RESET} (HP: {char.max_hp} | Spd: {char.speed})")
        print(f"{Colors.WHITE}Combos:{Colors.RESET} {char.combo_desc}")
        print(f"{Colors.YELLOW}Especial:{Colors.RESET} {char.special_desc}")
        print("-" * 50)
    input("\n[Pressione Enter para voltar]")
