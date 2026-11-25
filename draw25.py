#!/usr/bin/env python3
"""draw25.py - "Wednesday 25 November 2026" world-news poster (1024x1024).

Single source of truth: story data + all code-drawn art + layout.
Deterministic: no timestamps, no unseeded randomness (a fixed LCG scatters stars).
Run:  python3 draw25.py [out.png]
"""
import sys
import hashlib
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = sys.argv[1] if len(sys.argv) > 1 else "entry.png"

# ---------------------------------------------------------------- fonts
FD = "/usr/share/fonts/truetype/noto/"
FILES = {"r": "NotoSans-Condensed.ttf", "b": "NotoSans-CondensedBold.ttf",
         "x": "NotoSans-CondensedExtraBold.ttf"}
_fc = {}
SIZES_USED = set()
WARN = []


def F(size, w="r"):
    assert size >= 10, "font floor is 10px, asked %s" % size
    SIZES_USED.add(size)
    k = (size, w)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FD + FILES[w], size)
    return _fc[k]


def tw(s, size, w="r"):
    return F(size, w).getlength(s)


def T(d, x, y, s, size, fill, w="r", anchor="la"):
    d.text((x, y), s, font=F(size, w), fill=fill, anchor=anchor)


def wrap(s, size, w, maxw):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if tw(t, size, w) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, s, size, fill, maxw, maxlines, w="r", step=None, tag=""):
    lines = wrap(s, size, w, maxw)
    if len(lines) > maxlines:
        WARN.append("OVERFLOW %s: %d lines > %d: %s" % (tag, len(lines), maxlines, s[:40]))
    step = step or size + 2
    for i, ln in enumerate(lines):
        T(d, x, y + i * step, ln, size, fill, w)
    return y + len(lines) * step


def fit1(s, size, w, maxw, tag=""):
    if tw(s, size, w) > maxw:
        WARN.append("TOO WIDE %s (%.0f>%d): %s" % (tag, tw(s, size, w), maxw, s))


# ---------------------------------------------------------------- palette
INK = (20, 24, 32)
PAPER = (247, 244, 235)
NAVY = (14, 26, 48)
RED = (196, 16, 22)
GREY = (90, 96, 108)
REG = {  # region -> colour (all with white-text contrast)
    "EUROPE": (24, 76, 176),
    "MIDDLE EAST": (140, 48, 168),
    "NORTH AMERICA": (0, 120, 128),
    "LATIN AMERICA": (36, 146, 60),
    "EAST ASIA": (214, 36, 126),
    "SOUTH ASIA": (120, 118, 0),
    "SOUTHEAST ASIA": (16, 140, 214),
    "AFRICA": (128, 62, 24),
    "OCEANIA": (238, 120, 8),
}
REGIONS = list(REG)

# ---------------------------------------------------------------- stories
# id, region, lat, lon, headline, body, source, optional tag
S = {}


def st(i, region, lat, lon, head, body, src, tag=""):
    S[i] = dict(id=i, region=region, lat=lat, lon=lon, head=head, body=body, src=src, tag=tag)


# --- 3 leads
st(1, "MIDDLE EAST", 14.8, 42.9,
   "COALITION SAYS IT HIT HODEIDAH PORT; HOUTHIS THREATEN JEDDAH",
   "Saudi-led coalition says it hit 'operational capabilities' at the Houthi-run port after telling civilians "
   "to leave. Houthi spokesman Saree warns Jeddah and Saudi Red Sea ports would be targets. No casualties reported.",
   "AFP via Gulf News; Al Jazeera. CLAIM: both sides' accounts unverified", "CLAIM")
st(2, "EAST ASIA", 40.1, 99.9,
   "PAKISTAN'S FIRST ASTRONAUT REACHES CHINA'S SPACE STATION",
   "Muhammad Zeeshan Ali, 40, launched from Jiuquan on Shenzhou-24 with Tang Hongbo and Wu Yi and docked at "
   "Tiangong: the first foreign national aboard. He stays five to 10 days.",
   "AP; Al Jazeera. REPORTED by both")
st(3, "SOUTH ASIA", 23.8, 90.4,
   "BANGLADESH GARMENT PAY RISES 36%; UNIONS SAY NOT ENOUGH",
   "Wage board lifted the monthly minimum from Tk12,500 to Tk17,000 on a 4-2 vote. Unions rejected it, "
   "shutting factories and blocking highways after a month of unrest in a 4-million-worker industry.",
   "The Daily Star; The Business Standard; Al Jazeera")
# --- 10 smalls
st(4, "EAST ASIA", 37.5, 127.0, "ASIA'S CHIP STOCKS DIVE ON AI DOUBTS",
   "Kospi -6.2%, Taiex -4.8% (-8% earlier), Nikkei -2.8%. SK Hynix -11.1%, Tokyo Electron -12.5%.",
   "Al Jazeera")
st(5, "NORTH AMERICA", 39.3, -76.6, "ABREGO GARCIA LEAVES US FOR SPAIN",
   "Salvadoran, 31, sent to a Salvadoran prison in 2025 by US 'administrative error'; left on a judge's order.",
   "Al Jazeera")
st(6, "MIDDLE EAST", 31.8, 35.2, "ISRAEL: EISENKOT LANDS FIRST COALITION PARTNER",
   "Yashar (21 seats) and Lieberman's Our Home (7) agree a pact. His bloc: 48; 61 needed. Mandate ends 6 Dec.",
   "Al Jazeera; Reuters")
st(7, "EUROPE", 51.5, -0.1, "UK WARNS FIRMS OF RUSSIAN SABOTAGE",
   "MoD and security agency warn Ukraine suppliers of arson by proxies. REPORTED: no new evidence; Russia denies.",
   "Al Jazeera")
st(8, "LATIN AMERICA", 23.1, -82.4, "WHO CHIEF: END US FUEL BLOCKADE OF CUBA",
   "Tedros, in Havana, says curbs harm Cubans; life expectancy fell 78.8 to 74.4. US says it seeks change.",
   "Al Jazeera")
st(9, "AFRICA", 6.45, 7.5, "NOLLYWOOD'S PETE EDOCHIE DIES AT 79",
   "Nigerian actor, Okonkwo in 1987 'Things Fall Apart', died in Enugu at 00:30 local after prostate cancer.",
   "Vanguard; allAfrica")
st(10, "OCEANIA", -33.9, 151.2, "EX-POLICE OFFICER GUILTY OF SYDNEY DOUBLE MURDER",
   "Beau Lamarre-Condon found guilty of murdering TV presenter Jesse Baird and partner Luke Davies in 2024.",
   "The Guardian")
st(11, "OCEANIA", -35.3, 149.1, "AUSTRALIA PASSES 'DIGITAL DUTY OF CARE' LAW",
   "Platforms must proactively remove harmful content; fines to 5% of turnover or A$109m. Starts in a year.",
   "Reuters")
st(12, "NORTH AMERICA", 38.9, -77.0, "55% OF US VOTERS WANT IRAN WAR ENDED, ANY TERMS",
   "UMD-Ipsos poll, 1,022 adults: 80% of Democrats, 59% of independents, about 25% of Republicans agree.",
   "Al Jazeera")
st(13, "EUROPE", 53.2, 50.1, "UKRAINE DRONES 'HIT 2 RUSSIAN REFINERIES'",
   "REPORTED: Syzran and Kuibyshev plants in Samara region ablaze overnight, per monitoring channels. Unconfirmed.",
   "Kyiv Independent", "REPORTED")
