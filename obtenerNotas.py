from bs4  import BeautifulSoup
import sys
import re
import requests

def main(COD_ALUMNO='', CLAVE=''):
    uri = 'http://www.academico.uni.pe/intranet/public/alumno/entrar'
    uri_referer = 'http://www.orce.uni.edu.pe/'
    with requests.Session() as session:
        session.get(uri)
        login_data = dict(codUni=COD_ALUMNO, clave=CLAVE, tipo='acceso')
        session.post(uri, data=login_data, headers={"Referer": uri_referer})
        uri_notas = 'http://www.academico.uni.pe/intranet/public/alumno/mis-notas'
        page = session.get(uri_notas)
        soup = BeautifulSoup(page.content, 'html.parser')
        pattern = re.compile(r'(\S+)/(\w+)/(\w+)/(\w+)')
        cursos = soup.find_all('td', class_='hidden-phone')
        cursos_link = []
        cursos_nombre = []
        cursos = cursos[::2]
        #se deben cambiar la forma de jalar los cursos, no funciona de manera robusta :S

        for curso in cursos:
            cursos_nombre.append(curso.a.text)
            #Coloca en "cursos_nombre" todos los nombres de los cursos que estan disponibles en el ultimo semestre

        for link in cursos:
            cursos_link.append(uri_notas + pattern.sub(r'/\2/\3/\4', link.a.get('href'))) 
            #Coloca en "cursos_link" todos los enlaces COMPLETOS hacia los cursos en  orden de los elementos de "cursos_nombre"
        
        x=0
        for link in cursos_link:
            print("\n{:*^90}".format(re.sub(' +', ' ',cursos_nombre[x])))
            curso_page = session.get(link)
            curso_soup = BeautifulSoup(curso_page.content, 'html.parser')
            curso_notas_tabla = curso_soup.find_all('div', class_='row')
            curso_notas_tabla = curso_notas_tabla[2:]
            for tabla in curso_notas_tabla:
            
                evaluaciones = tabla.tbody.find_all('tr')
                for evaluacion in evaluaciones:
                    nota = evaluacion.find_all('td')
                    print("\t{0:<15}{1:^6}{2:^20}{3:>20}".format("EVALUACION", "NOTA", "PORCENT. APROBADOS", "PORCENT. ASISTENCIA"), end='\n')
                    print("\t{0:<15}{1:^6}{2:^20}{3:>13}".format(nota[0].text, nota[1].span.text, nota[3].text, nota[4].text), end='\n\n')
            x+=1

if __name__ == "__main__":
    try:
        main(sys.argv[1], sys.argv[2])
    except IndexError:
        main()
