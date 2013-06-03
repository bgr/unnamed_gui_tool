
from javax.swing import JFrame


def test_swing():
    frame = JFrame(
        'Hello, World!',
        defaultCloseOperation=JFrame.EXIT_ON_CLOSE,
        size=(300, 300),
        locationRelativeTo=None)
    frame.setVisible(True)

    assert frame.size.width == 300
    assert frame.size.height == 300
    assert frame.title == 'Hello, World!'
