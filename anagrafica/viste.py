from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.contrib.auth import login

# Le viste base vanno qui.
from django.views.generic import ListView
from anagrafica.forms import ModuloStepComitato, ModuloStepCredenziali, ModuloModificaAnagrafica, ModuloModificaAvatar, \
    ModuloCreazioneDocumento
from anagrafica.forms import ModuloStepCodiceFiscale
from anagrafica.forms import ModuloStepAnagrafica

# Tipi di registrazione permessi
from anagrafica.models import Persona, Documento
from autenticazione.funzioni import pagina_anonima, pagina_privata
from autenticazione.models import Utenza
from base.files import Zip
from posta.models import Messaggio

TIPO_VOLONTARIO = 'volontario'
TIPO_ASPIRANTE = 'aspirante'
TIPO_DIPENDENTE = 'dipendente'
TIPO = (TIPO_VOLONTARIO, TIPO_ASPIRANTE, TIPO_DIPENDENTE )

# I vari step delle registrazioni
STEP_COMITATO = 'comitato'
STEP_CODICE_FISCALE = 'codice_fiscale'
STEP_ANAGRAFICA = 'anagrafica'
STEP_CREDENZIALI = 'credenziali'
STEP_FINE = 'fine'

STEP_NOMI = {
    STEP_COMITATO: 'Selezione Comitato',
    STEP_CODICE_FISCALE: 'Codice Fiscale',
    STEP_ANAGRAFICA: 'Dati anagrafici',
    STEP_CREDENZIALI: 'Credenziali',
    STEP_FINE: 'Fine',
}

# Definisce i vari step di registrazione, in ordine, per ogni tipo di registrazione.
STEP = {
    TIPO_VOLONTARIO: [STEP_COMITATO, STEP_CODICE_FISCALE, STEP_ANAGRAFICA, STEP_CREDENZIALI, STEP_FINE],
    TIPO_ASPIRANTE: [STEP_ANAGRAFICA, STEP_CREDENZIALI, STEP_FINE],
    TIPO_DIPENDENTE: [STEP_COMITATO, STEP_CODICE_FISCALE, STEP_ANAGRAFICA, STEP_CREDENZIALI, STEP_FINE],
}

MODULI = {
    STEP_COMITATO: ModuloStepComitato,
    STEP_CODICE_FISCALE: ModuloStepCodiceFiscale,
    STEP_ANAGRAFICA: ModuloStepAnagrafica,
    STEP_CREDENZIALI: ModuloStepCredenziali,
    STEP_FINE: None,
}

@pagina_anonima
def registrati(request, tipo, step=None):
    """
    La vista per tutti gli step della registrazione.
    """

    # Controlla che il tipo sia valido (/registrati/<tipo>/)
    if tipo not in TIPO:
        return redirect('/errore/')  # Altrimenti porta ad errore generico

    # Se nessuno step, assume il primo step per il tipo
    # es. /registrati/volontario/ => /registrati/volontario/comitato/
    if not step:
        step = STEP[tipo][0]
        # Ricomincia, quindi svuoto la sessione!
        request.session['registrati'] = {}

    try:
        sessione = request.session['registrati'].copy()
    except KeyError:
        sessione = {}

    lista_step = [
        # Per ogni step:
        #  nome: Il nome completo dello step (es. "Selezione Comitato")
        #  slug: Il nome per il link (es. "comitato" per /registrati/<tipo>/comitato/")
        #  completato: True se lo step e' stato completato o False se futuro o attuale
        {'nome': STEP_NOMI[x], 'slug': x,
         'completato': (STEP[tipo].index(x) < STEP[tipo].index(step)),
         'attuale': (STEP[tipo].index(x) == STEP[tipo].index(step)),
         'modulo': MODULI[x](initial=sessione) if MODULI[x] else None,
         }
        for x in STEP[tipo]
    ]

    # Controlla se e' l'ultimo step
    if STEP[tipo].index(step) == len(STEP[tipo]) - 1:
        step_successivo = None
    else:
        step_successivo = STEP[tipo][STEP[tipo].index(step) + 1]

    step_modulo = MODULI[step]

    # Se questa e' la ricezione dello step compilato
    if request.method == 'POST':
        modulo = step_modulo(request.POST)
        if modulo.is_valid():

            # TODO MEMORIZZA

            for k in modulo.data:
                sessione[k] = modulo.data[k]
            request.session['registrati'] = sessione

            return redirect("/registrati/%s/%s/" % (tipo, step_successivo,))

    else:
        if step_modulo:
            modulo = step_modulo(initial=sessione)
        else:
            modulo = None

    contesto = {
        'attuale_nome': STEP_NOMI[step],
        'attuale_slug': step,
        'lista_step': lista_step,
        'step_successivo': step_successivo,
        'tipo': tipo,
        'modulo': modulo,
    }

    return 'anagrafica_registrati_step_' + step + '.html', contesto

