with open("filename.txt", "r") as f:
    filenames = f.readlines()

for file in filenames:
    with open(f"./map/{file.strip()}_cleaned.png", "rb") as p:
        open(f"./map/{file.strip().split("_")[0]}.png", "wb").write(p.read())