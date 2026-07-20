import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

ORACLE_GREEN = (0, 255, 65)
DARK_BG = (8, 8, 16)
CARD_BG = (16, 18, 30)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)
WHITE = (220, 220, 220)
GRAY = (100, 100, 120)
ACCENT = (0, 200, 255)
RED_ACCENT = (255, 60, 60)
TELEGRAM_BLUE = (0, 136, 204)


class ImageGenerator:
    def _font(self, size):
        try:
            return ImageFont.truetype("arial.ttf", size)
        except (IOError, OSError):
            return ImageFont.load_default()

    def _draw_gradient_bg(self, draw, w, h):
        for y in range(h):
            ratio = y / h
            r = int(8 + ratio * 10)
            g = int(8 + ratio * 18)
            b = int(16 + ratio * 30)
            draw.line([(0, y), (w, y)], fill=(r, g, b))

    def _draw_header(self, draw, w):
        draw.rectangle([(0, 0), (w, 90)], fill=(0, 0, 0, 180))
        draw.text((w // 2, 20), "ORACULO PITONISO", fill=ORACLE_GREEN, font=self._font(36), anchor="mt")
        draw.text((w // 2, 60), "TRANCE TRADING - COMPETENCIA DE IAS", fill=GRAY, font=self._font(16), anchor="mt")
        draw.line([(40, 90), (w - 40, 90)], fill=ACCENT, width=2)

    def _draw_footer(self, draw, w, h):
        draw.line([(40, h - 80), (w - 40, h - 80)], fill=ACCENT, width=1)
        draw.text((w // 2, h - 55), "UNETE AL ORACULO EN TELEGRAM", fill=TELEGRAM_BLUE, font=self._font(20), anchor="ms")
        draw.text((w // 2, h - 30), "t.me/+90UWmX0Iiks0MWUx", fill=ORACLE_GREEN, font=self._font(18), anchor="ms")

    def _draw_explainer_box(self, draw, w, h):
        box_y = h - 160
        draw.rounded_rectangle([(40, box_y), (w - 40, box_y + 55)], radius=8, fill=(0, 0, 0, 120))
        draw.text((w // 2, box_y + 15), "10 IAS COMPITIENDO EN VIVO", fill=ACCENT, font=self._font(18), anchor="mt")
        draw.text((w // 2, box_y + 38), "Elige que IAs copiar con /preferencias en Telegram", fill=WHITE, font=self._font(14), anchor="mt")

    def generate_ranking(self, strategies, output_path):
        w, h = 1080, 1350
        img = Image.new("RGB", (w, h), DARK_BG)
        draw = ImageDraw.Draw(img)
        self._draw_gradient_bg(draw, w, h)
        self._draw_header(draw, w)

        medal_colors = {0: GOLD, 1: SILVER, 2: BRONZE}
        medal_icons = {0: "1", 1: "2", 2: "3"}

        y_start = 120
        for i, s in enumerate(strategies[:10]):
            y = y_start + i * 115
            is_shadow = s.get("is_shadow", False)
            color = GRAY if is_shadow else WHITE
            stat_color = GRAY if is_shadow else WHITE
            bg_color = CARD_BG
            medal_color = medal_colors.get(i, GRAY)
            medal_num = medal_icons.get(i, f"{i+1}")

            draw.rounded_rectangle([(40, y), (w - 40, y + 100)], radius=10, fill=bg_color)
            draw.ellipse([(60, y + 20), (100, y + 60)], fill=medal_color)
            draw.text((80, y + 40), medal_num, fill=(0, 0, 0), font=self._font(24), anchor="mm")

            name = s.get("strategy", "???")
            pnl = s.get("total_pnl_pct", 0)
            wr = s.get("win_rate", 0)
            pf = s.get("profit_factor", 0)
            trades = s.get("trades", 0)

            tag = " [SOMBRA]" if is_shadow else ""
            draw.text((120, y + 15), f"{name}{tag}", fill=color, font=self._font(22))
            draw.text((120, y + 50), "Rendimiento:", fill=GRAY, font=self._font(14))

            pnl_color = ORACLE_GREEN if pnl >= 0 else RED_ACCENT
            draw.text((120, y + 68), f"{pnl:+.1f}%", fill=pnl_color, font=self._font(20))
            draw.text((250, y + 68), f"WR: {wr:.0f}%", fill=stat_color, font=self._font(20))
            draw.text((380, y + 68), f"PF: {pf:.2f}", fill=stat_color, font=self._font(20))
            draw.text((520, y + 68), f"Trades: {trades}", fill=stat_color, font=self._font(20))

        self._draw_explainer_box(draw, w, h)
        self._draw_footer(draw, w, h)
        draw.text((w // 2, h - 5), f"Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", fill=GRAY, font=self._font(12), anchor="ms")

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        img.save(output_path)
        return output_path

    def generate_golden_trade(self, trade, output_path):
        w, h = 1080, 1080
        img = Image.new("RGB", (w, h), DARK_BG)
        draw = ImageDraw.Draw(img)
        self._draw_gradient_bg(draw, w, h)

        draw.ellipse([(w // 2 - 60, 30), (w // 2 + 60, 150)], fill=GOLD)
        draw.text((w // 2, 90), "!", fill=(0, 0, 0), font=self._font(72), anchor="mm")

        draw.text((w // 2, 200), "EL ORACULO ESTALLO", fill=GOLD, font=self._font(42), anchor="mt")
        draw.line([(150, 240), (w - 150, 240)], fill=GOLD, width=2)

        strategy = trade.get("strategy", "IA")
        symbol = trade.get("symbol", "???")
        pnl = trade.get("pnl_pct", 0)
        ratio = trade.get("ratio", 0)

        draw.text((w // 2, 300), f"Estrategia: {strategy}", fill=WHITE, font=self._font(26), anchor="mt")
        draw.text((w // 2, 360), f"Par: {symbol}USDT", fill=ACCENT, font=self._font(28), anchor="mt")

        pnl_color = ORACLE_GREEN if pnl >= 0 else RED_ACCENT
        pnl_str = f"+{pnl*100:.2f}%" if pnl < 1 else f"{pnl:+.2f}%"
        draw.text((w // 2, 460), pnl_str, fill=pnl_color, font=self._font(64), anchor="mt")
        draw.text((w // 2, 530), "Rentabilidad", fill=GRAY, font=self._font(18), anchor="mt")

        if ratio > 0:
            draw.text((w // 2, 600), f"Ratio {ratio:.1f}:1", fill=GOLD, font=self._font(36), anchor="mt")

        draw.rounded_rectangle([(100, 680), (w - 100, 760)], radius=12, fill=(0, 0, 0, 100))
        draw.text((w // 2, 720), "ESTA IA COMPITE CONTRA OTRAS 9 EN EL ORACULO", fill=ACCENT, font=self._font(18), anchor="mm")

        draw.rounded_rectangle([(200, 820), (w - 200, 920)], radius=15, fill=(0, 0, 0, 100))
        draw.text((w // 2, 870), "SENALES EN VIVO EN TELEGRAM", fill=TELEGRAM_BLUE, font=self._font(24), anchor="mm")
        draw.line([(300, 930), (w - 300, 930)], fill=TELEGRAM_BLUE, width=1)
        draw.text((w // 2, 960), "t.me/+90UWmX0Iiks0MWUx", fill=ORACLE_GREEN, font=self._font(22), anchor="mt")

        draw.text((w // 2, 1020), "Resultados verificables en tiempo real", fill=GRAY, font=self._font(16), anchor="mt")
        draw.text((w // 2, 1050), f"{datetime.now().strftime('%d/%m/%Y %H:%M')}", fill=GRAY, font=self._font(14), anchor="mt")

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        img.save(output_path)
        return output_path


import logging
logger = logging.getLogger("ImageGenerator")
