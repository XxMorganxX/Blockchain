nonce = 0

for i in range(20):
    print(f"{nonce+(i*50)}, {(nonce+((i+1)*50))}")
nonce = (nonce+((20)*50))
for i in range(20):
    print(f"{nonce+(i*50)}, {(nonce+((i+1)*50))}")

