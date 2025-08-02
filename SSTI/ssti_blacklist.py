from flask import Flask, request, render_template_string,redirect

app = Flask(__name__)
def check_payload(payload):
    blacklist = blacklist = ['args', 'b', 'base', 'builtins', 'class', 'config', 'cycler', 'dict', 'eval', 'g', 'flag', 'get_flashed_messages', 'getitem', 'globals', 'import', 'init', 'joiner', 'length', 'lipsum', 'mro', 'namespace', 'os', 'popen', 'read', 'request', 'self', 'set', 'setitem', 'update', 'url_for', 'x', '\\', '+','method','__class__', '__bases__', '__subclasses__', '__mro__', '__globals__','__code__', '__getattr__', '__getitem__', '__setattr__', '__delattr__', '__import__','__module__', '__dict__', '__doc__', '__init__', '__call__', '__self__', '__func__','__name__', '__file__', '__package__', '__builtins__', 'url_for', 'get_flashed_messages','request', 'session', 'config', 'g', 'self', 'lipsum', 'namespace', 'cyclers', 'base','cycler']
    for bl in blacklist:
        if bl in payload:
            return True
    return False

@app.route("/")
def home():
    if request.args.get('c'):
        ssti=request.args.get('c')
        if(check_payload(ssti)):
            return "hack hack hack hack hack hack hack"
        else:
            return render_template_string(ssti)
    else:
        return redirect("""/?c={{ 7*7 }}""")


if __name__ == "__main__":
    app.run()