# --- 22 ALSO
ALSO_TXT = {
    14: ("EUROPE", 46.5, 30.7, "Odesa Oblast attack kills 2 incl. a teen; 1 dead in Kyiv Oblast", "Kyiv Independent"),
    15: ("EUROPE", 50.45, 30.5, "REPORTED: US rules out troops and bases in Ukraine guarantees", "Kyiv Independent"),
    16: ("EUROPE", 50.85, 4.35, "EU states want to aid Ukraine before key summit; can't agree how", "Kyiv Independent"),
    17: ("EUROPE", 59.3, 18.1, "Sweden: speaker schedules PM vote on Kristersson to end deadlock", "Reuters"),
    18: ("EUROPE", 56.95, 24.1, "Latvia's Rinkevics: war may reach a tipping point next year", "Reuters"),
    19: ("EUROPE", 50.5, 30.6, "CLAIM: Kyiv says Russia has lost 1,643,580 troops since 2022", "Kyiv Independent"),
    20: ("EUROPE", 46.2, 6.1, "UNAIDS: $4.3bn HIV funding gap could reverse gains", "allAfrica"),
    21: ("MIDDLE EAST", 31.5, 34.45, "Israeli strike kills four people in Gaza", "Al Jazeera"),
    22: ("MIDDLE EAST", 31.93, 34.87, "Gaza families wait as prisoners stay jailed after sentences end", "Al Jazeera"),
    23: ("NORTH AMERICA", 58.3, -134.4, "Alaska ends deal giving DOJ its voter records", "Al Jazeera"),
    24: ("NORTH AMERICA", 38.95, -77.15, "REPORTED: CIA, ODNI hit by intrusion exposing unclassified data", "NYT via MercoPress"),
    25: ("LATIN AMERICA", -34.6, -58.4, "Argentina in technical recession: second straight quarterly fall", "INDEC via MercoPress"),
    26: ("SOUTH ASIA", 24.0, 90.4, "Bangladesh: 87 garment factories shut; BGB sends 108 platoons", "Daily Star; TBS"),
    27: ("SOUTH ASIA", 28.6, 77.2, "India: PT Usha opts out of IOA presidency race; vote 5 Dec", "ESPN"),
    28: ("SOUTHEAST ASIA", 0.5, 101.4, "Indonesia: state-fund unit takes 338,536 ha of seized RAPP pulp land", "Reuters"),
    29: ("AFRICA", 30.0, 31.2, "Egypt: Amnesty urges reversal of Mada Masr closure; appeal set for 25 Nov", "allAfrica"),
    30: ("AFRICA", 34.0, -6.8, "Morocco's federation rejects CAS ruling for Senegal, eyes more action", "allAfrica"),
    31: ("AFRICA", 11.8, 34.4, "CLAIM: Sudan's Blue Nile: 28 women, girls abducted, rights group says", "allAfrica"),
    32: ("AFRICA", -13.96, 33.8, "Malawi: no deportation request received in fake-consul case", "allAfrica"),
    33: ("AFRICA", -1.29, 36.8, "Kenya's Ruto to hold talks with German President Steinmeier", "allAfrica"),
    34: ("OCEANIA", -27.5, 153.0, "Cricket: Khawaja says he sent Cricket Australia an olive branch", "The Star"),
    35: ("AFRICA", 9.06, 7.5, "Nigeria's Senate approves loan requests Tinubu had withdrawn", "allAfrica"),
}
for i, (rg, la, lo, tx, sr) in ALSO_TXT.items():
    st(i, rg, la, lo, tx, "", sr)

NSTORY = len(S)
assert NSTORY == 35 and sorted(S) == list(range(1, 36))
COUNTS = {r: sum(1 for s in S.values() if s["region"] == r) for r in REGIONS}
assert sum(COUNTS.values()) == NSTORY, COUNTS
assert all(COUNTS[r] >= 1 for r in REGIONS)

DATA = [  # (number, label, source)
    ("+36%", "Bangladesh garment min. wage", "Daily Star"),
    ("-6.2%", "Kospi close in Asia AI rout", "Al Jazeera"),
    ("5-10 days", "Pakistani astronaut in orbit", "Al Jazeera"),
    ("55%", "US voters: end Iran war, any terms", "UMD-Ipsos"),
    ("-4.4 yrs", "Cuba life expectancy, 2020-2025", "WHO / AJ"),
    ("1.64M", "Russian losses CLAIMED by Kyiv", "Kyiv Indep."),
]
UTC = [
    ("00:18", "Shenzhou-24 lifts off for Tiangong (planned time; AP story 00:45)"),
    ("~01:08", "Syzran, Kuibyshev refineries reported ablaze (03:08 Kyiv)"),
    ("~06:30", "Seoul and Tokyo close: Kospi -6.2%, Nikkei -2.8%"),
    ("~07:36", "Reuters files Australia duty-of-care law (15:36 MYT)"),
    ("08:20", "Poster cut-off: later Wednesday events not included"),
]
EXCLUDED = [
    ("Drone hits Riyadh's tallest tower, 11 hurt", "Tue 24 Nov"),
    ("Huawei convicted at US trial over Iran business", "24 Nov"),
    ("Ukraine hits Russian corvette Merkury, Benghazi", "Sun 22 Nov"),
    ("Nvidia reinstates Jensen Huang as CEO", "23 Nov"),
    ("Real Madrid beat PSV 5-1 in Champions League", "Tue 24 Nov"),
]

