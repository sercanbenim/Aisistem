import listen
import think
import speak


class Brain:
    """Simple orchestrator combining modules like a brain."""

    def run(self):
        while True:
            message = listen.get_input()
            if message.lower() == "quit":
                break
            response = think.generate_response(message)
            speak.say(response)


def run():
    Brain().run()


if __name__ == "__main__":
    run()

