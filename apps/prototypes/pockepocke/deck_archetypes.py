"""
deck_archetypes.py - 大規模軸定義 (生成数200〜300を想定)
各タイプごとに細かいシナジーやサブexを想定した「軸」を大量定義する。
"""
import copy

AXES = {
    # ===== 炎軸（フレイムパッチ推奨） =====
    "炎_メガリザX_速攻": { "axis_ex": ["メガリザードンXex"], "sub_ex_pool": ["エンテイex", "ウインディex"], "core_types": ["Fire"], "key_goods": ["フレイムパッチ"], "strategy": "aggro", "pin_mega": True },
    "炎_メガリザX_高火力": { "axis_ex": ["メガリザードンXex"], "sub_ex_pool": ["ホウオウex", "リザードンex"], "core_types": ["Fire"], "key_goods": ["フレイムパッチ", "博士の研究"], "strategy": "combo", "pin_mega": True },
    "炎_メガリザY_ワンパン": { "axis_ex": ["メガリザードンYex"], "sub_ex_pool": ["エンテイex"], "core_types": ["Fire"], "key_goods": ["フレイムパッチ"], "strategy": "aggro", "pin_mega": True },
    "炎_メガリザY_安定": { "axis_ex": ["メガリザードンYex"], "sub_ex_pool": ["ゴウカザルex", "ズガドーンex"], "core_types": ["Fire"], "key_goods": ["博士の研究"], "strategy": "tempo", "pin_mega": True },
    "炎_メガバシャ_再利用": { "axis_ex": ["メガバシャーモex"], "sub_ex_pool": ["エンテイex"], "core_types": ["Fire"], "key_goods": ["フレイムパッチ"], "strategy": "aggro", "pin_mega": True },
    "炎_エンテイ_ドロー": { "axis_ex": ["エンテイex"], "sub_ex_pool": ["メガリザードンXex", "ウインディex"], "core_types": ["Fire"], "key_goods": ["フレイムパッチ"], "strategy": "combo", "pin_mega": False },
    "炎_グレンアルマ_加速": { "axis_ex": ["グレンアルマex"], "sub_ex_pool": ["リザードンex", "ウインディex"], "core_types": ["Fire"], "key_goods": ["ふしぎなアメ"], "strategy": "combo", "pin_mega": False },
    "炎_ホウオウ_循環": { "axis_ex": ["ホウオウex"], "sub_ex_pool": ["エンテイex", "ゴウカザルex"], "core_types": ["Fire"], "key_goods": ["フレイムパッチ", "博士の研究"], "strategy": "tank", "pin_mega": False },

    # ===== 水軸（不思議な雨、カスミ推奨） =====
    "水_スイゲツ_環境": { "axis_ex": ["スイクンex", "ゲッコウガex"], "sub_ex_pool": ["フリーザーex"], "core_types": ["Water"], "key_goods": ["カスミ"], "strategy": "snipe", "pin_mega": False },
    "水_スイゲツ_ドロー": { "axis_ex": ["スイクンex", "ゲッコウガex"], "sub_ex_pool": ["パオジアンex", "ラプラスex"], "core_types": ["Water"], "key_goods": ["博士の研究", "モンスターボール"], "strategy": "tempo", "pin_mega": False },
    "水_フリスイ_後攻": { "axis_ex": ["フリーザーex", "スイクンex"], "sub_ex_pool": ["パオジアンex"], "core_types": ["Water"], "key_goods": ["カスミ", "ふしぎな広場"], "strategy": "tempo", "pin_mega": False },
    "水_パオジ_速攻": { "axis_ex": ["パオジアンex"], "sub_ex_pool": ["スイクンex", "ゲッコウガex"], "core_types": ["Water"], "key_goods": ["博士の研究"], "strategy": "aggro", "pin_mega": False },
    "水_メガギャラ_爆発": { "axis_ex": ["メガギャラドスex"], "sub_ex_pool": ["ギャラドスex", "ラプラスex"], "core_types": ["Water"], "key_goods": ["ふしぎなアメ"], "strategy": "combo", "pin_mega": True },
    "水_メガカメ_タンク": { "axis_ex": ["メガカメックスex"], "sub_ex_pool": ["カメックスex", "スイクンex"], "core_types": ["Water"], "key_goods": ["ふしぎなアメ", "きずぐすり"], "strategy": "tank", "pin_mega": True },
    "水_パルキア_高打点": { "axis_ex": ["パルキアex"], "sub_ex_pool": ["スイクンex", "アローラキュウコンex"], "core_types": ["Water"], "key_goods": ["カスミ"], "strategy": "combo", "pin_mega": False },

    # ===== 雷軸 =====
    "雷_メガライボ_速攻": { "axis_ex": ["メガライボルトex"], "sub_ex_pool": ["サンダースex", "ライチュウex"], "core_types": ["Lightning"], "key_goods": ["博士の研究"], "strategy": "aggro", "pin_mega": True },
    "雷_サンダース_加速": { "axis_ex": ["サンダースex"], "sub_ex_pool": ["ライコウex", "メガデンリュウex"], "core_types": ["Lightning"], "key_goods": ["モンスターボール"], "strategy": "combo", "pin_mega": False },
    "雷_ライコウ_2ex": { "axis_ex": ["ライコウex", "メガライボルトex"], "sub_ex_pool": ["サンダースex"], "core_types": ["Lightning"], "key_goods": ["博士の研究", "ふしぎなアメ"], "strategy": "combo", "pin_mega": True },
    "雷_ピカライ_進化": { "axis_ex": ["ピカチュウex", "ライチュウex"], "sub_ex_pool": ["サンダースex"], "core_types": ["Lightning"], "key_goods": ["モンスターボール"], "strategy": "aggro", "pin_mega": False },

    # ===== 超軸 =====
    "超_ミュウツ_サナ": { "axis_ex": ["ミュウツーex"], "sub_ex_pool": ["メガサーナイトex", "ミュウex"], "core_types": ["Psychic"], "key_goods": ["ふしぎなアメ"], "strategy": "control", "pin_mega": True },
    "超_ミュウ_完封": { "axis_ex": ["ミュウex"], "sub_ex_pool": ["ミュウツーex", "ネクロズマex"], "core_types": ["Psychic"], "key_goods": ["博士の研究", "きずぐすり"], "strategy": "control", "pin_mega": False },
    "超_ミュウゲン_2ex": { "axis_ex": ["ミュウツーex", "ゲンガーex"], "sub_ex_pool": ["ミュウex", "クレセリアex"], "core_types": ["Psychic"], "key_goods": ["博士の研究"], "strategy": "control", "pin_mega": False },
    "超_メガゲン_全体": { "axis_ex": ["メガゲンガーex"], "sub_ex_pool": ["ゲンガーex", "ミュウツーex"], "core_types": ["Psychic"], "key_goods": ["ふしぎなアメ", "博士の研究"], "strategy": "control", "pin_mega": True },
    "超_ネクロ_高火力": { "axis_ex": ["ネクロズマex"], "sub_ex_pool": ["ソルガレオex", "ルナアーラex"], "core_types": ["Psychic", "Metal"], "key_goods": ["モンスターボール"], "strategy": "combo", "pin_mega": False },
    "超_ルナアーラ_回復": { "axis_ex": ["ルナアーラex"], "sub_ex_pool": ["ソルガレオex", "クレセリアex"], "core_types": ["Psychic"], "key_goods": ["きずぐすり", "ふしぎなアメ"], "strategy": "tank", "pin_mega": False },

    # ===== 悪軸 =====
    "悪_サザンアブ_狙撃": { "axis_ex": ["メガアブソルex"], "sub_ex_pool": ["ダークライex", "ブラッキーex"], "core_types": ["Darkness"], "key_goods": ["博士の研究"], "strategy": "snipe", "pin_mega": True },
    "悪_ダーク_全体": { "axis_ex": ["ダークライex"], "sub_ex_pool": ["マニューラex", "アクジキングex"], "core_types": ["Darkness"], "key_goods": ["モンスターボール", "博士の研究"], "strategy": "combo", "pin_mega": False },
    "悪_アクジ_吸収": { "axis_ex": ["アクジキングex"], "sub_ex_pool": ["パルデアドオーex", "ブラッキーex"], "core_types": ["Darkness"], "key_goods": ["きずぐすり"], "strategy": "tank", "pin_mega": False },
    "悪_ブラッキ_強制": { "axis_ex": ["ブラッキーex"], "sub_ex_pool": ["マニューラex", "メガアブソルex"], "core_types": ["Darkness"], "key_goods": ["博士の研究"], "strategy": "control", "pin_mega": False },

    # ===== 格闘軸 =====
    "闘_ルカ_安定": { "axis_ex": ["ルカリオex"], "sub_ex_pool": ["ガブリアスex", "カイリキーex"], "core_types": ["Fighting"], "key_goods": ["博士の研究"], "strategy": "aggro", "pin_mega": False },
    "闘_ルカガブ_2ex": { "axis_ex": ["ルカリオex", "ガブリアスex"], "sub_ex_pool": ["マッシブーンex"], "core_types": ["Fighting"], "key_goods": ["モンスターボール", "ふしぎなアメ"], "strategy": "aggro", "pin_mega": False },
    "闘_ドンフ_耐久": { "axis_ex": ["ドンファンex"], "sub_ex_pool": ["ルカリオex", "ガラガラex"], "core_types": ["Fighting"], "key_goods": ["きずぐすり"], "strategy": "tank", "pin_mega": False },
    "闘_マッシ_詰め": { "axis_ex": ["マッシブーンex"], "sub_ex_pool": ["ルカリオex", "ガブリアスex"], "core_types": ["Fighting"], "key_goods": ["博士の研究"], "strategy": "aggro", "pin_mega": False },

    # ===== 鋼軸 =====
    "鋼_ディアルガ_ロマン": { "axis_ex": ["ディアルガex"], "sub_ex_pool": ["パルキアex"], "core_types": ["Metal", "Water"], "key_goods": ["ふしぎなアメ"], "strategy": "combo", "pin_mega": False },
    "鋼_ソルガレオ_コンボ": { "axis_ex": ["ソルガレオex"], "sub_ex_pool": ["ルナアーラex", "ネクロズマex"], "core_types": ["Metal", "Psychic"], "key_goods": ["博士の研究"], "strategy": "combo", "pin_mega": False },
    "鋼_サーフゴ_バフ": { "axis_ex": ["サーフゴーex"], "sub_ex_pool": ["メルメタルex", "メガハッサムex"], "core_types": ["Metal"], "key_goods": ["モンスターボール"], "strategy": "aggro", "pin_mega": False },
    "鋼_メガハガ_耐久": { "axis_ex": ["メガハガネールex"], "sub_ex_pool": ["メルメタルex", "エアームドex"], "core_types": ["Metal"], "key_goods": ["きずぐすり"], "strategy": "tank", "pin_mega": True },

    # ===== ドラゴン軸 =====
    "龍_レック_最強": { "axis_ex": ["レックウザex"], "sub_ex_pool": ["カイリューex", "ガブリアスex", "ギラティナex"], "core_types": ["Dragon"], "key_goods": ["ふしぎなアメ", "博士の研究"], "strategy": "aggro", "pin_mega": False },
    "龍_カイリュ_狙撃": { "axis_ex": ["カイリューex"], "sub_ex_pool": ["レックウザex", "メガラティオスex"], "core_types": ["Dragon"], "key_goods": ["モンスターボール"], "strategy": "snipe", "pin_mega": False },
    "龍_ウルネク_全体": { "axis_ex": ["ウルトラネクロズマex"], "sub_ex_pool": ["ギラティナex", "パルキアex"], "core_types": ["Dragon", "Psychic"], "key_goods": ["博士の研究"], "strategy": "combo", "pin_mega": False },

    # ===== 草軸 =====
    "草_フシギバ_どく": { "axis_ex": ["フシギバナex"], "sub_ex_pool": ["ミュウex", "メガフシギバナex"], "core_types": ["Grass"], "key_goods": ["博士の研究", "エリカ"], "strategy": "control", "pin_mega": True },
    "草_マスカ_妨害": { "axis_ex": ["マスカーニャex"], "sub_ex_pool": ["ジュナイパーex", "セレビィex"], "core_types": ["Grass"], "key_goods": ["エリカ"], "strategy": "control", "pin_mega": False },
    "草_エルフ_加速": { "axis_ex": ["エルフーンex"], "sub_ex_pool": ["フシギバナex", "メガカイロスex"], "core_types": ["Grass"], "key_goods": ["博士の研究"], "strategy": "combo", "pin_mega": False },

    # ===== 無色軸 =====
    "無色_ルギア_加速": { "axis_ex": ["ルギアex"], "sub_ex_pool": ["カビゴンex", "ピジョットex"], "core_types": ["Colorless"], "key_goods": ["博士の研究", "モンスターボール"], "strategy": "combo", "pin_mega": False },
    "無色_カビゴン_耐久": { "axis_ex": ["カビゴンex"], "sub_ex_pool": ["ルギアex", "ハピナスex"], "core_types": ["Colorless"], "key_goods": ["きずぐすり"], "strategy": "tank", "pin_mega": False },
    "無色_メガピジョ_速攻": { "axis_ex": ["メガピジョットex"], "sub_ex_pool": ["ピジョットex", "ルギアex"], "core_types": ["Colorless"], "key_goods": ["ふしぎなアメ"], "strategy": "aggro", "pin_mega": True },
}

