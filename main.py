from game import Game
if __name__ == "__main__":
    temp = ".W7.b2.b12.w2.w5.w.w.w.3w.3w.2w"
    temp2 = "4.b2.4b2.2b2.b2.w9.wbw.w.B3.3w.w4.w"

    board_str = "Wb.3b2.2b.4b7.2b.wb4.w2.13w.2w"
    game = Game(board_str, "jerem", "Player2")
    game.run()
