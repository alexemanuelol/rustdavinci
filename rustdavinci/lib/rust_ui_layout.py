#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Click positions for the current Rust painting side panel (brush / sliders / colour grid).

Calibrated from a full-panel reference capture (391×1024). OpenCV matches this image as
`opencv_template/rust_palette_template.png`; all coordinates are fractions of the matched
rectangle (ctrl_x, ctrl_y, ctrl_w, ctrl_h).

If Facepunch tweaks the UI again, adjust the *_FRAC constants below (keep values in 0–1).
"""

# --- Vertical bands (fraction of panel height) ---
UI_BRUSH_TIPS_Y_FRAC = 0.156  # row of 7 brush tip icons
UI_SIZE_SLIDER_Y_FRAC = 0.248  # SIZE slider track
UI_OPACITY_SLIDER_Y_FRAC = 0.352  # OPACITY slider track (4 discrete levels use indices 2–5)
UI_SAVE_BUTTON_FRAC = (0.50, 0.898)  # SAVE CHANGES — used as ctrl_update ("apply" / refresh canvas)
UI_CANCEL_BUTTON_FRAC = (0.50, 0.945)  # CANCEL — kept as ctrl_remove for compatibility (unused in app)

# Horizontal extent of slider tracks (thumb travel), as fraction of panel width from left edge
UI_SLIDER_X0_FRAC = 0.14
UI_SLIDER_X1_FRAC = 0.86

# Seven brush presets left→right; we map settings brush_type 0..3 to the first four icons.
UI_BRUSH_X0_FRAC = 0.10
UI_BRUSH_X1_FRAC = 0.90

# Colour grid: 4 columns; row-major order must match `rust_palette` indexing used by the game.
# Main visible block in the reference is ~13 rows; we use a uniform 4×16 grid (64 cells) so
# color%64 maps to physical swatches. Re-tune ROW0 and PITCH if colours mis-click.
UI_COLOR_COL_X_FRAC = (0.159, 0.391, 0.609, 0.834)
UI_COLOR_ROW0_Y_FRAC = 0.405  # Y fraction of first swatch row centre (top → bottom)
UI_COLOR_ROW_PITCH_FRAC = 0.02838  # centre-to-centre spacing between colour rows (16 rows)


def _lx(ctrl_x, ctrl_w, frac):
    return int(ctrl_x + ctrl_w * frac)


def _ly(ctrl_y, ctrl_h, frac):
    return int(ctrl_y + ctrl_h * frac)


def layout_painting_controls(ctrl_x, ctrl_y, ctrl_w, ctrl_h):
    """
    Returns ctrl_remove, ctrl_update, ctrl_size (6), ctrl_brush (4), ctrl_opacity (6), ctrl_color (64).
    """
    # Top tool row is ignored (brush is default). Size: 6 steps along SIZE slider.
    sx0, sx1 = UI_SLIDER_X0_FRAC, UI_SLIDER_X1_FRAC
    sy = UI_SIZE_SLIDER_Y_FRAC
    ctrl_size = []
    for i in range(6):
        t = (i + 0.5) / 6.0
        xf = sx0 + (sx1 - sx0) * t
        ctrl_size.append((_lx(ctrl_x, ctrl_w, xf), _ly(ctrl_y, ctrl_h, sy)))

    # Four brush types → first four of seven tip slots (spread across the row).
    bx0, bx1 = UI_BRUSH_X0_FRAC, UI_BRUSH_X1_FRAC
    by = UI_BRUSH_TIPS_Y_FRAC
    ctrl_brush = []
    for j in range(4):
        t = (j + 0.5) / 7.0
        xf = bx0 + (bx1 - bx0) * t
        ctrl_brush.append((_lx(ctrl_x, ctrl_w, xf), _ly(ctrl_y, ctrl_h, by)))

    # Opacity: six slots (only indices 2–5 used by choose_painting_controls). Even spacing on track.
    oy = UI_OPACITY_SLIDER_Y_FRAC
    ctrl_opacity = []
    for i in range(6):
        t = i / 5.0
        xf = sx0 + (sx1 - sx0) * t
        ctrl_opacity.append((_lx(ctrl_x, ctrl_w, xf), _ly(ctrl_y, ctrl_h, oy)))

    # 64 colours: 4 columns × 16 rows, row-major (top-left = index 0).
    ctrl_color = []
    cols = UI_COLOR_COL_X_FRAC
    pitch = UI_COLOR_ROW_PITCH_FRAC
    y0 = UI_COLOR_ROW0_Y_FRAC
    for row in range(16):
        yf = y0 + row * pitch
        for col in range(4):
            ctrl_color.append((_lx(ctrl_x, ctrl_w, cols[col]), _ly(ctrl_y, ctrl_h, yf)))

    ctrl_remove = (_lx(ctrl_x, ctrl_w, UI_CANCEL_BUTTON_FRAC[0]), _ly(ctrl_y, ctrl_h, UI_CANCEL_BUTTON_FRAC[1]))
    ctrl_update = (_lx(ctrl_x, ctrl_w, UI_SAVE_BUTTON_FRAC[0]), _ly(ctrl_y, ctrl_h, UI_SAVE_BUTTON_FRAC[1]))

    return {
        "ctrl_remove": ctrl_remove,
        "ctrl_update": ctrl_update,
        "ctrl_size": ctrl_size,
        "ctrl_brush": ctrl_brush,
        "ctrl_opacity": ctrl_opacity,
        "ctrl_color": ctrl_color,
    }
