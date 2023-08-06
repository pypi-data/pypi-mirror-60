from cond import LinkedCond, require

x = LinkedCond(range = 10)
y = LinkedCond(range = 10)


print(require("xy", (x,y), "=", 24))

print(x, y)

print(require("x - y", (x, y), ">", 0))

print(x, y)
