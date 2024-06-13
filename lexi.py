from flask import Flask, request, render_template_string
import re
import ply.lex as lex
import ply.yacc as yacc

app = Flask(__name__)

TOKENS = {
    'PR': r'\b(for|if|else|while|return)\b',
    'ID': r'\b[a-zA-Z_][a-zA-Z_0-9]*\b',
    'NUM': r'\b\d+\b',
    'SYM': r'[;{}()\[\]=<>!+-/*]',
    'ERR': r'.'
}

# Define the lexer
tokens = ('PR', 'ID', 'NUM', 'SYM', 'ERR', 'INT', 'SYSTEM', 'OUT', 'PRINTLN', 'LE', 'PLUSPLUS', 'STRING')

t_PR = r'\b(for|if|else|while|return)\b'
t_ID = r'\b[a-zA-Z_][a-zA-Z_0-9]*\b'
t_NUM = r'\b\d+\b'
t_LE = r'<='
t_PLUSPLUS = r'\+\+'
t_STRING = r'\".*?\"'
t_ignore = ' \t'

def t_INT(t):
    r'\bint\b'
    return t

def t_SYSTEM(t):
    r'\bSystem\b'
    return t

def t_OUT(t):
    r'\bout\b'
    return t

def t_PRINTLN(t):
    r'\bprintln\b'
    return t

def t_SYM(t):
    r'[;{}()\[\]=<>!+\-/*]'
    return t

def t_ERR(t):
    r'.'
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    t.lexer.skip(1)

lexer = lex.lex()

# Define the parser
def p_statement_for(p):
    'statement : PR "(" INT ID "=" NUM ";" ID LE NUM ";" ID PLUSPLUS ")" "{" statement_block "}"'
    p[0] = 'Sintaxis correcta'

def p_statement_block(p):
    '''statement_block : statement
                       | statement statement_block'''
    p[0] = p[1]

def p_statement_print(p):
    'statement : SYSTEM "." OUT "." PRINTLN "(" STRING ")" ";"'
    p[0] = 'Sintaxis correcta'

def p_error(p):
    if p:
        print(f"Error de sintaxis en '{p.value}'")
    else:
        print("Error de sintaxis en el final del archivo")

parser = yacc.yacc()

