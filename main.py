import utils
import engine
from characters import Ryu, Ken, ChunLi, Guile, Zangief

def main():
    while True:
        option = utils.show_main_menu()
        
        if option == '1':
            engine.run_pve_custom()
            
        elif option == '2':
            engine.run_tournament()
            
        elif option == '3':
            utils.show_rules()
            
        elif option == '4':
            roster = [Ryu, Ken, ChunLi, Guile, Zangief]
            utils.show_characters_info(roster)
            
        elif option == '5':
            print("Saindo...")
            break
        else:
            print("Inválido!")

if __name__ == "__main__":
    main()
