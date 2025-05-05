#Token types
#
#EOF (end-of-file) token is used to indicate that
#there is no more input left for lexical analysis
INTEGER, PLUS, MINUS, MUL, DIV, LPAREN, RPAREN, EOF, BEGIN, END, ID, ASSIGN, SEMI, DOT = ( 'INTEGER', 'PLUS', 'MINUS', 'MUL', 'DIV', '(', ')', 'EOF', 'BEGIN', 'END', 'ID', 'ASSIGN', 'SEMI', 'DOT' )

class Token(object):
    def __init__(self, type, value):
        # tokentype: INTEGER, MUL, DIV, or EOF
        self.type = type
        # token value: 0,1,2,3,4,5,6,7,8,9,+, or None
        # token value: non-negative integer value, '*', '/', '+', or None
        self.value = value

    def __str__(self):
        """String representation of the class instance.
        Examples:
            Token(INTEGER, 3)
            Token(PLUS, '+')
        """
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()

class Lexer(object):

    def __init__(self, text):
        #client string input, e.g. "3 * 5", "12 / 3 * 4", etc
        self.text = text
        #self.pos is an index into self.text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        """Advance the 'pos' pointer and set the 'current_char' variable."""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None #Indicates end of input
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        """Return a (multidigit) integer consumed from the input."""
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def peek(self):
        """Return the next character without consuming it."""
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    RESERVED_KEYWORDS ={
        'BEGIN' : Token('BEGIN', 'BEGIN'),
        'END' : Token('END', 'END'),
    }

    def _id(self):
        """Handle identifiers and reserved keywords."""
        result = ''
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()

        token = self.RESERVED_KEYWORDS.get(result, Token('ID', result))
        return token

    def get_next_token(self):
        """Lexical analyzer (also known as scanner or tokenizer)

        This method is responsible for breaking a sentence
        apart into tokens. One token at a time.
        """
        while self.current_char is not None:

            if self.current_char.isalpha():
                return self._id()

            if self.current_char == ':' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(ASSIGN, ':=')

            if self.current_char == ';':
                self.advance()
                return Token(SEMI, ';')

            if self.current_char == '.':
                self.advance()
                return Token(DOT, '.')

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(INTEGER, self.integer())

            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')

            if self.current_char == '*':
                self.advance()
                return Token(MUL, '*')

            if self.current_char == '/':
                self.advance()
                return Token(DIV, '/')

            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')

            self.error()

        return Token(EOF, None)

