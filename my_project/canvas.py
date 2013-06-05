from javax.swing import JPanel, JFrame
from java.awt import Color
from javax.swing import SwingUtilities

from util import invokeLater


class Canvas(JPanel):

    def __init__(self):
        super(Canvas, self).__init__()
        print "third: {0}".format(SwingUtilities.isEventDispatchThread())

    def paintComponent(self, g):
        self.drawColorRectangles(g)

    def drawColorRectangles(self, g):
        g.setColor(Color(120, 50, 10))
        g.fillRect(10, 15, 90, 60)


class App(JFrame):
    def __init__(self):
        super(App, self).__init__()
        canvas = Canvas()
        self.getContentPane().add(canvas)
        self.setTitle("Colors")
        self.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE)
        self.setSize(500, 400)
        self.locationRelativeTo = None
        self.setVisible(True)
        print "second: {0}".format(SwingUtilities.isEventDispatchThread())

if __name__ == '__main__':
    print "first: {0}".format(SwingUtilities.isEventDispatchThread())
    invokeLater(lambda: App())()
