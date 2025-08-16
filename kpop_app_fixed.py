import os, streamlit as st
import plotly.graph_objects as go
import pandas as pd
import openai
from typing import Dict, List
import json

# 页面配置
st.set_page_config(
    page_title="K-pop創作適性診断",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS样式 - 引用外部文件
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "aespa_cyber_css.css")
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # 添加简化的radio样式
    st.markdown("""
    <style>
    /* 简化的radio选项样式 */
    .stRadio > div {
        gap: 18px !important;
    }
    
    .stRadio > div > label {
        background: linear-gradient(135deg, 
            rgba(255, 255, 255, 0.06) 0%, 
            rgba(255, 182, 217, 0.03) 50%,
            rgba(255, 255, 255, 0.04) 100%) !important;
        backdrop-filter: blur(15px) !important;
        border: 1.5px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 20px !important;
        padding: 25px !important;
        margin-bottom: 18px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
        position: relative !important;
        display: flex !important;
        align-items: flex-start !important;
        gap: 15px !important;
        color: #ffffff !important;
        font-family: 'M PLUS Rounded 1c', sans-serif !important;
    }
    
    .stRadio > div > label:hover {
        border: 2px solid rgba(0, 212, 255, 0.6) !important;
        background: linear-gradient(135deg, 
            rgba(0, 212, 255, 0.08) 0%, 
            rgba(168, 230, 207, 0.05) 50%,
            rgba(255, 182, 217, 0.06) 100%) !important;
        transform: translateY(-5px) scale(1.02) !important;
        box-shadow: 0 15px 40px rgba(0, 212, 255, 0.2) !important;
    }
    
    .stRadio > div > label > div:last-child {
        color: #ffffff !important;
        font-family: 'M PLUS Rounded 1c', sans-serif !important;
        font-weight: 500 !important;
        line-height: 1.5 !important;
        font-size: 1.1rem !important;
    }
    
    /* 选中状态 */
    .stRadio > div > label:has(input[checked]) {
        border: 2px solid rgba(255, 182, 217, 0.8) !important;
        background: linear-gradient(135deg, 
            rgba(255, 182, 217, 0.12) 0%, 
            rgba(0, 212, 255, 0.06) 50%,
            rgba(168, 230, 207, 0.08) 100%) !important;
        box-shadow: 0 20px 50px rgba(255, 182, 217, 0.25) !important;
        transform: translateY(-5px) scale(1.02) !important;
    }
    
    /* Radio按钮样式 */
    .stRadio input[type="radio"] {
        width: 20px !important;
        height: 20px !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 50% !important;
        background: transparent !important;
        appearance: none !important;
        flex-shrink: 0 !important;
        margin: 3px 0 0 0 !important;
    }
    
    .stRadio input[type="radio"]:checked {
        border-color: rgba(255, 182, 217, 0.8) !important;
        background: radial-gradient(circle, #FFB6D9 30%, transparent 30%) !important;
        box-shadow: 0 0 15px rgba(255, 182, 217, 0.6) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
# 问题数据
QUESTIONS = [
    {
        "text": "普段よく飲むコーヒーは？",
        "options": [
            {
                "text": "ブラック一択",
                "desc": "余計なものはいらない派",
                "weights": {"concept": 2, "producer": 2, "lyric": 0, "visual": 0, "performance": 0, "fan": 0},
                "tags": ["Analytical", "Creative"]
            },
            {
                "text": "ラテとかミルク系",
                "desc": "バランス重視で安心する",
                "weights": {"concept": 0, "producer": 1, "lyric": 0, "visual": 2, "performance": 0, "fan": 1},
                "tags": ["Coordinative", "Analytical"]
            },
            {
                "text": "その日の気分で毎回違うやつ",
                "desc": "飽きるのが嫌",
                "weights": {"concept": 0, "producer": 0, "lyric": 2, "visual": 0, "performance": 2, "fan": 0},
                "tags": ["Creative", "Performing"]
            },
            {
                "text": "いつも同じお気に入りの一杯",
                "desc": "これが一番落ち着く",
                "weights": {"concept": 0, "producer": 2, "lyric": 0, "visual": 0, "performance": 0, "fan": 2},
                "tags": ["Analytical", "Coordinative"]
            },
            {
                "text": "実はコーヒーよりお茶派",
                "desc": "みんなと違うけどこれが好き",
                "weights": {"concept": 2, "producer": 0, "lyric": 1, "visual": 0, "performance": 0, "fan": 0},
                "tags": ["Creative", "Analytical"]
            }
        ]
    },
    {
        "text": "朝起きてすぐ聞きたい音楽は？",
        "options": [
            {
                "text": "静かなアコースティック系",
                "desc": "ゆっくり目覚めたい",
                "weights": {"concept": 2, "producer": 0, "lyric": 2, "visual": 0, "performance": 0, "fan": 0},
                "tags": ["Creative", "Coordinative"]
            },
            {
                "text": "アップテンポなやつ",
                "desc": "テンション上げて一日をスタート",
                "weights": {"concept": 0, "producer": 0, "lyric": 0, "visual": 0, "performance": 3, "fan": 1},
                "tags": ["Performing", "Coordinative"]
            },
            {
                "text": "心に響く歌詞のバラード",
                "desc": "感情を整理したい",
                "weights": {"concept": 1, "producer": 0, "lyric": 3, "visual": 0, "performance": 0, "fan": 0},
                "tags": ["Creative", "Coordinative"]
            },
            {
                "text": "電子音楽とかクールなサウンド",
                "desc": "なんかかっこいい気分になりたい",
                "weights": {"concept": 0, "producer": 3, "lyric": 0, "visual": 1, "performance": 0, "fan": 0},
                "tags": ["Analytical", "Creative"]
            },
            {
                "text": "その時のバイブスで決める",
                "desc": "気分に任せる派",
                "weights": {"concept": 0, "producer": 0, "lyric": 1, "visual": 0, "performance": 2, "fan": 0},
                "tags": ["Performing", "Creative"]
            }
        ]
    },
    {
        "text": "スマホの待ち受け画面は？",
        "options": [
            {
                "text": "シンプルな単色とか抽象的なやつ",
                "desc": "ごちゃごちゃしてるの苦手",
                "weights": {"concept": 2, "producer": 1, "lyric": 0, "visual": 0, "performance": 0, "fan": 0},
                "tags": ["Analytical", "Creative"]
            },
            {
                "text": "推しの写真",
                "desc": "毎日見て元気もらってる",
                "weights": {"concept": 0, "producer": 0, "lyric": 0, "visual": 0, "performance": 1, "fan": 3},
                "tags": ["Coordinative", "Performing"]
            },
            {
                "text": "風景とか自然の写真",
                "desc": "癒やされたい",
                "weights": {"concept": 1, "producer": 0, "lyric": 0, "visual": 3, "performance": 0, "fan": 0},
                "tags": ["Creative", "Coordinative"]
            },
            {
                "text": "家族とか友達の写真",
                "desc": "大切な人を忘れたくない",
                "weights": {"concept": 0, "producer": 0, "lyric": 2, "visual": 0, "performance": 0, "fan": 2},
                "tags": ["Coordinative", "Creative"]
            },
            {
                "text": "特にこだわりなし、デフォルトのまま",
                "desc": "面倒くさい",
                "weights": {"concept": 0, "producer": 2, "lyric": 0, "visual": 0, "performance": 0, "fan": 1},
                "tags": ["Analytical"]
            }
        ]
    },
    {
        "text": "無人島に一つだけ持っていけるとしたら？",
        "options": [
            {
                "text": "哲学書とか、深く考えられる本",
                "desc": "ひとりの時間を大切にしたい",
                "weights": {"concept": 3, "producer": 0, "lyric": 1, "visual": 0, "performance": 0, "fan": 0},
                "tags": ["Creative", "Analytical"]
            },
            {
                "text": "ナイフとかサバイバルグッズ",
                "desc": "とりあえず生き延びることを考える",
                "weights": {"concept": 0, "producer": 3, "lyric": 0, "visual": 0, "performance": 1, "fan": 0},
                "tags": ["Analytical", "Performing"]
            },
            {
                "text": "日記帳とペン",
                "desc": "自分の気持ちを書き留めておきたい",
                "weights": {"concept": 1, "producer": 0, "lyric": 3, "visual": 0, "performance": 0, "fan": 0},
                "tags": ["Creative", "Coordinative"]
            },
            {
                "text": "楽器か音が出るもの",
                "desc": "音楽がないと生きていけない",
                "weights": {"concept": 0, "producer": 1, "lyric": 0, "visual": 0, "performance": 3, "fan": 0},
                "tags": ["Performing", "Creative"]
            },
            {
                "text": "スマホ",
                "desc": "圏外でも写真とか撮りたい...",
                "weights": {"concept": 0, "producer": 0, "lyric": 0, "visual": 2, "performance": 0, "fan": 2},
                "tags": ["Coordinative", "Creative"]
            }
        ]
    },
    {
        "text": "タイムスリップできるなら、どの時代に行きたい？",
        "options": [
            {
                "text": "古代ギリシャとか、哲学が生まれた時代",
                "desc": "人類の知恵の原点を見てみたい",
                "weights": {"concept": 3, "producer": 0, "lyric": 1, "visual": 0, "performance": 0, "fan": 0},
                "tags": ["Creative", "Analytical"]
            },
            {
                "text": "産業革命とか、技術革新の現場",
                "desc": "歴史が動く瞬間に立ち会いたい",
                "weights": {"concept": 1, "producer": 3, "lyric": 0, "visual": 0, "performance": 0, "fan": 0},
                "tags": ["Analytical", "Creative"]
            },
            {
                "text": "平安時代とか、美しい文化が花開いた時代",
                "desc": "美意識の極致を体験したい",
                "weights": {"concept": 1, "producer": 0, "lyric": 0, "visual": 3, "performance": 0, "fan": 0},
                "tags": ["Creative", "Coordinative"]
            },
            {
                "text": "60年代とか、音楽文化が爆発した時代",
                "desc": "伝説のライブを生で見たい",
                "weights": {"concept": 0, "producer": 0, "lyric": 0, "visual": 0, "performance": 3, "fan": 1},
                "tags": ["Performing", "Coordinative"]
            },
            {
                "text": "未来",
                "desc": "今よりもっと進化した世界を見てみたい",
                "weights": {"concept": 0, "producer": 1, "lyric": 0, "visual": 1, "performance": 0, "fan": 2},
                "tags": ["Analytical", "Creative"]
            }
        ]
    },
    {
        "text": "ペットが急にK-pop歌い出したら？",
        "options": [
            {
                "text": "え、これやばくない？どういう現象？",
                "desc": "まず状況を理解したい",
                "weights": {"concept": 3, "producer": 1, "lyric": 0, "visual": 0, "performance": 0, "fan": 0},
                "tags": ["Analytical", "Creative"]
            },
            {
                "text": "とりあえず動画撮ってSNSに上げる",
                "desc": "みんなに見せたい！",
                "weights": {"concept": 0, "producer": 0, "lyric": 0, "visual": 1, "performance": 0, "fan": 3},
                "tags": ["Coordinative", "Performing"]
            },
            {
                "text": "音程とかリズム感をチェックしちゃう",
                "desc": "気になる性格",
                "weights": {"concept": 0, "producer": 3, "lyric": 0, "visual": 0, "performance": 0, "fan": 0},
                "tags": ["Analytical"]
            },
            {
                "text": "なんか感動して泣きそうになる",
                "desc": "感情が先に来る",
                "weights": {"concept": 1, "producer": 0, "lyric": 3, "visual": 0, "performance": 0, "fan": 0},
                "tags": ["Creative", "Coordinative"]
            },
            {
                "text": "ダンスも覚えさせてみたくなる",
                "desc": "もっと発展させたい",
                "weights": {"concept": 0, "producer": 0, "lyric": 0, "visual": 1, "performance": 3, "fan": 0},
                "tags": ["Performing", "Creative"]
            }
        ]
    },
    {
        "text": "友達にK-pop曲を推薦するなら？",
        "options": [
            {
                "text": "まずその人の好みを聞いて慎重に選ぶ",
                "desc": "相手のことを理解してから",
                "weights": {"concept": 1, "producer": 0, "lyric": 0, "visual": 0, "performance": 0, "fan": 3},
                "tags": ["Coordinative", "Analytical"]
            },
            {
                "text": "音楽的に完成度高いやつを推す",
                "desc": "クオリティで勝負",
                "weights": {"concept": 0, "producer": 3, "lyric": 0, "visual": 0, "performance": 0, "fan": 0},
                "tags": ["Analytical"]
            },
            {
                "text": "歌詞が刺さりそうなやつを選ぶ",
                "desc": "感情的に響きそうなもの",
                "weights": {"concept": 0, "producer": 0, "lyric": 3, "visual": 0, "performance": 0, "fan": 1},
                "tags": ["Creative", "Coordinative"]
            },
            {
                "text": "とりあえず今バズってるやつ",
                "desc": "みんなが聞いてるから安心",
                "weights": {"concept": 0, "producer": 0, "lyric": 0, "visual": 0, "performance": 1, "fan": 3},
                "tags": ["Coordinative", "Performing"]
            },
            {
                "text": "自分が一番好きなやつを熱弁",
                "desc": "自分の想いを伝えたい",
                "weights": {"concept": 2, "producer": 0, "lyric": 2, "visual": 0, "performance": 0, "fan": 0},
                "tags": ["Creative", "Performing"]
            }
        ]
    },
    {
        "text": "おばあちゃんにK-popダンスを教えるとしたら？",
        "options": [
            {
                "text": "まず簡単な手の動きから始める",
                "desc": "安全第一で段階的に",
                "weights": {"concept": 0, "producer": 2, "lyric": 0, "visual": 0, "performance": 0, "fan": 2},
                "tags": ["Analytical", "Coordinative"]
            },
            {
                "text": "おばあちゃんが知ってそうな曲調のやつを選ぶ",
                "desc": "親しみやすさ重視",
                "weights": {"concept": 2, "producer": 0, "lyric": 2, "visual": 0, "performance": 0, "fan": 0},
                "tags": ["Creative", "Coordinative"]
            },
            {
                "text": "一緒に楽しめる雰囲気作りを大切にする",
                "desc": "コミュニケーション重視",
                "weights": {"concept": 0, "producer": 0, "lyric": 1, "visual": 0, "performance": 0, "fan": 3},
                "tags": ["Coordinative", "Performing"]
            },
            {
                "text": "動画見せながら「こんな感じで〜」って説明",
                "desc": "ビジュアルで分かりやすく",
                "weights": {"concept": 0, "producer": 1, "lyric": 0, "visual": 3, "performance": 0, "fan": 0},
                "tags": ["Creative", "Analytical"]
            },
            {
                "text": "とりあえずノリで一緒に体動かす",
                "desc": "理屈より楽しさ優先",
                "weights": {"concept": 0, "producer": 0, "lyric": 0, "visual": 0, "performance": 3, "fan": 1},
                "tags": ["Performing", "Coordinative"]
            }
        ]
    },
    {
        "text": "電車で携帯の充電が切れたら？",
        "options": [
            {
                "text": "窓の外をぼーっと眺めて考え事",
                "desc": "内省モード",
                "weights": {"concept": 3, "producer": 0, "lyric": 1, "visual": 0, "performance": 0, "fan": 0},
                "tags": ["Creative", "Analytical"]
            },
            {
                "text": "車内の広告とか人間観察する",
                "desc": "周りの情報をインプット",
                "weights": {"concept": 0, "producer": 0, "lyric": 0, "visual": 2, "performance": 0, "fan": 2},
                "tags": ["Creative", "Coordinative"]
            },
            {
                "text": "目を閉じて音楽のメロディとか思い出す",
                "desc": "内なる感性と向き合う",
                "weights": {"concept": 0, "producer": 0, "lyric": 2, "visual": 0, "performance": 2, "fan": 0},
                "tags": ["Creative", "Performing"]
            },
            {
                "text": "降りた後のプランを頭の中で整理",
                "desc": "効率的に時間を使う",
                "weights": {"concept": 1, "producer": 3, "lyric": 0, "visual": 0, "performance": 0, "fan": 0},
                "tags": ["Analytical"]
            },
            {
                "text": "隣の人に「充電貸してもらえませんか」って声かける",
                "desc": "積極的に解決",
                "weights": {"concept": 0, "producer": 0, "lyric": 0, "visual": 0, "performance": 1, "fan": 3},
                "tags": ["Coordinative", "Performing"]
            }
        ]
    },
    {
        "text": "好きなK-pop曲がAI作曲だったと知ったら？",
        "options": [
            {
                "text": "「音楽の本質って何だろう」って考え込む",
                "desc": "哲学的に気になる",
                "weights": {"concept": 3, "producer": 0, "lyric": 1, "visual": 0, "performance": 0, "fan": 0},
                "tags": ["Creative", "Analytical"]
            },
            {
                "text": "クオリティ高いなら別に問題なくない？",
                "desc": "結果重視",
                "weights": {"concept": 0, "producer": 3, "lyric": 0, "visual": 0, "performance": 0, "fan": 1},
                "tags": ["Analytical", "Coordinative"]
            },
            {
                "text": "なんか複雑な気持ちになる",
                "desc": "感情がモヤモヤする",
                "weights": {"concept": 1, "producer": 0, "lyric": 3, "visual": 0, "performance": 0, "fan": 0},
                "tags": ["Creative", "Coordinative"]
            },
            {
                "text": "逆にかっこいいかも、時代だなあ",
                "desc": "新しい価値観で受け入れる",
                "weights": {"concept": 0, "producer": 0, "lyric": 0, "visual": 2, "performance": 2, "fan": 0},
                "tags": ["Creative", "Performing"]
            },
            {
                "text": "みんなの反応が気になる",
                "desc": "コミュニティの動向をチェック",
                "weights": {"concept": 0, "producer": 0, "lyric": 0, "visual": 1, "performance": 0, "fan": 3},
                "tags": ["Coordinative", "Performing"]
            }
        ]
    }
]

# 角色定義
ROLES = {
    "concept": {
        "title": "🎭 Concept Creator",
        "subtitle": "世界観の設計者",
        "description": "あなたは作品全体の方向性とメッセージを描く、創作プロセスの司令塔タイプです。",
        "strengths": [
            "複雑なアイデアを整理し、一貫したストーリーに組み立てる能力",
            "チーム全体に共通のビジョンを伝える統率力",
            "文化的・社会的文脈を作品に織り込む洞察力"
        ],
        "career": [
            "A&R（Artist & Repertoire）プロデューサー",
            "クリエイティブディレクター",
            "プロジェクトプロデューサー",
            "コンテンツプランナー"
        ],
        "next_steps": [
            "プロジェクト管理のスキルを磨く",
            "業界トレンドと文化的背景の研究",
            "多様なクリエイターとのネットワーク構築"
        ]
    },
    "producer": {
        "title": "🎹 Music Producer",
        "subtitle": "サウンドの魔術師",
        "description": "あなたは技術的精度と音楽的革新を両立する、制作の中核を担うタイプです。",
        "strengths": [
            "音楽理論と最新技術を融合させる専門性",
            "細部への集中力と完璧主義的な品質管理",
            "トレンドを先読みしながら独自性を生み出す能力"
        ],
        "career": [
            "音楽プロデューサー",
            "作曲家・編曲家",
            "サウンドエンジニア",
            "オーディオディレクター"
        ],
        "next_steps": [
            "DAWソフトウェアと音響技術の習得",
            "音楽理論と作曲技法の深化",
            "業界プロデューサーとの実習・コラボ経験"
        ]
    },
    "lyric": {
        "title": "✏️ Lyric Writer",
        "subtitle": "言葉の詩人",
        "description": "あなたは感情を言葉に変換し、人の心に直接響く表現を生み出すタイプです。",
        "strengths": [
            "複雑な感情を的確な言葉で表現する語彙力",
            "リズムと意味を両立させる詩的センス",
            "ターゲット層の心理と感性を理解する共感力"
        ],
        "career": [
            "作詞家",
            "シンガーソングライター",
            "コピーライター",
            "コンテンツライター"
        ],
        "next_steps": [
            "多言語での作詞スキル（韓国語、英語など）",
            "詩や文学の創作技法を学ぶ",
            "音楽のリズムと言葉の関係性を研究"
        ]
    },
    "visual": {
        "title": "🎬 Visual Director",
        "subtitle": "映像の芸術家",
        "description": "あなたは音楽を視覚的世界に翻訳し、記憶に残る美的体験を創造するタイプです。",
        "strengths": [
            "音楽と映像を融合させる感性",
            "色彩・構図・演出に対する美的感覚",
            "技術的制約の中で創造性を発揮する適応力"
        ],
        "career": [
            "ミュージックビデオディレクター",
            "映像クリエイター",
            "ビジュアルアートディレクター",
            "グラフィックデザイナー"
        ],
        "next_steps": [
            "映像制作ソフトウェアの習得",
            "映画・映像表現の研究",
            "フォトグラフィーと色彩理論の学習"
        ]
    },
    "performance": {
        "title": "💃 Performance Designer",
        "subtitle": "動きの演出家",
        "description": "あなたは身体表現と空間演出で観客の感情を直接的に動かすタイプです。",
        "strengths": [
            "身体の動きで音楽を表現する空間認識力",
            "観客との一体感を創り出すステージング力",
            "エネルギーとリズムを視覚化する感性"
        ],
        "career": [
            "コリオグラファー（振付師）",
            "ステージディレクター",
            "パフォーマンスコーチ",
            "イベントプロデューサー"
        ],
        "next_steps": [
            "ダンスと身体表現の技術向上",
            "ステージ演出と照明の知識習得",
            "アーティストとの振付コラボ経験"
        ]
    },
    "fan": {
        "title": "📱 Fan Experience Architect",
        "subtitle": "絆の設計者",
        "description": "あなたはアーティストとファンの間に持続的な関係性を築く、戦略的思考を持つタイプです。",
        "strengths": [
            "ファン心理とコミュニティ動向を読み取る分析力",
            "デジタルツールを活用したマーケティング戦略",
            "長期的な関係性を築くビジネス設計力"
        ],
        "career": [
            "ファンマーケティングマネージャー",
            "SNSストラテジスト",
            "デジタルマーケティングプランナー",
            "コミュニティマネージャー"
        ],
        "next_steps": [
            "デジタルマーケティングツールの習得",
            "データ分析とファン行動心理の研究",
            "SNSプラットフォームとコンテンツ戦略の学習"
        ]
    }
}

def initialize_session_state():
    """初始化session state"""
  
    if 'show_welcome' not in st.session_state:
        st.session_state.show_welcome = True
   
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'scores' not in st.session_state:
        st.session_state.scores = {
            'concept': 0, 'producer': 0, 'lyric': 0, 
            'visual': 0, 'performance': 0, 'fan': 0
        }
    if 'answers' not in st.session_state:
        st.session_state.answers = []
    if 'show_result' not in st.session_state:
        st.session_state.show_result = False

def render_progress_bar():
    """渲染进度条"""
    progress = (st.session_state.current_question + 1) / len(QUESTIONS)
    
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {progress * 100}%"></div>
    </div>
    <div class="progress-text">
        質問 {st.session_state.current_question + 1}/{len(QUESTIONS)}
    </div>
    """, unsafe_allow_html=True)

