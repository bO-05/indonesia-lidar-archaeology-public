# Next regions for lidar archaeology in Indonesia

*Researched November 2026. Where to look next after the NASA CMS Kalimantan, Jambi (GRO.data) and East Kalimantan (KNB) surveys, and what lidar or DEM data exists or can be obtained for each region.*

## Why change strategy
The first survey covered about 3,660 tiles of open lidar. The NASA tiles came from forest-carbon plots, which mostly sit in logging concessions and peat swamps, so they were picked for trees and not for history. Open lidar over Indonesia is now effectively used up. The table below lists what exists.

| Source | Status |
|---|---|
| NASA CMS Kalimantan (ORNL 1518 LAZ, 1540 DTM) | Fully reviewed |
| GRO.data ONUBEV (Jambi, 2022, 1 m DTM, CC0) | Reviewed (315 tiles + automatic mound detector) |
| GRO.data ZFPSYJ (Jambi, 2020) | Restricted |
| KNB F1CN71VP (East Kalimantan logging, 2013) | Reviewed |
| OpenTopography | Only two small drone photogrammetry sets (Sinabung, LUSI mud volcano) |
| Zenodo 4020697 / 4572775 | Sabah (Malaysia), 10 m DTM; not Indonesia |
| BIG DEMNAS | About 8 m, made from IFSAR/radar. Too coarse for earthworks but fine for landscape context |
| BIG RBI 1:5,000 lidar (2019 onward, per regency) | Lidar DSM/DTM at 0.25–1 m. The `DTM` folder on geoservices.big.go.id needs a token. The Kendari 2024 lidar DSM (0.25 m) is public as an ImageServer. Other areas are available through a formal data request to BIG |

So the next step is to **go where the archaeology is and get the data there**, not wait for more open data to appear. A good target has:
1. Durable, monumental remains (brick or stone platforms, terraces, moats, canals). Lidar shows these well, while wooden Dayak *kuta* show up poorly.
2. Canopy or farmland hiding the microrelief.
3. Lidar that already exists, or is cheap to fly, such as a drone lidar survey of 5–20 km².

## Top 5 (ranked)

### 1. Penanggungan and the Arjuno-Welirang slopes, East Java
- **Why:** The mountain is a sacred Hindu-Buddhist landscape from roughly the 10th to 15th centuries. Its forested volcanic slopes hold more than 100 known stone terrace sanctuaries (*punden berundak*), and many more are probably unrecorded. Stone terraces and paths are the closest Indonesian equivalent of the Maya case, because the architecture is durable and hidden by canopy and scrub.
- **Terrain:** Steep forest. Lidar is ideal here; walking surveys are slow and dangerous.
- **Prior lidar:** A consortium of the national research agency (Badan Riset dan Inovasi Nasional), Universitas Surabaya, the regional heritage office and the provincial culture office flew about **200 km²** of airborne lidar. They reported **958 new potential points** on top of about 200 known sites (press release, 9 Dec 2024). Most of these points are still unverified.
- **Data path:** The raw data is not open; access would require a research collaboration with the survey consortium (for example, automated screening of the 958 candidates). For slopes not yet covered, drone lidar is realistic.

### 2. Muara Jambi temple complex, Jambi
- **Why:** One of the largest Buddhist complexes in Southeast Asia (7th to 13th centuries). It has 80+ brick ruins, mostly unexcavated *menapo* mounds, plus canals and ponds. Junus Satrio Atmodjo says the lidar suggests the site may stretch about 9 km and shows "organised mounds and lines" that are still unexplained.
- **Terrain:** Lowland. Secondary forest, rubber and duku gardens, and swampy backswamps. Brick menapo 10–40 m across, rising 1–3 m, are well suited to lidar.
- **Prior lidar:** Djarum Foundation and Historia.id commissioned an airborne survey in December 2019 covering **7,192 ha**, processed by Waindo SpecTerra (Haryuatmanto 2023, *IOP Conf. Ser. EES* 1127 012012, doi:10.1088/1755-1315/1127/1/012012). Full interpretation is not published.
- **Data path:** Ask Djarum Foundation, Historia.id or Waindo for the data (or a DTM derivative), or partner with the regional heritage office or the national Muara Jambi revitalisation team. The open GRO.data Jambi blocks do **not** cover Muara Jambi.

### 3. Trowulan, the Majapahit capital, East Java
- **Why:** The 14th-century capital, a city of brick with water tanks and a disputed grid of canals. Riyanto (*Berkala Arkeologi*) argues the canal network was never properly tested in the field. Lidar microrelief can test it.
- **Terrain:** Open farmland, villages and brick kilns. Canopy is not the problem; ploughing and modern brick-making are. So the analysis must target very low relief (10–50 cm) plus patterns in the drainage.
- **Prior lidar:** The Ministry of Culture, ITS and Walubi (through CSR funding) flew lidar over the whole KCBN area (more than 13,000 ha) in September 2025, including a VTOL drone demo over about 20 km². In 2026 the Minister said lidar and excavation point to Sentonorejo as the royal core ("titik nol"). Detailed results are still being processed.
- **Data path:** Through the regional heritage office or ITS. Very hard to get as open data, but an analysis collaboration is plausible.

