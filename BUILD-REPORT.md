# BUILD REPORT - news-image-20261125: "Wednesday 25 November 2026"

- **Bounty:** Sum up 25 November's world news in one image (pot $100, deadline 27 Nov 2026 00:00 UTC).
- **Built:** 25 Nov 2026, 08:03-08:50 UTC, one session. Research -> fresh renderer (`draw25.py`, no earlier renderer code opened) -> 2 fix rounds + final full re-read -> report.
- **Entry:** `entry.png`, 1024x1024 RGB, **270,383 bytes** (limit 1 MiB).
- **Determinism:** three independent renders gave the same sha256 `fbe297e7b47463f69e4dd179588e3edc00bbbb8cae42888bd29192dd4567f12b`. No timestamps; a fixed-seed LCG only scatters stars in one art panel.
- **Renderer checks in code:** font floor asserted (every size >= 10; sizes used 10-16, 22, 30); region counts asserted to sum to 35; every text line width/line-count checked (final render: zero warnings).

## Research method and its limits
The day was still running at build time (08:23 UTC when the check ran), so the poster covers the day **so far** and says so (masthead "data to 08:20 UTC", UTC strip's last beat, footer). Stories came only from pages that carry a 25 Nov date: Al Jazeera section pages and articles, Gulf News/AFP, AP (via KSAT), Kyiv Independent, The Star (Reuters copy), MercoPress, allAfrica daily roundup, Wikipedia's 25 Nov Current Events, ESPN/myKhel bulletins. BBC, Guardian, Reuters, ABC, RNZ and others were unreachable from this machine; attributions to them rest on dated copies elsewhere (e.g. Guardian via Wikipedia's entry).

**Traps caught by checking (dropped or re-dated):** Al Jazeera video items "Iran whips singer" (June 2026) and "Venezuela wage protest" (April 2026) are old stories; Galatasaray/Israel UEFA complaint (Oct 2025 material); Phala Phala ruling (8 May 2026, nothing new found); Libertina Amathila death (could not confirm); Zambia treason indictment and DRC UNICEF Ebola survey (articles dated 24 Nov); Ethiopia polio campaign (launched 21 Nov); Sooryavanshi "204 off 53" (no source found); Vietnam $400m rail, Thailand "six-year low", Malaysia pardon-minutes leak (no dated confirmation); Cartagena supermarket hostages (24 Nov story, no 25 Nov update found); Huawei verdict (24 Nov US time) and Riyadh tower strike (Tuesday 24 Nov) went to DATE CHECK. Pete Edochie's death first looked like a recurring hoax (search showed only 2026 hoax denials); it was accepted only after an allAfrica/Vanguard report citing the family's statement (died 00:30 WAT Wednesday = 23:30 UTC 24 Nov; poster states local time).
**Source discrepancy resolved:** Al Jazeera summary said the new Bangladesh minimum is Tk17,500; the Daily Star (via Wikipedia) says Tk17,000 on a 4-2 vote, which equals +36% from Tk12,500. Poster uses Tk17,000.

## Story set - 35 stories, 9 regions (asserted in code)
| Region | N | Stories (pin: short headline) |
|---|---|---|
| EUROPE | 9 | 7 UK warns firms of Russian sabotage; 13 Ukraine drones reportedly hit 2 Russian refineries; 14 Odesa/Kyiv Oblast attacks; 15 US rules out troops in guarantees (REPORTED); 16 EU can't agree how to aid Ukraine; 17 Sweden PM vote on Kristersson; 18 Latvia: tipping point; 19 Kyiv claims 1,643,580 Russian losses (CLAIM); 20 UNAIDS $4.3bn gap |
| MIDDLE EAST | 4 | 1 Hodeidah strike / Houthi threat; 6 Eisenkot first coalition partner; 21 Gaza strike kills four; 22 Gaza prisoners after sentences |
| NORTH AMERICA | 4 | 5 Abrego Garcia leaves for Spain; 12 poll: 55% want Iran war ended; 23 Alaska ends DOJ voter-record deal; 24 CIA/ODNI intrusion (REPORTED) |
| LATIN AMERICA | 2 | 8 WHO chief on Cuba fuel blockade; 25 Argentina technical recession |
| EAST ASIA | 2 | 2 Pakistani astronaut at Tiangong; 4 Asia chip-stock rout |
| SOUTH ASIA | 3 | 3 Bangladesh garment wage +36%; 26 87 factories shut / 108 BGB platoons; 27 PT Usha opts out of IOA race |
| SOUTHEAST ASIA | 1 | 28 Indonesia state-fund unit takes 338,536 ha |
| AFRICA | 7 | 9 Pete Edochie dies; 29 Mada Masr appeal; 30 Morocco rejects CAS ruling; 31 Sudan Blue Nile abductions (CLAIM); 32 Malawi fake-consul case; 33 Ruto-Steinmeier talks; 35 Nigeria Senate loans |
| OCEANIA | 3 | 10 Lamarre-Condon guilty; 11 Australia Digital Duty of Care law; 34 Khawaja olive branch |

- **Leads (3):** 1 Hodeidah (AFP via Gulf News, Al Jazeera; CLAIM), 2 Pakistani astronaut (AP, Al Jazeera), 3 Bangladesh pay (Daily Star, TBS, Al Jazeera). All three have 2+ sources.
- **Smalls (10):** 4-13, each its own art function (candlesticks, plane/flags, pact blocks, warehouse fire, blackout, theatre mask + clapper, scales + gavel, phone shield, poll bar, refinery).
- **ALSO (22):** 14-35, one line each, region chips, source in parentheses, CLAIM/REPORTED in red.
- **Data strip (6):** +36% wage; -6.2% Kospi; 5-10 days stay; 55% poll; -4.4 yrs Cuba life expectancy; 1.64M Russian losses (CLAIMED).
- **UTC strip (5):** 00:18 Shenzhou-24 lift-off (planned time; AP story 00:45) -> ~01:08 refineries (03:08 Kyiv) -> ~06:30 Seoul/Tokyo close -> ~07:36 Reuters Australia law (15:36 MYT) -> 08:20 cut-off. Marked approximate.
- **DATE CHECK (5):** Riyadh tower hit - Tue 24 Nov; Huawei convicted - 24 Nov; corvette Merkury hit in Benghazi - Sun 22 Nov; Nvidia reinstates Huang - 23 Nov; Real Madrid 5-1 PSV - Tue 24 Nov.
- **Map:** world + Europe + Middle East insets, 35 pins (world 19, Europe 10, Middle East 6), 16px, deterministic repulsion with leader line + dot where displaced.

## Diagnosis - structure and why
Winner-density structure from the previous reports (3 huge leads + 10 smalls + ALSO + data strip + pinned map + region bar + UTC strip + DATE CHECK + sources/certainty footer) at **35 stories** (news-23 had 31 and finished final rank 5,450), with the legibility-first rule (no text below 10px, bodies 11px, headlines 12-15px). Noto Sans Condensed buys characters per line, which is what makes 35 stories fit at 10-11px. Leads are the three most consequential, spread over Middle East war, space/geopolitics and South Asian labour/economy.

## Eye-check log (every crop read at full resolution; crops in `eyecheck/`)
**Round 1** (first render, 2 renderer warnings):
1. Data labels "Bangladesh garment minimum wage" and "Pakistani astronaut aboard Tiangong" too wide - shortened. FIXED.
2. Footer line 2 clipped at the bottom edge - footer moved up, step 10. FIXED.
3. Lead 3 bar chart clipped at top ("Tk17,000" cut) and +36% badge on the bar - chart rescaled, badge moved. FIXED.
4. Small 5: the US flag was drawn as the Netherlands' (three stripes) - redrawn with 13-stripe pattern + canton. FIXED.
5. Small 8: "BLACK-OUT" overlapped the crossed bulb - bulb/candle moved left. FIXED.
6. Small 9: "NOLLYWOOD" label sat on the mask - mask shrunk, label below. FIXED.
7. Small 12: DEM/IND/GOP labels clipped, "KOSPI" tag in small 4 clipped - bar/labels re-laid. FIXED.
8. Morocco pin 30 clamped on the Europe inset's south edge - Europe window extended to 32N. FIXED.
9. Source lines touched panel borders - moved up 2px, body step 12. FIXED.
10. Data strip "78.8>74.4" read ambiguously - replaced by "-4.4 yrs" with the years in the label. FIXED.
11. Wording faithfulness: Houthi statement was conditional ("would be targets"); headline "Coalition says it hit" (claim); Abrego Garcia "wrongly deported" changed to the US's own phrase "administrative error"; Mada Masr "appeal heard" changed to "appeal set for 25 Nov"; Indonesia "pulp giant" made specific. FIXED.
**Round 2:** stray rail line in lead 3 art and wave strokes through "THREAT: JEDDAH" in lead 1 removed. FIXED.
**Final re-read (round 3):** full poster plus top, leads 1-3, smalls rows 1-2, map, ALSO list, bottom: **zero defects**. Every art sub-label unique to its panel (HODEIDAH/THREAT: JEDDAH/RED SEA; SHENZHOU-24/TIANGONG/PAKISTAN; Tk12,500/Tk17,000/+36%; -6.2%/KOSPI; US/ES; 21/7/48/61 NEEDED; BLACK-OUT; NOLLYWOOD; GUILTY; 5% FINE/A$109M; END WAR/OTHER/DEM/IND/GOP; SAMARA). Region bar: EUROPE 9, MIDDLE EAST 4, NORTH AMERICA 4, LATIN AMERICA 2, EAST ASIA 2, SOUTH ASIA 3, SOUTHEAST ASIA 1, AFRICA 7, OCEANIA 3 = 35. All 35 pins present and numbered.
**300px test** (`eyecheck/r3_300px.png`): masthead date, three lead banners, six data numbers and the coloured pins all still read; small bodies and the ALSO list blur out by design.

## Known nits
- Poster covers Wednesday up to 08:20 UTC only; evening fixtures and markets are not included (Champions League Wednesday matches, chess game 2, etc.).
- Several items are 24 Nov events first reported 25 Nov (Alaska voter-record decision announced Monday; CIA/ODNI breach first reported by NYT on Tuesday; UK sabotage warning issued Tuesday; Edochie died 00:30 WAT = 23:30 UTC 24 Nov). They are dated by first publication/local date and the footer says so for Edochie.
- Stock moves are Al Jazeera's closing figures; other outlets quote different intraday numbers (Kospi -6.1%, Nikkei -3.6%). The stock story has one outlet cited in the panel.
- Headline-only sources (Gaza strike, Gaza prisoners, Kenya talks, Nigeria Senate, Khawaja, Sweden vote, Latvia): details were not opened; lines state only what the headline says.
- Story 15 (US rules out troops) and 24 (CIA breach) rest on anonymous officials; marked REPORTED. 13, 19, 31 marked REPORTED/CLAIM.
- Map shapes are hand-keyed and schematic; the Middle East inset is horizontally stretched and says so. Pin 30 (Rabat) sits at the Europe inset's south-west corner.
- Pins for 5/12/24 (Washington area), 10/11/34 (Australia) and others are displaced by repulsion; leader lines + dots mark the true spots.
- No git push (no credentials on this machine, per brief); commits are local only.