class Parser(object):

    def program(self):
        """program : compound_statement DOT"""
        node = self.compound_statement()
        self.eat(DOT)
        return node

    def compound_statement(self):
        """compound_statement : BEGIN statement_list END"""
        self.eat(BEGIN)
        nodes = self.statement_list()
        self.eat(END)

        root = Compound()
        for node in nodes:
            root.children.append(node)

        return root

    def statement_list(self):
        node = self.statement()
        results = [node]
        while self.current_token.type == SEMI:
            self.eat(SEMI)
            results.append(self.statement())

        if self.current_token.type == ID:
            self.error()

        return results

    def statement(self):
        if self.current_token.type == BEGIN:
            node = self.compound_statement()
        elif self.current_token.type == ID:
            node = self.assignment_statement()
        else:
            node = self.empty()
        return node

    def assignment_statement(self):
        left = self.variable()
        token = self.current_token
        self.eat(ASSIGN)
        right = self.expr()
        node = Assign(left,token,right)
        return node

    def variable(self):
        node = Var(self.current_token)
        self.eat(ID)
        return node

    def empty(self):
        return NoOp()

    def __init__(self, lexer):
        # client string input, e.g. "3+5"
        self.lexer = lexer
        # self.pos is an index into self.text
        # self.pos = 0
        # # current token instance
        # self.current_token = None
        # self.current_char = self.text[self.pos]
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()

    def term(self):
        """term : factor ((MUL | DIV) factor)*"""
        node = self.factor()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == DIV:
                self.eat(DIV)

            node = BinOp(left=node, op=token, right=self.factor())
        return node

    def factor(self):
        token = self.current_token
        if token.type == PLUS:
            self.eat(PLUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == MINUS:
            self.eat(MINUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == INTEGER:
            self.eat(INTEGER)
            return Num(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node
        else:
            node = self.variable()
            return node

    # def advance(self):
    #     """Advance the 'pos' pointer and set 'current_char' variable."""
    #     self.pos += 1
    #     if self.pos > len(self.text) - 1:
    #         self.current_char = None #Indicates end of input
    #     else:
    #         self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid Syntax')

    # def get_next_token(self):
    #     """Lexical analyzer (also known as scanner or tokenizer)

    #     This method is responsible for breaking a sentence
    #     apart into tokens. One token at a time.
    #     """
    #     while self.current_char is not None:
    #         if self.current_char.isspace():
    #             self.skip_whitespace()
    #             continue

    #         if self.current_char.isdigit():
    #             return Token(INTEGER, self.integer())

    #         if self.current_char == '*':
    #             self.advance()
    #             return Token(MUL, '*')

    #         if self.current_char == '/':
    #             self.advance()
    #             return Token(DIV, '/')

    #         self.error()

    #     return Token(EOF, None)
        # text = self.text

        # while self.pos < len(text) and text[self.pos].isspace():
        #     self.pos += 1

        # is self.pos index past the end of the self.text ?
        # if so, then return EOF token because there is no more
        # input left to convert into tokens

        # if self.pos > len(text) - 1:
        #     return Token(EOF, None)

        #get a character at the position self.pos and decide
        #what token to create based on the single character
        # current_char = text[self.pos]

        #if the character is a digit then convert it to
        #integer, create an INTEGER token, increment self.pos
        #index to point to the next character after the digit,
        #and return the INTEGER token
        # if current_char.isdigit():
        #     start_pos = self.pos
        #     while self.pos < len(text) and text[self.pos].isdigit():
        #         self.pos += 1
        #     token = Token(INTEGER, int(text[start_pos:self.pos]))
        #     return token

        # if current_char == '+':
        #     self.pos += 1
        #     return Token(PLUS, current_char)

        # self.error()

    # def skip_whitespace(self):
    #     while self.current_char is not None and self.current_char.isspace():
    #         self.advance()

    # def integer(self):
    #     """Return a (multidigit) integer consumed from the input."""
    #     result = ''
    #     while self.current_char is not None and self.current_char.isdigit():
    #         result += self.current_char
    #         self.advance()
    #     return int(result)

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    # def term(self):
    #     """Return an INTEGER token value"""
    #     token = self.current_token
    #     self.eat(INTEGER)
    #     return token.value

    def expr(self):
        """Parser / Interpreter
        expr   : term ((PLUS | MINUS) term)*
        term   : factor ((MUL | DIV) factor)*
        factor : INTEGER
        """
        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)

            node = BinOp(left=node, op=token, right=self.term())
        return node

    def parse(self):
        node = self.program()
        if self.current_token.type != EOF:
            self.error()
        return node

        # set current token to the first token taken from the input
        # self.current_token = self.get_next_token()

        # result = self.term()
        # while self.current_token.type in (PLUS, MINUS):
        #     token = self.current_token
        #     if token.type == PLUS:
        #         self.eat(PLUS)
        #         result = result + self.term()
        #     elif token.type == MINUS:
        #         self.eat(MINUS)
        #         result = result - self.term()
        # return result
        # expect the current token to be a single-digit integer
        # left = self.current_token
        # self.eat(INTEGER)

        # expect the current token to be a '+' token
        # op = self.current_token
        # if op.type == PLUS:
        #     self.eat(PLUS)
        # else:
        #     self.eat(MINUS)

        # # expect the current token to be a single-digit integer
        # right = self.current_token
        # self.eat(INTEGER)
        # # after the above call the self.current_token is set to
        # EOF token

        # at this point INTEGER PLUS INTEGER sequence of tokens
        # has been successfully found and the method can just
        # return the result of adding two integers, thus
        # effectively interpreting client input
        # if op.type == PLUS:
        #     result = left.value + right.value
        # else:
        #     result = left.value - right.value
        # return result

class AST(object):
    pass

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))

class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
        self.GLOBAL_SCOPE = {}

    def visit_BinOp(self, node):
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == DIV:
            return self.visit(node.left) // self.visit(node.right)

    def visit_Num(self, node):
        return node.value

    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)

    def visit_UnaryOp(self, node):
        op = node.op.type
        if op == PLUS:
            return +self.visit(node.expr)
        elif op == MINUS:
            return -self.visit(node.expr)

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_Assign(self, node):
        var_name = node.left.value
        self.GLOBAL_SCOPE[var_name] = self.visit(node.right)

    def visit_Var(self, node):
        var_name = node.value
        val = self.GLOBAL_SCOPE.get(var_name)
        if val is None:
            raise NameError(repr(var_name))
        else:
            return val

    def visit_NoOp(self, node):
        pass

class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr

class Compound(AST):
    def __init__(self):
        self.children = []

class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class Var(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class NoOp(AST):
    pass

def main():
    while True:
        try:
            try:
                text = raw_input('spi> ')
            except NameError:
                text = input('spi> ')
        except EOFError:
            break
        if not text:
            continue
        lexer = Lexer(text)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        print(result)
        # Add this line to show all variables after execution
        print(interpreter.GLOBAL_SCOPE)

if __name__ == '__main__':
    main()