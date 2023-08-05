#!/usr/bin/python

from .utils.methods import *
from .models.models import *


def run():

    # Argument Handling

    hard_mode = False
    s_rank = False
    args_list = []
    accepted_arguments = ["--hard", "--s-hard", "--show-inputs", "--help", "--version"]

    for eachArg in sys.argv[1:]:
        if eachArg in accepted_arguments:
            args_list.append(eachArg)
        else:
            print(eachArg + " is not an accepted argument")
            print_help()

    print_functions(args_list)

    if args_list.__contains__("--s-hard"):
        hard_mode = True
        s_rank = True
        print("\n*** SUPER-HARD-MODE ACTIVE ***")
    elif args_list.__contains__("--hard"):
        hard_mode = True
        print("\n** HARD-MODE ACTIVE **")

    # help trackers

    input_helper = False
    move_helper = False

    # initialize game

    game = Grid()

    # game logic

    def turn():

        nonlocal input_helper
        nonlocal move_helper

        try:
            print(game)
            your_move = input("your move: ").lower()

            if is_input_valid(your_move):

                move_key = input_to_move_key(your_move)

                if is_move_valid(game, move_key):

                    setattr(game, move_key, Move( move_key, "X"))

                    if check_for_win_wrapper(game, "congratulations! %s's win"):
                        run()

                    if hard_mode:
                        cpu_move_key = computer_move_hard(game)
                    else:
                        cpu_move_key = computer_move(game)

                    setattr(game, cpu_move_key, Move(cpu_move_key, "O"))
                    print("computer makes a move: " + moves_map.get(cpu_move_key)[0])

                    if check_for_win_wrapper(game, "you lose! %s's win"):
                        run()

                    turn()
                else:
                    print("\nmove is NOT valid - move %s is already taken" % your_move)

                    if move_helper:
                        show_available_moves(game)
                    else:
                        move_helper = True

                    turn()
            else:
                print("invalid input")

                if input_helper:
                    show_available_inputs()
                else:
                    input_helper = True

                turn()
        except KeyboardInterrupt:
            print(" - program exited")
            print("bye bye!")
            sys.exit()

    # first move by cpu on super-hard-mode

    if s_rank:
        print("computer makes first move ...")
        cpu_move_key = computer_move_hard(game)
        setattr(game, cpu_move_key, Move(cpu_move_key, "O"))

    turn()


if __name__ == "__main__":
    run()