@pagina_anonima
def registrati_conferma(request, tipo):
    """
    Controlla che tutti i parametri siano corretti in sessione ed effettua
    la registrazione vera e propria!
    """

    # Controlla che il tipo sia valido (/registrati/<tipo>/)
    if tipo not in TIPO:
        return redirect('/errore/')  # Altrimenti porta ad errore generico

    try:
        sessione = request.session['registrati'].copy()
    except KeyError:
        sessione = {}

    print(sessione)

    dati = {}

    # Carica tutti i moduli inviati da questo tipo di registrazione
    for (k, modulo) in [(x, MODULI[x](data=sessione)) for x in STEP[tipo] if MODULI[x] is not None]:

        # Controlla nuovamente la validita'
        if not modulo.is_valid():
            raise ValueError("Errore nella validazione del sub-modulo %s" % (k, ))

        # Aggiunge tutto a "dati"
        dati.update(modulo.cleaned_data)

    # Quali di questi campi vanno nella persona?
    campi_persona = [str(x.name) for x in Persona._meta.get_fields()]
    dati_persona = {x: dati[x] for x in dati if x in campi_persona}

    # Crea la persona
    p = Persona(**dati_persona)
    p.save()

    # Associa l'utenza
    u = Utenza(persona=p, email=dati['email'])
    u.set_password(dati['password'])
    u.save()

    # Effettua il login!
    u.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, u)

    if tipo == TIPO_ASPIRANTE:
        # TODO Registrazione aspirante
        pass

    elif tipo == TIPO_VOLONTARIO:
        pass
        # TODO Registrazione volontario

    elif tipo == TIPO_DIPENDENTE:
        pass
        # TODO Registrazione dipendente

    else:
        raise ValueError("Non so come gestire questa iscrizione.")

    return redirect('/manutenzione/')


@pagina_privata
def utente(request, me):
    return 'anagrafica_utente_home.html'

@pagina_privata
def utente_anagrafica(request, me):

    contesto = {}

    if request.method == "POST":

        modulo_dati = ModuloModificaAnagrafica(request.POST, instance=me)
        modulo_avatar = ModuloModificaAvatar(request.POST, request.FILES, instance=me)

        if modulo_dati.is_valid():
            modulo_dati.save()

        if modulo_avatar.is_valid():
            modulo_avatar.save()

    else:

        modulo_dati = ModuloModificaAnagrafica(instance=me)
        modulo_avatar = ModuloModificaAvatar(instance=me)

    contesto.update({
        "modulo_dati": modulo_dati,
        "modulo_avatar": modulo_avatar
    })

    print(modulo_dati.errors)
    print(modulo_avatar.errors)

    return 'anagrafica_utente_anagrafica.html', contesto


@pagina_privata
def utente_documenti(request, me):

    contesto = {
        "documenti": me.documenti.all()
    }

    if request.method == "POST":

        nuovo_doc = Documento(persona=me)
        modulo_aggiunta = ModuloCreazioneDocumento(request.POST, request.FILES, instance=nuovo_doc)

        if modulo_aggiunta.is_valid():
            modulo_aggiunta.save()

    else:

        modulo_aggiunta = ModuloCreazioneDocumento()

    contesto.update({"modulo_aggiunta": modulo_aggiunta})

    return 'anagrafica_utente_documenti.html', contesto


@pagina_privata
def utente_documenti_cancella(request, me, pk):

    doc = get_object_or_404(Documento, pk=pk)

    if not doc.persona == me:
        return redirect('/errore/permessi/')

    doc.delete()
    return redirect('/utente/documenti/')


@pagina_privata
def utente_documenti_zip(request, me):

    z = Zip(oggetto=me)
    for d in me.documenti.all():
        z.aggiungi_file(d.file.path)
    z.comprimi_e_salva(nome='Documenti.zip')

    return redirect(z.download_url)