VARIANT_PATTERNS = [
    {"name": "安定_サブ2枚", "sub_count": 2, "pin_mega": False, "goods_heavy": False},
    {"name": "安定_サブ1ピン刺し", "sub_count": 1, "pin_mega": False, "goods_heavy": False},
    {"name": "グッズ偏重_サブ2", "sub_count": 2, "pin_mega": False, "goods_heavy": True},
    {"name": "グッズ偏重_ピンサブ", "sub_count": 1, "pin_mega": False, "goods_heavy": True},
    {"name": "メガピン刺し_サブ1", "sub_count": 1, "pin_mega": True,  "goods_heavy": False},
    {"name": "純正_サブ0枚", "sub_count": 0, "pin_mega": False, "goods_heavy": True},
]

def generate_all_archetypes():
    archetypes = {}
    for axis_name, axis in AXES.items():
        for vi, vp in enumerate(VARIANT_PATTERNS):
            if vp.get("pin_mega") and not axis.get("pin_mega"): continue

            key = f"{axis_name}_V{vi+1}_{vp['name']}"
            sub_pool = axis["sub_ex_pool"]
            
            sub_count = min(vp["sub_count"], len(sub_pool))
            subs = sub_pool[:sub_count]
            
            archetypes[key] = {
                "axis_ex": axis["axis_ex"],
                "sub_ex": subs,
                "core_types": axis["core_types"],
                "key_goods": axis["key_goods"],
                "strategy": axis["strategy"],
                "pin_mega": vp.get("pin_mega", False) and axis.get("pin_mega", False),
                "goods_heavy": vp.get("goods_heavy", False),
            }
    return archetypes

ARCHETYPES = generate_all_archetypes()
