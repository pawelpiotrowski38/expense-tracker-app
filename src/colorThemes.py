from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QToolTip


def darkTheme():
    darkThemePalette = QPalette()
    darkThemePalette.setColor(QPalette.ColorRole.Window, QColor(44, 45, 50, 255))
    darkThemePalette.setColor(QPalette.ColorRole.WindowText, QColor(228, 231, 235, 255))
    darkThemePalette.setColor(QPalette.ColorRole.Button, QColor(44, 45, 50, 255))
    darkThemePalette.setColor(QPalette.ColorRole.Text, QColor(239, 241, 241, 255))
    darkThemePalette.setColor(QPalette.ColorRole.ButtonText, QColor(228, 231, 235, 255))
    darkThemePalette.setColor(QPalette.ColorRole.Base, QColor(27, 29, 30, 255))
    
    darkThemePalette.setColor(QPalette.ColorRole.Highlight, QColor(138, 180, 247, 255))
    darkThemePalette.setColor(QPalette.ColorRole.HighlightedText, QColor(44, 45, 50, 255))
    darkThemePalette.setColor(QPalette.ColorRole.Link, QColor(44, 45, 50, 255))
    darkThemePalette.setColor(QPalette.ColorRole.AlternateBase, QColor(35, 37, 40, 255))
    darkThemePalette.setColor(QPalette.ColorRole.ToolTipBase, QColor(35, 37, 40, 255))
    darkThemePalette.setColor(QPalette.ColorRole.ToolTipText, QColor(228, 231, 235, 255))
    darkThemePalette.setColor(QPalette.ColorRole.LinkVisited, QColor(197, 138, 248, 255))

    if hasattr(QPalette.ColorRole, "Foreground"):
        darkThemePalette.setColor(QPalette.ColorRole.Foreground, QColor(228, 231, 235, 255))
    if hasattr(QPalette.ColorRole, "PlaceholderText"):
        darkThemePalette.setColor(QPalette.ColorRole.PlaceholderText, QColor(138, 139, 141, 255))
    
    darkThemePalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(105, 113, 119, 255))
    darkThemePalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(105, 113, 119, 255))
    darkThemePalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, QColor(30, 32, 35, 255))
    darkThemePalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(70, 71, 73, 255))
    darkThemePalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(83, 87, 91, 255))
    darkThemePalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(105, 113, 119, 255))
    darkThemePalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Link, QColor(105, 113, 119, 255))
    darkThemePalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.LinkVisited, QColor(105, 113, 119, 255))
    
    darkThemePalette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, QColor(57, 61, 65, 255))
    QToolTip.setPalette(darkThemePalette)

    return darkThemePalette


def lightTheme():
    lightThemePalette = QPalette()
    lightThemePalette.setColor(QPalette.ColorRole.Window, QColor(248, 249, 250, 255))
    lightThemePalette.setColor(QPalette.ColorRole.WindowText, QColor(77, 81, 87, 255))
    lightThemePalette.setColor(QPalette.ColorRole.Button, QColor(248, 249, 250, 255))
    lightThemePalette.setColor(QPalette.ColorRole.Text, QColor(77, 81, 87, 255))
    lightThemePalette.setColor(QPalette.ColorRole.ButtonText, QColor(77, 81, 87, 255))
    lightThemePalette.setColor(QPalette.ColorRole.Base, QColor(248, 249, 250, 255))
    
    lightThemePalette.setColor(QPalette.ColorRole.Highlight, QColor(0, 129, 219, 255))
    lightThemePalette.setColor(QPalette.ColorRole.HighlightedText, QColor(248, 249, 250, 255))
    lightThemePalette.setColor(QPalette.ColorRole.Link, QColor(248, 249, 250, 255))
    lightThemePalette.setColor(QPalette.ColorRole.AlternateBase, QColor(233, 236, 239, 255))
    lightThemePalette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255, 255))
    lightThemePalette.setColor(QPalette.ColorRole.ToolTipText, QColor(77, 81, 87, 255))
    lightThemePalette.setColor(QPalette.ColorRole.LinkVisited, QColor(102, 0, 152, 255))

    if hasattr(QPalette.ColorRole, "Foreground"):
        lightThemePalette.setColor(QPalette.ColorRole.Foreground, QColor(77, 81, 87, 255))
    if hasattr(QPalette.ColorRole, "PlaceholderText"):
        lightThemePalette.setColor(QPalette.ColorRole.PlaceholderText, QColor(105, 106, 108, 255))
    
    lightThemePalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(186, 189, 194, 255))
    lightThemePalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(186, 189, 194, 255))
    lightThemePalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, QColor(250, 250, 250, 255))
    lightThemePalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(218, 220, 224, 255))
    lightThemePalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(218, 220, 224, 255))
    lightThemePalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(186, 189, 194, 255))
    lightThemePalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Link, QColor(186, 189, 194, 255))
    lightThemePalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.LinkVisited, QColor(186, 189, 194, 255))
    
    lightThemePalette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, QColor(228, 230, 242, 255))
    QToolTip.setPalette(lightThemePalette)

    return lightThemePalette
