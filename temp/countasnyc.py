import asyncio

# ASYNCY
# async def count():
#     print("One")
#     await asyncio.sleep(1)
#     print("Two")

# async def main():
#     await asyncio.gather(count(), count(), count())

# if __name__ == "__main__":
#     import time
#     s = time.perf_counter()
#     asyncio.run(main())
#     elapsed = time.perf_counter() - s
#     print(f"{__file__} executed in {elapsed:0.2f} seconds.")

# SYNC
import time
def count():
    print("One")
    time.sleep(1)
    print("Two")

def main():
    for _ in range(3):
        count()

if __name__ == "__main__":
    s = time.perf_counter()
    main()
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")