from numpy import exp, log10

# linear equation
class linear:

    func = 'x * k + b'

    def get_funcstr(self):
        return self.func

    def get_function(self, x, k ,b):
        return eval(self.func)

    @staticmethod
    def get_vars():
        return ['k','b']


# exponential (e based)
class e_exponential:

    func = 'exp(x) + b'
    
    def get_funcstr(self):
        return self.func
    
    def get_function(self, x, b):
        return eval(self.func)

    @staticmethod
    def get_vars():
        return ['b']

# exponential (other based)
class exponential:

    func = 'exp(x) + b'

    def get_funcstr(self):
        return self.func
    
    def get_function(self, x, a, b):
        return eval(self.func)

    @staticmethod
    def get_var():
        return['a', 'b']

class e_exponential_with_param:

    func = 'exp(x) * k + b'

    def get_funcstr(self):
        return self.func
    
    def get_function(self, x, k, b):
        return eval(self.func)

    @staticmethod
    def get_vars():
        return ['k', 'b']

class exponential_with_param:
    
    func = ' k * a ** x + b'
    def get_funcstr(self):
        return self.func
    
    def get_function(self, x, k, a, b):
        return eval(self.func)

    @staticmethod
    def get_vars():
        return['k', 'a', 'b']

# class logarithm:
#     func = 'log10(x) + b'

#     def get_funcstr(self):
#         return self.func
        
#     def get_function(self, x, a, b):
#         return eval(self.func)

#     @staticmethod
#     def get_vars():
    #         return ['a', 'b']

class logarithm:
    func = ' b + k * log10(x)'

    def get_funcstr(self):
        return self.func
    
    def get_function(self, x, k, b):
        return eval(self.func)

    @staticmethod
    def get_vars():
        return ['k', 'b']


__all__ = ["linear", "exponential", "e_exponential", "e_exponential_with_param", "exponential_with_param", "logarithm"]