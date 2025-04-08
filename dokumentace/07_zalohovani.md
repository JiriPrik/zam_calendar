# Zálohování a obnova dat

## Úvod

Tato dokumentace popisuje systém zálohování a obnovy dat v aplikaci. Systém umožňuje vytvářet zálohy databáze, obnovovat data ze zálohy a spravovat existující zálohy.

## Funkce zálohování

### Vytvoření zálohy

Aplikace umožňuje vytvářet zálohy databáze. Zálohy jsou ukládány do adresáře `backups` v kořenovém adresáři aplikace. Každá záloha obsahuje:

- Soubor databáze (`.db`) - obsahuje všechna data aplikace
- Soubor metadat (`.json`) - obsahuje informace o záloze (čas vytvoření, velikost, atd.)

Zálohy jsou pojmenovány podle data a času vytvoření ve formátu `backup_YYYYMMDD_HHMMSS.db`.

### Stažení zálohy

Uživatel může stáhnout zálohu do svého počítače kliknutím na tlačítko "Stáhnout" u příslušné zálohy. Záloha je stažena jako soubor databáze.

### Obnovení ze zálohy

Aplikace umožňuje obnovit data ze zálohy. Obnovení probíhá následujícím způsobem:
- Uživatel vybere zálohu, ze které chce obnovit data.
- uživatel zkopíruje soubor databáze zálohy do adresáře `instance` aplikace.
- uživatel ukončí aplikaci
- uživatel smaže původní soubor databáze "app.db" 
- uživatel přejmenuje zálohu na "app.db"
- uživatel spustí aplikaci.


## Technické detaily

### Struktura adresářů

- `backups/` - adresář obsahující všechny zálohy
 
### Implementace

Zálohování je implementováno v následujících souborech:

- `app/routes/backup.py` - obsahuje routy pro zálohování, obnovení a správu záloh
- `app/utils/backup.py` - obsahuje pomocné funkce pro zálohování a obnovu
- `app/templates/settings/backup.html` - obsahuje šablonu pro stránku zálohování

### Funkce pro zálohování

- `backup_database()` - vytvoří zálohu databáze
- `get_backups()` - získá seznam všech záloh

## Doporučení pro správu záloh

1. Pravidelně vytvářejte zálohy, zejména před důležitými změnami v aplikaci.
2. Uchovávejte zálohy na více místech (lokálně, v cloudu, atd.).
3. Pravidelně testujte obnovení ze zálohy, abyste se ujistili, že proces funguje správně.
4. Staré a nepotřebné zálohy pravidelně mažte, aby nezabíraly zbytečně místo.

## Řešení problémů

### Záloha se nevytvoří

1. Zkontrolujte, zda má aplikace práva pro zápis do adresáře `backups`.
2. Zkontrolujte, zda je dostatek místa na disku.
3. Zkontrolujte logy aplikace pro případné chybové zprávy.

### Nelze obnovit ze zálohy

1. Zkontrolujte, zda soubor zálohy existuje a není poškozen.
2. Zkontrolujte, zda má aplikace práva pro čtení souboru zálohy.
3. Zkontrolujte logy aplikace pro případné chybové zprávy.

### Nelze smazat zálohu

1. Zkontrolujte, zda je dostatek místa na disku.
2. Zkontrolujte logy aplikace pro případné chybové zprávy.