# ---------------------------------------------------------------- geography
LAND = {
    "eurasia": [(-9.0, 37.0), (-9.5, 38.7), (-8.9, 41.5), (-9.3, 43.0), (-1.8, 43.4), (-1.2, 46.0), (-4.5, 48.4),
                (-1.6, 48.7), (-1.3, 49.7), (1.5, 50.1), (3.2, 51.3), (4.5, 52.4), (5.0, 53.3), (8.0, 53.7),
                (8.6, 55.0), (8.2, 56.8), (10.6, 57.7), (10.0, 55.0), (11.0, 54.0), (14.2, 53.9), (18.5, 54.8),
                (21.0, 55.3), (21.0, 57.5), (23.5, 57.0), (24.4, 58.4), (23.5, 59.2), (28.0, 59.5), (30.0, 59.9),
                (27.5, 60.5), (22.0, 60.0), (21.5, 61.0), (21.4, 63.0), (25.0, 65.0), (25.4, 65.6), (22.0, 65.8),
                (21.0, 63.5), (17.5, 61.0), (18.8, 60.0), (17.0, 58.8), (16.5, 57.0), (14.5, 56.0), (12.8, 55.5),
                (12.0, 57.5), (11.2, 59.0), (8.0, 58.0), (5.5, 59.0), (5.0, 61.0), (7.5, 63.0), (10.8, 64.5),
                (14.0, 67.0), (16.5, 68.8), (20.0, 70.0), (25.0, 71.0), (30.0, 70.5), (33.0, 69.5), (41.0, 67.0),
                (37.0, 66.0), (34.0, 66.5), (35.0, 64.5), (38.0, 64.5), (40.0, 65.5), (44.0, 66.0), (46.0, 67.8),
                (54.0, 68.5), (60.0, 69.0), (68.0, 69.0), (70.0, 73.0), (80.0, 73.5), (87.0, 75.0), (100.0, 76.5),
                (112.0, 75.8), (128.0, 73.0), (140.0, 72.5), (160.0, 70.0), (170.0, 70.0), (180.0, 68.8),
                (180.0, 65.0), (170.0, 60.0), (163.0, 59.5), (162.0, 56.5), (160.0, 53.0), (156.5, 51.0),
                (155.5, 56.0), (151.0, 59.5), (143.0, 59.0), (136.0, 54.5), (141.0, 53.0), (140.5, 48.5),
                (135.5, 43.5), (131.0, 42.5), (129.7, 41.0), (128.0, 38.5), (129.4, 36.0), (126.5, 34.5),
                (126.3, 37.0), (125.0, 38.5), (124.8, 40.0), (121.5, 39.0), (122.0, 40.5), (118.5, 39.2),
                (119.5, 37.2), (122.5, 37.2), (119.0, 35.0), (121.0, 31.5), (122.0, 29.5), (120.5, 27.0),
                (117.5, 23.5), (113.5, 22.2), (110.5, 21.0), (108.0, 21.6), (106.5, 19.5), (108.8, 15.0),
                (109.2, 12.0), (107.0, 10.4), (105.0, 8.6), (104.8, 10.5), (100.9, 12.8), (100.1, 13.5),
                (99.5, 10.0), (100.4, 7.0), (102.5, 2.5), (104.0, 1.4), (103.4, 1.3), (101.3, 2.8), (100.3, 5.5),
                (98.3, 8.0), (98.5, 12.0), (97.5, 16.5), (94.5, 16.0), (94.2, 19.0), (92.3, 21.5), (91.5, 22.5),
                (89.0, 21.7), (86.8, 21.0), (85.0, 19.5), (82.3, 16.5), (80.2, 15.0), (80.2, 13.0), (79.9, 10.3),
                (78.2, 8.9), (77.5, 8.1), (76.3, 10.0), (74.8, 12.8), (73.0, 17.5), (72.8, 21.0), (72.5, 21.5),
                (70.0, 20.9), (68.9, 22.3), (70.5, 23.2), (68.2, 23.6), (66.5, 25.4), (61.5, 25.2), (57.0, 25.6),
                (56.5, 27.2), (54.0, 26.7), (51.5, 27.9), (50.0, 30.2), (48.5, 30.0), (48.0, 29.5), (48.8, 27.5),
                (50.2, 26.0), (50.8, 24.8), (51.5, 24.2), (52.5, 24.1), (54.5, 24.3), (56.0, 26.1), (56.4, 24.6),
                (58.7, 23.6), (59.8, 22.3), (58.5, 20.4), (57.8, 19.0), (55.2, 17.2), (52.2, 15.8), (49.0, 14.3),
                (45.0, 12.8), (43.5, 12.7), (43.2, 13.5), (42.6, 16.0), (41.0, 19.0), (39.1, 21.5), (38.5, 24.0),
                (36.8, 26.5), (35.0, 28.0), (34.9, 29.6), (34.3, 31.3), (35.1, 33.0), (35.9, 34.6), (36.0, 36.0),
                (36.6, 36.8), (35.5, 36.6), (34.0, 36.2), (32.5, 36.1), (30.5, 36.3), (28.0, 36.7), (27.2, 37.0),
                (26.2, 38.2), (26.5, 39.5), (26.0, 40.8), (24.0, 40.3), (23.6, 39.2), (24.0, 38.0), (23.0, 36.5),
                (21.7, 36.8), (21.2, 38.3), (20.2, 39.7), (19.4, 41.9), (18.5, 42.5), (16.0, 43.5), (14.5, 45.2),
                (13.7, 45.5), (12.3, 45.3), (12.5, 43.8), (14.0, 42.5), (16.0, 41.5), (18.5, 40.2), (17.0, 39.0),
                (16.0, 38.0), (15.7, 39.9), (15.0, 40.5), (12.5, 41.7), (10.5, 43.0), (8.9, 44.4), (7.5, 43.8),
                (5.0, 43.3), (3.2, 43.0), (3.2, 41.9), (0.8, 41.0), (-0.3, 39.5), (0.2, 38.7), (-0.7, 37.6),
                (-2.2, 36.7), (-4.5, 36.7), (-5.4, 36.0), (-6.3, 36.6), (-7.4, 37.2)],
    "africa": [(-5.9, 35.8), (-2.0, 35.2), (3.0, 36.8), (10.0, 37.2), (10.5, 36.5), (10.2, 34.5), (11.0, 33.2),
               (15.2, 32.4), (19.5, 30.4), (20.5, 32.0), (23.0, 32.7), (25.0, 31.6), (29.0, 30.9), (32.0, 31.3),
               (32.6, 29.8), (33.7, 27.0), (35.5, 24.0), (37.0, 21.5), (38.5, 18.0), (39.0, 15.5), (42.7, 12.5),
               (43.2, 11.8), (44.2, 10.5), (48.0, 11.2), (51.2, 11.8), (51.0, 10.4), (48.5, 5.0), (45.0, 2.0),
               (41.5, -1.5), (39.7, -4.5), (40.5, -10.5), (40.5, -15.0), (35.5, -20.0), (35.0, -24.0),
               (32.8, -26.5), (32.5, -28.5), (30.0, -31.0), (27.0, -33.5), (25.0, -34.0), (20.0, -34.8),
               (18.4, -34.2), (17.2, -29.0), (14.5, -22.0), (11.8, -17.5), (13.5, -12.0), (12.5, -6.0), (9.0, -1.0),
               (9.5, 3.8), (6.0, 4.3), (4.0, 6.3), (1.0, 6.0), (-2.0, 4.8), (-5.0, 5.0), (-8.0, 4.5), (-11.5, 7.0),
               (-13.5, 9.5), (-16.7, 12.4), (-17.5, 14.7), (-16.5, 19.5), (-16.0, 22.0), (-13.0, 27.5),
               (-10.0, 29.5), (-9.8, 31.0), (-8.5, 33.5), (-6.8, 34.2)],
    "sinai": [(32.5, 31.1), (34.3, 31.3), (34.9, 29.5), (34.0, 27.8), (33.6, 28.0), (32.6, 29.9)],
    "namerica": [(-168.0, 65.6), (-166.0, 68.3), (-156.5, 71.3), (-141.0, 69.7), (-128.0, 70.2), (-115.0, 68.5),
                 (-108.0, 68.0), (-96.0, 68.5), (-94.0, 64.0), (-94.5, 60.5), (-92.5, 57.5), (-89.0, 56.5),
                 (-85.0, 55.5), (-82.5, 53.0), (-80.5, 51.5), (-79.0, 52.5), (-78.8, 55.0), (-77.3, 58.0),
                 (-77.8, 62.2), (-73.5, 62.0), (-70.0, 61.0), (-69.5, 59.5), (-65.0, 60.0), (-64.5, 58.0),
                 (-61.5, 56.0), (-57.5, 54.5), (-55.8, 52.2), (-59.0, 50.5), (-66.0, 50.0), (-64.5, 49.2),
                 (-64.5, 48.0), (-61.0, 45.5), (-65.5, 43.5), (-67.0, 44.8), (-70.5, 43.5), (-70.0, 41.8),
                 (-72.0, 41.2), (-74.0, 40.5), (-74.0, 39.0), (-75.5, 38.0), (-76.0, 35.5), (-78.0, 33.8),
                 (-81.0, 31.5), (-81.0, 30.0), (-80.0, 26.8), (-80.5, 25.2), (-81.8, 26.0), (-82.8, 28.0),
                 (-83.5, 29.7), (-85.0, 29.6), (-88.0, 30.4), (-89.5, 29.0), (-90.5, 29.2), (-93.5, 29.7),
                 (-97.0, 27.8), (-97.3, 25.5), (-97.7, 22.0), (-96.0, 19.0), (-94.5, 18.2), (-91.5, 18.5),
                 (-90.5, 21.0), (-87.0, 21.5), (-87.6, 18.5), (-88.2, 16.0), (-84.0, 15.8), (-83.2, 14.5),
                 (-83.5, 11.0), (-81.5, 9.0), (-79.5, 9.5), (-77.4, 8.6), (-78.0, 7.5), (-80.0, 7.3),
                 (-82.8, 8.2), (-85.5, 10.0), (-87.5, 13.0), (-91.5, 14.0), (-94.5, 16.0), (-97.0, 15.8),
                 (-101.0, 17.2), (-105.5, 20.0), (-105.5, 22.5), (-109.0, 25.8), (-112.5, 29.5), (-114.7, 31.7),
                 (-114.8, 30.0), (-112.2, 27.0), (-110.0, 23.0), (-112.0, 24.8), (-114.5, 28.0), (-116.5, 31.0),
                 (-117.2, 32.7), (-118.5, 34.0), (-120.6, 34.6), (-122.5, 37.5), (-124.2, 40.5), (-124.0, 46.2),
                 (-124.7, 48.3), (-122.5, 48.0), (-123.5, 49.2), (-125.5, 50.0), (-128.5, 52.8), (-130.5, 54.7),
                 (-133.5, 57.0), (-136.5, 58.5), (-140.0, 59.7), (-144.0, 60.0), (-148.0, 60.0), (-152.0, 59.0),
                 (-154.0, 57.5), (-158.0, 56.5), (-162.0, 55.0), (-164.5, 54.8), (-160.0, 58.5), (-162.5, 60.5),
                 (-165.0, 62.0), (-161.0, 64.5), (-166.0, 65.0)],
    "baffin": [(-90, 73), (-75, 72.5), (-62, 67), (-65, 62.5), (-75, 64), (-80, 70)],
    "ellesmere": [(-90, 76), (-70, 78), (-62, 82), (-85, 83), (-95, 80)],
    "greenland": [(-73, 78), (-60, 82), (-30, 83.5), (-18, 80), (-20, 72), (-22, 70), (-32, 68), (-43, 60),
                  (-50, 61), (-54, 66), (-58, 75)],
    "iceland": [(-24, 65.5), (-22, 66.4), (-15, 66.4), (-13.5, 65), (-18, 63.4), (-22.5, 63.8)],
    "samerica": [(-77.4, 8.6), (-75.5, 10.8), (-72.0, 12.2), (-70.0, 12.0), (-68.0, 10.7), (-64.5, 10.5),
                 (-62.0, 10.7), (-60.5, 8.5), (-57.5, 6.0), (-54.0, 5.8), (-51.5, 4.2), (-50.0, 1.5),
                 (-48.5, -1.0), (-44.5, -2.4), (-40.0, -3.0), (-35.2, -5.5), (-34.8, -8.0), (-37.5, -12.0),
                 (-39.0, -17.5), (-40.8, -22.0), (-44.0, -23.1), (-48.5, -26.0), (-48.7, -28.5), (-52.0, -32.0),
                 (-54.5, -34.8), (-57.5, -34.5), (-56.5, -36.5), (-57.5, -38.2), (-62.0, -39.0), (-65.0, -41.0),
                 (-63.5, -42.8), (-65.5, -45.0), (-67.5, -46.5), (-66.0, -48.0), (-69.0, -51.0), (-68.5, -52.5),
                 (-71.0, -54.0), (-74.5, -52.0), (-75.5, -47.0), (-74.0, -43.0), (-73.5, -37.5), (-71.5, -30.5),
                 (-70.5, -22.0), (-70.2, -18.5), (-76.0, -14.0), (-79.0, -8.0), (-81.2, -5.0), (-80.0, -2.0),
                 (-80.5, 0.5), (-78.8, 2.0), (-77.5, 4.0)],
    "cuba": [(-85, 22), (-82, 23.2), (-78, 22.5), (-74.2, 20.2), (-77.5, 19.9), (-80, 21.5)],
    "hispaniola": [(-74.5, 18.5), (-72, 19.9), (-68.4, 18.6), (-71, 17.8)],
    "uk": [(-5, 50), (-3, 50.5), (1.5, 51.3), (1.7, 52.7), (0, 53.5), (-1.5, 55), (-2.0, 57.5), (-4, 57.7),
           (-3.2, 58.6), (-5.0, 58.6), (-6.0, 57.2), (-5, 55.5), (-3.0, 54.8), (-3.2, 53.4), (-4.6, 52.5),
           (-5.2, 51.7), (-3.0, 51.3), (-5.7, 50.0)],
    "ireland": [(-10, 51.7), (-6, 52), (-6, 54.2), (-8, 55.3), (-10, 54.2)],
    "honshu": [(130.8, 31.2), (131.5, 34), (135, 34.5), (137, 34.5), (139.8, 35), (141, 38), (141.5, 41.4),
               (140, 40.5), (139.5, 38), (136.8, 37), (135.5, 35.7), (132, 35.5), (130.9, 34.0)],
    "hokkaido": [(140, 41.5), (145.5, 43.5), (142, 45.5), (140.3, 43.5)],
    "luzon": [(120, 18.5), (122.2, 18.3), (122, 14), (124, 13), (120.5, 14.2)],
    "mindanao": [(122, 7), (126.5, 7), (126, 9.5), (123.5, 8.7)],
    "sumatra": [(95.3, 5.5), (98.5, 4), (104, -1), (106, -3.2), (104, -5.8), (101, -3), (97, 2.5)],
    "java": [(105.2, -6.8), (114.5, -7.8), (114, -8.7), (106, -7.5)],
    "borneo": [(109, 1.5), (111, 2), (116, 7), (119, 5), (118, 1), (116.5, -4), (111, -3), (110, -2)],
    "newguinea": [(131, -1), (141, -2.5), (150.5, -10.5), (143, -9), (138, -8), (133, -4)],
    "australia": [(113, -22), (114, -26), (115, -34), (118, -35), (124, -33.5), (131, -31.5), (135.5, -34.5),
                  (138, -35), (140, -38), (144, -38.5), (147, -38), (150, -37.5), (153, -31), (153.5, -26),
                  (150, -22.5), (146, -19), (145.5, -15), (143.5, -14), (142.5, -10.8), (141.5, -13), (140, -17.5),
                  (136.5, -15.8), (135.5, -12), (132, -11.3), (130, -13), (127, -14), (125, -15), (122.3, -18),
                  (121, -19.5), (116, -20.5)],
    "tasmania": [(144.7, -40.7), (148.3, -41), (147.8, -43.3), (145.9, -43.4)],
    "nzn": [(172.7, -34.4), (175, -37), (178.5, -37.7), (176, -41.5), (174.8, -41.3), (173.8, -39.5)],
    "nzs": [(172.7, -40.5), (174, -41.7), (173, -43.5), (171, -44.5), (169, -46.6), (166.5, -46), (168, -44),
            (171.5, -41.5)],
    "madagascar": [(49.3, -12), (50.5, -15.5), (47, -25), (44, -24.5), (43.5, -21), (44.5, -16.5)],
    "srilanka": [(79.8, 9.7), (81.8, 7.5), (80.6, 6.0), (79.8, 7.5)],
    "taiwan": [(121.0, 25.2), (122.0, 24.5), (120.8, 22.0), (120.1, 23.5)],
    "sakhalin": [(142.0, 46.0), (143.5, 49.5), (143.0, 54.0), (142.0, 51.0)],
}
WATER = {  # lakes / inland seas drawn over land
    "blacksea": [(27.8, 42.0), (29.0, 41.2), (33.0, 42.0), (36.0, 41.3), (41.5, 41.2), (41.7, 42.5), (39.5, 44.2),
                 (37.5, 45.3), (35.5, 45.2), (33.5, 44.5), (32.5, 46.0), (31.0, 46.6), (30.3, 45.8), (29.5, 45.0),
                 (28.6, 43.8), (28.0, 42.7)],
    "caspian": [(47, 45), (50, 46), (53, 45), (53.5, 42.5), (54, 40), (53.5, 37), (51, 36.7), (49, 37.5),
                (49.5, 40), (48, 42), (47.5, 43.5)],
    "hudson": [(-95, 59), (-93, 61), (-89, 64), (-85, 66), (-81, 64), (-78, 62), (-78, 59), (-77, 56),
               (-79, 54), (-82, 53), (-85, 55), (-89, 56.5), (-92, 57.5)],
}
SEA = (168, 200, 224)
LANDC = (232, 226, 204)
LANDEDGE = (150, 140, 112)


