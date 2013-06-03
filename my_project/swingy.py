from javax.swing import JFrame


frame = JFrame(
    'Hello, World!',
    defaultCloseOperation=JFrame.EXIT_ON_CLOSE,
    size=(300, 300),
    locationRelativeTo=None)

frame.setVisible(True)
