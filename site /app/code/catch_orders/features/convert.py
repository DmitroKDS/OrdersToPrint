def px_to_cm(pixels, dpi=150):
    """Конвертує пікселі в сантиметри"""
    return (pixels / dpi) * 2.54

def cm_to_px(cm, dpi=150):
    """Конвертує сантиметри в пікселі"""
    return int((cm / 2.54) * dpi)