def proj(lon, lat, win, w, h):
    lo0, lo1, la0, la1 = win
    return ((lon - lo0) / (lo1 - lo0) * w, (la1 - lat) / (la1 - la0) * h)


def draw_map_tile(win, w, h, labels=()):
    im = Image.new("RGB", (w, h), SEA)
    d = ImageDraw.Draw(im)
    for nm, pts in LAND.items():
        xy = [proj(lo, la, win, w, h) for lo, la in pts]
        d.polygon(xy, fill=LANDC, outline=LANDEDGE)
    for nm, pts in WATER.items():
        xy = [proj(lo, la, win, w, h) for lo, la in pts]
        d.polygon(xy, fill=SEA, outline=LANDEDGE)
    return im, d


WORLD_WIN = (-180, 180, -58, 80)
EUR_WIN = (-12, 54, 32, 66)
ME_WIN = (26, 58, 8, 38)


def inwin(s, win):
    return win[0] <= s["lon"] <= win[1] and win[2] <= s["lat"] <= win[3]


def place_pins(pts, w, h, rad=8, mind=17.5):
    """pts: list of (id, x, y) true spots -> list of (id, tx, ty, px, py). Deterministic repulsion."""
    pos = [[x, y] for _, x, y in pts]
    n = len(pos)
    for it in range(400):
        moved = False
        for a in range(n):
            for b in range(a + 1, n):
                dx = pos[b][0] - pos[a][0]
                dy = pos[b][1] - pos[a][1]
                dist = (dx * dx + dy * dy) ** 0.5
                if dist < mind:
                    if dist < 0.01:
                        dx, dy, dist = 0.7 * (1 if (a + b) % 2 else -1), 0.7, 1.0
                    push = (mind - dist) / 2 + 0.05
                    ux, uy = dx / dist, dy / dist
                    pos[a][0] -= ux * push
                    pos[a][1] -= uy * push
                    pos[b][0] += ux * push
                    pos[b][1] += uy * push
                    moved = True
        for p in pos:
            p[0] = min(max(p[0], rad + 1), w - rad - 1)
            p[1] = min(max(p[1], rad + 1), h - rad - 1)
        if not moved:
            break
    return [(pts[i][0], pts[i][1], pts[i][2], pos[i][0], pos[i][1]) for i in range(n)]


