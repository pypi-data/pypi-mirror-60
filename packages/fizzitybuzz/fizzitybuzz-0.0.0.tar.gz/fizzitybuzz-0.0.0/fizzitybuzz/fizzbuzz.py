class Fizzbuzz:
    @staticmethod
    def fizzbuzz(start=1, stop=100):
       to_return = []
       for i in range(start, stop):
           if i % 15 == 0:
               to_return.append("Fizzbuzz")
           elif i % 5 == 0:
               to_return.append("Buzz")
           elif i % 3 == 0:
               to_return.append("Fizz")
           else:
               to_return.append(str(i))
       return ", ".join(to_return)
