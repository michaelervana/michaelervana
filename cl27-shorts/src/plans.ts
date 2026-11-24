// What each video shows, line by line. Media keys: "r:" = clip from the reference documentary (16:9, shown in a card),
// "g:" = Champions League 27 gameplay (9:16, full screen). "@n" starts the clip n seconds in.
// `big` is a slammed-in number or year, `sub` a small label under it.

export type Beat = { media: string[]; big?: string; sub?: string };
export type Plan = {
  id: string;
  title: string; // hook headline on the opening line
  tag: string; // small topic label at the top
  outro: string; // gameplay clip behind the end card
  beats: Beat[]; // one per voiceover line
};

export const PLANS: Plan[] = [
  {
    id: "cuju",
    title: "SEPAK BOLA BUKAN DARI INGGRIS?",
    tag: "CUJU · CHINA KUNO",
    outro: "g:orbit",
    beats: [
      { media: ["g:kick_smoke"] },
      { media: ["r:cuju_painting", "r:cuju_town"], big: "2.000+", sub: "TAHUN LALU" },
      { media: ["r:cuju_scroll"], big: "CU + JU", sub: "TENDANG + BOLA" },
      { media: ["r:cuju_court"], big: "FIFA", sub: "BENTUK TERTUA YANG TERCATAT" },
      { media: ["r:cuju_painting", "r:cuju_scroll@2"], sub: "DINASTI HAN · LATIHAN TENTARA" },
      { media: ["r:oldball", "g:ballcam"], sub: "BULU → UDARA" },
      { media: ["r:cuju_court", "r:cuju_scroll@1"], big: "DINASTI SONG", sub: "GAWANG = LUBANG DI JARING" },
      { media: ["g:goal_net"], big: "COMING HOME?" },
    ],
  },
  {
    id: "kemari",
    title: "MAIN BOLA TANPA MENANG KALAH",
    tag: "KEMARI · JEPANG",
    outro: "g:tifo",
    beats: [
      { media: ["g:players"] },
      { media: ["r:kemari_live"], big: "1.000+", sub: "TAHUN" },
      { media: ["r:kemari_live@2.5"], sub: "PARA BANGSAWAN ISTANA" },
      { media: ["r:kemari_live@5"], big: "JANGAN JATUH", sub: "BOLA HARUS TETAP DI UDARA" },
      { media: ["r:kemari_live@1"], sub: "KULIT RUSA · 4 POHON DI SUDUT" },
      { media: ["g:broadcast"], big: "TEAMWORK" },
      { media: ["r:kemari_live@6"], big: "KYOTO", sub: "KUIL SHIMOGAMO · TIAP AWAL TAHUN" },
      { media: ["g:ballcam"], big: "FIRST TOUCH" },
    ],
  },
  {
    id: "larangan1314",
    title: "MAIN BOLA BISA DIPENJARA",
    tag: "LONDON · 1314",
    outro: "g:kick_smoke",
    beats: [
      { media: ["r:mob_photo", "r:mob_engraving"] },
      { media: ["r:engravings"], big: "1314", sub: "LONDON" },
      { media: ["r:football_engraving"], sub: "ATAS NAMA RAJA EDWARD II" },
      { media: ["r:engravings@4"], big: "PENJARA", sub: "HUKUMAN BAGI YANG MAIN" },
      { media: ["r:mob_engraving", "r:football_engraving@5"], big: "DESA VS DESA", sub: "RATUSAN ORANG · HAMPIR TANPA ATURAN" },
      { media: ["r:engravings@8"], sub: "BIAR RAKYAT LATIHAN MEMANAH" },
      { media: ["g:broadcast"], big: "CLASSIC." },
      { media: ["r:mob_photo", "g:kick_smoke@2"], sub: "MASIH DIMAINKAN SAMPAI SEKARANG" },
    ],
  },
  {
    id: "soccer",
    title: "KATA 'SOCCER' ITU DARI INGGRIS",
    tag: "ASAL KATA",
    outro: "g:broadcast",
    beats: [
      { media: ["r:nfl_catch"] },
      { media: ["r:rugby_school"], big: "MADE IN ENGLAND" },
      { media: ["r:fa_crest", "r:rules1863"], big: "1863", sub: "FOOTBALL ASSOCIATION" },
      { media: ["r:old_stadium"], big: "RUGBY → RUGGER", sub: "SLANG ANAK KAMPUS" },
      { media: ["r:bw_match"], big: "ASSOC → SOCCER" },
      { media: ["r:nfl_catch"], sub: "DI AMERIKA, FOOTBALL = INI" },
      { media: ["g:broadcast"], big: "IRONIS." },
    ],
  },
  {
    id: "skorgila",
    title: "SKOR 149-0. SERIUS.",
    tag: "SKOR PALING GILA",
    outro: "g:goal_net",
    beats: [
      { media: ["g:broadcast"] },
      { media: ["r:arbroath"], big: "36-0", sub: "ARBROATH · 1885" },
      { media: ["r:arbroath"], sub: "KLUB KRIKET?" },
      { media: ["r:samoa_match", "r:samoa_goal"], big: "31-0", sub: "AUSTRALIA VS AMERICAN SAMOA · 2001" },
      { media: ["r:samoa_goal"], big: "13 GOL", sub: "SATU PEMAIN" },
      { media: ["g:goal_net"], big: "149-0", sub: "MADAGASKAR · 2002" },
      { media: ["g:ballcam"], big: "GOL BUNUH DIRI", sub: "PROTES KE WASIT" },
      { media: ["g:players"], big: "CHILL." },
    ],
  },
  {
    id: "maracanazo",
    title: "KEKALAHAN PALING TRAUMATIS",
    tag: "MARACANAZO · 1950",
    outro: "g:orbit",
    beats: [
      { media: ["r:maraca_stands@4"] },
      { media: ["r:rio", "r:poster1950"], big: "16 JULI 1950", sub: "BRASIL VS URUGUAY" },
      { media: ["r:match1950"], sub: "CUKUP SERI UNTUK JUARA" },
      { media: ["r:invasion1950", "g:orbit"], big: "±200.000", sub: "PENONTON DI MARACANÃ" },
      { media: ["r:match1950@2"], big: "URU 2-1 BRA" },
      { media: ["r:maraca_face", "r:maraca_stands"], big: "MARACANAZO" },
      { media: ["r:maraca_stands@6"], sub: "SERAGAM PUTIH DITINGGALKAN" },
      { media: ["g:tifo"], big: "LAHIR DARI PATAH HATI" },
    ],
  },
  {
    id: "perangbola",
    title: "PERANG GARA-GARA BOLA?",
    tag: "EL SALVADOR VS HONDURAS",
    outro: "g:kick_smoke",
    beats: [
      { media: ["r:celebrate1969"] },
      { media: ["r:flags_slv_hon"], big: "1969", sub: "KUALIFIKASI PIALA DUNIA" },
      { media: ["r:honduras_paper", "r:flags_slv_hon@4"], sub: "SENGKETA TANAH & MIGRAN" },
      { media: ["r:celebrate1969@4"], big: "SLV 3-2 HON", sub: "MEXICO CITY · PERPANJANGAN WAKTU" },
      { media: ["r:soldiers"], big: "±100 JAM", sub: "PERANG PECAH" },
      { media: ["r:redcross"], sub: "RIBUAN KORBAN JIWA" },
      { media: ["r:flags_slv_hon@7"], sub: "BOLA HANYA PEMICU" },
      { media: ["g:players"], big: "DI LAPANGAN AJA" },
    ],
  },
  {
    id: "bolatertua",
    title: "BOLA TERTUA DI DUNIA",
    tag: "STIRLING · SKOTLANDIA",
    outro: "g:ballcam",
    beats: [
      { media: ["r:oldball"] },
      { media: ["r:stirling_view", "r:oldball"], sub: "KASTIL STIRLING" },
      { media: ["r:oldball"], big: "1540-AN", sub: "HAMPIR 500 TAHUN" },
      { media: ["r:oldball"], sub: "KANDUNG KEMIH BABI + KULIT" },
      { media: ["g:rain"], big: "PAS HUJAN?" },
      { media: ["r:football_engraving"], big: "1800-AN", sub: "KARET VULKANISIR" },
      { media: ["g:ballcam"], sub: "BOLA MODERN" },
      { media: ["r:oldball"], big: "RESPECT THE OG" },
    ],
  },
  {
    id: "kartu",
    title: "KARTU MERAH DARI LAMPU MERAH",
    tag: "ASAL KARTU",
    outro: "g:broadcast",
    beats: [
      { media: ["r:trafficlight"] },
      { media: ["r:coleman", "r:santiago_match"], big: "1962", sub: "KEN ASTON · CHILE VS ITALIA" },
      { media: ["r:santiago_match@3"], big: "BATTLE OF SANTIAGO" },
      { media: ["r:bw_match"], sub: "BELUM ADA KARTU" },
      { media: ["r:old_stadium"], big: "1966", sub: "TAHU DARI KORAN BESOKNYA" },
      { media: ["r:trafficlight"], big: "KUNING · MERAH" },
      { media: ["r:ken_aston", "r:yellowcard"], big: "1970", sub: "PIALA DUNIA MEKSIKO" },
      { media: ["g:broadcast"], big: "LAMPU MERAH." },
    ],
  },
  {
    id: "gawang",
    title: "KENAPA GAWANG 7,32 METER?",
    tag: "UKURAN GAWANG",
    outro: "g:goal_net",
    beats: [
      { media: ["r:goal_frame"], big: "7,32 × 2,44 M" },
      { media: ["r:park_goal"], big: "8 YARD × 8 KAKI" },
      { media: ["r:goal_sunset"], sub: "PITA → MISTAR KAYU" },
      { media: ["r:ball_net", "r:oldgoal"], big: "±1890", sub: "JARING · JOHN BRODIE" },
      { media: ["r:oldgoal@3"], big: "MASUK ATAU NGGAK?" },
      { media: ["g:goal_net"], sub: "UKURAN TAK PERNAH BERUBAH" },
      { media: ["r:goal_frame"], sub: "USUL GAWANG DIPERBESAR" },
      { media: ["g:goal_net@1"], big: "THAT FEELING" },
    ],
  },
];
