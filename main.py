from library import *


def main():
    counter = 0
    with Live(
        console=Console(), refresh_per_second=2
    ) as live:
        while True:

            console.print(Padding(menuInterface(), (0, 10)))
            choice = console.input("[bold]Input: [/bold]")
            match choice:
                case "1":
                    print("jkdsj")
                    console.print(loginInterface())
                    break
                case "2":

                    break
                case _:
                    console.print("Invalid choice...")
                    tm.sleep(0.5)


main()