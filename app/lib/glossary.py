from dataclasses import dataclass
from urllib.parse import quote_plus


@dataclass(frozen=True)
class GlossaryEntry:
    description: str
    search_query: str


TERMS: dict[str, GlossaryEntry] = {
    "株価トレンド": GlossaryEntry(
        "株価と短期・長期移動平均線の位置関係から、現在の大まかな方向性を判定したものです。",
        "株価 トレンド 移動平均線",
    ),
    "ゴールデンクロス": GlossaryEntry(
        "短期移動平均線が長期移動平均線を下から上へ抜ける現象です。上昇の兆候として使われますが、将来の上昇を保証しません。",
        "ゴールデンクロス 株",
    ),
    "PER": GlossaryEntry(
        "株価収益率。株価が1株当たり利益の何倍かを示す、利益に対する株価水準の指標です。",
        "PER 株価収益率 意味",
    ),
    "PBR": GlossaryEntry(
        "株価純資産倍率。株価が1株当たり純資産の何倍かを示します。",
        "PBR 株価純資産倍率 意味",
    ),
    "ROE": GlossaryEntry(
        "自己資本利益率。株主資本を使ってどれだけ利益を生み出したかを示します。",
        "ROE 自己資本利益率 意味",
    ),
    "時価総額": GlossaryEntry(
        "株価に発行済株式数を掛けた、株式市場における企業価値の目安です。",
        "時価総額 意味",
    ),
    "ADF p値": GlossaryEntry(
        "単位根の存在を帰無仮説とするADF検定のp値です。一般に小さいほど、時系列が定常である根拠が強まります。",
        "ADF検定 p値 単位根",
    ),
    "Ljung–Box p値": GlossaryEntry(
        "複数ラグの自己相関がすべてゼロという帰無仮説を検定するp値です。小さいほど自己相関の存在が示唆されます。",
        "Ljung Box検定 p値",
    ),
    "ラグ1自己相関": GlossaryEntry(
        "当日の値と1期前の値の線形な関連の強さです。-1から1の範囲を取ります。",
        "ラグ1 自己相関 意味",
    ),
}


def term_help(term: str) -> str | None:
    """Return Markdown help text with an optional external search link."""
    entry = TERMS.get(term)
    if entry is None:
        return None
    search_url = f"https://www.google.com/search?q={quote_plus(entry.search_query)}"
    return f"{entry.description}\n\n[Googleで詳しく調べる]({search_url})"
