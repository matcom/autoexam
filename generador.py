#! /usr/bin/python
#-*-coding: utf8-*-

import os.path
import collections
import jinja2
import random
import qrcode
import json
import os

tags = u"""s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,s14,s15,
        web,clustering,crawler,meta,booleano,vectorial,
        probab,booleanoext,evaluacion,retroalimentacion,
        clasificacion,web25"""
        
end_phrases = [
  u"ninguna de las anteriores",
  u"ninguno de los anteriores",
  u"todos los anteriores",
  u"todas las anteriores",
  u"ninguna de las anteriores es una respuesta correcta",
  u"ninguno de los anteriores es una respuesta correcta",
  u"todos los anteriores son respuestas correctas",
  u"todas las anteriores son respuestas correctas",
]

data_base = collections.defaultdict(lambda: [])

now = 1

def parser():
    f = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), u"SI.txt"))
    lines = f.readlines()
    
    lquestion = []
    i = 0
    while i < len(lines):
        l = lines[i].strip().decode('utf8')
        
        #parsear una pregunta
        while l and i < len(lines):
            l = lines[i].strip().decode('utf8')
            lquestion.append(l)
            i += 1
            
        parse_question(lquestion)
        lquestion = []
    
    f.close()
            

def parse_question(lines):
    """crea el objeto pregunta y la agrega en los contenidos 
    que se evalúan en la misma"""    
    
    print(lines)    
    
    #la pregunta empieza con un listado de tags
    ts = lines.pop(0).split()

    #parsear el header    
    header = ""
    while lines and lines[0][0] != u'_':
        header += " " + lines.pop(0)
    print("=============")    
    print(header)
    print("=============")
    
    #parsear las opciones
    ops = []
    for l in lines:
        if l and l[0] == u'_':
            ops.append(l[1:].strip())
        else:
            ops[-1] += " " +l
    
    #construir el objeto question
    question = Question(header,ops)
  
    #agregar las preguntas en el contenido correspondiente
    for t in ts:
        data_base[t].append(question)
        
    return question
    
class Question:
    """las preguntas tienen un header que es el enunciado,
    y 4 opciones donde la primera es la correcta"""     
    
    def __init__(self, header, options):
        if (not header or len(options) != 4):
            print(header)
            print(len(options))
            raise Exception(u"La pregunta está mal redactada.")
        self.options = options
        self.header = header
        self.correct_option = self.options[0]
        self.correct = 0
        
    def shuffle(self):
        random.shuffle(self.options)
        
        # Poner la opción final (ninguna o todas las anteriores)
        # al final de la pregunta
        for idx, i in enumerate(self.options):
            if i.lower().strip().strip('.') in end_phrases:
                o = self.options[-1]
                self.options[idx] = o
                self.options[-1] = i
                break
        
        # Buscar la respuesta correcta
        for i,o in enumerate(self.options):
            if o == self.correct_option:
                self.correct = i
                return                              
        
    def __str__(self):
        return self.header + "/n" + self.options
        

def generate_qrcode(data, filename='qrcode.png'):
    f = open(filename, 'w')
    qr = qrcode.QRCode(version=2, box_size=10, border=0)
    qr.add_data(data)
    qr.make()
    img = qr.make_image()
    img.save(f)
    f.close()


def generateTest():
    tmp_file = open('latex/pruebas.tex')
    names = open('names.txt').readlines()
    template = jinja2.Template(tmp_file.read().decode('utf8'))  
    
    for i in range(0, len(names), 2):      
        name1 = names[i].strip().decode('utf8')
        name2 = names[i+1].strip().decode('utf8') if i+1 < len(names) else ""
        
        # Generar los qr-code
        generate_qrcode(u'{0}|{1}|0.0|20|4'.format(name1, i), u'generated/v{1}/qrcode-{0}.png'.format(i, now))
        generate_qrcode(u'{0}|{1}|0.0|20|4'.format(name2, i+1), u'generated/v{1}/qrcode-{0}.png'.format(i+1, now))

        out = open(u'generated/v{4}/{0}-{1}-{2}-{3}.tex'.format(name1, i, name2, i+1, now), 'w')
        out.write(template.render(student=[name1, name2], number=[i, i+1]).encode('utf8'))        
        out.close()
        
    tmp_file.close()
    
    
def generateQuiz(n, exclude=()):
    """Genera una lista de preguntas escogidas al azar.
    Se puede especificar una lista de temas a excluir.
    """
    test = set()
    topics = list(set(data_base.keys()) - set(exclude))
    print('Temas disponibles')
    print(topics)
    
    tries = 0
    while (len(test) < n) and (tries < n * 5):
        topic = random.choice(topics)
        print(topic)
        question = random.choice(data_base[topic])
        question.shuffle()
        test.add(question)
        tries += 1
        
    if len(test) < n:
        raise Exception('!!!! Incomplete test')
        
    return test
        
EXCLUDE = '#s1 #s2 #s3 #s4 #s5 #s6 #s7 #s8 #web #booleano #web #crawler #meta #booleano #vectorial #probab #boolextendido #evaluacion'.split()       
        
def generateTextTest():
    tmp_file = open('latex/pruebasTexto.tex')
    template = jinja2.Template(tmp_file.read().decode('utf8'))
    
    names = open('names.txt').readlines()
    
    for i in range(len(names)):
        test = generateQuiz(20, exclude=EXCLUDE)
        # Genera las soluciones
        sol = open(u'generated/v{1}/TestSolution-{0}.txt'.format(i, now), 'w')
        for q in test:
            sol.write('{0}\n\n'.format(q.correct))
        sol.close()
        # Genera el archivo latex del texto del examen
        out = open(u'generated/v{1}/Test-{0}.tex'.format(i, now), 'w')
        out.write(template.render(questions=test, number=i).encode('utf8'))        
        out.close()
    
    tmp_file.close()
    
    
def generatePattern():
    tmp_file = open('latex/pruebasTexto.tex')
    template = jinja2.Template(tmp_file.read().decode('utf8'))
    
    test = []
    
    for tags, l in data_base.items():
        if not tags in EXCLUDE:
            for q in l:
                test.append(q)
            
    # Genera el archivo latex del texto del examen
    out = open(u'generated/v{0}/Questions.tex'.format(now), 'w')
    out.write(template.render(questions=test, number='').encode('utf8'))        
    out.close()
    
    tmp_file.close()
    
        
def evaluator():
    tmp_file = open('tests_results.txt')
    
    tests= json.load(tmp_file)
    
    gs = {}
    
    for i in tests:
        sol = open(os.path.join( "generated",u"TestSolution-" + str(i) + u".txt"))
        f = read_evaluate_test(sol)
        gs[tests[i]["student_id"]] = (evaluate_test(f, tests[i]))
        
    print gs
    
def read_evaluate_test(file_test):
    
    file_test = file_test.readlines()
    f = []    
    
    for i in file_test:
        f_i = i.strip()                   
        if f_i:
            f.append(int(f_i))
    
    return f
    
def evaluate_test(answers, test):
 
    g = 0   
    
    for i in range(len(answers)):
        if answers[i] == test["questions"][str(i+1)]["answers"][0]:
            g += 1
            
    return g

if __name__ == '__main__':
    for d in os.listdir('generated'):
        num = int(d[1:])
        if num >= now:
            now = num + 1

    os.mkdir('generated/v{0}'.format(now))
            
    parser()
    generateTest()
    generateTextTest()
    generatePattern()
    
    print('Generated v{0}'.format(now))
    