import os
import json
import logging
import sys
import random
from datetime import datetime
from pathlib import Path

from publishers.facebook_client import FacebookClient
from publishers.twitter_client import TwitterClient
from publishers.instagram_client import InstagramClient
from publishers.telegram_client import TelegramClient
from utils.image_generator import ImageGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("SocialPublisher")

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

env_path = BASE_DIR / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

TG_LINK = os.getenv("TELEGRAM_GROUP_LINK", "t.me/+90UWmX0Iiks0MWUx")
TG_BOT = os.getenv("BOT_REFERRAL_LINK", "t.me/PITONISO_BOT")


def load_results():
    path = DATA_DIR / "competition_results.json"
    if not path.exists():
        logger.warning(f"No se encuentra {path}. Usando datos de ejemplo.")
        return get_sample_data()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_golden_trades():
    path = DATA_DIR / "golden_trades_pending.json"
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, Exception):
        return []


def save_golden_trades(trades):
    path = DATA_DIR / "golden_trades_pending.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(trades, f, indent=2)


def get_sample_data():
    return {
        "start_time": datetime.now().isoformat(),
        "strategies": {
            "Meme Hunter": {"author": "Antigravity", "trades": 165, "wins": 100, "losses": 65, "total_pnl_pct": 3.158, "win_rate": 60.6, "profit_factor": 2.14, "avg_rr": 2.53, "signals_generated": 30251},
            "Trance Trading": {"author": "Trance", "trades": 139, "wins": 118, "losses": 21, "total_pnl_pct": 0.31, "win_rate": 84.9, "profit_factor": 2.1, "avg_rr": 1.5, "signals_generated": 25000},
            "Wyckoff Scout": {"author": "Kimi AI", "trades": 75, "wins": 35, "losses": 40, "total_pnl_pct": 1.992, "win_rate": 46.7, "profit_factor": 1.8, "avg_rr": 2.8, "signals_generated": 18000},
            "SMC Tactico": {"author": "Gemini", "trades": 50, "wins": 30, "losses": 20, "total_pnl_pct": 0.48, "win_rate": 60.0, "profit_factor": 1.5, "avg_rr": 2.0, "signals_generated": 12000},
            "Markov SMC Elite": {"author": "opencode", "trades": 40, "wins": 28, "losses": 12, "total_pnl_pct": 0.8, "win_rate": 70.0, "profit_factor": 2.5, "avg_rr": 2.2, "signals_generated": 10000},
            "Antigravity Swing": {"author": "Antigravity", "trades": 30, "wins": 18, "losses": 12, "total_pnl_pct": 0.6, "win_rate": 60.0, "profit_factor": 1.9, "avg_rr": 2.4, "signals_generated": 8000},
            "ML Sniper": {"author": "Pitoniso AI", "trades": 90, "wins": 40, "losses": 50, "total_pnl_pct": -0.2, "win_rate": 44.4, "profit_factor": 0.9, "avg_rr": 1.8, "signals_generated": 20000},
        }
    }


def build_leaderboard(results):
    strategies = results.get("strategies", {})
    ranked = []
    for name, data in strategies.items():
        ranked.append({
            "strategy": name,
            "total_pnl_pct": data.get("total_pnl_pct", 0),
            "win_rate": data.get("win_rate", 0),
            "profit_factor": data.get("profit_factor", 0),
            "trades": data.get("trades", 0),
            "wins": data.get("wins", 0),
            "losses": data.get("losses", 0),
            "avg_rr": data.get("avg_rr", 0),
            "is_shadow": data.get("is_shadow", False),
        })
    ranked.sort(key=lambda x: x["total_pnl_pct"], reverse=True)
    return ranked


def get_page_token():
    user_token = os.getenv("USER_TOKEN")
    if not user_token:
        logger.error("Falta USER_TOKEN en .env")
        return None, None
    try:
        import requests as req
        r = req.get(f"https://graph.facebook.com/v25.0/me/accounts?access_token={user_token}")
        data = r.json()
        page = data["data"][0]
        return page["id"], page["access_token"]
    except Exception as e:
        logger.error(f"Error obteniendo page token: {e}")
        return None, None


def _get_clients(page_id=None, page_token=None):
    tw = TwitterClient()
    tg = TelegramClient()
    ig = InstagramClient(page_id, page_token) if page_id else None
    return tw, tg, ig