def draw_pins(d, placed):
    # leader lines first, pins on top
    for i, tx, ty, px, py in placed:
        if ((tx - px) ** 2 + (ty - py) ** 2) ** 0.5 > 3.5:
            d.line([(tx, ty), (px, py)], fill=(30, 30, 30), width=1)
            d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=(30, 30, 30), outline=(255, 255, 255))
    for i, tx, ty, px, py in placed:
        c = REG[S[i]["region"]]
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=c, outline=(255, 255, 255), width=1)
        T(d, px, py - 0.5, str(i), 10, (255, 255, 255), "x", "mm")


def make_map():
    """returns composite (456 x 320) image with world + two insets, and per-tile pin ids."""
    MW, MH = 456, 320
    out = Image.new("RGB", (MW, MH), (255, 255, 255))
    ww, wh = 456, 170
    ew, eh = 224, 146
    world, wd = draw_map_tile(WORLD_WIN, ww, wh)
    eur, ed = draw_map_tile(EUR_WIN, ew, eh)
    me, md = draw_map_tile(ME_WIN, ew, eh)
    ids_e = [i for i, s in S.items() if inwin(s, EUR_WIN)]
    ids_m = [i for i, s in S.items() if i not in ids_e and inwin(s, ME_WIN)]
    ids_w = [i for i in S if i not in ids_e and i not in ids_m]
    # inset frames on the world map
    for win, col in ((EUR_WIN, (24, 76, 176)), (ME_WIN, (140, 48, 168))):
        x0, y0 = proj(win[0], win[3], WORLD_WIN, ww, wh)
        x1, y1 = proj(win[1], win[2], WORLD_WIN, ww, wh)
        wd.rectangle([x0, y0, x1, y1], outline=col, width=2)
    for tile, td, win, ids, (tw_, th_) in ((world, wd, WORLD_WIN, ids_w, (ww, wh)),
                                          (eur, ed, EUR_WIN, ids_e, (ew, eh)),
                                          (me, md, ME_WIN, ids_m, (ew, eh))):
        pts = []
        for i in sorted(ids):
            x, y = proj(S[i]["lon"], S[i]["lat"], win, tw_, th_)
            pts.append((i, x, y))
        draw_pins(td, place_pins(pts, tw_, th_))
    # tags
    T(ed, 4, 3, "EUROPE inset", 10, (24, 76, 176), "x")
    T(md, ew - 4, 3, "MIDDLE EAST inset (stretched)", 10, (140, 48, 168), "x", "ra")
    out.paste(world, (0, 0))
    out.paste(eur, (0, wh + 4))
    out.paste(me, (ew + 8, wh + 4))
    d = ImageDraw.Draw(out)
    d.rectangle([0, 0, ww - 1, wh - 1], outline=INK)
    d.rectangle([0, wh + 4, ew - 1, wh + 4 + eh - 1], outline=INK)
    d.rectangle([ew + 8, wh + 4, ew + 8 + ew - 1, wh + 4 + eh - 1], outline=INK)
    return out, (ids_w, ids_e, ids_m)


# ================================================================ ART
def lcg(seed):
    s = [seed]

    def nxt():
        s[0] = (s[0] * 1103515245 + 12345) & 0x7FFFFFFF
        return s[0] / 0x7FFFFFFF
    return nxt


def vgrad(d, x, y, w, h, c0, c1):
    for j in range(h):
        t = j / max(1, h - 1)
        c = tuple(int(c0[k] + (c1[k] - c0[k]) * t) for k in range(3))
        d.line([(x, y + j), (x + w - 1, y + j)], fill=c)


# ---- leads (334 x ART_H)
def art_hodeidah(d, x, y, w, h):
    vgrad(d, x, y, w, h, (28, 24, 60), (226, 120, 60))
    sea_y = y + int(h * 0.62)
    d.rectangle([x, sea_y, x + w, y + h], fill=(18, 52, 96))
    for k in range(3):
        d.line([(x + 6 + k * 70, sea_y + 8 + (k % 2) * 8), (x + 40 + k * 70, sea_y + 8 + (k % 2) * 8)],
               fill=(60, 110, 160))
    d.ellipse([x + 256, y + 8, x + 280, y + 32], fill=(250, 244, 214))  # moon
    # Yemeni port: cranes + containers + warehouse
    d.rectangle([x, sea_y - 8, x + 150, sea_y], fill=(70, 70, 82))
    for k in range(4):
        cx = x + 14 + k * 34
        d.line([(cx, sea_y - 8), (cx, sea_y - 44)], fill=(30, 30, 38), width=3)
        d.line([(cx - 14, sea_y - 44), (cx + 22, sea_y - 44)], fill=(30, 30, 38), width=3)
        d.line([(cx + 20, sea_y - 44), (cx + 20, sea_y - 24)], fill=(30, 30, 38), width=1)
    for k, c in enumerate([(190, 70, 50), (60, 120, 170), (210, 170, 60), (90, 150, 90)]):
        d.rectangle([x + 20 + k * 22, sea_y - 17, x + 40 + k * 22, sea_y - 9], fill=c)
    # explosion burst
    cx, cy = x + 98, sea_y - 24
    pts = []
    for k in range(16):
        r = 26 if k % 2 == 0 else 12
        import math
        a = k * math.pi / 8
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=(255, 150, 20), outline=(255, 230, 90))
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(255, 245, 160))
    T(d, x + 6, y + 6, "HODEIDAH", 12, (255, 255, 255), "x")
    # dashed threat arrow to Jeddah target
    for k in range(9):
        sx = x + 140 + k * 12
        d.line([(sx, y + 52 - k * 2), (sx + 7, y + 50 - k * 2)], fill=(255, 70, 70), width=2)
    tx, ty = x + 270, y + 40
    for r in (20, 12, 5):
        d.ellipse([tx - r, ty - r, tx + r, ty + r], outline=(255, 70, 70), width=2)
    d.polygon([(tx - 18, ty - 12), (tx - 8, ty - 6), (tx - 20, ty - 3)], fill=(255, 70, 70))
    T(d, tx, ty + 24, "THREAT: JEDDAH", 12, (255, 220, 220), "x", "ma")
    T(d, x + w - 4, y + h - 4, "RED SEA", 10, (190, 220, 250), "b", "rd")


def art_astronaut(d, x, y, w, h):
    vgrad(d, x, y, w, h, (4, 8, 28), (20, 48, 110))
    r = lcg(7)
    for _ in range(46):
        sx, sy = x + int(r() * w), y + int(r() * h * 0.8)
        d.point((sx, sy), fill=(255, 255, 255))
        if r() > 0.8:
            d.point((sx + 1, sy), fill=(200, 210, 255))
    d.ellipse([x - 60, y + h - 26, x + w + 60, y + h + 200], fill=(34, 90, 170), outline=(120, 190, 250), width=2)
    d.ellipse([x + 60, y + h - 12, x + 150, y + h + 20], fill=(70, 130, 70))
    # Tiangong: core module + solar panels
    sx, sy = x + 132, y + 44
    d.rectangle([sx, sy - 6, sx + 72, sy + 6], fill=(206, 206, 214), outline=(120, 120, 130))
    d.rectangle([sx + 28, sy - 14, sx + 44, sy + 14], fill=(226, 226, 232), outline=(120, 120, 130))
    for px in (sx - 38, sx + 82):
        d.rectangle([px, sy - 20, px + 40, sy - 4], fill=(40, 70, 150), outline=(150, 190, 250))
        d.rectangle([px, sy + 4, px + 40, sy + 20], fill=(40, 70, 150), outline=(150, 190, 250))
        for gx in range(px, px + 40, 8):
            d.line([(gx, sy - 20), (gx, sy - 4)], fill=(90, 130, 210))
            d.line([(gx, sy + 4), (gx, sy + 20)], fill=(90, 130, 210))
    T(d, sx + 36, sy + 24, "TIANGONG", 12, (255, 255, 255), "x", "ma")
    # capsule docking
    d.polygon([(sx + 72, sy - 3), (sx + 100, sy - 7), (sx + 100, sy + 7), (sx + 72, sy + 3)], fill=(236, 220, 190),
              outline=(150, 130, 100))
    d.rectangle([sx + 100, sy - 7, sx + 112, sy + 7], fill=(190, 190, 200))
    T(d, x + w - 6, y + 6, "SHENZHOU-24", 12, (255, 235, 150), "x", "ra")
    # Pakistan flag chip
    fx, fy = x + 8, y + 8
    d.rectangle([fx, fy, fx + 52, fy + 34], fill=(255, 255, 255))
    d.rectangle([fx + 14, fy, fx + 52, fy + 34], fill=(1, 100, 44))
    d.ellipse([fx + 24, fy + 7, fx + 44, fy + 27], fill=(255, 255, 255))
    d.ellipse([fx + 28, fy + 6, fx + 46, fy + 26], fill=(1, 100, 44))
    T(d, fx + 26, fy + 38, "PAKISTAN", 10, (255, 255, 255), "x", "ma")


