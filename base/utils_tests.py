import random
import string

import names

from anagrafica.costanti import LOCALE
from anagrafica.models import Persona, Sede, Appartenenza, Delega
from anagrafica.permessi.applicazioni import PRESIDENTE
from attivita.models import Area


def codice_fiscale(length=16):
   return ''.join(random.choice(string.lowercase) for i in range(length))

def crea_persona():
    p = Persona(
        nome=names.get_first_name(),
        cognome=names.last_name(),
        codice_fiscale=codice_fiscale(),
        data_nascita="1994-2-5"
    )
    p.save()
    return p

def crea_sede(presidente=None, genitore=None):
    s = Sede(
        nome="Comitato Regionale di Sicilia",
        tipo=Sede.COMITATO,
        estensione=LOCALE,
        genitore=genitore,
    )
    s.save()
    if presidente is not None:
        d = Delega(
            inizio="1980-12-10",
            persona=presidente,
            tipo=PRESIDENTE,
            oggetto=s
        )
        d.save()
    return s


def crea_appartenenza(persona, sede):
    app = Appartenenza(
        persona=persona,
        sede=sede,
        membro=Appartenenza.VOLONTARIO,
        inizio="1980-12-10",
    )
    app.save()
    return app


def crea_persona_sede_appartenenza(presidente=None):
    p = crea_persona()
    s = crea_sede(presidente)
    a = crea_appartenenza(p, s)
    return p, s, a


def crea_area(sede):
    area = Area(
        nome="6",
        obiettivo=6,
        sede=sede,
    )
    area.save()
    return area
