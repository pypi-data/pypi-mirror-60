import asyncio

from actions_in_fly.fly import fly


def main():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(fly())
    finally:
        loop.close()


if __name__ == '__main__':
    main()
