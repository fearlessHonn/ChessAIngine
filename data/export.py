import math


def export_pgn(board_obj):
    output = '[Event "?"]\n' + '[Site "?"]\n' + '[Date "????.??.??"]\n' + '[Round "?"]\n' + '[White "?"]\n' + '[Black "?"]\n' + '[Result "*"]\n'

    for i in range(math.ceil(len(board_obj.moves) / 2)):
        try:
            output += f"{i + 1}. {board_obj.moves[2 * i]} {board_obj.moves[2 * i + 1]} \n"
        except IndexError:
            output += f"{i + 1}. {board_obj.moves[2 * i]}"

    return output
