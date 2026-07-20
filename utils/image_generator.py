import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime


class ImageGenerator:
    def __init__(self):
        self.bg_color = (10, 10, 10)
        self.green = (0, 255, 65)
        self.gray = (150, 150, 150)
        self.blue = (0, 200, 255)
        self.white = (220, 220, 220)
        self.red = (255, 60, 60)
        self.yellow = (255, 200, 50)

    def _load_font(self, size: int):
        try:
            return ImageFont.truetype("arial.ttf", size)
        except (IOError, OSError):
            return ImageFont.load_default()

    def generate_ranking(self, strategies: list, output_path: str):
        img = Image.new("RGB", (1080, 1080), self.bg_color)
        draw = ImageDraw.Draw(img)
        font_lg = self._load_font(36)
        font_md = self._load_font(28)
        font_sm = self._load_font(22)

        draw.text((540, 40), "RANKING DEL ORACULO PITONISO", fill=self.blue, font=font_lg, anchor="mt")
        draw.text((540, 85), "Competencia de IAs - Trance Trading", fill=self.gray, font=font_sm, anchor="mt")

        y = 150
        for i, s in enumerate(strategies[:10]):
            name = s.get("strategy", "Unknown")
            pnl = s.get("total_pnl_pct", 0)
            wr = s.get("win_rate", 0)
            pf = s.get("profit_factor", 0)
            trades = s.get("trades", 0)
            is_shadow = s.get("is_shadow", False)

            if is_shadow:
                color = self.gray
                flag = " [SOMBRA]"
            else:
                color = self.green
                flag = ""

            medals = {0: "🥇", 1: "🥈", 2: "🥉"}
            medal = medals.get(i, f"#{i+1}")

            pnl_str = f"{pnl:+.1f}%" if isinstance(pnl, (int, float)) else str(pnl)
            wr_str = f"{wr:.0f}%" if isinstance(wr, (int, float)) else str(wr)
            pf_str = f"{pf:.2f}" if isinstance(pf, (int, float)) else str(pf)

            line = f"{medal} {name}{flag}"
            stats = f"PnL: {pnl_str}  |  WR: {wr_str}  |  PF: {pf_str}  |  Trades: {trades}"

            draw.text((60, y), line, fill=color, font=font_md)
            draw.text((60, y + 40), stats, fill=self.white, font=font_sm)
            draw.line([(60, y + 80), (1020, y + 80)], fill=(40, 40, 40))
            y += 100

        draw.text((540, 1030), f"Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", fill=self.gray, font=font_sm, anchor="ms")
        draw.text((540, 1065), "Ingresa al Oráculo -> t.me/PITONISO_BOT", fill=self.blue, font=font_sm, anchor="ms")

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        img.save(output_path)
        logger.info(f"Imagen de ranking generada: {output_path}")
        return output_path

    def generate_signal_card(self, symbol: str, direction: str, pnl: float, ratio: float,
                             strategy: str, output_path: str):
        img = Image.new("RGB", (1080, 1080), self.bg_color)
        draw = ImageDraw.Draw(img)
        font_lg = self._load_font(40)
        font_md = self._load_font(30)
        font_sm = self._load_font(22)

        draw.text((540, 60), "SEÑAL DESTACADA", fill=self.blue, font=font_lg, anchor="mt")
        draw.text((540, 120), f"{symbol}USDT", fill=self.white, font=self._load_font(52), anchor="mt")

        dir_color = self.green if direction == "LONG" else self.red
        dir_icon = "🟢 LONG" if direction == "LONG" else "🔴 SHORT"
        draw.text((540, 200), dir_icon, fill=dir_color, font=self._load_font(48), anchor="mt")

        pnl_color = self.green if pnl >= 0 else self.red
        draw.text((540, 300), f"Resultado: {pnl:+.2f}%", fill=pnl_color, font=font_md, anchor="mt")
        draw.text((540, 360), f"Ratio: {ratio:.1f}:1", fill=self.yellow, font=font_md, anchor="mt")

        draw.text((540, 460), f"Estrategia: {strategy}", fill=self.gray, font=font_sm, anchor="mt")
        draw.text((540, 520), f"Timestamp: {datetime.now().strftime('%d/%m/%Y %H:%M')}", fill=self.gray, font=font_sm, anchor="mt")

        draw.text((540, 700), "Operaciones verificables en tiempo real", fill=self.gray, font=font_sm, anchor="mt")
        draw.text((540, 740), "t.me/PITONISO_BOT", fill=self.blue, font=font_md, anchor="mt")

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        img.save(output_path)
        logger.info(f"Imagen de señal generada: {output_path}")
        return output_path


import logging
logger = logging.getLogger("ImageGenerator")