html_template = '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Lexical, Syntactic, and Semantic Analyzer</title>
    <style>
      body {
        font-family: 'Arial', sans-serif;
        background-color: #f0f8ff;
        margin: 0;
        padding: 0;
      }
      .container {
        width: 90%;
        margin: 20px auto;
        padding: 20px;
        background-color: #fff;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
      }
      header {
        text-align: center;
        padding: 10px;
        background-color: #4682b4;
        color: #fff;
        border-radius: 10px 10px 0 0;
      }
      header h1 {
        margin: 0;
        font-size: 2em;
      }
      form {
        margin: 20px 0;
      }
      textarea {
        width: 100%;
        height: 200px;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
        font-size: 1em;
        font-family: 'Courier New', Courier, monospace;
      }
      input[type="submit"] {
        display: block;
        width: 100%;
        padding: 10px;
        background-color: #4682b4;
        color: #fff;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 1.2em;
      }
      input[type="submit"]:hover {
        background-color: #5a9bd6;
      }
      table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
      }
      table, th, td {
        border: 1px solid #ddd;
      }
      th, td {
        padding: 10px;
        text-align: left;
      }
      th {
        background-color: #4682b4;
        color: #fff;
      }
      .results {
        margin-top: 20px;
      }
      .results h2 {
        font-size: 1.5em;
        color: #4682b4;
      }
      pre {
        background-color: #f8f8f8;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
        white-space: pre-wrap;
        word-wrap: break-word;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <header>
        <h1>Lexical, Syntactic, and Semantic Analyzer</h1>
      </header>
      <form method="post">
        <textarea name="code">{{ code }}</textarea><br>
        <input type="submit" value="Analyze">
      </form>
      <div class="results">
        <h2>Lexical Analyzer</h2>
        <table>
          <tr>
            <th>Tokens</th><th>PR</th><th>ID</th><th>Numbers</th><th>Symbols</th><th>Error</th>
          </tr>
          {% for row in lexical %}
          <tr>
            <td>{{ row[0] }}</td><td>{{ row[1] }}</td><td>{{ row[2] }}</td><td>{{ row[3] }}</td><td>{{ row[4] }}</td><td>{{ row[5] }}</td>
          </tr>
          {% endfor %}
          <tr>
            <td>Total</td><td>{{ total['PR'] }}</td><td>{{ total['ID'] }}</td><td>{{ total['NUM'] }}</td><td>{{ total['SYM'] }}</td><td>{{ total['ERR'] }}</td>
          </tr>
        </table>
        <h2>Syntactic and Semantic Analyzer</h2>
        <table>
          <tr>
            <th>Syntactic</th><th>Semantic</th>
          </tr>
          <tr>
            <td>{{ syntactic }}</td><td>{{ semantic }}</td>
          </tr>
        </table>
        <h2>Corrected Code</h2>
        <pre>{{ corrected_code }}</pre>
      </div>
    </div>
  </body>
</html>
'''

def analyze_lexical(code):
    results = {'PR': 0, 'ID': 0, 'NUM': 0, 'SYM': 0, 'ERR': 0}
    rows = []
    for line in code.split('\n'):
        row = [''] * 6
        for token_name, token_pattern in TOKENS.items():
            for match in re.findall(token_pattern, line):
                results[token_name] += 1
                row[list(TOKENS.keys()).index(token_name)] = 'x'
        rows.append(row)
    return rows, results

def correct_syntactic(code, var_name):
    corrected_code = re.sub(r'\bfor\s*\(\s*.*?\s*=\s*.*?\s*;\s*.*?\s*<=\s*.*?\s*;\s*.*?\s*\)\s*\{', 
                            f'for (int {var_name} = 1; {var_name} <= 19; {var_name}++) {{', code)
    corrected_code = re.sub(r'\{.*\}', r'{\n    System.out.println("Este es el correcto");\n}', corrected_code, flags=re.DOTALL)
    return corrected_code

def correct_semantic(code):
    corrected_code = re.sub(r'\bSystem\.out\.println\s*\(.*\)\s*;', r'System.out.println("Este es el correcto");', code)
    return corrected_code

def analyze_syntactic(code):
    syntactic_errors = []
    semantic_errors = []
    corrected_code = code
    
    match = re.search(r'\bfor\s*\(\s*int\s+(\w+)\s*=\s*\d+\s*;\s*\1\s*<=\s*\d+\s*;\s*\1\+\+\s*\)\s*\{', code)
    if not match:
        syntactic_errors.append("Error en la sintaxis del bucle 'for'.")
        corrected_code = correct_syntactic(corrected_code, "i")
    else:
        var_name = match.group(1)
        corrected_code = correct_syntactic(corrected_code, var_name)

    if not re.search(r'\bSystem\.out\.println\s*\(\s*".*"\s*\)\s*;', code):
        semantic_errors.append("Error semántico en System.out.println.")
        corrected_code = correct_semantic(corrected_code)
    
    syntactic_result = "Sintaxis correcta" if not syntactic_errors else " ".join(syntactic_errors)
    semantic_result = "Uso correcto" if not semantic_errors else " ".join(semantic_errors)

    return syntactic_result, semantic_result, corrected_code

@app.route('/', methods=['GET', 'POST'])
def index():
    code = ''
    lexical_results = []
    total_results = {'PR': 0, 'ID': 0, 'NUM': 0, 'SYM': 0, 'ERR': 0}
    syntactic_result = ''
    semantic_result = ''
    corrected_code = ''
    if request.method == 'POST':
        code = request.form['code']
        lexical_results, total_results = analyze_lexical(code)
        syntactic_result, semantic_result, corrected_code = analyze_syntactic(code)
    return render_template_string(html_template, code=code, lexical=lexical_results, total=total_results, syntactic=syntactic_result, semantic=semantic_result, corrected_code=corrected_code)

if __name__ == '__main__':
    app.run(debug=True)