def publish_ranking():
    logger.info("=== RANKING ===")
    results = load_results()
    leaderboard = build_leaderboard(results)

    page_id, page_token = get_page_token()
    if not page_id or not page_token:
        return

    fb = FacebookClient(page_id, page_token)
    tw, tg, ig = _get_clients(page_id, page_token)
    img_gen = ImageGenerator()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    img_path = OUTPUT_DIR / "ranking_latest.png"
    img_gen.generate_ranking(leaderboard, str(img_path))

    top = leaderboard[0] if leaderboard else {}
    top_name = top.get("strategy", "")
    top_pnl = top.get("total_pnl_pct", 0)
    top_wr = top.get("win_rate", 0)

    n_ais = len(leaderboard)
    total_trades = sum(s.get("trades", 0) for s in results.get("strategies", {}).values())
    total_wins = sum(s.get("wins", 0) for s in results.get("strategies", {}).values())
    overall_wr = (total_wins / total_trades * 100) if total_trades > 0 else 0

    msg = (
        f"COMPETENCIA DE IAS EN VIVO\n"
        f"========================\n\n"
        f"{n_ais} inteligencias artificiales compiten en tiempo real "
        f"analizando las 150 criptomonedas mas liquidas de Binance Futures.\n\n"
        f"Cada IA tiene su propia estrategia:\n"
        f"  - Meme Hunter (sentimiento social)\n"
        f"  - Wyckoff Scout (acumulacion institucional)\n"
        f"  - SMC Tactico (order blocks)\n"
        f"  - Liquidation Hunter (liquidez)\n"
        f"  - Y 6 mas...\n\n"
        f"LIDER ACTUAL: {top_name}\n"
        f"  PnL: {top_pnl:+.1f}%  |  WR: {top_wr:.0f}%  |  Trades: {top.get('trades', 0)}\n\n"
        f"GLOBAL DEL ECOSISTEMA:\n"
        f"  Senales totales: {total_trades}\n"
        f"  Aciertos: {total_wins}\n"
        f"  Win Rate: {overall_wr:.1f}%\n\n"
        f"COMO FUNCIONA:\n"
        f"  1. Las IAs analizan el mercado 24/7\n"
        f"  2. Generan senales con entry, SL y TP\n"
        f"  3. Puedes elegir que IAs copiar\n"
        f"  4. Todo es transparente y verificable\n\n"
        f"Todo esto ocurre en vivo en nuestro grupo de Telegram.\n"
        f"Entra, mira los resultados y decide por ti mismo:\n"
        f"{TG_LINK}\n\n"
        f"Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    )

    result = fb.post_photo(str(img_path), msg)
    if not result:
        fb.post_text(msg)

    tw_short = f"Ranking Oraculo Pitoniso:\nLider: {top_name} ({top_pnl:+.1f}%)\nWR: {top_wr:.0f}% | {n_ais} IAs compitiendo\n{TG_LINK}"
    tw.post_photo(str(img_path), tw_short)
    tg.post_photo(str(img_path), msg[:1024])
    if ig:
        ig.post_photo(str(img_path), f"Ranking Oraculo Pitoniso - Lider: {top_name} ({top_pnl:+.1f}%)")
    logger.info("RANKING OK")


def publish_golden_trade():
    logger.info("=== GOLDEN TRADE ===")
    trades = load_golden_trades()
    if not trades:
        logger.info("No hay golden trades")
        return

    trade = trades[0]
    strategy = trade.get("strategy", "IA")
    symbol = trade.get("symbol", "???")
    pnl = trade.get("pnl_pct", 0)
    ratio = trade.get("ratio", 0)

    pnl_str = f"+{pnl*100:.2f}%" if pnl < 1 else f"{pnl:+.2f}%"
    ratio_str = f"Ratio {ratio:.1f}:1" if ratio > 0 else "Precision algoritmica"

    page_id, page_token = get_page_token()
    if not page_id or not page_token:
        return

    fb = FacebookClient(page_id, page_token)
    tw, tg, ig = _get_clients(page_id, page_token)
    img_gen = ImageGenerator()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    img_path = OUTPUT_DIR / "golden_trade_latest.png"
    img_gen.generate_golden_trade(trade, str(img_path))

    msg = (
        f"OPERACION DESTACADA DEL ORACULO\n"
        f"============================\n\n"
        f"La IA {strategy} acaba de cerrar una operacion en {symbol}USDT.\n\n"
        f"Resultado: {pnl_str}\n"
        f"Ratio riesgo/beneficio: {ratio_str}\n\n"
        f"Esta es UNA de las 10 IAs que operan en nuestro ecosistema.\n"
        f"Cada una con su propia estrategia, compitiendo para ver cual "
        f"genera mejores resultados.\n\n"
        f"Tu decides a cual copiar:\n"
        f"  - Quieres precision? -> Trance Trading (85% WR)\n"
        f"  - Quieres rentabilidad? -> Meme Hunter (+3.1%)\n"
        f"  - Quieres consistencia? -> Todas a la vez\n\n"
        f"En nuestro grupo de Telegram recibes las senales en el momento "
        f"exacto en que se generan, con entry, stop loss y take profit.\n\n"
        f"Resultados reales, sin filtros, verificables:\n"
        f"{TG_LINK}"
    )

    result = fb.post_photo(str(img_path), msg)
    if not result:
        fb.post_text(msg)

    tw_short = f"{strategy} cerro {symbol}USDT: {pnl_str} (ratio {ratio_str})\n10 IAs compitiendo en vivo\n{TG_LINK}"
    tw.post_photo(str(img_path), tw_short)
    tg.post_photo(str(img_path), f"Operacion destacada: {strategy} en {symbol}USDT - {pnl_str}")
    if ig:
        ig.post_photo(str(img_path), f"{strategy} cerro {symbol}USDT: {pnl_str}")

    trades.pop(0)
    save_golden_trades(trades)
    logger.info(f"Golden trade {strategy} {symbol} publicado")


def publish_explainer():
    logger.info("=== EXPLAINER ===")
    results = load_results()
    leaderboard = build_leaderboard(results)

    page_id, page_token = get_page_token()
    if not page_id or not page_token:
        return

    fb = FacebookClient(page_id, page_token)
    tw, tg, ig = _get_clients(page_id, page_token)
    img_gen = ImageGenerator()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    img_path = OUTPUT_DIR / "ranking_latest.png"
    img_gen.generate_ranking(leaderboard, str(img_path))

    total_trades = sum(s.get("trades", 0) for s in results.get("strategies", {}).values())
    total_wins = sum(s.get("wins", 0) for s in results.get("strategies", {}).values())
    overall_wr = (total_wins / total_trades * 100) if total_trades > 0 else 0
    top = leaderboard[0] if leaderboard else {}

    hooks = [
        f"Imagina tener 10 traders elite trabajando para ti 24/7, "
        f"cada uno especializado en una estrategia diferente, "
        f"compitiendo para ver quien gana mas dinero.",
        f"La mayoria de los grupos de senales tienen UNA persona "
        f"detras. Nosotros tenemos 10 IAs compitiendo. La mejor "
        f"gana, tu copias a todas.",
        f"No vendemos cursos. No tenemos gurus. Solo 10 IAs "
        f"compitiendo con dinero real en Binance. Resultados "
        f"publicos y verificables.",
    ]
    hook = random.choice(hooks)

    msg = (
        f"COMO FUNCIONA EL ORACULO PITONISO\n"
        f"==============================\n\n"
        f"{hook}\n\n"
        f"EL SISTEMA:\n"
        f"  10 IAs analizan las 150 criptos mas liquidas\n"
        f"  Cada 5 minutos evaluan senales de compra/venta\n"
        f"  Cuando una IA detecta una oportunidad, envia la senal\n"
        f"  Tu eliges cuales IAs seguir y cuales ignorar\n\n"
        f"TRANSPARENCIA TOTAL:\n"
        f"  - Ranking publico actualizado en tiempo real\n"
        f"  - Cada trade registrado con su resultado\n"
        f"  - IAs con mal rendimiento entran en modo sombra\n"
        f"  - Nunca ocultamos una perdida\n\n"
        f"RESULTADOS ACTUALES:\n"
        f"  Senales totales: {total_trades}\n"
        f"  Aciertos: {total_wins}\n"
        f"  Win Rate Global: {overall_wr:.1f}%\n"
    )
    if top:
        msg += f"  IA lider: {top['strategy']} ({top['total_pnl_pct']:+.1f}%)\n\n"

    msg += (
        f"COMO EMPEZAR:\n"
        f"  1. Entra al grupo de Telegram\n"
        f"  2. Habla con el bot @PITONISO_BOT\n"
        f"  3. Usa /preferencias para elegir tus IAs\n"
        f"  4. Recibe senales en tiempo real\n\n"
        f"Gratuito. Sin compromiso. Resultados reales.\n"
        f"{TG_LINK}"
    )

    img_path2 = OUTPUT_DIR / "explainer_latest.png"
    img_gen.generate_ranking(leaderboard, str(img_path2))
    result = fb.post_photo(str(img_path2), msg)
    if not result:
        fb.post_text(msg)

    tw_short = f"{hook[:100]}...\nResultados: {total_trades} senales, WR {overall_wr:.0f}%\n{TG_LINK}"
    tw.post_photo(str(img_path2), tw_short)
    tg.post_photo(str(img_path2), f"{hook[:200]}...\n\n{TG_LINK}")
    if ig:
        ig.post_photo(str(img_path2), f"Oraculo Pitoniso - {total_trades} senales, {overall_wr:.0f}% WR")
    logger.info("EXPLAINER OK")


def publish_daily_summary():
    logger.info("=== RESUMEN DIARIO ===")
    results = load_results()
    leaderboard = build_leaderboard(results)

    page_id, page_token = get_page_token()
    if not page_id or not page_token:
        return

    fb = FacebookClient(page_id, page_token)
    tw, tg, ig = _get_clients(page_id, page_token)
    total_trades = sum(s.get("trades", 0) for s in results.get("strategies", {}).values())
    total_wins = sum(s.get("wins", 0) for s in results.get("strategies", {}).values())
    overall_wr = (total_wins / total_trades * 100) if total_trades > 0 else 0
    top = leaderboard[0] if leaderboard else {}

    active_ais = len([s for s in results.get("strategies", {}).values() if not s.get("is_shadow")])
    shadow_ais = len([s for s in results.get("strategies", {}).values() if s.get("is_shadow")])

    msg = (
        f"ORACULO PITONISO - CIERRE DEL DIA\n"
        f"{datetime.now().strftime('%d/%m/%Y')}\n"
        f"==============================\n\n"
        f"ACTIVIDAD:\n"
        f"  Senales generadas: {total_trades}\n"
        f"  Aciertos: {total_wins}\n"
        f"  Win Rate Global: {overall_wr:.1f}%\n"
        f"  IAs activas: {active_ais}\n"
        f"  IAs en sombra: {shadow_ais}\n"
    )
    if top:
        msg += (
            f"\nIA DEL DIA:\n"
            f"  {top['strategy']}\n"
            f"  PnL: {top['total_pnl_pct']:+.1f}%  |  WR: {top['win_rate']:.0f}%\n"
        )

    msg += (
        f"\nRECORDATORIO:\n"
        f"  - Puedes elegir que IAs copiar con /preferencias\n"
        f"  - Las senales incluyen entry, SL y TP\n"
        f"  - Todo es transparente y verificable\n\n"
        f"Manana seguimos. Las IAs no descansan.\n"
        f"{TG_LINK}"
    )

    result = fb.post_text(msg)
    if not result:
        img_gen = ImageGenerator()
        img_path = OUTPUT_DIR / "ranking_latest.png"
        img_gen.generate_ranking(leaderboard, str(img_path))
        fb.post_photo(str(img_path), msg)

    tw_short = f"Oraculo Pitoniso - Cierre del dia:\n{total_trades} senales | WR {overall_wr:.0f}%\nIAs activas: {active_ais}"
    if top:
        tw_short += f"\nLider: {top['strategy']} ({top['total_pnl_pct']:+.1f}%)"
    tw_short += f"\n{TG_LINK}"
    tw.post_text(tw_short)
    tg.post_text(msg[:4096])
    if ig:
        ig.post_text(f"Oraculo Pitoniso - Cierre del dia\n{total_trades} senales, {overall_wr:.0f}% WR, {active_ais} IAs activas")
    logger.info("RESUMEN DIARIO OK")
    logger.info("=== BEGINNER ===")
    results = load_results()
    leaderboard = build_leaderboard(results)

    page_id, page_token = get_page_token()
    if not page_id or not page_token:
        return

    fb = FacebookClient(page_id, page_token)
    tw, tg, ig = _get_clients(page_id, page_token)
    img_gen = ImageGenerator()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    img_path = OUTPUT_DIR / "ranking_latest.png"
    img_gen.generate_ranking(leaderboard, str(img_path))

    total_trades = sum(s.get("trades", 0) for s in results.get("strategies", {}).values())
    top = leaderboard[0] if leaderboard else {}

    hooks = [
        f"Quieres aprender a operar y generar ingresos?\n"
        f"No necesitas experiencia previa.\n"
        f"Te ensenamos con 10 IAs compitiendo en vivo.",
        f"De cero a trader: nuestras IAs te muestran cada operacion\n"
        f"en tiempo real. Aprendes viendo, practicas copiando.",
        f"El mejor curso de trading es ver a 10 expertos\n"
        f"compitiendo con dinero real. Eso es el Oraculo.",
        f"La mayoria pierde dinero porque opera sin estrategia.\n"
        f"Nosotros te mostramos 10 estrategias diferentes en accion.\n"
        f"Elige la que mas te guste y copiala.",
    ]
    hook = random.choice(hooks)

    msg = (
        f"APRENDE A OPERAR CON INTELIGENCIA ARTIFICIAL\n"
        f"==========================================\n\n"
        f"{hook}\n\n"
        f"COMO FUNCIONA:\n"
        f"  1. Entras a nuestro grupo de Telegram\n"
        f"  2. Ves en vivo como 10 IAs analizan el mercado\n"
        f"  3. Cada IA te ensena una estrategia diferente:\n"
        f"     - Meme Hunter -> trading con sentimiento social\n"
        f"     - Wyckoff Scout -> acumulacion institucional\n"
        f"     - SMC Tactico -> order blocks profesionales\n"
        f"     - Liquidation Hunter -> caza de liquidaciones\n"
        f"     - Y 6 estrategias mas...\n"
        f"  4. Copias las senales o aprendes la estrategia\n\n"
        f"PARA QUIEN ES:\n"
        f"  - Principiantes que quieren aprender desde cero\n"
        f"  - Traders que quieren mejorar su estrategia\n"
        f"  - Cualquiera que quiera generar ingresos extra\n\n"
        f"NO VENDEMOS CURSOS:\n"
        f"  No tenemos guru, no vendemos humo.\n"
        f"  Son 10 IAs compitiendo. Resultados reales.\n"
        f"  Tu decides si copias, si aprendes, o ambas.\n\n"
        f"RESULTADOS DEL ECOSISTEMA:\n"
        f"  Senales totales: {total_trades}\n"
    )
    if top:
        msg += (
            f"  IA lider: {top['strategy']} ({top['total_pnl_pct']:+.1f}%)\n"
            f"  Win Rate: {top['win_rate']:.0f}%\n"
        )

    msg += (
        f"\nEntra gratis, aprende, y empieza a operar:\n"
        f"{TG_LINK}"
    )

    img_path2 = OUTPUT_DIR / "beginner_latest.png"
    img_gen.generate_ranking(leaderboard, str(img_path2))
    result = fb.post_photo(str(img_path2), msg)
    if not result:
        fb.post_text(msg)

    tw_short = f"{hook[:120]}...\n{TG_LINK}"
    tw.post_photo(str(img_path2), tw_short)
    tg.post_photo(str(img_path2), f"{hook[:200]}...\n\n{TG_LINK}")
    if ig:
        ig.post_photo(str(img_path2), f"Aprende a operar con 10 IAs - {total_trades} senales en vivo")
    logger.info("BEGINNER OK")
    command = sys.argv[1] if len(sys.argv) > 1 else "ranking"
    if command == "ranking":
        publish_ranking()
    elif command == "golden":
        publish_golden_trade()
    elif command == "explainer":
        publish_explainer()
    elif command == "beginner":
        publish_beginner()
    elif command == "daily":
        publish_daily_summary()
    elif command == "all":
        publish_beginner()
        publish_explainer()
        publish_ranking()
        publish_golden_trade()
        publish_daily_summary()
    else:
        print("Comandos: ranking, golden, explainer, beginner, daily, all")