def art_garment(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(236, 228, 208))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(120, 110, 100))
    # sawtooth factory
    fx = x + 8
    base = y + h - 14
    d.rectangle([fx, base - 40, fx + 134, base], fill=(176, 92, 66), outline=(90, 40, 30))
    for k in range(4):
        d.polygon([(fx + k * 34, base - 40), (fx + k * 34 + 34, base - 40), (fx + k * 34 + 34, base - 62)],
                  fill=(140, 70, 50), outline=(90, 40, 30))
    d.rectangle([fx + 110, base - 80, fx + 124, base - 40], fill=(110, 60, 50))
    for k in range(5):
        d.rectangle([fx + 8 + k * 24, base - 28, fx + 22 + k * 24, base - 14], fill=(250, 226, 130))
    # garment shirts on rail
    # bar chart: old vs new minimum wage
    b0x, b1x = x + 188, x + 262
    bb = y + h - 14
    d.rectangle([b0x, bb - 40, b0x + 46, bb], fill=(120, 130, 150), outline=INK)
    d.rectangle([b1x, bb - 54, b1x + 46, bb], fill=(30, 140, 70), outline=INK)
    T(d, b0x + 23, bb - 53, "Tk12,500", 10, INK, "x", "ma")
    T(d, b1x + 23, bb - 67, "Tk17,000", 10, INK, "x", "ma")
    d.polygon([(b0x + 52, bb - 36), (b1x - 6, bb - 52), (b1x - 6, bb - 40)], fill=(30, 140, 70))
    d.rounded_rectangle([x + 200, y + 6, x + 262, y + 28], radius=6, fill=RED)
    T(d, x + 231, y + 17, "+36%", 14, (255, 255, 255), "x", "mm")
    # protest placards
    for k in range(3):
        px = x + 160 + k * 8
        d.line([(px, base), (px, base - 30 - k * 4)], fill=(80, 60, 40), width=2)
    d.rectangle([x + 152, base - 44, x + 184, base - 34], fill=(255, 255, 255), outline=INK)
    d.line([(x + 156, base - 39), (x + 180, base - 39)], fill=RED, width=2)


# ---- smalls (200 x 38)
def art_stocks(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(250, 240, 240))
    d.line([(x + 4, y + h - 3), (x + w - 4, y + h - 3)], fill=(150, 150, 150))
    vals = [(8, 30, 12, 24), (20, 26, 8, 20), (32, 22, 12, 16), (44, 14, 6, 12), (56, 18, 8, 10)]
    k = 0
    for i in range(10):
        cx = x + 10 + i * 13
        top = y + 5 + i * 2
        bot = top + 10 + (i % 3) * 3
        col = (200, 30, 30) if i != 3 else (30, 150, 70)
        d.line([(cx, top - 3), (cx, bot + 3)], fill=col)
        d.rectangle([cx - 3, top, cx + 3, bot], fill=col)
    d.rounded_rectangle([x + 146, y + 3, x + 196, y + 19], radius=4, fill=(200, 30, 30))
    T(d, x + 171, y + 11, "-6.2%", 12, (255, 255, 255), "x", "mm")
    T(d, x + 171, y + 22, "KOSPI", 10, (160, 20, 20), "x", "ma")


def art_plane(d, x, y, w, h):
    vgrad(d, x, y, w, h, (150, 200, 240), (230, 244, 252))
    d.arc([x + 20, y + 8, x + 180, y + 70], 200, 340, fill=(60, 60, 80), width=1)
    d.polygon([(x + 78, y + 18), (x + 114, y + 14), (x + 124, y + 17), (x + 114, y + 21), (x + 82, y + 22)],
              fill=(250, 250, 250), outline=(60, 60, 80))
    d.polygon([(x + 92, y + 16), (x + 100, y + 5), (x + 104, y + 5), (x + 100, y + 16)], fill=(220, 220, 230),
              outline=(60, 60, 80))
    d.polygon([(x + 92, y + 22), (x + 100, y + 33), (x + 104, y + 33), (x + 100, y + 22)], fill=(220, 220, 230),
              outline=(60, 60, 80))
    d.rectangle([x + 6, y + 20, x + 46, y + 34], fill=(255, 255, 255), outline=INK)
    for k in range(0, 14, 4):
        d.rectangle([x + 7, y + 21 + k, x + 45, y + 22 + k], fill=(200, 30, 30))
    d.rectangle([x + 7, y + 21, x + 22, y + 28], fill=(30, 60, 150))
    for gx in range(9, 21, 4):
        for gy in (23, 26):
            d.point((x + gx, y + gy), fill=(255, 255, 255))
    T(d, x + 26, y + 5, "US", 12, INK, "x", "ma")
    d.rectangle([x + 154, y + 20, x + 194, y + 34], fill=(198, 11, 30))
    d.rectangle([x + 154, y + 23, x + 194, y + 31], fill=(255, 196, 0))
    T(d, x + 174, y + 5, "ES", 12, INK, "x", "ma")


def art_pact(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(236, 230, 246))
    d.rectangle([x + 14, y + 6, x + 78, y + 34], fill=(120, 60, 170), outline=INK)
    d.rectangle([x + 100, y + 14, x + 140, y + 34], fill=(180, 130, 210), outline=INK)
    d.polygon([(x + 78, y + 14), (x + 90, y + 14), (x + 90, y + 20), (x + 100, y + 20), (x + 100, y + 28),
               (x + 90, y + 28), (x + 90, y + 34), (x + 78, y + 34)], fill=(250, 220, 90), outline=INK)
    T(d, x + 46, y + 20, "21", 16, (255, 255, 255), "x", "mm")
    T(d, x + 120, y + 24, "7", 14, INK, "x", "mm")
    d.rounded_rectangle([x + 150, y + 8, x + 196, y + 32], radius=4, fill=(255, 255, 255), outline=INK)
    T(d, x + 173, y + 14, "48/61", 12, (140, 48, 168), "x", "mm")
    T(d, x + 173, y + 26, "NEEDED", 10, GREY, "b", "mm")


