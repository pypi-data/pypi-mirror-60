import readline


def show():
    for i in range(readline.get_current_history_length()):
        print(str(i) + "\t" + readline.get_history_item(i + 1))


if __name__ == '__main__':
    show()
