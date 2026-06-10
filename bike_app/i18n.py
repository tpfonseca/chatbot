"""Translations for every user-facing string.

English is the source of truth: any key missing from another language
falls back to English at runtime, and the test suite asserts all
languages ship the same key set. The selected language lives in
st.session_state["lang"], initialized from the ?lang= query param so
shared links open in the sender's language.
"""

import streamlit as st

DEFAULT_LANG = "en"
LANGUAGES = {
    "en": "English",
    "sv": "Svenska",
    "da": "Dansk",
    "no": "Norsk",
}

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "tagline": "Know it's not stolen. In seconds.",
        "stats": "{n} verified report(s) in the database.",
        "search_placeholder": "Type the frame serial and press Enter",
        "try_demo": "Try a demo serial",
        "serial_help_title": "Where do I find the serial?",
        "serial_help_body": (
            "The serial number is etched onto the bike frame. The most common spot "
            "is **under the bottom bracket** — flip the bike over and look at the "
            "joint where the pedals attach. It can also be on the **seat tube**, "
            "the **head tube**, or near the **rear wheel mount**. Numbers and "
            "letters only; spaces and dashes are ignored when we search."
        ),
        "no_reports_title": "No reports found.",
        "no_reports_body": (
            "That's a good sign — but it doesn't guarantee the bike isn't stolen. "
            "Many thefts are never reported here."
        ),
        "stolen_banner": "This bike has been reported stolen ({n} report(s)).",
        "dont_buy_title": "Don't buy this bike.",
        "advisory_home_body": (
            "Contact your local police and, if you can, keep a record of the "
            "seller's details. Buying a bike you believe was stolen can be a "
            "crime in your jurisdiction."
        ),
        "advisory_landing_body": (
            "Even though the seller shared a check link, this serial is now "
            "flagged as stolen. Contact your local police."
        ),
        "selling_title": "Selling this bike?",
        "selling_caption": (
            "Add proof to your listing — buyers trust it, and your bike sells faster."
        ),
        "badge_png": "Badge PNG",
        "selling_explainer": (
            "Paste the link into your listing, or download the badge image "
            "(with QR code) to upload as a photo. When a buyer clicks the "
            "link or scans the QR, we re-check the serial live."
        ),
        "tile_report_title": "Report a stolen bike",
        "tile_report_body": (
            "Tell future buyers it's gone, so no one buys your bike from the thief."
        ),
        "tile_report_cta": "Start →",
        "tile_recover_title": "Mark a bike as recovered",
        "tile_recover_body": (
            "Got your bike back? Take down your warning so future searches stay accurate."
        ),
        "tile_recover_cta": "Open →",
        "how_title": "How it works",
        "how_body": (
            "**Search.** Type a frame serial. We match it against verified reports — "
            "spaces, dashes, and casing are ignored.\n\n"
            "**Report.** Submit your serial and email. Click the link we send you and "
            "your report goes live.\n\n"
            "**Recover.** Got your bike back? Take your report down with the same "
            "serial and email."
        ),
        "disclaimer": (
            "A prototype. Reports are user-submitted and not a substitute "
            "for a police report or an official registry."
        ),
        "badge_reported_stolen": "Reported stolen",
        "unknown_bike": "Unknown bike",
        "serial_word": "Serial",
        "stolen_word": "Stolen",
        "in_word": "in",
        "view_on_map": "View on map ↗",
        "reported_on": "Reported on",
        "back": "← Back",
        "report_header_body": (
            "Tell us about it. We'll warn the next buyer. "
            "Your email stays private — we only use it to verify the report."
        ),
        "label_serial": "Serial number",
        "label_brand": "Brand",
        "label_model": "Model",
        "label_color": "Color",
        "label_theft_date": "Theft date",
        "label_theft_location": "Theft location",
        "label_email": "Email",
        "label_photo": "Photo",
        "required_tag": "Required",
        "ph_serial": "Frame serial number",
        "ph_color": "Matte black",
        "ph_email": "you@example.com",
        "ph_location_text": "City, neighborhood",
        "ph_location_search": "Start typing…",
        "location_caption": (
            "Start typing a city, area, or street. We fetch real geo data so the "
            "report shows up in the right place."
        ),
        "adjust_pin": "Adjust the pin on a map",
        "move_pin_tooltip": "Click anywhere on the map to move the pin",
        "email_help": "Used to verify the report and contact you on a match.",
        "submit_report": "Submit report",
        "err_required": "Serial number and email are required.",
        "err_email": "That email doesn't look right.",
        "success_dev": (
            "Report submitted. Email delivery is in dev mode — "
            "this is the link we'd send to {email}."
        ),
        "open_verify_link": "Open verification link →",
        "success_sent": (
            "Report submitted. We sent a verification link to {email}. "
            "Click it to make your report live."
        ),
        "warn_send_failed": (
            "Report submitted, but the verification email failed to send ({err}). "
            "Check server logs."
        ),
        "recover_caption": (
            "We'll take your report down so future searches don't show a false "
            "warning. We match on the serial and the email you used to report it."
        ),
        "recover_email_label": "Email used in the original report",
        "recover_checkbox": "Yes, I have my bike back. Take the warning down.",
        "recover_submit": "Mark recovered",
        "recover_success": (
            "Marked as recovered. The report no longer appears in searches."
        ),
        "recover_error": (
            "Couldn't find a verified report matching that serial and email. "
            "Double-check both, or contact us if your bike is still listed."
        ),
        "landing_clean_title": "No reports for this bike.",
        "landing_clean_body": (
            "Serial {serial} doesn't match any reported-stolen bike in our database."
        ),
        "seller_posted": "Seller posted this check on {date}.",
        "heads_up": (
            "**Heads up.** This means the serial isn't on our list — it does "
            "not prove the seller owns the bike. When you meet, check the "
            "serial on the badge matches the serial etched on the frame."
        ),
        "check_another": "Check another bike",
        "bike_word": "Bike",
        "stolen_on": "Stolen on",
        "stolen_in": "Stolen in",
        "verify_ok": "Report verified. It will now appear in searches.",
        "verify_bad": "This verification link is invalid or has already been used.",
        "back_home": "Back to homepage",
        "badge_checked": "Checked {date} — no theft reports.",
        "badge_scan": "Scan or visit the URL to verify live.",
        "email_subject": "Verify your stolen bike report",
        "email_body": (
            "Thanks for submitting a stolen bike report.\n\n"
            "Click the link below to verify your report so it appears in searches:\n\n"
            "{link}\n\n"
            "If you didn't submit this, you can ignore this email."
        ),
    },
    "sv": {
        "tagline": "Vet att den inte är stulen. På några sekunder.",
        "stats": "{n} verifierad(e) rapport(er) i databasen.",
        "search_placeholder": "Skriv ramnumret och tryck Enter",
        "try_demo": "Prova ett demo-ramnummer",
        "serial_help_title": "Var hittar jag ramnumret?",
        "serial_help_body": (
            "Ramnumret är ingraverat i cykelramen. Den vanligaste platsen är "
            "**under vevlagret** — vänd cykeln upp och ner och titta vid leden "
            "där pedalerna sitter. Det kan också finnas på **sadelröret**, "
            "**styrröret** eller nära **bakhjulsfästet**. Endast siffror och "
            "bokstäver; mellanslag och bindestreck ignoreras när vi söker."
        ),
        "no_reports_title": "Inga rapporter hittades.",
        "no_reports_body": (
            "Det är ett gott tecken — men det garanterar inte att cykeln inte är "
            "stulen. Många stölder rapporteras aldrig här."
        ),
        "stolen_banner": "Den här cykeln har rapporterats stulen ({n} rapport(er)).",
        "dont_buy_title": "Köp inte den här cykeln.",
        "advisory_home_body": (
            "Kontakta polisen och spara om möjligt säljarens uppgifter. "
            "Att köpa en cykel du tror är stulen kan vara ett brott."
        ),
        "advisory_landing_body": (
            "Även om säljaren delade en kontrollänk är det här ramnumret nu "
            "flaggat som stulet. Kontakta polisen."
        ),
        "selling_title": "Säljer du den här cykeln?",
        "selling_caption": (
            "Lägg till bevis i din annons — köpare litar på det, "
            "och cykeln säljs snabbare."
        ),
        "badge_png": "Badge (PNG)",
        "selling_explainer": (
            "Klistra in länken i din annons, eller ladda ner badge-bilden "
            "(med QR-kod) och lägg upp den som ett foto. När en köpare klickar "
            "på länken eller skannar QR-koden kontrollerar vi ramnumret på nytt "
            "i realtid."
        ),
        "tile_report_title": "Rapportera en stulen cykel",
        "tile_report_body": (
            "Berätta för framtida köpare att den är borta, så att ingen köper "
            "din cykel av tjuven."
        ),
        "tile_report_cta": "Starta →",
        "tile_recover_title": "Markera en cykel som återfunnen",
        "tile_recover_body": (
            "Fått tillbaka cykeln? Ta bort varningen så att framtida sökningar stämmer."
        ),
        "tile_recover_cta": "Öppna →",
        "how_title": "Så fungerar det",
        "how_body": (
            "**Sök.** Skriv ett ramnummer. Vi matchar det mot verifierade rapporter — "
            "mellanslag, bindestreck och versaler ignoreras.\n\n"
            "**Rapportera.** Skicka in ramnummer och e-post. Klicka på länken vi "
            "skickar så blir rapporten synlig.\n\n"
            "**Återfunnen.** Fått tillbaka cykeln? Ta bort rapporten med samma "
            "ramnummer och e-post."
        ),
        "disclaimer": (
            "En prototyp. Rapporterna är inskickade av användare och ersätter inte "
            "en polisanmälan eller ett officiellt register."
        ),
        "badge_reported_stolen": "Rapporterad stulen",
        "unknown_bike": "Okänd cykel",
        "serial_word": "Ramnummer",
        "stolen_word": "Stulen",
        "in_word": "i",
        "view_on_map": "Visa på karta ↗",
        "reported_on": "Rapporterad",
        "back": "← Tillbaka",
        "report_header_body": (
            "Berätta för oss. Vi varnar nästa köpare. Din e-post förblir privat — "
            "vi använder den bara för att verifiera rapporten."
        ),
        "label_serial": "Ramnummer",
        "label_brand": "Märke",
        "label_model": "Modell",
        "label_color": "Färg",
        "label_theft_date": "Stölddatum",
        "label_theft_location": "Stöldplats",
        "label_email": "E-post",
        "label_photo": "Foto",
        "required_tag": "Obligatoriskt",
        "ph_serial": "Cykelns ramnummer",
        "ph_color": "Mattsvart",
        "ph_email": "du@exempel.com",
        "ph_location_text": "Stad, stadsdel",
        "ph_location_search": "Börja skriva…",
        "location_caption": (
            "Börja skriva en stad, ett område eller en gata. Vi hämtar riktig "
            "geodata så att rapporten hamnar på rätt plats."
        ),
        "adjust_pin": "Justera nålen på en karta",
        "move_pin_tooltip": "Klicka var som helst på kartan för att flytta nålen",
        "email_help": "Används för att verifiera rapporten och kontakta dig vid en träff.",
        "submit_report": "Skicka rapport",
        "err_required": "Ramnummer och e-post krävs.",
        "err_email": "Den e-postadressen ser inte rätt ut.",
        "success_dev": (
            "Rapporten har skickats. E-postleverans är i utvecklingsläge — "
            "det här är länken vi skulle skicka till {email}."
        ),
        "open_verify_link": "Öppna verifieringslänken →",
        "success_sent": (
            "Rapporten har skickats. Vi har skickat en verifieringslänk till {email}. "
            "Klicka på den för att aktivera rapporten."
        ),
        "warn_send_failed": (
            "Rapporten har skickats, men verifieringsmejlet kunde inte skickas "
            "({err}). Kontrollera serverloggarna."
        ),
        "recover_caption": (
            "Vi tar bort din rapport så att framtida sökningar inte visar en falsk "
            "varning. Vi matchar på ramnumret och e-postadressen du använde i rapporten."
        ),
        "recover_email_label": "E-post som användes i den ursprungliga rapporten",
        "recover_checkbox": "Ja, jag har fått tillbaka min cykel. Ta bort varningen.",
        "recover_submit": "Markera som återfunnen",
        "recover_success": (
            "Markerad som återfunnen. Rapporten visas inte längre i sökningar."
        ),
        "recover_error": (
            "Hittade ingen verifierad rapport som matchar det ramnumret och den "
            "e-postadressen. Dubbelkolla båda, eller kontakta oss om din cykel "
            "fortfarande är listad."
        ),
        "landing_clean_title": "Inga rapporter för den här cykeln.",
        "landing_clean_body": (
            "Ramnummer {serial} matchar ingen cykel som rapporterats stulen i vår databas."
        ),
        "seller_posted": "Säljaren publicerade den här kontrollen den {date}.",
        "heads_up": (
            "**Obs!** Det betyder att ramnumret inte finns på vår lista — det "
            "bevisar inte att säljaren äger cykeln. När ni ses, kontrollera att "
            "ramnumret på märket stämmer med numret på ramen."
        ),
        "check_another": "Kontrollera en annan cykel",
        "bike_word": "Cykel",
        "stolen_on": "Stulen den",
        "stolen_in": "Stulen i",
        "verify_ok": "Rapporten är verifierad. Den visas nu i sökningar.",
        "verify_bad": "Verifieringslänken är ogiltig eller har redan använts.",
        "back_home": "Tillbaka till startsidan",
        "badge_checked": "Kontrollerad {date} — inga stöldrapporter.",
        "badge_scan": "Skanna eller besök länken för att verifiera live.",
        "email_subject": "Verifiera din stöldanmälan",
        "email_body": (
            "Tack för att du rapporterade en stulen cykel.\n\n"
            "Klicka på länken nedan för att verifiera din rapport så att den "
            "visas i sökningar:\n\n"
            "{link}\n\n"
            "Om du inte skickade in detta kan du ignorera det här mejlet."
        ),
    },
    "da": {
        "tagline": "Vid, at den ikke er stjålet. På få sekunder.",
        "stats": "{n} verificerede anmeldelse(r) i databasen.",
        "search_placeholder": "Indtast stelnummeret og tryk Enter",
        "try_demo": "Prøv et demo-stelnummer",
        "serial_help_title": "Hvor finder jeg stelnummeret?",
        "serial_help_body": (
            "Stelnummeret er præget i cykelstellet. Det mest almindelige sted er "
            "**under krankboksen** — vend cyklen om og se ved samlingen, hvor "
            "pedalerne sidder. Det kan også stå på **sadelrøret**, **kronrøret** "
            "eller nær **baghjulsophænget**. Kun tal og bogstaver; mellemrum og "
            "bindestreger ignoreres, når vi søger."
        ),
        "no_reports_title": "Ingen anmeldelser fundet.",
        "no_reports_body": (
            "Det er et godt tegn — men det garanterer ikke, at cyklen ikke er "
            "stjålet. Mange tyverier bliver aldrig anmeldt her."
        ),
        "stolen_banner": "Denne cykel er anmeldt stjålet ({n} anmeldelse(r)).",
        "dont_buy_title": "Køb ikke denne cykel.",
        "advisory_home_body": (
            "Kontakt politiet, og gem om muligt sælgerens oplysninger. "
            "At købe en cykel, du tror er stjålet, kan være strafbart."
        ),
        "advisory_landing_body": (
            "Selvom sælgeren delte et kontrollink, er dette stelnummer nu "
            "markeret som stjålet. Kontakt politiet."
        ),
        "selling_title": "Sælger du denne cykel?",
        "selling_caption": (
            "Tilføj dokumentation til din annonce — købere stoler på det, "
            "og din cykel sælges hurtigere."
        ),
        "badge_png": "Badge (PNG)",
        "selling_explainer": (
            "Indsæt linket i din annonce, eller download badge-billedet "
            "(med QR-kode) og upload det som et foto. Når en køber klikker på "
            "linket eller scanner QR-koden, tjekker vi stelnummeret live igen."
        ),
        "tile_report_title": "Anmeld en stjålet cykel",
        "tile_report_body": (
            "Fortæl fremtidige købere, at den er væk, så ingen køber din cykel af tyven."
        ),
        "tile_report_cta": "Start →",
        "tile_recover_title": "Markér en cykel som fundet",
        "tile_recover_body": (
            "Har du fået din cykel tilbage? Fjern advarslen, så fremtidige "
            "søgninger er korrekte."
        ),
        "tile_recover_cta": "Åbn →",
        "how_title": "Sådan fungerer det",
        "how_body": (
            "**Søg.** Indtast et stelnummer. Vi matcher det mod verificerede "
            "anmeldelser — mellemrum, bindestreger og store/små bogstaver "
            "ignoreres.\n\n"
            "**Anmeld.** Indsend stelnummer og e-mail. Klik på linket, vi sender, "
            "og din anmeldelse bliver synlig.\n\n"
            "**Fundet.** Har du fået cyklen tilbage? Fjern anmeldelsen med samme "
            "stelnummer og e-mail."
        ),
        "disclaimer": (
            "En prototype. Anmeldelser er indsendt af brugere og erstatter ikke "
            "en politianmeldelse eller et officielt register."
        ),
        "badge_reported_stolen": "Anmeldt stjålet",
        "unknown_bike": "Ukendt cykel",
        "serial_word": "Stelnummer",
        "stolen_word": "Stjålet",
        "in_word": "i",
        "view_on_map": "Se på kort ↗",
        "reported_on": "Anmeldt",
        "back": "← Tilbage",
        "report_header_body": (
            "Fortæl os om det. Vi advarer den næste køber. Din e-mail forbliver "
            "privat — vi bruger den kun til at verificere anmeldelsen."
        ),
        "label_serial": "Stelnummer",
        "label_brand": "Mærke",
        "label_model": "Model",
        "label_color": "Farve",
        "label_theft_date": "Tyveridato",
        "label_theft_location": "Tyveristed",
        "label_email": "E-mail",
        "label_photo": "Foto",
        "required_tag": "Påkrævet",
        "ph_serial": "Cyklens stelnummer",
        "ph_color": "Matsort",
        "ph_email": "dig@eksempel.com",
        "ph_location_text": "By, kvarter",
        "ph_location_search": "Begynd at skrive…",
        "location_caption": (
            "Begynd at skrive en by, et område eller en gade. Vi henter rigtige "
            "geodata, så anmeldelsen vises det rigtige sted."
        ),
        "adjust_pin": "Justér nålen på et kort",
        "move_pin_tooltip": "Klik hvor som helst på kortet for at flytte nålen",
        "email_help": "Bruges til at verificere anmeldelsen og kontakte dig ved et match.",
        "submit_report": "Indsend anmeldelse",
        "err_required": "Stelnummer og e-mail er påkrævet.",
        "err_email": "Den e-mailadresse ser ikke rigtig ud.",
        "success_dev": (
            "Anmeldelsen er indsendt. E-mail-levering er i udviklingstilstand — "
            "dette er linket, vi ville sende til {email}."
        ),
        "open_verify_link": "Åbn bekræftelseslinket →",
        "success_sent": (
            "Anmeldelsen er indsendt. Vi har sendt et bekræftelseslink til {email}. "
            "Klik på det for at gøre din anmeldelse aktiv."
        ),
        "warn_send_failed": (
            "Anmeldelsen er indsendt, men bekræftelses-e-mailen kunne ikke sendes "
            "({err}). Tjek serverloggene."
        ),
        "recover_caption": (
            "Vi fjerner din anmeldelse, så fremtidige søgninger ikke viser en "
            "falsk advarsel. Vi matcher på stelnummeret og den e-mail, du brugte "
            "i anmeldelsen."
        ),
        "recover_email_label": "E-mail brugt i den oprindelige anmeldelse",
        "recover_checkbox": "Ja, jeg har fået min cykel tilbage. Fjern advarslen.",
        "recover_submit": "Markér som fundet",
        "recover_success": (
            "Markeret som fundet. Anmeldelsen vises ikke længere i søgninger."
        ),
        "recover_error": (
            "Kunne ikke finde en verificeret anmeldelse, der matcher det "
            "stelnummer og den e-mail. Tjek begge dele igen, eller kontakt os, "
            "hvis din cykel stadig er på listen."
        ),
        "landing_clean_title": "Ingen anmeldelser for denne cykel.",
        "landing_clean_body": (
            "Stelnummer {serial} matcher ikke nogen cykel, der er anmeldt "
            "stjålet i vores database."
        ),
        "seller_posted": "Sælgeren delte dette tjek den {date}.",
        "heads_up": (
            "**Bemærk.** Det betyder, at stelnummeret ikke er på vores liste — "
            "det beviser ikke, at sælgeren ejer cyklen. Når I mødes, så tjek, at "
            "stelnummeret på badgen stemmer overens med nummeret på stellet."
        ),
        "check_another": "Tjek en anden cykel",
        "bike_word": "Cykel",
        "stolen_on": "Stjålet den",
        "stolen_in": "Stjålet i",
        "verify_ok": "Anmeldelsen er bekræftet. Den vises nu i søgninger.",
        "verify_bad": "Bekræftelseslinket er ugyldigt eller er allerede brugt.",
        "back_home": "Tilbage til forsiden",
        "badge_checked": "Tjekket {date} — ingen tyverianmeldelser.",
        "badge_scan": "Scan eller besøg linket for at verificere live.",
        "email_subject": "Bekræft din anmeldelse af stjålet cykel",
        "email_body": (
            "Tak, fordi du anmeldte en stjålet cykel.\n\n"
            "Klik på linket nedenfor for at bekræfte din anmeldelse, så den "
            "vises i søgninger:\n\n"
            "{link}\n\n"
            "Hvis du ikke har indsendt dette, kan du ignorere denne e-mail."
        ),
    },
    "no": {
        "tagline": "Vit at den ikke er stjålet. På sekunder.",
        "stats": "{n} verifiserte rapport(er) i databasen.",
        "search_placeholder": "Skriv rammenummeret og trykk Enter",
        "try_demo": "Prøv et demo-rammenummer",
        "serial_help_title": "Hvor finner jeg rammenummeret?",
        "serial_help_body": (
            "Rammenummeret er gravert inn i sykkelrammen. Det vanligste stedet er "
            "**under kranklageret** — snu sykkelen og se ved leddet der pedalene "
            "sitter. Det kan også stå på **seterøret**, **styrerøret** eller nær "
            "**bakhjulsfestet**. Kun tall og bokstaver; mellomrom og bindestreker "
            "ignoreres når vi søker."
        ),
        "no_reports_title": "Ingen rapporter funnet.",
        "no_reports_body": (
            "Det er et godt tegn — men det garanterer ikke at sykkelen ikke er "
            "stjålet. Mange tyverier blir aldri rapportert her."
        ),
        "stolen_banner": "Denne sykkelen er rapportert stjålet ({n} rapport(er)).",
        "dont_buy_title": "Ikke kjøp denne sykkelen.",
        "advisory_home_body": (
            "Kontakt politiet, og ta om mulig vare på selgerens opplysninger. "
            "Å kjøpe en sykkel du tror er stjålet, kan være straffbart."
        ),
        "advisory_landing_body": (
            "Selv om selgeren delte en kontrollenke, er dette rammenummeret nå "
            "flagget som stjålet. Kontakt politiet."
        ),
        "selling_title": "Selger du denne sykkelen?",
        "selling_caption": (
            "Legg ved bevis i annonsen — kjøpere stoler på det, "
            "og sykkelen selges raskere."
        ),
        "badge_png": "Badge (PNG)",
        "selling_explainer": (
            "Lim inn lenken i annonsen, eller last ned badge-bildet (med QR-kode) "
            "og last det opp som et bilde. Når en kjøper klikker på lenken eller "
            "skanner QR-koden, sjekker vi rammenummeret på nytt direkte."
        ),
        "tile_report_title": "Rapporter en stjålet sykkel",
        "tile_report_body": (
            "Fortell fremtidige kjøpere at den er borte, så ingen kjøper "
            "sykkelen din av tyven."
        ),
        "tile_report_cta": "Start →",
        "tile_recover_title": "Marker en sykkel som gjenfunnet",
        "tile_recover_body": (
            "Fått sykkelen tilbake? Fjern advarselen slik at fremtidige søk stemmer."
        ),
        "tile_recover_cta": "Åpne →",
        "how_title": "Slik fungerer det",
        "how_body": (
            "**Søk.** Skriv et rammenummer. Vi matcher det mot verifiserte "
            "rapporter — mellomrom, bindestreker og store/små bokstaver "
            "ignoreres.\n\n"
            "**Rapporter.** Send inn rammenummer og e-post. Klikk på lenken vi "
            "sender, så blir rapporten synlig.\n\n"
            "**Gjenfunnet.** Fått sykkelen tilbake? Fjern rapporten med samme "
            "rammenummer og e-post."
        ),
        "disclaimer": (
            "En prototype. Rapportene er sendt inn av brukere og erstatter ikke "
            "en politianmeldelse eller et offisielt register."
        ),
        "badge_reported_stolen": "Rapportert stjålet",
        "unknown_bike": "Ukjent sykkel",
        "serial_word": "Rammenummer",
        "stolen_word": "Stjålet",
        "in_word": "i",
        "view_on_map": "Vis på kart ↗",
        "reported_on": "Rapportert",
        "back": "← Tilbake",
        "report_header_body": (
            "Fortell oss om det. Vi advarer neste kjøper. E-posten din forblir "
            "privat — vi bruker den bare til å verifisere rapporten."
        ),
        "label_serial": "Rammenummer",
        "label_brand": "Merke",
        "label_model": "Modell",
        "label_color": "Farge",
        "label_theft_date": "Tyveridato",
        "label_theft_location": "Tyveristed",
        "label_email": "E-post",
        "label_photo": "Foto",
        "required_tag": "Obligatorisk",
        "ph_serial": "Sykkelens rammenummer",
        "ph_color": "Mattsvart",
        "ph_email": "du@eksempel.com",
        "ph_location_text": "By, nabolag",
        "ph_location_search": "Begynn å skrive…",
        "location_caption": (
            "Begynn å skrive en by, et område eller en gate. Vi henter ekte "
            "geodata slik at rapporten vises på riktig sted."
        ),
        "adjust_pin": "Juster nålen på et kart",
        "move_pin_tooltip": "Klikk hvor som helst på kartet for å flytte nålen",
        "email_help": "Brukes til å verifisere rapporten og kontakte deg ved treff.",
        "submit_report": "Send inn rapport",
        "err_required": "Rammenummer og e-post er påkrevd.",
        "err_email": "Den e-postadressen ser ikke riktig ut.",
        "success_dev": (
            "Rapporten er sendt inn. E-postlevering er i utviklingsmodus — "
            "dette er lenken vi ville sendt til {email}."
        ),
        "open_verify_link": "Åpne verifiseringslenken →",
        "success_sent": (
            "Rapporten er sendt inn. Vi har sendt en verifiseringslenke til {email}. "
            "Klikk på den for å aktivere rapporten."
        ),
        "warn_send_failed": (
            "Rapporten er sendt inn, men verifiserings-e-posten kunne ikke "
            "sendes ({err}). Sjekk serverloggene."
        ),
        "recover_caption": (
            "Vi fjerner rapporten din slik at fremtidige søk ikke viser en falsk "
            "advarsel. Vi matcher på rammenummeret og e-posten du brukte i rapporten."
        ),
        "recover_email_label": "E-post brukt i den opprinnelige rapporten",
        "recover_checkbox": "Ja, jeg har fått sykkelen min tilbake. Fjern advarselen.",
        "recover_submit": "Marker som gjenfunnet",
        "recover_success": (
            "Markert som gjenfunnet. Rapporten vises ikke lenger i søk."
        ),
        "recover_error": (
            "Fant ingen verifisert rapport som matcher det rammenummeret og den "
            "e-posten. Dobbeltsjekk begge, eller kontakt oss hvis sykkelen din "
            "fortsatt er oppført."
        ),
        "landing_clean_title": "Ingen rapporter for denne sykkelen.",
        "landing_clean_body": (
            "Rammenummer {serial} matcher ingen sykkel som er rapportert "
            "stjålet i databasen vår."
        ),
        "seller_posted": "Selgeren la ut denne kontrollen {date}.",
        "heads_up": (
            "**Merk.** Det betyr at rammenummeret ikke står på listen vår — det "
            "beviser ikke at selgeren eier sykkelen. Når dere møtes, sjekk at "
            "rammenummeret på badgen stemmer med nummeret på rammen."
        ),
        "check_another": "Sjekk en annen sykkel",
        "bike_word": "Sykkel",
        "stolen_on": "Stjålet den",
        "stolen_in": "Stjålet i",
        "verify_ok": "Rapporten er verifisert. Den vises nå i søk.",
        "verify_bad": "Verifiseringslenken er ugyldig eller allerede brukt.",
        "back_home": "Tilbake til forsiden",
        "badge_checked": "Sjekket {date} — ingen tyverirapporter.",
        "badge_scan": "Skann eller besøk lenken for å verifisere direkte.",
        "email_subject": "Bekreft rapporten om stjålet sykkel",
        "email_body": (
            "Takk for at du rapporterte en stjålet sykkel.\n\n"
            "Klikk på lenken nedenfor for å bekrefte rapporten din slik at den "
            "vises i søk:\n\n"
            "{link}\n\n"
            "Hvis du ikke har sendt inn dette, kan du ignorere denne e-posten."
        ),
    },
}


def init_language() -> None:
    """Pick the session language once, from ?lang= if present."""
    if "lang" not in st.session_state:
        q = st.query_params.get("lang", "")
        st.session_state.lang = q if q in LANGUAGES else DEFAULT_LANG


def current_lang() -> str:
    try:
        return st.session_state.get("lang", DEFAULT_LANG)
    except Exception:
        return DEFAULT_LANG


def t_for(lang: str, key: str, **kwargs) -> str:
    """Translate for an explicit language (emails, badge images)."""
    table = STRINGS.get(lang, STRINGS[DEFAULT_LANG])
    s = table.get(key) or STRINGS[DEFAULT_LANG][key]
    return s.format(**kwargs) if kwargs else s


def t(key: str, **kwargs) -> str:
    """Translate for the current session language."""
    return t_for(current_lang(), key, **kwargs)


def clear_query_params_keep_lang() -> None:
    """Wipe deep-link params (?verify=, ?v=) without losing the language."""
    lang = current_lang()
    st.query_params.clear()
    if lang != DEFAULT_LANG:
        st.query_params["lang"] = lang
