# emiter-nextcloud-api
 Mikroserwis do integracji api emitera z kalendarzem w Nextcloud

## Działanie

Usługa pobiera dane z kalendarza Nextclouda (lub innego wspierającego CalDAV) i przetwarza go na API emiterowe, które to hostuje.

Przy zapytaniu do API program odpytuje CalDAV w poszukiwaniu kalendarzy `emiter_audycje` i `emiter_powtorki`, do którego edycji ma dostęp RedProg i administracja. System zawsze "patrzy" na 7 następnych dni w kalendarzu od dnia dzisiejszego. Na podstawie nazwy wpisu (*summary*) określa kod (slug) audycji i przypisaną jej godzinę audycji na żywo/powtórki. Dodatkowo z danaych wpisu w kalendarzu audycjcji na żywo pobierane są:

* Nazwa audycji - z pola *description*
* RDS - z pola *Location*

Aby nie zapychać API CalDAV, dane są zapamiętywane domyślnie na 30 minut

#### Not bugs, but features....

* Można dodawać audycje co 2 tygodnie, co miesiąc itd.
* Można dodawać jednorazowe audycje, ale żeby nie robić syfu w Emiterze, warto dawać audycjom specjalnym w jednym cyklu dawać te same nazwy np. jeśli jest RA Studyjnie to za każdym razem Slug może nazywać się *koncert* albo *rastudyjnie*
* Audycja może kończyć się po północy następnego dnia (jak *Czwarty Wymiar*)
* Można zrobić wiele tych samych audycji w tygodniu o różnych porach dnia.
* Można zrobić wiele powtórek tej samej audycji w tygodniu - za każdym razem poleci powtórka ostatniej audycji na żywo, jeśli w ramach slotu takowa się odbyła.
* **Proszę nie nakładać audycji na siebie** - Emiter nie przewidział takiego zachowania i w skrajnym przypadku może to skraszować całą emisję!

## Konfiguracja

Konfiguracja poprzedzać musi uruchomienie kontenera

```
cp config.py.example.py config.py
nano config.py
```

W config.py ustawiamy usera i hasło z nextclouda. User musi być ownerem kalendarzy `emiter_audycje` i `emiter_powtorki`

## Uruchomienie

**Docker**

Jest Dockerfile, więc odpalenie API w kontenerze sprowadzi się do buildu kontenera...

```
docker build -t raktywne/calapi:1.0 .
```

...i odpalenia kontenera:

```
docker run -dt -p 8000:8000 --name calapi raktywne/calapi:1.0
```

Kontener nadaje na porcie 8000, który możemy przekierować poprzez odpowiednią modyfikację argumentu `-p PORT:8000`

**W systemie (ale nie w tle)**

Przed odpaleniem upewnij się czy masz wszystkie pakiety:

```
pip3 install fastapi uvicorn caldav icalendar
```

Uruchamiamy API poleceniem:
```
uvicorn main:app --host 0.0.0.0 --port 8000
```
