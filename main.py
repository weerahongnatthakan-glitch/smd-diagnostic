# Smart Maintenance Diagnostic System
# version 0.1

print("Smart Maintenance Diagnostic System")

problem = input("Enter problem: ")

if problem == "pump not working":
    print("Check power supply")
    print("Check overload relay")

elif problem == "motor hot":
    print("Check bearing")
    print("Check voltage")

else:
    print("Problem not in database")
