# Prozess-Erschöpfung Fixes - Übersicht

## Problem
`BlockingIOError: [Errno 11] Resource temporarily unavailable` trat auf, weil:
1. Der Thread-Timeout-Mechanismus in `main.py` Threads nicht beenden konnte
2. Playwright-Browser-Prozesse als Zombies zurückblieben
3. Container-Ressourcen (PIDs, Memory) erschöpft waren

## Angewendete Fixes

### 1. Thread-Timeout-Mechanismus entfernt (`main.py`)
- **Problem**: Python kann Threads nicht forcieren, daher blieben blockierte Threads aktiv
- **Lösung**: Timeout-Wrapper entfernt, native Playwright-Timeouts in Tests nutzen
- **Vorteil**: Keine hängenden Threads mehr, die Ressourcen blockieren

### 2. Robustes Playwright Cleanup (`monitor_base.py`)
- **Problem**: Wenn `teardown()` fehlschlug, blieben Browser-Prozesse offen
- **Lösung**: Jeder Cleanup-Step mit Try-Except umhüllt, erzwungene Reference-Cleanup
- **Vorteil**: Selbst bei Fehlern werden Ressourcen freigegeben

### 3. Container-Ressourcen erhöht (`docker-compose.yml`)
- **Hinzugefügt**:
  - `mem_limit: 2g` - 2 GB Memory-Limit
  - `memswap_limit: 2g` - Swap-Limit
  - `pids_limit: 512` - Max. 512 Prozesse (statt Standard 100)
  - `shm_size: 512m` - Shared Memory für Chromium
- **Vorteil**: Mehr Spielraum für parallele Browser-Instanzen

### 4. Automatisches Zombie-Process-Cleanup
- **Neue Dateien**:
  - `cleanup_processes.sh` - Findet und killt Browser-Prozesse älter als 10 Minuten
  - `entrypoint.sh` - Startet Cleanup-Loop (alle 10 Min) + Hauptapplikation
- **Dockerfile**: `procps` installiert für `ps`-Kommando, Scripts executable gemacht
- **Vorteil**: Selbst wenn Prozesse hängen bleiben, werden sie automatisch aufgeräumt

## Deployment

### Rebuild & Restart erforderlich:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Logs prüfen:
```bash
docker-compose logs -f monitor-app
```

### Prozess-Cleanup manuell testen (im Container):
```bash
docker exec -it web-monitor-app /app/cleanup_processes.sh
```

## Erwartetes Verhalten nach Fix
- Keine `BlockingIOError` mehr
- Browser-Prozesse werden ordnungsgemäß beendet
- Bei hängenden Tests: Automatisches Cleanup nach 10 Minuten
- Logs zeigen Cleanup-Aktivität alle 10 Minuten

## Monitoring
Prüfen Sie nach Deployment:
1. Keine `Resource temporarily unavailable` Fehler in Logs
2. `docker stats web-monitor-app` - Memory/PID-Usage stabil
3. `docker exec web-monitor-app ps aux | grep chromium` - Keine alten Prozesse
