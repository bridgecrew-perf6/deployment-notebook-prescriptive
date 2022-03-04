import re, operator

class ValueIsAlphabet(Exception):
    "Raised when the input contain an alphabet"
    pass

class NoValue(Exception):
    "Raised when the input is blank/ None"
    pass

class MathExpression:
    def __init__(self, input):
        self.input = input
        self.error_message = ""
        self.ops = []
        self.values = []
    
    def isNull(self):
        tokens= self.input
        if len(tokens)==0:
            return True

    def isFloat(self, value):
        try:
            float(value)
            return True
        except:
            return False

    def precedence(self, op):
        if op == '+' or op == '-':
            return 1
        elif op == '*' or op == '/':
            return 2
        elif op=='!=':
            return 0
        elif op == '>' or op == '<' or op == '==' or op == '>=' or op == '<=':
            return -1
        elif op == '&&' or op=='||':
            return -2
        return -99
    
    def applyOp(self, a, b, op):
        # normal equation
        if op == '+': return a + b
        if op == '-': return a - b
        if op == '*': return a * b
        if op == '/': return a // b
        
        # boolean eq
        if op == '&&': return a and b
        if op == '||': return a or b
        if op == '!=': return a != b
        if op == '==': return a == b

        if op == '>': return a > b
        if op == '<': return a < b
        if op == '>=': return a >= b
        if op == '<=': return a <= b

    def boolEval(self):
        if self.precedence(self.ops[-1])==0:
            pass
        elif self.precedence(self.ops[-1])==-1:
            pass
        elif self.precedence(self.ops[-1])==-2:
            pass

    def evaluate(self):
        and_or = ['&', '|']
        values = []
        ops = []
        i = 0
        # tokens=self.input
        reg = re.compile(r'(\+|\*|\/|\-|!=|==|<=|>=|<|>|\(|\)|&&|\|\|)')
        tokens = reg.split(self.input)
        # print(tokens)
        tokens = [t.strip() for t in tokens if t.strip() != ""]
        # tokens = self.parse_exp
        # print(tokens)
        precedence = [self.precedence(i) for i in tokens]
        # print('precedence', precedence)
        try:
            if self.isNull() == True:
                raise NoValue

            # cara 2
            while i < len(tokens):
                try:
                    if tokens[i].isalpha():
                        raise ValueIsAlphabet
                    elif tokens[i] == '(':
                        self.ops.append(tokens[i])

                    elif tokens[i].isdigit():
                        self.values.append(int(tokens[i]))
                    
                    elif self.isFloat(tokens[i]):
                        # print(tokens[i])
                        self.values.append(float(tokens[i]))

                    elif tokens[i]==')':
                        while len(self.ops) != 0 and self.ops[-1] != '(':
                            val2 = self.values.pop()
                            val1 = self.values.pop()
                            op = self.ops.pop()
                            self.values.append(self.applyOp(val1, val2, op))
                        self.ops.pop()

                    else:
                        # print('token: ',tokens[i])
                        # numerical
                        while (len(self.ops) != 0 and self.precedence(self.ops[-1]) > 0 and
                            self.precedence(self.ops[-1]) >= self.precedence(tokens[i])
                            ):
                                    
                            val2 = self.values.pop()
                            val1 = self.values.pop()
                            op = self.ops.pop()
                            
                            self.values.append(self.applyOp(val1, val2, op))
                        # boolean
                        while (len(self.ops)!=0 and self.precedence(self.ops[-1])<=0 and 
                            self.precedence(self.ops[-1]) >= self.precedence(tokens[i])
                            ):
                            # print('------boolean----')
                            # print(self.precedence(self.ops[-1]), self.values,self.precedence(tokens[i]))
                            val2=self.values.pop()
                            val1=self.values.pop()
                            op = self.ops.pop()

                            self.values.append(self.applyOp(val1,val2,op))
                        
                        self.ops.append(tokens[i])
                    i += 1
                    # print(self.ops, self.values)
                except ValueIsAlphabet:
                    return "Wrong Input! Your input value contain an alphabet"
            
            # print('-----------AKHIR-----------')
            while len(self.ops) != 0:
                # print(self.ops,self.values)
                val2 = self.values.pop()
                val1 = self.values.pop()
                op = self.ops.pop()
                self.values.append(self.applyOp(val1, val2, op))
            # print(self.values[-1])
            return self.values[-1]

        except NoValue:
            return "The input field is blank, please insert some expressions!"

class NumericalExpression(MathExpression):
    def __init__(self,input):
        super(NumericalExpression, self).__init__(input)
        
    def checkInput(self):
        op = ['>','=','!','<']
        input = self.input
        i=0
        if self.isNull():
            return False
        else:
            while i < len(input):
                if input[i] in op:
                    return False
                i+=1
            return True

    def evaluate(self):
        if self.checkInput():
            return super(NumericalExpression,self).evaluate()
        else:
            return "Please check again the input, this is only numerical expression"


class BooleanExpression(MathExpression):
    def __init__(self,input):
        super(BooleanExpression, self).__init__(input)

    def checkInput(self):
        op = ['+','-','*','-']
        input = self.input
        i=0
        if self.isNull():
            return False
        else:
            while i<len(input):
                if input[i] in op:
                    return False
                i+=1

            return True

    def evaluate(self):
        if self.checkInput():
            return super(BooleanExpression, self).evaluate()
        else:
            return "Please check again the input, this is only boolean expression"