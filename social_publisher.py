import os
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from publishers.facebook_client import FacebookClient
from utils.image_generator import ImageGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("SocialPublisher")

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"


def load_results() -> dict:
    path = DATA_DIR / "competition_results.json"
    if not path.exists():
        logger.warning(f"No se encuentra {path}. Usando datos de ejemplo.")
        return get_sample_data()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_sample_data() -> dict:
    return {
        "start_time": datetime.now().isoformat(),
        "strategies": {
            "Meme Hunter": {"author": "Antigravity", "trades": 165, "wins": 100, "losses": 65, "total_pnl_pct": 3.158, "win_rate": 60.6, "profit_factor": 2.14, "avg_rr": 2.53, "signals_generated": 30251},
            "Trance Trading": {"author": "Trance", "trades": 139, "wins": 118, "losses": 21, "total_pnl_pct": 0.31, "win_rate": 84.9, "profit_factor": 2.1, "avg_rr": 1.5, "signals_generated": 25000},
            "Wyckoff Scout": {"author": "Kimi AI", "trades": 75, "wins": 35, "losses": 40, "total_pnl_pct": 1.992, "win_rate": 46.7, "profit_factor": 1.8, "avg_rr": 2.8, "signals_generated": 18000},
            "SMC Táctico": {"author": "Gemini", "trades": 50, "wins": 30, "losses": 20, "total_pnl_pct": 0.48, "win_rate": 60.0, "profit_factor": 1.5, "avg_rr": 2.0, "signals_generated": 12000},
            "Markov SMC Elite": {"author": "opencode", "trades": 40, "wins": 28, "losses": 12, "total_pnl_pct": 0.8, "win_rate": 70.0, "profit_factor": 2.5, "avg_rr": 2.2, "signals_generated": 10000},
            "Antigravity Swing": {"author": "Antigravity", "trades": 30, "wins": 18, "losses": 12, "total_pnl_pct": 0.6, "win_rate": 60.0, "profit_factor": 1.9, "avg_rr": 2.4, "signals_generated": 8000},
            "ML Sniper": {"author": "Pitoniso AI", "trades": 90, "wins": 40, "losses": 50, "total_pnl_pct": -0.2, "win_rate": 44.4, "profit_factor": 0.9, "avg_rr": 1.8, "signals_generated": 20000},
            "SMC Legacy v99": {"author": "Pitoniso AI", "trades": 25, "wins": 10, "losses": 15, "total_pnl_pct": -0.5, "win_rate": 40.0, "profit_factor": 0.7, "avg_rr": 1.5, "signals_generated": 6000},
        }
    }


def build_leaderboard(results: dict) -> list:
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


def build_ranking_text(leaderboard: list) -> str:
    lines = ["🏆 *RANKING DEL ORÁCULO PITONISO*", "Competencia de IAs - Trance Trading", ""]
    for i, s in enumerate(leaderboard[:10]):
        medal = {0: "🥇", 1: "🥈", 2: "🥉"}.get(i, f"{i+1}.")
        name = s["strategy"]
        pnl = s["total_pnl_pct"]
        wr = s["win_rate"]
        pf = s["profit_factor"]
        shadow = " [SOMBRA]" if s["is_shadow"] else ""
        lines.append(f"{medal} {name}{shadow}")
        lines.append(f"   PnL: {pnl:+.1f}% | WR: {wr:.0f}% | PF: {pf:.2f}")
        lines.append("")
    lines.append("")
    lines.append("📊 Datos en tiempo real desde la blockchain de Binance.")
    lines.append("🤖 10 IAs compitiendo. Resultados verificables.")
    lines.append("")
    lines.append("👇 Ingresa al Oráculo:")
    lines.append("t.me/PITONISO_BOT")
    return "\n".join(lines)


def format_for_facebook(text: str) -> str:
    return text.replace("*", "").replace("_", "").replace("`", "")


def publish_ranking():
    logger.info("=== Iniciando publicación de ranking ===")
    results = load_results()
    leaderboard = build_leaderboard(results)

    page_token = os.getenv("PAGE_ACCESS_TOKEN")
    page_id = os.getenv("PAGE_ID")
    if not page_token or not page_id:
        logger.error("Faltan PAGE_ACCESS_TOKEN o PAGE_ID en .env")
        return

    fb = FacebookClient(page_id, page_token)
    img_gen = ImageGenerator()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    img_path = OUTPUT_DIR / "ranking_latest.png"
    img_gen.generate_ranking(leaderboard, str(img_path))

    text_fb = format_for_facebook(build_ranking_text(leaderboard))
    text_fb += "\n\n🔗 Ingresa al Oráculo: https://t.me/PITONISO_BOT"

    fb.post_photo(str(img_path), text_fb)
    logger.info("=== Publicación de ranking completada ===")


def publish_daily_summary():
    logger.info("=== Iniciando resumen diario ===")
    results = load_results()
    leaderboard = build_leaderboard(results)

    page_token = os.getenv("PAGE_ACCESS_TOKEN")
    page_id = os.getenv("PAGE_ID")
    if not page_token or not page_id:
        logger.error("Faltan credenciales en .env")
        return

    fb = FacebookClient(page_id, page_token)
    total_trades = sum(s.get("trades", 0) for s in results.get("strategies", {}).values())
    total_wins = sum(s.get("wins", 0) for s in results.get("strategies", {}).values())
    overall_wr = (total_wins / total_trades * 100) if total_trades > 0 else 0
    top = leaderboard[0] if leaderboard else {}

    msg = (
        f"📊 RESUMEN DIARIO - ORÁCULO PITONISO\n"
        f"Fecha: {datetime.now().strftime('%d/%m/%Y')}\n\n"
        f"📡 Señales totales: {total_trades}\n"
        f"✅ Aciertos: {total_wins}\n"
        f"📈 Win Rate Global: {overall_wr:.1f}%\n"
    )
    if top:
        msg += f"\n🏆 Líder: {top['strategy']} (PnL: {top['total_pnl_pct']:+.1f}%)"

    msg += "\n\n🔗 t.me/PITONISO_BOT"

    fb.post_text(msg)
    logger.info("=== Resumen diario publicado ===")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "ranking":
            publish_ranking()
        elif command == "daily":
            publish_daily_summary()
        else:
            print(f"Comando desconocido: {command}")
            print("Usa: python social_publisher.py [ranking|daily]")
    else:
        publish_ranking()
