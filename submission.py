def one():
    a = float(input("First number: "))
    b = float(input("Second number: "))
    print(f"Sum = {a+b}")
    print(f"Product = {a*b}")
    print(f"Ratio = {a/b}")
    print(f"Modulus = {a%b}")
    print(f"Exponent = {a**b}")


def two():
    temp = float(input("Temperature in Celsius: "))
    print(f"{temp*(9/5)+32}")

pi = 3.141
def three():
    rad = float(input("Radius: "))
    print(f"Area = {pi*rad**2}")
    print(f"Circumference = {2*pi*rad}")

def four():
    rad = float(input("Radius: "))
    print(f"Area = {4*pi*rad**2}")

def five():
    rad = float(input("Radius: "))
    height = float(input("Height: "))
    print(f"Area = {2*pi*rad*height+2*pi*r**2}")


def six():
    f_name = input("First Name: ")
    l_name = input("Last Name: ")
    print(f_name[0] + l_name[0])

def seven():
    age = int(input("Age: "))
    print(age > 18)
