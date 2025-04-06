# Vývoj aplikace pro registraci dovolených - Část 3

## Implementace reportingu
1. Vytvoření nových rout pro reporting:
   - `/reports` - Hlavní stránka reportů s přehledem dostupných reportů
   - `/reports/leave-summary` - Report se shrnutím volna zaměstnanců
   - `/reports/employee/<id>` - Detailní report o volnu konkrétního zaměstnance

2. Implementace logiky pro získání dat o volnu zaměstnanců:
   - Získání statistik pro každého zaměstnance (celkový nárok, čerpání, zbývající dovolená)
   - Rozdělení čerpání volna podle typů
   - Rozdělení čerpání volna podle měsíců

3. Vytvoření šablon pro zobrazení reportů:
   - `report/index.html` - Hlavní stránka reportů
   - `report/leave_summary.html` - Shrnutí volna zaměstnanců
   - `report/employee_detail.html` - Detail volna konkrétního zaměstnance

4. Implementace grafů pro vizualizaci dat:
   - Použití Chart.js pro vytvoření grafů
   - Graf čerpání volna podle měsíců
   - Graf čerpání volna podle typů

5. Omezení přístupu k reportům:
   - Pouze manažeři a admini mají přístup k reportům
   - Manažeři vidí pouze své podřízené
   - Admini vidí všechny zaměstnance

## Implementace kontroly překrývajících se žádostí o volno
1. Přidání metody pro kontrolu překrývajících se žádostí do modelu `LeaveRequest`:
   ```python
   @staticmethod
   def check_overlapping_leave(user_id, start_date, end_date, request_id=None):
       """Kontroluje, zda se žádost o volno nepřekrývá s existujícími žádostmi"""
       query = LeaveRequest.query.filter(
           LeaveRequest.user_id == user_id,
           LeaveRequest.status.in_([LeaveStatus.PENDING, LeaveStatus.APPROVED]),
           # Kontrola překrytí: (start1 <= end2) AND (end1 >= start2)
           LeaveRequest.start_date <= end_date,
           LeaveRequest.end_date >= start_date
       )
       
       # Pokud upravujeme existující žádost, vyloučíme ji z kontroly
       if request_id:
           query = query.filter(LeaveRequest.id != request_id)
       
       return query.all()
   ```

2. Aktualizace formuláře `LeaveRequestForm` o validaci překrývajících se žádostí:
   - Přidání metody `validate_overlapping` pro kontrolu překrývajících se žádostí
   - Přidání skrytého pole `request_id` pro případ úpravy existující žádosti

3. Úprava routy pro vytvoření žádosti o volno:
   - Volání metody `validate_overlapping` před vytvořením nové žádosti
   - Zachycení výjimky `ValidationError` a zobrazení chybové hlášky uživateli

4. Aktualizace šablony pro žádost o volno:
   - Přidání skrytého pole `request_id` do formuláře

## Úprava zobrazení v kalendáři
1. Úprava routy pro kalendář, aby nezobrazovala zamítnuté žádosti:
   ```python
   leave_requests = LeaveRequest.query.join(User, LeaveRequest.user_id == User.id).filter(
       User.manager_id == current_user.id,
       LeaveRequest.status != LeaveStatus.REJECTED
   ).all()
   ```

2. Úprava šablony kalendáře, aby zobrazovala neschválená volna jinou barvou:
   ```html
   color: '{% if request.status == "pending" %}#6c757d{% else %}{{ request.leave_type.color_code }}{% endif %}',
   ```

3. Úprava šablon pro zobrazení data a času podání žádosti:
   ```html
   <td>{{ request.created_at.strftime('%d.%m.%Y %H:%M') }}</td>
   ```

## Výhody implementovaných funkcí
1. **Reporting:**
   - Poskytuje manažerům a adminům přehledné informace o čerpání volna zaměstnanců
   - Umožňuje lépe plánovat a řídit lidské zdroje
   - Vizualizace dat pomocí grafů usnadňuje rychlé pochopení situace

2. **Kontrola překrývajících se žádostí:**
   - Zabraňuje vytvoření překrývajících se žádostí o volno
   - Zlepšuje integritu dat a usnadňuje správu volna
   - Poskytuje okamžitou zpětnou vazbu uživateli

3. **Úprava zobrazení v kalendáři:**
   - Zlepšuje přehlednost kalendáře
   - Neschválená volna jsou jasně odlišena od schválených
   - Zamítnuté žádosti nezanáší kalendář