### 4. Palembang Sriwijaya sites: Karanganyar, Bukit Seguntang, Musi wetlands, South Sumatra
- **Why:** Sriwijaya-period (7th to 10th centuries) canals, moats, tanks with central islands, and a moated enclosure of about 310 × 230 m at Karanganyar (Wolters 1986; Bambang Budi Utomo; excavations 1986–93). Much of the hydraulic landscape around the city and in nearby swamps is still unmapped. It is being lost to urban growth, which makes the work urgent.
- **Terrain:** Urban fringe, rice fields and peat swamp. Linear water features and moats, often 0.5–2 m deep, show up well in a lidar DTM.
- **Prior lidar:** No peer-reviewed archaeological lidar study found. BIG's 1:5,000 RBI programme has flown lidar over many cities and regencies, so Palembang may already be covered.
- **Data path:** Request the BIG RBI lidar DTM formally (stating the research purpose; partnering with an Indonesian university such as UNSRI or UI helps). A drone lidar survey of 5–10 km² over the Karanganyar/Gandus wetlands is a cheap alternative.

### 5. Lore Lindu megalith valleys: Bada, Besoa/Behoa, Napu, Central Sulawesi
- **Why:** More than 2,000 stone megaliths (kalamba vats, tuatena lids, statues, stone circles, "stone roads") at 118 sites, on the UNESCO Tentative List. BRIDA Sulteng (2024) recorded 1,863 remains. Lidar could find buried kalamba fields, stone-walled or terraced settlement platforms and *tumulus* mounds on the forested valley edges, where walking surveys rarely go.
- **Terrain:** Open grassland valley floors surrounded by forested hills, inside Lore Lindu National Park. Individual kalamba (1–2 m) need dense drone lidar (more than 50 points/m²); settlement terraces show at 1 m.
- **Prior lidar:** None found. Existing work uses drone photogrammetry, including 3D models for VR.
- **Data path:** A drone lidar project with Universitas Tadulako, the regional heritage office and the Lore Lindu National Park authority. Use DEMNAS for landscape context.

## Also considered (lower priority)
| Region | Why lower |
|---|---|
| **Muara Kaman / Kutai Martadipura** (East Kalimantan) | Historically very important (Yupa inscriptions, around the 4th–5th century). But the remains are mostly brick fragments and wood on a riverbank and lakes landscape that has been heavily disturbed, and the NASA CMS plots don't cover it. Worth it only with a dedicated drone lidar survey over Muara Kaman Ulu and Danau Lipan. |
| **Gunung Padang** (West Java) | Well-known site, already being studied by Ali Akbar's team, including drone lidar (2025). The 2023 "buried pyramid" paper was retracted. Little left to discover and a lot of controversy. |
| **Liangan** (Temanggung) | Buried under metres of volcanic deposits, so lidar cannot see it. |
| **Kota Cina** (North Sumatra), **Barus / Lobu Tua** | Small trading-port sites that have been excavated (French-Indonesian teams). Mostly built over or in mangrove. Lidar would add little. |
| **Banten Girang / Banten Lama** | Mostly built over. Better served by archives and excavation. |
| **Dieng** (Central Java) | Temples are known and the landscape is intensively farmed. Lidar could map lost temple platforms but the gain is modest. |

## Suggested approach
1. Seek research collaborations with holders of existing lidar (Penanggungan, Muara Jambi, Trowulan), offering the open pipeline in this repository for screening and classification.
2. Request BIG RBI 1:5,000 lidar DTM for Palembang (Karanganyar, Bukit Seguntang) and Muara Jambi, if covered.
3. Where no data can be obtained, scope a one-day drone lidar survey (5–10 km²) at the highest-value target. Indicative cost in Indonesia: roughly Rp 15–40 million; obtain local quotes.

## Sources
- Badan Riset dan Inovasi Nasional, "Temukan Potensi 958 Titik Baru Lanskap Arkeologi di Kawasan Gunung Penanggungan", press release, 9 Dec 2024.
- Haryuatmanto, G. (2023) "Analysis of Airborne LiDAR Data for Archaeology, Study Case: Sriwijaya Muaro Jambi Site", IOP Conf. Ser. EES 1127 012012.
- Historia.id, "Teknologi Pemindai Muarajambi" and "Temuan Baru di Situs Muarajambi". Green Network Asia, "Pemanfaatan LIDAR di Situs Muarajambi".
- detik.com, 22 Sep 2025, "Hadiri Uji Coba LiDAR, Menbud Tekankan Narasi Peradaban Majapahit". diswaymojokerto.id, 22 Sep and 4 Nov 2025. voi.id/en/news/593919.
- Riyanto, S. "Tinjauan Kembali Keberadaan 'Kanal' di Kota Majapahit", Berkala Arkeologi.
- Wolters, O.W. (1986) "Restudying some Chinese writings on Sriwijaya", Indonesia 42 (Karanganyar description).
- UNESCO Tentative List 6826, "Megalithic Cultural Heritage of Lore Lindu Area". BRIDA Sulteng seminar, 30 Aug 2024.
- detikJabar, 31 Jul 2025, "Drone-Lidar Digunakan dalam Penelitian Lanjutan Situs Gunung Padang". Retraction of doi:10.1002/arp.1912.
- BIG geoservices: `geoservices.big.go.id/raster/rest/services/DEMNAS/DSM_SULAWESI_KENDARI_2024_TILE` (lidar DSM 0.25 m, public); the `DTM` folder needs a token.