def art_sabotage(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(70, 74, 90))
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(40, 40, 50))
    d.rectangle([x + 10, y + 12, x + 100, y + h - 6], fill=(150, 150, 160), outline=INK)
    d.polygon([(x + 6, y + 12), (x + 55, y + 2), (x + 104, y + 12)], fill=(110, 110, 120), outline=INK)
    d.rectangle([x + 40, y + 20, x + 70, y + h - 6], fill=(90, 90, 100), outline=INK)
    for fx, fh in ((x + 112, 22), (x + 124, 30), (x + 136, 18)):
        d.polygon([(fx, y + h - 6), (fx + 6, y + h - 6 - fh), (fx + 12, y + h - 6)], fill=(255, 140, 20))
        d.polygon([(fx + 3, y + h - 6), (fx + 6, y + h - 6 - fh // 2), (fx + 9, y + h - 6)], fill=(255, 230, 90))
    d.polygon([(x + 168, y + 4), (x + 192, y + 32), (x + 144, y + 32)], fill=(250, 200, 20), outline=INK)
    T(d, x + 168, y + 24, "!", 16, INK, "x", "mm")


def art_blackout(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 26, 40))
    for k, hh in enumerate([20, 30, 16, 26]):
        d.rectangle([x + 6 + k * 22, y + h - hh, x + 24 + k * 22, y + h], fill=(44, 48, 66))
    d.rectangle([x + 50, y + h - 22, x + 54, y + h - 18], fill=(250, 220, 100))
    # candle
    d.rectangle([x + 102, y + 20, x + 110, y + 36], fill=(240, 230, 200))
    d.polygon([(x + 103, y + 20), (x + 106, y + 8), (x + 109, y + 20)], fill=(255, 190, 40))
    # unlit bulb, crossed out
    d.ellipse([x + 124, y + 3, x + 152, y + 29], outline=(200, 200, 210), width=2)
    d.rectangle([x + 132, y + 29, x + 144, y + 35], fill=(150, 150, 160))
    d.line([(x + 128, y + 6), (x + 148, y + 26)], fill=(220, 60, 60), width=2)
    d.line([(x + 148, y + 6), (x + 128, y + 26)], fill=(220, 60, 60), width=2)
    T(d, x + 194, y + 8, "BLACK-", 11, (210, 210, 230), "x", "ra")
    T(d, x + 194, y + 21, "OUT", 11, (210, 210, 230), "x", "ra")


def art_theatre(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(60, 20, 30))
    for side in (0, 1):
        for k in range(5):
            cx = x + 8 + k * 11 if side == 0 else x + w - 8 - k * 11
            d.polygon([(cx - 6, y), (cx + 6, y), (cx + 3, y + h), (cx - 3, y + h)], fill=(160, 30, 40 + k * 8))
    d.ellipse([x + 72, y + 2, x + 106, y + 25], fill=(240, 220, 170), outline=(120, 90, 40), width=2)
    d.ellipse([x + 80, y + 9, x + 86, y + 14], fill=(30, 20, 20))
    d.ellipse([x + 92, y + 9, x + 98, y + 14], fill=(30, 20, 20))
    d.arc([x + 80, y + 14, x + 98, y + 24], 200, 340, fill=(30, 20, 20), width=2)
    d.rectangle([x + 118, y + 12, x + 150, y + 26], fill=(30, 30, 34), outline=(240, 240, 240))
    for k in range(4):
        d.polygon([(x + 118 + k * 8, y + 12), (x + 126 + k * 8, y + 12), (x + 122 + k * 8, y + 5), (x + 114 + k * 8, y + 5)],
                  fill=(240, 240, 240) if k % 2 == 0 else (30, 30, 34))
    T(d, x + 100, y + h - 1, "NOLLYWOOD", 10, (255, 230, 150), "x", "mb")


def art_scales(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(228, 232, 238))
    d.line([(x + 60, y + 33), (x + 60, y + 10)], fill=INK, width=3)
    d.line([(x + 36, y + 12), (x + 84, y + 12)], fill=INK, width=3)
    for cx in (x + 36, x + 84):
        d.line([(cx, y + 12), (cx - 8, y + 26)], fill=INK)
        d.line([(cx, y + 12), (cx + 8, y + 26)], fill=INK)
        d.arc([cx - 10, y + 20, cx + 10, y + 34], 0, 180, fill=INK, width=2)
    d.rectangle([x + 50, y + 32, x + 70, y + 35], fill=INK)
    # gavel
    d.rectangle([x + 112, y + 8, x + 138, y + 20], fill=(120, 70, 30), outline=INK)
    d.line([(x + 125, y + 20), (x + 140, y + 33)], fill=(120, 70, 30), width=4)
    d.rectangle([x + 128, y + 31, x + 156, y + 35], fill=(90, 50, 20))
    d.rounded_rectangle([x + 150, y + 6, x + 196, y + 26], radius=3, fill=(255, 255, 255), outline=RED, width=2)
    T(d, x + 173, y + 16, "GUILTY", 12, RED, "x", "mm")


def art_lawphone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(230, 242, 250))
    d.rounded_rectangle([x + 22, y + 3, x + 56, y + 36], radius=5, fill=(40, 44, 60), outline=INK)
    d.rectangle([x + 26, y + 9, x + 52, y + 30], fill=(120, 190, 240))
    d.polygon([(x + 39, y + 11), (x + 49, y + 15), (x + 47, y + 25), (x + 39, y + 29), (x + 31, y + 25), (x + 29, y + 15)],
              fill=(30, 140, 70), outline=(255, 255, 255))
    d.line([(x + 34, y + 20), (x + 38, y + 24), (x + 45, y + 15)], fill=(255, 255, 255), width=2)
    d.rounded_rectangle([x + 78, y + 8, x + 128, y + 30], radius=4, fill=(255, 255, 255), outline=INK)
    T(d, x + 103, y + 19, "5% FINE", 12, (160, 40, 20), "x", "mm")
    d.rounded_rectangle([x + 138, y + 8, x + 194, y + 30], radius=4, fill=(238, 120, 8))
    T(d, x + 166, y + 19, "A$109M", 12, (255, 255, 255), "x", "mm")


def art_poll(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(236, 244, 244))
    d.rectangle([x + 8, y + 3, x + 190, y + 18], fill=(210, 214, 220), outline=INK)
    d.rectangle([x + 8, y + 3, x + 8 + int(182 * 0.55), y + 18], fill=(0, 120, 128), outline=INK)
    T(d, x + 8 + 50, y + 10.5, "END WAR", 10, (255, 255, 255), "x", "mm")
    T(d, x + 8 + 148, y + 10.5, "OTHER", 10, GREY, "x", "mm")
    d.rectangle([x + 8, y + 22, x + 30, y + h - 1], fill=(40, 70, 130), outline=INK)
    d.rectangle([x + 12, y + 24, x + 26, y + 26], fill=(10, 10, 20))
    for k, lab in enumerate(("DEM 80%", "IND 59%", "GOP 25%")):
        T(d, x + 40 + k * 52, y + 22, lab, 10, INK, "b")


def art_refinery(d, x, y, w, h):
    vgrad(d, x, y, w, h, (60, 40, 60), (200, 110, 70))
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(40, 36, 36))
    for k, (tx, th) in enumerate(((x + 14, 24), (x + 40, 30), (x + 66, 20))):
        d.rectangle([tx, y + h - 6 - th, tx + 18, y + h - 6], fill=(150, 150, 160), outline=INK)
    d.rectangle([x + 96, y + 6, x + 102, y + h - 6], fill=(70, 70, 80))
    d.polygon([(x + 93, y + 8), (x + 99, y - 2), (x + 105, y + 8)], fill=(255, 150, 20))
    for fx, fh in ((x + 112, 22), (x + 150, 26)):
        d.polygon([(fx - 8, y + h - 6), (fx, y + h - 6 - fh), (fx + 8, y + h - 6)], fill=(255, 130, 20))
        d.polygon([(fx - 4, y + h - 6), (fx, y + h - 6 - fh // 2), (fx + 4, y + h - 6)], fill=(255, 230, 90))
    d.ellipse([x + 130, y + 2, x + 170, y + 14], fill=(80, 70, 70))
    T(d, x + w - 4, y + 4, "SAMARA", 10, (255, 235, 200), "x", "ra")


SMALL_ART = {4: art_stocks, 5: art_plane, 6: art_pact, 7: art_sabotage, 8: art_blackout, 9: art_theatre,
             10: art_scales, 11: art_lawphone, 12: art_poll, 13: art_refinery}
LEAD_ART = {1: art_hodeidah, 2: art_astronaut, 3: art_garment}


# ================================================================ LAYOUT
def build():
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)

    # ---------------- masthead 0..54
    d.rectangle([0, 0, W, 54], fill=NAVY)
    T(d, 10, 1, "WEDNESDAY 25 NOVEMBER 2026", 30, (255, 255, 255), "x")
    summ = ("The day in one line: Gulf port strike, first foreign astronaut at Tiangong, Asia's chip rout, "
            "Bangladesh pay deal, Ukraine refinery hits")
    fit1(summ, 12, "b", 740, "summary")
    T(d, 10, 37, summ, 12, (255, 214, 110), "b")
    d.rounded_rectangle([794, 6, 1016, 48], radius=6, fill=RED)
    T(d, 905, 14, "35 STORIES - 9 REGIONS", 13, (255, 255, 255), "x", "mm")
    T(d, 905, 33, "data to 08:20 UTC, 25 Nov", 11, (255, 230, 230), "b", "mm")

    # ---------------- data strip 56..98
    cw = 1016 / 6
    for k, (num, lab, src) in enumerate(DATA):
        x0 = 4 + k * cw
        d.rectangle([x0, 56, x0 + cw - 3, 98], fill=(255, 255, 255), outline=(190, 186, 170))
        d.rectangle([x0, 56, x0 + 4, 98], fill=RED)
        T(d, x0 + 10, 55, num, 22, RED, "x")
        fit1(lab, 10, "b", cw - 14, "data label")
        T(d, x0 + 10, 80, lab, 10, INK, "b")
        fit1(src, 10, "r", 50, "data src")
        T(d, x0 + cw - 8, 58, src, 10, GREY, "r", "ra")

    # ---------------- leads 100..308
    LY, LH, LW = 100, 208, 334
    ART_H = 108
    for k, i in enumerate((1, 2, 3)):
        s = S[i]
        lx = 4 + k * (LW + 7)
        col = REG[s["region"]]
        d.rectangle([lx, LY, lx + LW, LY + LH], fill=(255, 255, 255), outline=INK, width=2)
        d.rectangle([lx, LY, lx + LW, LY + 38], fill=RED)
        d.ellipse([lx + 5, LY + 8, lx + 25, LY + 28], fill=col, outline=(255, 255, 255), width=2)
        T(d, lx + 15, LY + 18, str(i), 12, (255, 255, 255), "x", "mm")
        hl = wrap(s["head"], 15, "x", LW - 38)
        if len(hl) > 2:
            WARN.append("lead headline >2 lines: %s" % s["head"])
        for j, ln in enumerate(hl[:2]):
            T(d, lx + 32, LY + 2 + j * 18, ln, 15, (255, 255, 255), "x")
        ay = LY + 40
        sub = Image.new("RGB", (LW - 3, ART_H), (0, 0, 0))
        sd = ImageDraw.Draw(sub)
        LEAD_ART[i](sd, 0, 0, LW - 3, ART_H)
        im.paste(sub, (lx + 2, ay))
        d.rectangle([lx + 2, ay + ART_H, lx + LW - 2, ay + ART_H], fill=INK)
        by = ay + ART_H + 3
        by = para(d, lx + 5, by, s["body"], 11, INK, LW - 10, 3, "r", 13, "lead%d" % i)
        fit1(s["src"], 10, "b", LW - 10, "lead src %d" % i)
        T(d, lx + 5, LY + LH - 13, s["src"], 10, GREY, "b")

    # ---------------- smalls 312..568
    SY, SH, SW = 312, 124, 200
    for n, i in enumerate(range(4, 14)):
        s = S[i]
        sx = 4 + (n % 5) * (SW + 4)
        sy = SY + (n // 5) * (SH + 8)
        col = REG[s["region"]]
        d.rectangle([sx, sy, sx + SW - 1, sy + SH - 1], fill=(255, 255, 255), outline=INK)
        d.rectangle([sx, sy, sx + SW - 1, sy + 3], fill=col)
        d.rounded_rectangle([sx + 3, sy + 7, sx + 19, sy + 20], radius=3, fill=col)
        T(d, sx + 11, sy + 14, str(i), 10, (255, 255, 255), "x", "mm")
        hl = wrap(s["head"], 12, "x", SW - 28)
        if len(hl) > 2:
            WARN.append("small headline >2 lines (%d): %s" % (i, s["head"]))
        for j, ln in enumerate(hl[:2]):
            T(d, sx + 23, sy + 5 + j * 13, ln, 12, INK, "x")
        ay = sy + 33
        sub = Image.new("RGB", (SW - 2, 38), (0, 0, 0))
        sd = ImageDraw.Draw(sub)
        SMALL_ART[i](sd, 0, 0, SW - 2, 38)
        im.paste(sub, (sx + 1, ay))
        d.line([(sx + 1, ay + 38), (sx + SW - 2, ay + 38)], fill=INK)
        para(d, sx + 4, ay + 40, s["body"], 11, INK, SW - 8, 3, "r", 12, "small%d" % i)
        fit1(s["src"], 10, "b", SW - 8, "small src %d" % i)
        T(d, sx + 4, sy + SH - 14, s["src"], 10, GREY, "b")

    # ---------------- ALSO list 572..892 (left) + map (right)
    AY = 572
    d.rectangle([4, AY, 553, AY + 320], fill=(255, 255, 255), outline=INK)
    T(d, 10, AY + 3, "ALSO ON THE DAY", 12, RED, "x")
    T(d, 150, AY + 4, "region-coloured chips match the map pins - CLAIM / REPORTED labels mark contested items",
      10, GREY, "r")
    ly = AY + 19
    for i in range(14, 36):
        s = S[i]
        col = REG[s["region"]]
        d.rounded_rectangle([9, ly, 31, ly + 12], radius=3, fill=col)
        T(d, 20, ly + 6, str(i), 10, (255, 255, 255), "x", "mm")
        line = s["head"]
        srcs = " (%s)" % s["src"]
        full = line + srcs
        fit1(full, 11, "r", 514, "also %d" % i)
        # bold CLAIM/REPORTED prefix
        x = 36
        for tag in ("CLAIM:", "REPORTED:"):
            if line.startswith(tag):
                T(d, x, ly - 1, tag, 11, RED, "x")
                x += tw(tag + " ", 11, "x")
                line = line[len(tag) + 1:]
                break
        T(d, x, ly - 1, line, 11, INK, "r")
        x += tw(line, 11, "r")
        T(d, x, ly - 1, srcs, 11, GREY, "r")
        ly += 13.6

    mp, mids = make_map()
    im.paste(mp, (560, AY))
    # ---------------- region bar 896..916
    ry = 896
    segw = 1016 / 9
    tot = 0
    for k, r in enumerate(REGIONS):
        x0 = 4 + k * segw
        d.rectangle([x0, ry, x0 + segw - 1, ry + 20], fill=REG[r])
        lab = "%s %d" % (r, COUNTS[r])
        fit1(lab, 11, "x", segw - 4, "region bar")
        T(d, x0 + segw / 2, ry + 10, lab, 11, (255, 255, 255), "x", "mm")
        tot += COUNTS[r]
    assert tot == NSTORY

    # ---------------- UTC strip 920..958
    uy = 920
    bw = 1016 / 5
    d.rectangle([4, uy, 1020, uy + 36], fill=(236, 240, 248), outline=INK)
    for k, (tm, tx) in enumerate(UTC):
        x0 = 4 + k * bw
        if k:
            d.line([(x0, uy + 2), (x0, uy + 34)], fill=(160, 170, 190))
        T(d, x0 + 6, uy + 1, tm + " UTC", 11, RED, "x")
        ls = wrap(tx, 10, "r", bw - 12)
        if len(ls) > 2:
            WARN.append("utc text >2 lines: %s" % tx)
        for j, ln in enumerate(ls[:2]):
            T(d, x0 + 6, uy + 13 + j * 11, ln, 10, INK, "r")
    # ---------------- DATE CHECK 960..1002
    dy = 960
    d.rectangle([4, dy, 1020, dy + 40], fill=(255, 238, 238), outline=RED, width=2)
    T(d, 10, dy + 2, "DATE CHECK - NOT 25 NOV, NOT ON THIS POSTER:", 12, RED, "x")
    x = 10
    y = dy + 16
    for k, (tx, dt) in enumerate(EXCLUDED):
        label = "%s - %s" % (tx, dt)
        wd = tw(label, 10, "b")
        if x + wd > 1016:
            x = 10
            y += 11
        T(d, x, y, tx + " - ", 10, INK, "r")
        xx = x + tw(tx + " - ", 10, "r")
        T(d, xx, y, dt, 10, RED, "x")
        x = xx + tw(dt, 10, "x") + 12
    if y > dy + 28:
        WARN.append("date-check overflow")
    T(d, 1014, dy + 2, "Nothing else here is dated to any other day.", 11, INK, "b", "ra")
    # ---------------- footer 1002..1024
    fy = 1002
    foot1 = ("Sources: Al Jazeera, AFP/Gulf News, AP, Reuters, Kyiv Independent, Daily Star, Business Standard, "
             "Vanguard, allAfrica, MercoPress, Guardian, ESPN, UMD-Ipsos.")
    foot2 = ("CLAIM = one side's assertion, unverified. REPORTED = anonymous or single-source. Local times: Edochie died "
             "00:30 WAT 25 Nov. Evening events not covered.")
    fit1(foot1, 10, "r", 1010, "foot1")
    fit1(foot2, 10, "r", 1010, "foot2")
    T(d, 6, fy, foot1, 10, GREY, "r")
    T(d, 6, fy + 10, foot2, 10, GREY, "r")
    return im, mids


def main():
    im, mids = build()
    assert min(SIZES_USED) >= 10, SIZES_USED
    if WARN:
        for w in WARN:
            print("WARN:", w, file=sys.stderr)
    im.save(OUT, optimize=True)
    data = open(OUT, "rb").read()
    print("pins world/europe/me:", [len(m) for m in mids], "total", sum(len(m) for m in mids))
    print("sizes used:", sorted(SIZES_USED), "bytes:", len(data), "sha256:", hashlib.sha256(data).hexdigest())
    print("counts:", COUNTS, "sum", sum(COUNTS.values()))
    if WARN:
        sys.exit(2)


if __name__ == "__main__":
    main()