def render_question():
    """渲染当前问题 - 修复版本"""
    question = QUESTIONS[st.session_state.current_question]
    
    # 问题文字直接显示
    st.markdown(f"""
    <div class="main-container">
    <div class="question-text">{question['text']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 创建选项文本，让Streamlit能正常显示
    option_texts = []
    for option in question['options']:
        # 组合主文本和描述文本，格式更清晰
        combined_text = f"{option['text']} — {option['desc']}"
        option_texts.append(combined_text)
    
    # 使用Streamlit原生radio
    selected = st.radio(
        "選択してください：",
        option_texts,
        key=f"question_{st.session_state.current_question}",
        label_visibility="collapsed"
    )
    
    return selected

def calculate_scores(selected_option_text, question_idx):
    """计算得分"""
    question = QUESTIONS[question_idx]
    
    # 找到选择的选项
    for i, option in enumerate(question['options']):
        if selected_option_text.startswith(option['text']):
            # 更新得分
            for role, weight in option['weights'].items():
                st.session_state.scores[role] += weight
            break

def get_result():
    """获取诊断结果"""
    max_score = max(st.session_state.scores.values())
    result_role = [role for role, score in st.session_state.scores.items() if score == max_score][0]
    return result_role

def render_radar_chart():
    """生成雷达图 - aespa cyber风格"""
    categories = ['Concept', 'Producer', 'Lyric', 'Visual', 'Performance', 'Fan']
    values = [st.session_state.scores[role.lower()] for role in categories]
    
    fig = go.Figure()
    
    # 主要数据线 - 霓虹粉红色
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='あなたの適性',
        line=dict(color='#ff006e', width=3),
        fillcolor='rgba(255, 0, 110, 0.15)',
        marker=dict(color='#ff006e', size=8, symbol='circle')
    ))
    
    # 添加发光效果 - 青色边框
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill=None,
        name='',
        line=dict(color='#00ffff', width=1.5),
        showlegend=False,
        marker=dict(color='#00ffff', size=4, symbol='circle')
    ))
    
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0, 0, 0, 0.3)',
            radialaxis=dict(
                visible=True,
                range=[0, max(values) + 3],
                gridcolor='rgba(0, 255, 255, 0.2)',
                gridwidth=1,
                linecolor='rgba(0, 255, 255, 0.3)',
                tickcolor='#00ffff',
                tickfont=dict(color='#00ffff', size=10, family='Orbitron'),
                showticklabels=True
            ),
            angularaxis=dict(
                gridcolor='rgba(255, 0, 110, 0.2)',
                gridwidth=1,
                linecolor='rgba(255, 0, 110, 0.3)',
                tickcolor='#ff006e',
                tickfont=dict(color='#ffffff', size=12, family='Orbitron', weight='bold'),
                showticklabels=True
            )
        ),
        showlegend=False,
        title=dict(
            text="🎯 あなたの創作適性マップ",
            x=0.5,
            y=0.95,
            font=dict(
                color='#ffffff',
                size=20,
                family='Orbitron',
                weight='bold'
            )
        ),
        width=600,
        height=500,
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(t=80, b=20, l=20, r=20)
    )
    
    # 添加发光边框效果
    fig.update_layout(
        shapes=[
            dict(
                type="circle",
                xref="paper", yref="paper",
                x0=0.1, y0=0.1, x1=0.9, y1=0.9,
                line=dict(color="rgba(0, 255, 255, 0.3)", width=2, dash="dot"),
            )
        ]
    )
    
    return fig

def generate_ai_analysis(result_role, scores):
    """AI分析生成（需要配置OpenAI API）"""
    try:
        # 这里需要配置你的OpenAI API key
        # openai.api_key = "your-api-key"
        
        prompt = f"""
        ユーザーのK-pop創作適性診断結果を分析してください。

        結果：{ROLES[result_role]['title']}
        各分野のスコア：{scores}

        以下の形式で、個性的で具体的なアドバイスを200字程度で生成してください：
        - その人の特徴的な強み
        - 具体的な行動提案
        - 業界での成功のヒント
        """
        
        # response = openai.Completion.create(
        #     engine="text-davinci-003",
        #     prompt=prompt,
        #     max_tokens=300,
        #     temperature=0.7
        # )
        # return response.choices[0].text.strip()
        
        # APIが設定されていない場合のフォールバック
        return "🤖 AI分析機能は現在準備中です。OpenAI APIキーを設定すると、個性的な分析を受け取ることができます！"
        
    except Exception as e:
        return f"AI分析でエラーが発生しました: {str(e)}"

def render_result():
    """结果页面 - 重新设计布局"""
    result_role = get_result()
    role_data = ROLES[result_role]
    
    # 主标题区域
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 40px;">
        <div class="result-role">{role_data['title']}</div>
        <div style="font-family: 'Poppins', sans-serif; font-size: 1.4em; color: #00ffff; 
                    text-shadow: 0 0 15px #00ffff; margin-bottom: 20px;">
            {role_data['subtitle']}
        </div>
        <div class="result-description">{role_data['description']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 雷达图重点展示区域
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
                border: 1px solid rgba(0, 255, 255, 0.3); border-radius: 25px; padding: 30px;
                margin-bottom: 40px; backdrop-filter: blur(15px);
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1);">
    """, unsafe_allow_html=True)
    
    # 雷达图居中显示
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        fig = render_radar_chart()
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 详细信息分区块展示
    col1, col2 = st.columns(2)
    
    with col1:
        # 强项区块
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(255, 0, 110, 0.08) 0%, rgba(255, 0, 110, 0.02) 100%);
                    border: 1px solid rgba(255, 0, 110, 0.3); border-radius: 20px; padding: 25px;
                    margin-bottom: 20px; backdrop-filter: blur(10px);
                    box-shadow: 0 15px 35px rgba(255, 0, 110, 0.1);">
            <h3 style="color: #ff006e; font-family: 'Orbitron', monospace; 
                       text-shadow: 0 0 15px #ff006e; margin-bottom: 20px;">
                🎯 あなたの強み
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        for strength in role_data['strengths']:
            st.markdown(f"""
            <div style="color: #ffffff; font-family: 'Poppins', sans-serif; 
                       margin-bottom: 15px; padding-left: 20px; position: relative;
                       line-height: 1.5;">
                <span style="position: absolute; left: 0; color: #00ffff; text-shadow: 0 0 5px #00ffff;">▶</span>
                {strength}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # 推奨キャリア区块
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(0, 255, 255, 0.08) 0%, rgba(0, 255, 255, 0.02) 100%);
                    border: 1px solid rgba(0, 255, 255, 0.3); border-radius: 20px; padding: 25px;
                    margin-bottom: 20px; backdrop-filter: blur(10px);
                    box-shadow: 0 15px 35px rgba(0, 255, 255, 0.1);">
            <h3 style="color: #00ffff; font-family: 'Orbitron', monospace; 
                       text-shadow: 0 0 15px #00ffff; margin-bottom: 20px;">
                💼 推奨キャリアパス
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        for career in role_data['career']:
            st.markdown(f"""
            <div style="color: #ffffff; font-family: 'Poppins', sans-serif; 
                       margin-bottom: 15px; padding-left: 20px; position: relative;
                       line-height: 1.5;">
                <span style="position: absolute; left: 0; color: #ff006e; text-shadow: 0 0 5px #ff006e;">▶</span>
                {career}
            </div>
            """, unsafe_allow_html=True)
    
    # 次のステップ区块（全宽）
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(138, 43, 226, 0.08) 0%, rgba(138, 43, 226, 0.02) 100%);
                border: 1px solid rgba(138, 43, 226, 0.3); border-radius: 20px; padding: 25px;
                margin: 30px 0; backdrop-filter: blur(10px);
                box-shadow: 0 15px 35px rgba(138, 43, 226, 0.1);">
        <h3 style="color: #8a2be2; font-family: 'Orbitron', monospace; 
                   text-shadow: 0 0 15px #8a2be2; margin-bottom: 20px; text-align: center;">
            📈 次のステップ
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 分栏显示next steps
    cols = st.columns(len(role_data['next_steps']))
    for i, step in enumerate(role_data['next_steps']):
        with cols[i]:
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <div style="color: #ffffff; font-family: 'Poppins', sans-serif; 
                           font-size: 1.1em; line-height: 1.5;
                           background: rgba(255, 255, 255, 0.03); 
                           border-radius: 15px; padding: 20px;
                           border: 1px solid rgba(255, 255, 255, 0.1);">
                    <span style="color: #8a2be2; font-size: 1.5em; margin-bottom: 10px; display: block;">
                        {i+1}
                    </span>
                    {step}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # AI分析区块
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
                border: 1px solid rgba(0, 255, 255, 0.3); border-radius: 20px; padding: 25px;
                margin-top: 30px; backdrop-filter: blur(10px);
                box-shadow: 0 15px 35px rgba(0, 255, 255, 0.1);">
        <h3 style="color: #00ffff; font-family: 'Orbitron', monospace; 
                   text-shadow: 0 0 15px #00ffff; margin-bottom: 20px;">
            🤖 AI個別分析
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    ai_analysis = generate_ai_analysis(result_role, st.session_state.scores)
    st.markdown(f"""
    <div style="background: rgba(0, 255, 255, 0.05); border: 1px solid rgba(0, 255, 255, 0.2);
                border-radius: 15px; padding: 20px; color: #ffffff;
                font-family: 'Poppins', sans-serif; line-height: 1.6;
                text-shadow: 0 0 5px rgba(255, 255, 255, 0.3);">
        {ai_analysis}
    </div>
    """, unsafe_allow_html=True)

def main():
    """主函数：从欢迎页 → 问卷页 → 结果页的完整流程"""
    # 清理可能冲突的radio keys
    keys_to_remove = [k for k in st.session_state.keys() if k.startswith(('question_', 'radio_'))]
    for key in keys_to_remove:
        del st.session_state[key]

    # 1. 初始化 session state 并加载自定义 CSS
    initialize_session_state()
    load_css()

    # 2. 欢迎页：首次进入或重置后显示
    if st.session_state.show_welcome:
        # 欢迎页顶部导航 - 把大标题放在容器里
        st.markdown("""
        <div class="custom-header">
            <div class="main-title">🎵 K-pop創作適性診断</div>
            <div class="main-subtitle">K-popの未来をつくるのは、キミかも？</div>
        </div>
        """, unsafe_allow_html=True)

        # 欢迎文字 - 移除重复的标题
        st.markdown("""
        <div class="welcome-container">
            <p class="welcome-description">10問で今すぐ診断する！</p>
            <p class="welcome-teaser">5分でわかる、あなたの"クリエイタータイプ"</p>
        </div>
        """, unsafe_allow_html=True)

        # 开始按钮
        if st.button("診断を始める", key="welcome_start", use_container_width=True):
            st.session_state.show_welcome = False
            st.rerun()

        # 关闭容器
        st.markdown('</div>', unsafe_allow_html=True)
        return  # 只渲染欢迎页，其它逻辑暂不执行

    # 3. 问卷页和结果页顶部导航
    st.markdown("""
    <div class="custom-header">
        <div class="main-title">🎵 K-pop創作プロセス適性診断</div>
        <div class="main-subtitle">あなたの創作での最適ポジションを発見しよう</div>
    </div>
    """, unsafe_allow_html=True)


    # 5. 问卷流程：未查看结果时
    if not st.session_state.show_result:
        # 5.1 进度条 + 当前问题
        render_progress_bar()
        selected = render_question()

        # 5.2 导航按钮：左右对称布局
        left_col, right_col = st.columns([1, 1], gap="large")
        
        with left_col:
            # 左侧：返回按钮（不是第一题时才显示）
            if st.session_state.current_question > 0:
                if st.button("⬅️ 前へ", key="prev_btn"):
                    st.session_state.current_question -= 1
                    st.rerun()

        with right_col:
            # 右侧：前进按钮（选择了选项时才显示）
            if selected:
                # 不是最后一题：显示"次へ"
                if st.session_state.current_question < len(QUESTIONS) - 1:
                    if st.button("次へ ➡️", key="next_btn"):
                        calculate_scores(selected, st.session_state.current_question)
                        st.session_state.answers.append(selected)
                        st.session_state.current_question += 1
                        st.rerun()
                # 最后一题：显示"結果を見る"
                else:
                    if st.button("🎯 結果を見る", key="result_btn"):
                        calculate_scores(selected, st.session_state.current_question)
                        st.session_state.answers.append(selected)
                        st.session_state.show_result = True
                        st.rerun()

    # 6. 结果页
    else:
        render_result()
        if st.button("🔄 もう一度診断する", key="restart_btn"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


if __name__ == "__main__":
    main()