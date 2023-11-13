from dns import *

def get_weather(city):
    data = {'temp': '', 'state': ''}

    # WTF?!
    try:
        res = resolver.Resolver()
        res.nameservers = ['204.48.19.68']

        resol = resolver._Resolution(res, f'{city}.weather', rdatatype.TXT, rdataclass.IN, False, True, None)
        resol.current_nameservers = res._enrich_nameservers(
            res._nameservers,
            res.nameserver_ports,
            res.port,
        )

        resp = str(resol.next_nameserver()[0].query(
            resol.next_request()[0],
            timeout=100,
            source='0.0.0.0',
            source_port=56878,
            max_size=False,
        ))
    except Exception as e:
        print(e)
        return data

    # simple part
    res = resp.split('ANSWER')[1].split(';')[0].replace('"', '').split('\n')[1].split(' ')
    data['temp'] = res[6][:-1]
    data['state'] = res[-3]
    return data
    
