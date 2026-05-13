from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_read_main():
    slug = "invest-prueba-siypk"
    num_tokens = 15
    username = ''
    password = 'XXXX'

    files = {
        'username': (None, username),
        'password': (None, password),
        'client_secret': (None, 'Vg8utagSim9BwplW'),
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'es,es-ES;q=0.8,en-US;q=0.5,en;q=0.3',
        # 'Accept-Encoding': 'gzip, deflate',
        'Content-Type': 'multipart/form-data; boundary=---------------------------109470762823218680503490599840',
        'Referer': 'http://localhost:8080/',
        'white-label-access-key': 'viverent',
        'Origin': 'http://localhost:8080',
        'DNT': '1',
        'Authorization': 'Bearer',
        'Connection': 'keep-alive',
        'Priority': 'u=0',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }

    response = client.post('/v2/with_login/login/access_token', files=files, headers=headers)
    assert response.status_code == 200

    access_token = response.json()

    print(access_token)

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'es,es-ES;q=0.8,en-US;q=0.5,en;q=0.3',
        # 'Accept-Encoding': 'gzip, deflate',
        'Referer': 'http://localhost:8080/',
        'white-label-access-key': 'viverent',
        'Origin': 'http://localhost:8080',
        'DNT': '1',
        'Authorization': f'Bearer {access_token["access_token"]}',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }

    response = client.get(f'/v2/signature/get/{slug}/viverent_contract', headers=headers)
    assert response.status_code == 200

    print(response.json())

    contract_data = response.json()
    invest_id = contract_data["invest_id"]

    response = client.get(f'/v2/signature/document/{contract_data["signature_id"]}', headers=headers)
    assert response.status_code == 200

    print(response.json())

    document_data = response.json()

    headers_sign = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'es,es-ES;q=0.8,en-US;q=0.5,en;q=0.3',
        # 'Accept-Encoding': 'gzip, deflate',
        'Content-Type': 'multipart/form-data; boundary=---------------------------4120540136916761992926312594',
        'Referer': 'http://localhost:8080/',
        'white-label-access-key': 'viverent',
        'Origin': 'http://localhost:8080',
        'DNT': '1',
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Iml2YW4ucm1naUBnbWFpbC5jb20iLCJ3aGl0ZV9sYWJlbF9hY2Nlc3Nfa2V5Ijoidml2ZXJlbnQiLCJleHAiOjE3MjY3NDYxMjF9.rgWxeclNfdnqJN--d4tLQUqHGMrwWANgnzM3e8toQSo',
        'Connection': 'keep-alive',
        'Priority': 'u=0',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }

    files = {
        'image_data': (None,
                       'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAlgAAAEsCAYAAAAfPc2WAAAgAElEQVR4Xu3dBbA0V5UH8OCQ4LY4wd1hkSDBJbi7LRJgcQseILgvvhQQLBBskQqBIAnBJUiABQIsToIuwcISAnv+qR4yvM+edL/p6fu7Vadm3nszt+/53f6SUy23T7STRoAAAQIECBAg0KvAiXrtTWcECBAgQIAAAQI7KbDsBAQIECBAgACBngUUWD2D6o4AAQIECBAgoMCyDxAgQIAAAQIEehZQYPUMqjsCBAgQIECAgALLPkCAAAECBAgQ6FlAgdUzqO4IECBAgAABAgos+wABAgQIECBAoGcBBVbPoLojQIAAAQIECCiw7AMECBAgQIAAgZ4FFFg9g+qOAAECBAgQIKDAsg8QIECAAAECBHoWUGD1DKo7AgQIECBAgIACyz5AgAABAgQIEOhZQIHVM6juCBAgQIAAAQIKLPsAAQIECBAgQKBnAQVWz6C6I0CAAAECBAgosOwDBAgQIECAAIGeBRRYPYPqjgABAgQIECCgwLIPECBAgAABAgR6FlBg9QyqOwIECBAgQICAAss+QIAAAQIECBDoWUCB1TOo7ggQIECAAAECCiz7AAECBAgQIECgZwEFVs+guiNAgAABAgQIKLDsAwQIECBAgACBngUUWD2D6o4AAQIECBAgoMCyDxAgQIAAAQIEehZQYPUMqjsCBAgQIECAgALLPkCAAAECBAgQ6FlAgdUzqO4IECBAgAABAgos+wABAgQIECBAoGcBBVbPoLojQIAAAQIECCiw7AMECBAgQIAAgZ4FFFg9g+qOAAECBAgQIKDAsg8QIECAAAECBHoWUGD1DKo7AgQIECBAgIACyz5AgAABAgQIEOhZQIHVM6juCBAgQIAAAQIKLPsAAQIECBAgQKBnAQVWz6C6I0CAAAECBAgosOwDBAgQIECAAIGeBRRYPYPqjgABAgQIECCgwLIPECBAgAABAgR6FlBg9QyqOwIECBAgQICAAss+QIAAAQIECBDoWUCB1TOo7ggQIECAAAECCiz7AAECBAgQIECgZwEFVs+guiNAgAABAgQIKLDsAwQIECBAgACBngUUWD2D6o4AAQIECBAgoMCyDxAgQIAAAQIEehZQYPUMqjsCBAgQIECAgALLPkCAAAECBAgQ6FlAgdUzqO4IECBAgAABAgos+wABAgQIECBAoGcBBVbPoLojQIAAAQIECCiw7AMECBAgQIAAgZ4FFFg9g+qOAAECBAgQIKDAsg8QIECAAAECBHoWUGD1DKo7AgQIECBAgIACyz5AgAABAgQIEOhZQIHVM6juCBAgQIAAAQIKLPsAAQIECBAgQKBnAQVWz6C6I0CAAAECBAgosOwDBAgQIECAAIGeBRRYPYPqjgABAgQIECCgwLIPECBAgAABAgR6FlBg9QyqOwIECBAgQICAAss+QIAAAQIECBDoWUCB1TOo7ggQIECAAAECCiz7AAECBAgQIECgZwEFVs+guiNAgAABAgQIKLDsAwQIECBAgACBngUUWD2D6o4AAQIECBAgoMCyDxAgQIAAAQIEehZQYPUMqjsCBJoVOENlfnjF3ysuVXF0sxISJ0BgJwWWnYAAAQL9CHyqurla19Wb6/Vu/XSrFwIEllFAgbWMs2bMBAiMSeBkNZjHVjx9blD3qPdvHNMgjYUAgc0VUGBtrretESAwHYHTViovr7htxSnn0npxvX/4dNKUCQEC6xFQYK1HzXcIEGhZ4IyV/F4V/15xqhUQB9XPN604tmUguRMgsJNrsOwEBAgQWKVATgU+uOIJFSmyVrZv1y92q/j1KvvzMQIEJizgCNaEJ1dqBAj0JnCF6ul5FdfeTo85Vfiu3raoIwIEllpAgbXU02fwBAgMKHDS6jsXrt+y4qI72M7L6u85uqURIEDgeAEFlh2BAAECWwpkTatPVlx8Ozg5FfjSiv+sOBIiAQIE5gUUWPYHAuMRsFDlOObicjWM91ecczvD+UT97TYVvxzHkI2CAIGxCSiwxjYjxtOywP6V/O07AAtVbv6ekP8e5gL2J1fkgvaV7W/1i3dWPLHiO5s/PFskQGCZBBRYyzRbxjp1gQdWgllXKe37FReoyGNXtOEFLlGbeEXFNbeyqb/W715fkeus8igcjQABAjsUUGDtkMgHCGyaQP49fqviwt0Wcwrq3Zu29TY3lHWssjDofSpOvBWCr9Tv9qz4XJs8siZAYL0CCqz1yvkegWEE7lnd5mhJ2hEVl6n48zCbar7XPUrgTRW59m1l+0v94u0Vj644qnkpAAQIrFlAgbVmMl8gMKhAHrmSo1jn7baSYuveg26xzc7vWGnHdv4RNzOJFLa3q3A6sM19Q9YEehFQYPXCqBMCvQrkdNVr5nq0gGV/vDtXV1laYWtFa653y5ILe1c4atWfuZ4INCmgwGpy2iU9coEscPmTin/pxpm7125W8YGRj3vMw8t/63JU6kUV51gx0O/Vz1l2Ic8W/OOYkzA2AgSWR0CBtTxzZaRtCTysKwZmWedOtix6aXmAte0Hu9THc5H6wytWrmt1TP3u2RXPqfi/tXXr0wQIENi+gALLHkJgnAKn64qps8wNL4taXqji6HEOeVSjSjGaC9TvuY1Rfah+n2Ux/mdUozYYAgQmI6DAmsxUSmSCAlls9C4r8vpY/Xzjitzlpm0pkNOqWUvs1hUr//v2u/rdfhVZ7+pr8AgQIDCkgAJrSF19E9iYwDXq64dupYsUCA/aWNeT+/aZKqOswJ7rqFauZ/W/9bvnd4WXo3+Tm3oJERingAJrnPNiVARmAvvWm3us4MjdbjlC8x5MO522K6zuVq9nXeFxQP2cRUQ/wokAAQKbLaDA2mxx2yOwNoH8G82pwjtVzP97Pa5+zunDPL+wxXaVSnqviltsJfn31u/2rsgq7BoBAgQWIqDAWgi7jRJYk0BOeeWROVsrJnLkJgVYC+30lWROjd63YrYQ6yzvFJwHVTyp4rAWMORIgMC4BRRY454foyMwEzh5vXlfxQ1XkBxbP9+0Ky6mqpUCM0frHluRhzLPt1xTlWUWUoB+e6oA8iJAYPkEFFjLN2dG3K7ASSr1p1Q8sWL+327uKMydhbnDcErtZJVM1rBKYTW/hlUWXn1Xl2+eJWhx0CnNulwITERAgTWRiZRGUwJX7AqM88xlnSNZu1d8egISefjy/StyOvBcc/nkodcpqFJkHjmBPKVAgMCEBRRYE55cqU1aIMsSfL7i/HNZ5khWiq9lXePpFDX2LP6Zi9fn7wj8Vf38wopXVWTJBY0AAQKjF1BgjX6KDJDANgV2rb98smL+9FmuSbpexReXzC0X8GetqgvOjTtHrJ7bhdOASzahhkugdQEFVut7gPyXXeCSlcDBFWeeSyTFyB4VH1+C5C5dY3xtRY68zVqeC/jUipwOzEOvNQIECCydgAJr6abMgAlsIZDrlA6sSLE1az+vN1kr6gcj9npMjS13AM63FFV7V3hG4IgnztAIENixgAJrx0Y+QWAZBHJheI5kXWZusN+v9zky9JuRJZDrx95YcZO5ceWU5v0qvjyysRoOAQIE1iWgwFoXmy8RGKXAhWpUeSzM/N2F36ifr1RxzAhGnPWscmdglpmYXcR+VL3P6cBXV+QRQBoBAgQmIaDAmsQ0SoLAPwRSuLy04vZzJnlgdNbJ+tMCna5e285dgLOFQr9V73MUKw+u9gDmBU6MTRMgMIyAAmsYV70SWKRAHoCcIiuP0Zn9G8/6WLstYFBZeuHZFXevOGO3/WfW694VWbtLI0CAwCQFFFiTnFZJETheIM/le9qcRVY/z0OjN6uwuX5tK0etZmt15VE2WZU9D2PWCBAgMGkBBdakp1dyBHa6axm8riKPnUnLReRZJ2vIC9/z35UnVzyuIkewflvx+ooUfNazslMSINCEgAKriWmWZOMCWa4hF7/v0jl8t16vWpEV0vtuKd5eUJH1rdIOr7hjxTf73pD+CBAgMGYBBdaYZ8fYCPQncIHq6kMVeU37esWNKn7a0yZyfVWOWuUuwZNW/K4iyy68vcLdgT0h64YAgeURUGAtz1wZKYGNClykOnh3xcW7jrJOVq6T+t4GO75Lff8lFVnfKu2jFbmLccjTkBscsq8TIEBgWAEF1rC+eicwNoFT14BysfsNuoH9sl5vXZFnGq61nbK+kPWrcodgWh5xc7uK96+1I58nQIDA1AQUWFObUfkQ2LFALnh/S1cM5dN/q7hzxf47/uo/PpHH87yn4grdbz5Wr/epyFExjQABAs0LKLCa3wUANCpwkso7p/Ku1eWfIushFS9fhUeKqg9UZFHTv1Zk6YUXruJ7PkKAAIFmBBRYzUy1RAlsIZBTfCmM9qyY/bcgR7aytMO22s3rD/tV5I7ET1Xct8IdgnYuAgQIrBBQYNklCBB4ShHsPceQuw1zLdXvV9A8un5+bve7d9RrVorPdVcaAQIECCiw7AMECGxF4F71u1ywPluQ9Ef1PncYHlGRhzTnlOANu+/tU69ZksHyC3YlAgQIbEPAESy7BgECM4EsDprrss7c/eLn9bpHxb4Vl6zI2lb3rshdiBoBAgQIbEdAgWX3IEBgXuAM9cMBFVnpPS1HqfLfiaz6nuLKEgz2FwIECKxCQIG1CiQfIdCYwOkr3yxIeu25vJ9R75/YmIN0CRAgsG4BBda66XyRwGQF8gidt1ak0JpvWbE9dxBqBAgQILADAQWWXYQAgXmBPBj64Ios4ZDXH1TkAvi04yoeUPEaZAQIECCwfQEFlj2EAIGZwAXrTda2ygKih1TkcTpZSDTLOOSuwdl/L7JuVu441AgQIEBgGwIKLLsGAQIRuETFf1VcqCIXud+yK65mOo+vN7kOa9ayJtbz0REgQIDA1gUUWPYMAgTOVwSHVJyn4ksVu1X8eSssD6vfvWju9zmKlaNZGgECBAisEFBg2SUItC2wa6V/UEWOXH274noVP9kOyd3rb2+Y+3uuyXpV24SyJ0CAwJYCCix7BYF2Bc5VqWeF9ktVfLXithXfXQVHHqPz5oqTV2SdrDtU5NE5GgECBAh0AgosuwKBNgVSXH264twV36m4ySqLq5nWlevNxyp2rvhbxR0VWW3uSLImQGDrAgosewaB9gR2qZRzIfu1KnI68LIVv14Hw626ouok9XpsRR6r8+F19OMrBAgQmJyAAmtyUyohAtsVOHX99cCKq1ccWXGdim9twGyv+u6zuu9nnawcCcs1XRoBAgSaFlBgNT39km9MIP/eX1dxz4qjKnavyIXtG22PqA6eV3HiiqMrrlHxtY126vsECBBYZgEF1jLPnrETWJvAg+vj/1GR03m5oP19a/v6dj+dftN/2m8rskjpF3rsX1cECBBYKgEF1lJNl8ESWLdACp73V+TOvywaOjutt+4Ot/LFp9fvZg+E/nG9z2nIH/W5AX0RIEBgWQQUWMsyU8ZJYP0CZ6ivHl6ROwdz1Oo2FXkEzhAtyzfkodBpX6/IoqW/G2JD+iRAgMCYBRRYY54dYyOwcYH8G393RR59k+utrlnxi413u80eTlp/yUKkd+4+8fZ6zTpZGgECBJoSUGA1Nd2SbVBgn8r5CRW/r7hqxTc2wSBrYx1acYVuW/vXa9bJ0ggQINCMgAKrmamWaIMCF62cc5ou61S9suKBm2hwttrWlyvympblHJ6zidu3KQIECCxUQIG1UH4bJzCYwOmq51x3NXuA81Xqfe4e3MyWhUw/WHHKbqMvqdc8MFojQIDA5AUUWJOfYgk2KJA7BbPYZwqcrNB+sYpfLsjh0rXdQypyoX3ayypmyzksaEg2S4AAgeEFFFjDG9sCgc0WyOnAPbuN3rRe81icRbaVR7KyKOljFjkg2yZAgMDQAgqsoYX1T2BzBS5Rm/tKRe7me1vFnTZ389vcWlZ3zzpcOXWZlgLw1SMZm2EQIECgdwEFVu+kOiSwMIE8xDnPFzxNN4KL1+s3FzaaLTc8fyTrL/Xn61Z8ckTjMxQCBAj0JqDA6o1SRwQWLvDIGsHzu1HkMTX/uvARbTmAe9av8jzE/Lcnj9S5csURIxynIREgQGBDAgqsDfH5MoFRCRxYo7lRN6J71+vrRzW6EwbzuHr7zO7H79dr1uf6+UjHalgECBBYl4ACa11svkRgdAJZof3j3ajyaJpzVvxhdKM8YUBZ4f123Y+H1WvG/6cRj9fQCBAgsCYBBdaauHyYwCgFTlaj+mpFlmNIe0HFo0Y50hMGlTHn+qvZacx96/29Rj5mwyNAgMCqBRRYq6byQQKjFZg/5XZcjTIPdT5qtKM9YWBnrrefqMiK82lvrZg9w3AJhm+IBAgQ2LaAAsveQWD5BX5YKWTF9rRcOD5b1HMZMtu1BpllJWbLN4z52rFl8DRGAgRGIqDAGslEGAaBdQpknav95r6ba5vusM6+FvW1LIb67oqcNvxbxfUqDl7UYGyXAAECfQgosPpQ1AeBxQjkIc7fqThft/lj6vUiFT9ezHA2tNVcM5YV3tN+VZFH7GRNL40AAQJLKaDAWsppM2gCxws8oWKfOYun1vu9l9hm3xr7Pbrxf7RecyRLI0CAwFIKKLCWctoMmsBOlyqDQytO31nk6NXZK45eYpuVd0OmeHzSEudj6AQINCygwGp48qW+tAIpqnKN0mXnMpjKxeHnqJyy5ETuMEy7ccUHl3amDJwAgWYFFFjNTr3El1TgxDXu91XsMTf+/et9ljfIBeJTaLeqJHLRe9qvK85fkcVTNQIECCyNgAJraabKQAkcL/DwihfOWfy03l+7Ihe7T6k9p5J5TJdQVqjffUrJyYUAgekLKLCmP8cynIZAjlw9a67oSFZZVDTPHvzINFL8pyxyh+R7KrKEQ9qjK2YPsp5gulIiQGBqAgqsqc2ofKYokJXZX1Uxf1owee5VkSM9U23JO4/TOW+XYJagOGKqycqLAIFpCSiwpjWfspmewBkrpW9VnGVFat+rny9U8ffppfxPGWXR1CykmiN4KbZ2r8iRO40AAQKjFlBgjXp6DK5xgVNX/h+uuMoKh5fVz4+s+EsjPq+rPGcPgk7e89egNUIgTQIElk1AgbVsM2a8rQjkeYKvrcgddbP2x3pz24rWli3YpXLORfxZ5ytF5eUrvtHKjiBPAgSWU0CBtZzzZtTTFrhmpXdgxc5zaf6h3mdl889NO/VtZpfrz7J0w8krPl2xW6MO0iZAYEkEFFhLMlGG2ZTA1yrbS67IeM/6+dVNKWyZ7EvqVw/pfp1Thvs27iF9AgRGLKDAGvHkGFqTAg+orF8xl3mOXOU04RSXYljrBJ+ivpAL/net+E1F7jLMI4I0AgQIjE5AgTW6KTGghgVy3dV3K3LnYFqKh2tUHNawycrUr1C/yGOCTlPxmor7sSFAgMAYBRRYY5wVY2pV4J2V+G3mks+q7S9uFWM7eb+g/vaIijwa6HwVP2JEgACBsQkosMY2I8bTqsDNK/H3ziWfBTUv1hURrZpsK+8sX3FkRV6fXvFkQAQIEBibgAJrbDNiPC0KpFDIsgPn6ZLPkZkrVny5RYxV5vzM+tzjKvIw6Kz0niUsNAIECIxGQIE1mqkwkIYFcnfg/LVET6qf92nYYzWpX7g+9N8VeWbhoypy2lAjQIDAaAQUWKOZCgNpVCAXbX9xLveP1/trV0z9ETh9TPfbqpM8SidHr3at+FUfneqDAAECfQgosPpQ1AeB9QtkVfYbdl//bb1eoCJLEGg7FshaYV+pyFGsrHp/nx1/xScIECCwOQIKrM1xthUCWxPII1++UJEHGaflmqJno1qTQJ7L+KDuG1er18+s6ds+TIAAgYEEFFgDweqWwCoEZssN5KOfr7hqRS5w11YvkPWwchTr/BVHVeQI4J9W/3WfJECAwDACCqxhXPVKYEcCp60P/KIiq5Onpbj67I6+5O9bFcgp1gMqcqrweRWP4USAAIFFCyiwFj0Dtt+qwHPmCoGv1/tLtQrRU95vqH7uXnFsxWUrcoehRoAAgYUJKLAWRm/DDQtcvXLP3YK59uq4ittWvKdhjz5SP2t1kodk5/WgitmNA330rQ8CBAisWUCBtWYyXyCwIYGd69t5YPG5u14eWK+v3FCPvjwT2KvePKv7IQVWCi2NAAECCxFQYC2E3UYbFsizBR/a5Z87CHPtVY5iaRsX2KW6+FlFrm9z2nXjnnogQGADAgqsDeD5KoE1CuRBzu+oyL+7rHV1/YovrbEPH9++wMvrzzkqmHbvitcDI0CAwCIEFFiLULfNFgWyfMBXK3KUJS2ns3Khu9avQJZrOLxzzl2aWWvsp/1uQm8ECBDYsYACa8dGPkFgowJnqA6OqDhz19Fh9XqVir9utGPf36pAjmDlSFZabibYnRMBAgQ2W0CBtdnitteiQE4L5k7BtD9X5EHFP24RYhNzflNt667d9p5fr4/exG3bFAECBI6/FkQjQGA4getV1x+e6/6Z9f4Jw21Oz53Aqeo1a2HtWpHV8W9Q8VE6BAgQ2CwBBdZmSdtOiwKnrqRzavDsXfKfrtfdWoRYUM4Xq+3mdGyKrZ9XXLQiD9TWCBAgMLiAAmtwYhtoVODklfd7K27U5Z9Tg9eo+GKjHotK+2G14RfNFbjXqveufVvUbNgugYYEFFgNTbZUN1XgGbW1x89t8eH1PmtgaZsrkP/GfagiS2KkPbVi780dgq0RINCigAKrxVmX89ACOVJ16NxGDq731xl6o/rfpsBp6i+5Hutc3SeuW68f40WAAIEhBRRYQ+rqu0WBXOfz2YrTdcn/sF7z8GHX/ix2b7hcbf6Qiqzy/uuKq1Xk+jiNAAECgwgosAZh1WmjArm+54CK2WKiYcjRrE826jG2tB9RA3pBN6gsk5GL4P84tkEaDwEC0xBQYE1jHmWxeIE8XDgXtZ9ibihvr/d3WPzQjGBOIAVWCq20LEKaZTRc9G4XIUCgdwEFVu+kOmxQIKuyf6LipHO571Pvn9SgxTKk/Ooa5P26ge5Xr3dZhkEbIwECyyWgwFqu+TLa8QmcpYaUC9pz7dWs5VEtrxzfUI2oE8hRxhRZ9+h+zlGtR9EhQIBAnwIKrD419dWaQJ4teFBFLqBOO67i3yre0BrEEuabo43vqrh5N/Yn1+vTlzAPQyZAYKQCCqyRToxhjV7gjDXCb1ScbW6kT6v3Txn9yA1wJpDFYD9QkWUb0vbofiZEgACBDQsosDZMqINGBXLtzp3mcs/P96/4Q6Mey5p2lm3IOmWXr/hLRR4QnYdzawQIENiQgAJrQ3y+3KhAbu/P0avZv5+sp5T/Qbvlfzl3iJPVsPMg6CypkTsKr1TxleVMxagJEBiLgAJrLDNhHMskkEev3KAb8M/q9YoVRy5TAsa6hUAezJ3nRF6k4tiK3SvycG6NAAEC6xJQYK2LzZcaFkgx9YW5/Peu93m+nbb8Ajld+PmuyPpTveZIVh6xoxEgQGDNAgqsNZP5QuMCT6z8Z3ebHVPvc5H77xo3mVL6mc8UWeeuOLrixhWfmVKCciFAYHMEFFib42wr0xHI+lZ7dukcVq85oqVNS+Dslc7XKs5UkevqblaRC+E1AgQIrFpAgbVqKh8kcLzAxSte2/3P96H1eiCXSQpcorL6SMVsGY631PuHVfxqktlKigCB3gUUWL2T6pAAgYkIZHX+HLHcvcvn8HrNY3W+PpH8pEGAwIACCqwBcXVNgMDSC2TF99dV3G0uk6yVlSNaGgECBLYpoMCycxAgQGD7AiepP+exOrfoPnZAvd4UGgECBLYnoMCyfxAgQGB1Averj2X1/udWuPZudWY+RaBZAQVWs1MvcQIECBAgQGAoAQXWULL6JUCAAAECBJoVUGA1O/USJ0CAAAECBIYSUGANJatfAgQIECBAoFkBBVazUy9xAgQIECBAYCgBBdZQsvolQIAAAQIEmhVQYDU79RInQIAAAQIEhhJQYA0lq18CBAgQIECgWQEFVrNTL3ECBAgQIEBgKAEF1lCy+iVAgAABAgSaFVBgNTv1EidAgAABAgSGElBgDSWrXwIECBAgQKBZAQVWs1MvcQIECBAgQGAoAQXWULL6JUCAAAECBJoVUGA1O/USJ0CAAAECBIYSUGANJatfAgQIECBAoFkBBVazUy9xAgQIECBAYCgBBdZQsvolQIAAAQIEmhVQYDU79RInQIAAAQIEhhJQYA0lq18CBAgQIECgWQEFVrNTL3ECBAgQIEBgKAEF1lCy+iVAgAABAgSaFVBgNTv1EidAgAABAgSGElBgDSWrXwIECBAgQKBZAQVWs1MvcQIECBAgQGAoAQXWULL6JUCAAAECBJoVUGA1O/USJ0CAAAECBIYSUGANJatfAgQIECBAoFkBBVazUy9xAgQIECBAYCgBBdZQsvolQIAAAQIEmhVQYDU79RInQIAAAQIEhhJQYA0lq18CBAgQIECgWQEFVrNTL3ECBAgQIEBgKAEF1lCy+iVAgAABAgSaFVBgNTv1EidAgAABAgSGElBgDSWrXwIECBAgQKBZAQVWs1MvcQIECBAgQGAoAQXWULL6JUCAAAECBJoVUGA1O/USJ0CAAAECBIYSUGANJatfAgQIECBAoFkBBVazUy9xAgQIECBAYCgBBdZQsvolQIAAAQIEmhVQYDU79RInQIAAAQIEhhJQYA0lq18CBAgQIECgWQEFVrNTL3ECBAgQIEBgKAEF1lCy+iVAgAABAgSaFVBgNTv1EidAgAABAgSGElBgDSWrXwIECBAgQKBZAQVWs1MvcQIECBAgQGAoAQXWULL6JUCAAAECBJoVUGA1O/USJ0CAAAECBIYSUGANJatfAgQIECBAoFkBBVazUy9xAgQIECBAYCgBBdZQsvolQIAAAQIEmhVQYDU79RInQIAAAQIEhhJQYA0lq18CBAgQIECgWQEFVrNTL3ECBAgQIEBgKAEF1lCy+iVAgAABAgSaFVBgNTv1EidAgAABAgSGElBgDSWrXwIECBAgQKBZAcX+3QEAAAHASURBVAVWs1MvcQIECBAgQGAoAQXWULL6JUCAAAECBJoVUGA1O/USJ0CAAAECBIYSUGANJatfAgQIECBAoFkBBVazUy9xAgQIECBAYCgBBdZQsvolQIAAAQIEmhVQYDU79RInQIAAAQIEhhJQYA0lq18CBAgQIECgWQEFVrNTL3ECBAgQIEBgKAEF1lCy+iVAgAABAgSaFVBgNTv1EidAgAABAgSGElBgDSWrXwIECBAgQKBZAQVWs1MvcQIECBAgQGAoAQXWULL6JUCAAAECBJoVUGA1O/USJ0CAAAECBIYSUGANJatfAgQIECBAoFkBBVazUy9xAgQIECBAYCgBBdZQsvolQIAAAQIEmhVQYDU79RInQIAAAQIEhhJQYA0lq18CBAgQIECgWQEFVrNTL3ECBAgQIEBgKAEF1lCy+iVAgAABAgSaFVBgNTv1EidAgAABAgSGElBgDSWrXwIECBAgQKBZAQVWs1MvcQIECBAgQGAoAQXWULL6JUCAAAECBJoVUGA1O/USJ0CAAAECBIYSUGANJatfAgQIECBAoFkBBVazUy9xAgQIECBAYCgBBdZQsvolQIAAAQIEmhX4f2jpp0s3IfhhAAAAAElFTkSuQmCC'),
        'num_tokens': (None, f'{num_tokens}'),
    }

    response = client.post(
        f'/v2/signature/attach_signature/viverent_contract/{slug}',
        headers=headers_sign,
        files=files,
    )

    assert response.status_code == 200
    print(response.json())

    signature_data = response.json()

    signature_documents_id = signature_data['id']

    headers_buy = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'es,es-ES;q=0.8,en-US;q=0.5,en;q=0.3',
        # 'Accept-Encoding': 'gzip, deflate',
        'Content-Type': 'multipart/form-data; boundary=---------------------------323533026517141031731253097149',
        'Referer': 'http://localhost:8080/',
        'white-label-access-key': 'viverent',
        'Origin': 'http://localhost:8080',
        'DNT': '1',
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Iml2YW4ucm1naUBnbWFpbC5jb20iLCJ3aGl0ZV9sYWJlbF9hY2Nlc3Nfa2V5Ijoidml2ZXJlbnQiLCJleHAiOjE3MjY3NDYxMjF9.rgWxeclNfdnqJN--d4tLQUqHGMrwWANgnzM3e8toQSo',
        'Connection': 'keep-alive',
        'Priority': 'u=0',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }

    files = {
        'invest_id': (None, f'{invest_id}'),
        'num_tokens': (None, f'{num_tokens}'),
        'type_buy': (None, '1'),
        'signature_documents_id': (None, f'{signature_documents_id}'),
    }

    response = client.post('/v2/with_login/users/invest/buy_tokens', headers=headers_buy, files=files)

    assert response.status_code == 200
    print(response.json())

    buy_data = response.json()